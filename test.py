import society
import pprint
pp = pprint.PrettyPrinter(indent=4)

test_accounts = {
    'member': 'FUfBKr2pDxKrxmExGp4hjU6St4BDgffzKcyAqv6pruGnez1',
    'nonmember': 'D6CuPyACRzF5a7vkRX4UF9Vhw1TBneEo81jUmuhBYvCZ27Y',
    'suspended_member': 'CgEt8AwW9SThQXpLBAZy3MpKgNG7ZHaEDGeV5MLqHVPVoJg',
    'suspended_candidate': 'EkjeSWp3BsyJoh9hbRa6JbnWFWN3g3dnfvhGeqjLmL1FdNA',
    # This one will need updating regularly until we have a decent test chain
    'candidate': 'FXKYsF5CujHpwL5MegfrXkUB657mLA2Xfx7WbZkrN21BxpC',
    'founder': 'Dikw9VJqJ4fJFcXuKaSqu3eSwBQM6zC8ja9rdAP3RbfeK1Y',
    'bad_addr': 'asdasdasdasd',
}

def test_membership_states():
    assert society.get_member_state(test_accounts['member']) == society.MemberState.MEMBER
    assert society.get_member_state(test_accounts['nonmember']) == society.MemberState.NON_MEMBER
    assert society.get_member_state(test_accounts['suspended_member']) == society.MemberState.SUSPENDED_MEMBER
    assert society.get_member_state(test_accounts['suspended_candidate']) == society.MemberState.SUSPENDED_CANDIDATE
    assert society.get_member_state(test_accounts['candidate']) == society.MemberState.CANDIDATE
    # The founder is just another member
    assert society.get_member_state(test_accounts['founder']) == society.MemberState.MEMBER

