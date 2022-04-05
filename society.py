import substrateinterface
import pprint
from enum import Enum

pp = pprint.PrettyPrinter(indent=4)

class MemberState(Enum):
    MEMBER = 1
    CANDIDATE = 2
    SUSPENDED_MEMBER = 3
    SUSPENDED_CANDIDATE = 4
    NON_MEMBER = 5

ws_url = "wss://kusama-rpc.polkadot.io"
# Hope we can leave the interface open for the whole session
rpc = substrateinterface.SubstrateInterface(url = ws_url)

test_accounts = {
    'member': 'FUfBKr2pDxKrxmExGp4hjU6St4BDgffzKcyAqv6pruGnez1',
    'nonmember': 'D6CuPyACRzF5a7vkRX4UF9Vhw1TBneEo81jUmuhBYvCZ27Y',
    'suspended_member': 'CgEt8AwW9SThQXpLBAZy3MpKgNG7ZHaEDGeV5MLqHVPVoJg',
    'suspended_candidate': 'EkjeSWp3BsyJoh9hbRa6JbnWFWN3g3dnfvhGeqjLmL1FdNA',
    'candidate': 'FXKYsF5CujHpwL5MegfrXkUB657mLA2Xfx7WbZkrN21BxpC',
    'founder': 'Dikw9VJqJ4fJFcXuKaSqu3eSwBQM6zC8ja9rdAP3RbfeK1Y',
    'bad_addr': 'asdasdasdasd',
}

def is_member(address):
    return address in rpc.query(module = 'Society', storage_function = 'Members').value

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

def get_strikes(address):
    return rpc.query(module = 'Society', storage_function = 'Strikes', params = [address]).value

def get_matrix(address):
    try:
        return rpc.query(module = 'Identity', storage_function = 'IdentityOf', params = [address]).value['info']['riot']['Raw']
    except:
        return None

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

for account,address in test_accounts.items():
    try:
        print(f'{account}:{address}')
        pp.pprint(get_member_info(address))
    except:
        print(f'error with {account}:{address}')