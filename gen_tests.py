import random
import society
import pprint

soc = society.Society()

test_accounts = {
    'member': 'FUfBKr2pDxKrxmExGp4hjU6St4BDgffzKcyAqv6pruGnez1',
    'nonmember': 'D6CuPyACRzF5a7vkRX4UF9Vhw1TBneEo81jUmuhBYvCZ27Y',
    'bad_addr': 'asdasdasdasd',
}

test_accounts['defender'] = soc.get_defending_raw()[0]
test_accounts['founder'] = soc.get_founder()
candidates = soc.get_candidates_raw()
if len(candidates) > 0:
    test_accounts['candidate'] = random.choice(candidates)[0]
suspended_members = soc.get_suspended_members_addresses()
if len(suspended_members) > 0:
    test_accounts['suspended_member'] = random.choice(suspended_members)

pp = pprint.PrettyPrinter(indent=4)
pp.pprint(test_accounts)