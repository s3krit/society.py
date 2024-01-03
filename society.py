from enum import Enum
import re
import sqlite3
import time
import logging
from dataclasses import dataclass

import substrateinterface
logging.getLogger()

# util
def is_valid_matrix_handle(matrix_handle):
    matrix_handle_re = re.compile(r'^@[^:]+:.*\..*$')
    return bool(matrix_handle_re.search(matrix_handle))

def is_valid_address(address):
    return substrateinterface.base.is_valid_ss58_address(address)

class MemberState(Enum):
    MEMBER = 1
    CANDIDATE = 2
    SUSPENDED_MEMBER = 3
    NON_MEMBER = 5

import datetime
@dataclass
class Period:
    period: str = "voting"
    voting_blocks_left: int = 72000
    claim_blocks_left: int = 28800
    voting_time_left: datetime.timedelta = datetime.timedelta(seconds = voting_blocks_left * 6)
    claim_time_left: datetime.timedelta = datetime.timedelta(seconds = claim_blocks_left * 6)

    def __post_init__(self):
        self.voting_time_left = datetime.timedelta(seconds = self.voting_blocks_left * 6)
        self.claim_time_left = datetime.timedelta(seconds = self.claim_blocks_left * 6)

class Society:

    DEFAULT_DB_PATH = "./society_overrides.db"
    DEFAULT_RPC_URL = "wss://kusama-rpc.polkadot.io/"

    def __init__(self, rpc_url=DEFAULT_RPC_URL, db_path=DEFAULT_DB_PATH):
        self.rpc = substrateinterface.SubstrateInterface(url = rpc_url)
        self.db_conn = sqlite3.connect(db_path)
        self.db_cur = self.db_conn.cursor()

    def rpc_call(self, module, storage_function, params = [], map = False):
        # Loop 10 times attempting to make the call
        for i in range(10):
            self.rpc.connect_websocket()
            try:
                if map:
                    return self.rpc.query_map(module = module, storage_function = storage_function, params = params)
                else:
                    return self.rpc.query(module = module, storage_function = storage_function, params = params)
            except Exception as e:
                logging.error("RPC call failed {} times, :{}, retrying in 5s".format(i+1,e))
                time.sleep(5)
                try:
                    self.rpc.connect_websocket()
                except Exception as e:
                    logging.error("Websocket connection failed: {}".format(e))
        logging.error("RPC call failed 10 times, giving up. Probably restart the bot")

    # sets

    # sets an override for the matrix handle - will use this even if the address has an identity set
    def set_matrix_handle(self, address, matrix_handle):
        if not is_valid_matrix_handle(matrix_handle) or not is_valid_address(address):
            return False
        self.db_cur.execute(''' INSERT OR REPLACE INTO accounts (address, matrix_handle) VALUES (?, ?) ''', (address, matrix_handle))
        self.db_conn.commit()
        return True

    def unset_matrix_handle(self, address):
        self.db_cur.execute(''' DELETE FROM accounts WHERE matrix_handle = ? ''', (address,))
        self.db_conn.commit()
        return True if self.db_cur.rowcount > 0 else False

    # gets
    def get_members_addresses(self):
        members = self.rpc_call(module = 'Society', storage_function = 'Members', map = True)
        return list(map(lambda x: x.decode(), map(lambda x: x[0], members)))
    
    def get_suspended_members_addresses(self):
        members = self.rpc_call(module = 'Society', storage_function = 'SuspendedMembers', map = True)
        return list(map(lambda x: x.decode(), map(lambda x: x[0], members)))

    def get_candidates_raw(self):
        candidates = self.rpc_call(module = 'Society', storage_function = 'Candidates', map = True)
        return list(map(lambda candidate: (list(map(lambda field: field.decode(), candidate))), candidates))

    def get_candidates(self):
        candidates = self.get_candidates_raw()
        for candidate in candidates:
            handle = self.get_matrix_handle(candidate[0])
            if handle:
                candidate[0] = handle
        return candidates

    def get_strikes(self, address):
        if self.is_member(address) or self.is_suspended_member(address):
            return self.rpc_call(module = 'Society', storage_function = 'Members', params = [address]).decode()['strikes']
        else:
            return 0

    def get_defending_raw(self):
        return list(self.rpc_call(module = 'Society', storage_function = 'Defending').decode())

    def get_head_address(self):
        return self.rpc_call(module = 'Society', storage_function = 'Head').decode()

    def get_defending(self):
        defender_info = self.get_defending_raw()
        defender = defender_info[0]
        skeptic = defender_info[1]
        # Remove skeptic from return result
        if defender:
            handle = self.get_matrix_handle(defender)
            if handle:
                defender_info[0] = handle
        if skeptic:
            handle = self.get_matrix_handle(skeptic)
            if handle:
                defender_info[1] = handle
        return defender_info

    def get_candidate_skeptic(self):
        skeptic = self.rpc_call(module = 'Society', storage_function = 'Skeptic').decode()
        if skeptic:
            handle = self.get_matrix_handle(skeptic)
            if handle:
                return handle
        return skeptic

    def get_matrix_handle(self, address):
        # first check if we have an override
        self.db_cur.execute(''' SELECT matrix_handle FROM accounts WHERE address = ? ''', (address,))
        self.db_conn.commit()
        row = self.db_cur.fetchone()
        if row:
            return row[0]
        try:
            return self.rpc_call(module = 'Identity', storage_function = 'IdentityOf', params = [address]).value['info']['riot']['Raw']
        except:
            return None

    def get_member_info(self, address):
        info = {
            'address': address,
            'state': self.get_member_state(address),
            'element_handle': self.get_matrix_handle(address),
            'strikes': self.get_strikes(address),
            'is_founder': self.is_founder(address),
            'is_defender': self.is_defender(address),
        }
        return info

    def get_founder(self):
        return self.rpc_call(module = 'Society', storage_function = 'Founder').value

    def get_member_state(self, address):
        if self.is_member(address):
            return MemberState.MEMBER
        elif self.is_suspended_member(address):
            return MemberState.SUSPENDED_MEMBER
        elif self.is_candidate(address):
            return MemberState.CANDIDATE
        else:
            return MemberState.NON_MEMBER

    def get_candidate_period(self):
        block = self.rpc_call(module = "System", storage_function = "Number").value
        # vote period = 5 days in blocks
        vote_period = 72000
        # claim period = 2 days in blocks
        claim_period = 28800
        if block % (vote_period + claim_period) < vote_period:
            period = "voting"
            voting_blocks_left = vote_period - block % (vote_period + claim_period)
            claim_blocks_left = claim_period
            return Period(period, voting_blocks_left, claim_blocks_left)
        else:
            period = "claim"
            voting_blocks_left = 0
            claim_blocks_left = vote_period + claim_period - block % (vote_period + claim_period)
            return Period(period, voting_blocks_left, claim_blocks_left)

    def get_address_for_matrix_handle(self, matrix_handle):
        # first check if we have an override
        self.db_cur.execute(''' SELECT address FROM accounts WHERE matrix_handle = ? ''', (matrix_handle,))
        self.db_conn.commit()
        row = self.db_cur.fetchone()
        if row:
            return row[0]
        # try:
        #     return self.rpc_call(module = 'Identity', storage_function = 'SubsOf', params = [matrix_handle]).value
        # except:
        #     return None
        else:
            return None
        
    # checks

    def is_member(self, address):
        return address in self.get_members_addresses()

    def is_suspended_member(self, address):
        return self.rpc_call(module = 'Society', storage_function = 'SuspendedMembers', params = [address] ).value

    def is_candidate(self, address):
        for candidate in self.get_candidates_raw():
            if candidate[0] == address:
                return True

    def is_founder(self, address):
        return self.rpc_call(module = 'Society', storage_function = 'Founder').value == address

    def is_defender(self, address):
        return self.get_defending_raw()[0] == address
