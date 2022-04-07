import substrateinterface
from enum import Enum

class MemberState(Enum):
    MEMBER = 1
    CANDIDATE = 2
    SUSPENDED_MEMBER = 3
    SUSPENDED_CANDIDATE = 4
    NON_MEMBER = 5

ws_url = "wss://kusama-rpc.polkadot.io"
# Hope we can leave the interface open for the whole session
rpc = substrateinterface.SubstrateInterface(url = ws_url)

# gets
def get_members():
    return rpc.query(module = 'Society', storage_function = 'Members').value

def get_candidates():
    return rpc.query(module = 'Society', storage_function = 'Candidates').value

def get_strikes(address):
    return rpc.query(module = 'Society', storage_function = 'Strikes', params = [address]).value

def get_defender(address):
    return rpc.query(module = 'Society', storage_function = 'Defender', params = [address]).value

def get_matrix(address):
    try:
        return rpc.query(module = 'Identity', storage_function = 'IdentityOf', params = [address]).value['info']['riot']['Raw']
    except:
        return None

# checks

def is_member(address):
    return address in get_members()

def is_suspended_member(address):
    return rpc.query(module = 'Society', storage_function = 'SuspendedMembers', params = [address] ).value

def is_candidate(address):
    for candidate in rpc.query(module = 'Society', storage_function = 'Candidates').value:
        if candidate['who'] == address:
            return True

def is_suspended_candidate(address):
    return rpc.query(module = 'Society', storage_function = 'SuspendedCandidates', params = [address] ).value

def is_founder(address):
    return rpc.query(module = 'Society', storage_function = 'Founder').value == address

def get_member_info(address):
    info = {
        'address': address,
        'state': get_member_state(address),
        'element_handle': get_matrix(address),
        'strikes': get_strikes(address),
        'is_founder': is_founder(address),
    }
    return info

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
