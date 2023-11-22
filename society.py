from enum import Enum
import re
import sqlite3
import time
from substrateinterface import SubstrateInterface
import logging
logging.getLogger()

class MemberState(Enum):
    MEMBER = 1
    CANDIDATE = 2
    SUSPENDED_MEMBER = 3
    SUSPENDED_CANDIDATE = 4
    NON_MEMBER = 5

class Period(Enum):
    CLAIM =1
    VOTING = 2

DEFAULT_DB_PATH = "./society_overrides.db"
DEFAULT_RPC_URL = "wss://kusama-rpc.polkadot.io/"
def init(rpc_url=DEFAULT_RPC_URL, db_path=DEFAULT_DB_PATH):
    # Hope we can leave the interface open for the whole session
    global __RPC__
    __RPC__ = SubstrateInterface(url = rpc_url)

    # We set up a database for locally overriding things like matrix handle
    global __DB_CONN__
    global __DB_CUR__
    __DB_CONN__ = sqlite3.connect(db_path)
    __DB_CUR__ = __DB_CONN__.cursor()

def rpc_call(module, storage_function, params = [], map = False):
    # Loop 10 times attempting to make the call
    for i in range(10):
        try:
            if map:
                return __RPC__.query_map(module = module, storage_function = storage_function, params = params)
            else:
                return __RPC__.query(module = module, storage_function = storage_function, params = params)
        except Exception as e:
            logging.error("RPC call failed {} times, :{}, retrying in 5s".format(i+1,e))
            time.sleep(5)
            try:
                __RPC__.connect_websocket()
            except Exception as e:
                logging.error("Websocket connection failed: {}".format(e))
    logging.error("RPC call failed 10 times, giving up. Probably restart the bot")

# sets

# sets an override for the matrix handle - will use this even if the address has an identity set
def set_matrix_handle(address, matrix_handle):
    if not is_valid_matrix_handle(matrix_handle) or not is_valid_address(address):
        return False
    __DB_CUR__.execute(''' INSERT OR REPLACE INTO accounts (address, matrix_handle) VALUES (?, ?) ''', (address, matrix_handle))
    __DB_CONN__.commit()
    return True

def unset_matrix_handle(address):
    __DB_CUR__.execute(''' DELETE FROM accounts WHERE address = ? ''', (address,))
    __DB_CONN__.commit()
    return True

# gets
def get_members_addresses():
    members = rpc_call(module = 'Society', storage_function = 'Members', map = True)
    return list(map(lambda x: x.decode(), map(lambda x: x[0], members)))

def get_candidates_addresses():
    candidates = rpc_call(module = 'Society', storage_function = 'Candidates', map = True)
    return list(candidates)

def get_candidates():
    candidates = []
    for candidate in get_candidates_addresses():
        handle = get_matrix_handle(candidate['who'])
        if handle:
            candidates.append(handle)
        else:
            candidates.append(candidate['who'])
    return candidates

def get_strikes(address):
    return rpc_call(module = 'Society', storage_function = 'Members', params = [address]).decode()['strikes']

def get_defending_raw():
    return list(rpc_call(module = 'Society', storage_function = 'Defending').decode())

def get_head_address():
    return rpc_call(module = 'Society', storage_function = 'Head').decode()

def get_defending():
    defender_info = get_defending_raw()
    defender = defender_info[0]
    skeptic = defender_info[1]
    # Remove skeptic from return result
    if defender:
        handle = get_matrix_handle(defender)
        if handle:
            defender_info[0] = handle
    if skeptic:
        handle = get_matrix_handle(skeptic)
        if handle:
            defender_info[1] = handle
    return defender_info

def get_matrix_handle(address):
    # first check if we have an override
    __DB_CUR__.execute(''' SELECT matrix_handle FROM accounts WHERE address = ? ''', (address,))
    __DB_CONN__.commit()
    row = __DB_CUR__.fetchone()
    if row:
        return row[0]
    try:
        return rpc_call(module = 'Identity', storage_function = 'IdentityOf', params = [address]).value['info']['riot']['Raw']
    except:
        return None

def get_member_info(address):
    info = {
        'address': address,
        'state': get_member_state(address),
        'element_handle': get_matrix_handle(address),
        'strikes': get_strikes(address),
        'is_founder': is_founder(address),
        'is_defender': is_defender(address),
    }
    return info

def get_founder():
    return rpc_call(module = 'Society', storage_function = 'Founder').value

def get_member_state(address):
    if is_member(address):
        return MemberState.MEMBER
    elif is_suspended_member(address):
        return MemberState.SUSPENDED_MEMBER
    elif is_candidate(address):
        return MemberState.CANDIDATE
    elif is_suspended_candidate(address):
        return MemberState.SUSPENDED_CANDIDATE
    else:
        return MemberState.NON_MEMBER

def get_blocks_until_next_period():
    # Current block number
    block = rpc_call(module = "System", storage_function = "Number").value
    period = 100800
    return period - (block % period)

def get_address_for_matrix_handle(matrix_handle):
    # first check if we have an override
    __DB_CUR__.execute(''' SELECT address FROM accounts WHERE matrix_handle = ? ''', (matrix_handle,))
    __DB_CONN__.commit()
    row = __DB_CUR__.fetchone()
    if row:
        return row[0]
    # try:
    #     return rpc_call(module = 'Identity', storage_function = 'SubsOf', params = [matrix_handle]).value
    # except:
    #     return None
    else:
        return None

# checks

def is_member(address):
    return address in get_members_addresses()

def is_suspended_member(address):
    return rpc_call(module = 'Society', storage_function = 'SuspendedMembers', params = [address] ).value

def is_candidate(address):
    for candidate in get_candidates_addresses():
        if candidate['who'] == address:
            return True

def is_suspended_candidate(address):
    return rpc_call(module = 'Society', storage_function = 'SuspendedCandidates', params = [address] ).value

def is_founder(address):
    return rpc_call(module = 'Society', storage_function = 'Founder').value == address

def is_defender(address):
    return get_defending_raw()[0] == address

# util
def is_valid_matrix_handle(matrix_handle):
    matrix_handle_re = re.compile(r'^@[^:]+:.*\..*$')
    return bool(matrix_handle_re.search(matrix_handle))

def is_valid_address(address):
    return __RPC__.is_valid_ss58_address(address)
