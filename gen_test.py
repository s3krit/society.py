import random
import society
import pickle

society.init()

test_accounts = {
    'member': 'FUfBKr2pDxKrxmExGp4hjU6St4BDgffzKcyAqv6pruGnez1',
    'nonmember': 'D6CuPyACRzF5a7vkRX4UF9Vhw1TBneEo81jUmuhBYvCZ27Y',
    'suspended_member': 'CgEt8AwW9SThQXpLBAZy3MpKgNG7ZHaEDGeV5MLqHVPVoJg',
    'suspended_candidate': 'EkjeSWp3BsyJoh9hbRa6JbnWFWN3g3dnfvhGeqjLmL1FdNA',
    'candidate': 'D2wLG2HMJfYkpnSnSTrYYH5Js5yooNTwKotxx55ayfriefH',
    'bad_addr': 'asdasdasdasd',
}

test_accounts['defender'] = society.get_defending_raw()
test_accounts['founder'] = society.get_founder()
candidates = society.get_candidates_addresses()
if len(candidates) > 0:
    test_accounts['candidate'] = random.choice(candidates)['who']

print(test_accounts)
