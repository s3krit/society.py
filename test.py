import society
import pprint
import db_setup

pp = pprint.PrettyPrinter(indent=4)

test_accounts = {
    'member': 'FUfBKr2pDxKrxmExGp4hjU6St4BDgffzKcyAqv6pruGnez1',
    'nonmember': 'D6CuPyACRzF5a7vkRX4UF9Vhw1TBneEo81jUmuhBYvCZ27Y',
    'suspended_member': 'CgEt8AwW9SThQXpLBAZy3MpKgNG7ZHaEDGeV5MLqHVPVoJg',
    'suspended_candidate': 'EkjeSWp3BsyJoh9hbRa6JbnWFWN3g3dnfvhGeqjLmL1FdNA',
    # This one will need updating regularly until we have a decent test chain
    'candidate': 'FXKYsF5CujHpwL5MegfrXkUB657mLA2Xfx7WbZkrN21BxpC',
    'founder': 'Dikw9VJqJ4fJFcXuKaSqu3eSwBQM6zC8ja9rdAP3RbfeK1Y',
    'defender': 'Ft2cSCw4V47d2S7V9nN2S6V5ByGmAnkfbkFbWUVuHVuaMvW',
    'bad_addr': 'asdasdasdasd',
}
society.init("wss://kusama-rpc.polkadot.io/", "./society_overrides_test.db")
db_setup.setup_test()

def test_membership_enum():
    assert society.get_member_state(test_accounts['member']) == society.MemberState.MEMBER
    assert society.get_member_state(test_accounts['nonmember']) == society.MemberState.NON_MEMBER
    assert society.get_member_state(test_accounts['suspended_member']) == society.MemberState.SUSPENDED_MEMBER
    assert society.get_member_state(test_accounts['suspended_candidate']) == society.MemberState.SUSPENDED_CANDIDATE
    assert society.get_member_state(test_accounts['candidate']) == society.MemberState.CANDIDATE
    # The founder is just another member
    assert society.get_member_state(test_accounts['founder']) == society.MemberState.MEMBER

def test_additional_membership_functions():
    assert society.is_founder(test_accounts['founder'])
    assert society.is_defender(test_accounts['defender'])

def test_matrix_handle_overrides():
    matrix_test_accounts = {
        # Has a matrix account defined on-chain
        "onchain_matrix": "FUfBKr2pDxKrxmExGp4hjU6St4BDgffzKcyAqv6pruGnez1",
        # Has a matrix account defined in the database but *not* on-chain
        "offchain_matrix": "D6CuPyACRzF5a7vkRX4UF9Vhw1TBneEo81jUmuhBYvCZ27Y",
        # Has a matrix account on-chain that is overriden by the database
        "overridden_matrix": "HL8bEp8YicBdrUmJocCAWVLKUaR2dd1y6jnD934pbre3un1",
    }
    assert society.get_matrix(matrix_test_accounts['onchain_matrix']) == "@s3krit:fairydust.space"
    assert society.get_matrix(matrix_test_accounts['offchain_matrix']) == "@testuser1:matrix.org"
    assert society.get_matrix(matrix_test_accounts['overridden_matrix']) == "@testuser2:matrix.org"

def test_setting_and_unsetting_override():
    test_account = "FUfBKr2pDxKrxmExGp4hjU6St4BDgffzKcyAqv6pruGnez1"
    assert society.get_matrix(test_account) == "@s3krit:fairydust.space"
    society.set_matrix(test_account, "@testoverride:matrix.org")
    assert society.get_matrix(test_account) == "@testoverride:matrix.org"
    society.unset_matrix(test_account)
    assert society.get_matrix(test_account) == "@s3krit:fairydust.space"