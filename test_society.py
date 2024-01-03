import society
import pprint
import db_setup

pp = pprint.PrettyPrinter(indent=4)

test_accounts = {
    'bad_addr': 'asdasdasdasd',
    'candidate': 'G75yJUM2TveDikvysHHW5XhkP35gXqDAsgRLYQTh3gVDir9',
    'defender': 'DGE8ATd2NaitqX4jdvZNXFNMmY9Qui6swnfoheCiz7efWGG',
    'founder': 'Dikw9VJqJ4fJFcXuKaSqu3eSwBQM6zC8ja9rdAP3RbfeK1Y',
    'member': 'FUfBKr2pDxKrxmExGp4hjU6St4BDgffzKcyAqv6pruGnez1',
    'nonmember': 'D6CuPyACRzF5a7vkRX4UF9Vhw1TBneEo81jUmuhBYvCZ27Y',
    'suspended_member': 'J9c2fcmRhhNaJAxA8yLMkxap7PEWuYc1UaaTqxunfKscjG3'
}

soc = society.Society("wss://kusama-rpc.polkadot.io/", "./society_overrides_test.db")
db_setup.setup_test()

def test_membership_enum():
    assert soc.get_member_state(test_accounts['member']) == society.MemberState.MEMBER
    assert soc.get_member_state(test_accounts['nonmember']) == society.MemberState.NON_MEMBER
    assert soc.get_member_state(test_accounts['suspended_member']) == society.MemberState.SUSPENDED_MEMBER
    assert soc.get_member_state(test_accounts['candidate']) == society.MemberState.CANDIDATE
    # The founder is just another member
    assert soc.get_member_state(test_accounts['founder']) == society.MemberState.MEMBER

def test_additional_membership_functions():
    assert soc.is_founder(test_accounts['founder'])
    assert soc.is_defender(test_accounts['defender'])

# def test_matrix_handle_overrides():
#     matrix_test_accounts = {
#         # Has a matrix account defined on-chain
#         "onchain_matrix": "FUfBKr2pDxKrxmExGp4hjU6St4BDgffzKcyAqv6pruGnez1",
#         # Has a matrix account defined in the database but *not* on-chain
#         "offchain_matrix": "D6CuPyACRzF5a7vkRX4UF9Vhw1TBneEo81jUmuhBYvCZ27Y",
#         # Has a matrix account on-chain that is overriden by the database
#         "overridden_matrix": "HL8bEp8YicBdrUmJocCAWVLKUaR2dd1y6jnD934pbre3un1",
#     }
#     assert soc.get_matrix_handle(matrix_test_accounts['onchain_matrix']) == "@s3krit:fairydust.space"
#     assert soc.get_matrix_handle(matrix_test_accounts['offchain_matrix']) == "@testuser1:matrix.org"
#     assert soc.get_matrix_handle(matrix_test_accounts['overridden_matrix']) == "@testuser2:matrix.org"

# def test_setting_and_unsetting_override():
#     test_account = "FUfBKr2pDxKrxmExGp4hjU6St4BDgffzKcyAqv6pruGnez1"
#     assert soc.get_matrix_handle(test_account) == "@s3krit:fairydust.space"
#     soc.set_matrix_handle(test_account, "@testoverride:matrix.org")
#     assert soc.get_matrix_handle(test_account) == "@testoverride:matrix.org"
#     soc.unset_matrix_handle(test_account)
#     assert soc.get_matrix_handle(test_account) == "@s3krit:fairydust.space"

def test_matrix_handle_validation():
    test_cases = {
        "@testuser:matrix.org" : True,
        "asdasdas dasf sdf " : False,
        "testuser@matrix.org" : False,
        "@good_address:matrix.org" : True,
        "@test:dodgydomain." : True,
    }
    for test_case in test_cases:
        assert society.is_valid_matrix_handle(test_case) == test_cases[test_case]
