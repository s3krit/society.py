from enum import Enum
import re
import sqlite3
from substrateinterface import SubstrateInterface

class MemberState(Enum):
    MEMBER = 1
    CANDIDATE = 2
    SUSPENDED_MEMBER = 3
    SUSPENDED_CANDIDATE = 4
    NON_MEMBER = 5

DEFAULT_DB_PATH = "./society-overrides.db"
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

# sets

# sets an override for the matrix handle - will use this even if the address has an identity set
def set_matrix(address, matrix_handle):
    if not is_valid_matrix_handle(matrix_handle):
        return False
    __DB_CUR__.execute(''' INSERT OR REPLACE INTO accounts (address, matrix_handle) VALUES (?, ?) ''', (address, matrix_handle))
    __DB_CONN__.commit()
    return True

def unset_matrix(address):
    __DB_CUR__.execute(''' DELETE FROM accounts WHERE address = ? ''', (address,))
    __DB_CONN__.commit()
    return True

# gets
def get_members():
    return __RPC__.query(module = 'Society', storage_function = 'Members').value

def get_candidates():
    return __RPC__.query(module = 'Society', storage_function = 'Candidates').value

def get_strikes(address):
    return __RPC__.query(module = 'Society', storage_function = 'Strikes', params = [address]).value

def get_defender():
    return __RPC__.query(module = 'Society', storage_function = 'Defender').value

def get_matrix_handle(address):
    # first check if we have an override
    __DB_CUR__.execute(''' SELECT matrix_handle FROM accounts WHERE address = ? ''', (address,))
    __DB_CONN__.commit()
    row = __DB_CUR__.fetchone()
    if row:
        return row[0]
    try:
        return __RPC__.query(module = 'Identity', storage_function = 'IdentityOf', params = [address]).value['info']['riot']['Raw']
    except:
        return None

def get_member_info(address):
    info = {
        'address': address,
        'state': get_member_state(address),
        'element_handle': get_matrix_handle(address),
        'strikes': get_strikes(address),
        'is_founder': is_founder(address),
    }
    return info

def get_founder():
    return __RPC__.query(module = 'Society', storage_function = 'Founder').value

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

# checks

def is_member(address):
    return address in get_members()

def is_suspended_member(address):
    return __RPC__.query(module = 'Society', storage_function = 'SuspendedMembers', params = [address] ).value

def is_candidate(address):
    for candidate in __RPC__.query(module = 'Society', storage_function = 'Candidates').value:
        if candidate['who'] == address:
            return True

def is_suspended_candidate(address):
    return __RPC__.query(module = 'Society', storage_function = 'SuspendedCandidates', params = [address] ).value

def is_founder(address):
    return __RPC__.query(module = 'Society', storage_function = 'Founder').value == address

def is_defender(address):
    return get_defender() == address

# util
def is_valid_matrix_handle(matrix_handle):
    matrix_handle_re = re.compile(r'^@[^:]+:.*\..*$')
    return bool(matrix_handle_re.search(matrix_handle))
