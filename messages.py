from mako.template import Template

def candidates_message(candidates):
    DIVISOR = 1000000000000
    template = Template("""\
% if len(candidates) > 1:
The current candidates are:
%   for candidate in candidates:
* ${candidate[0]}
  * Bid: ${candidate[1]['bid']/DIVISOR} KSM
  * Approvals: ${candidate[1]['tally']['approvals']}, Rejections: ${candidate[1]['tally']['rejections']}
%   endfor
% elif len(candidates) == 1:
* ${candidates[0][0]}
  * Bid: ${candidates[0][1]['bid']/DIVISOR} KSM
  * Approvals: ${candidates[0][1]['tally']['approvals']}, Rejections: ${candidates[0][1]['tally']['rejections']}
% else:
There are no candidates
% endif
""")
    return template.render(candidates = candidates, DIVISOR = DIVISOR)

def period_message(candidate_period, defender_info, candidates, head, new_period: True):
    candidate_text = candidates_message(candidates)
    print(candidate_period)
    template = Template("""\
<% import math %>
% if new_period:
A new candidate period has started.
% endif

% if candidate_period.period == "voting":
We are currently in the voting period. Candidates should provide proof of ink. Members should vote on candidates. Blocks until end of voting period: ${candidate_period.voting_blocks_left} (${candidate_period.voting_time_left.days} days, ${math.floor(candidate_period.voting_time_left.seconds / 3600)} hours, ${math.floor(candidate_period.voting_time_left.seconds % 3600 / 60)} minutes, ${candidate_period.voting_time_left.seconds % 60} seconds)
 
${candidate_text}
% endif

% if candidate_period.period == "claim":
We are currently in the claim period. If you were a candidate in the previous period and received a clear majority of votes, you may now claim your membership. Blocks until end of claim period: ${candidate_period.claim_blocks_left} (${candidate_period.claim_time_left.days} days, ${math.floor(candidate_period.claim_time_left.seconds / 3600)} hours, ${math.floor(candidate_period.claim_time_left.seconds % 3600 / 60)} minutes, ${candidate_period.claim_time_left.seconds % 60} seconds)
% endif

% if candidate_period.period == "voting":
The current head is ${head}.
% endif

-----

%if candidate_period.period == "voting" and new_period:
A new challenge period has also started.
%endif

<%
challenge_blocks = candidate_period.voting_blocks_left + candidate_period.claim_blocks_left
challenge_time_left = candidate_period.voting_time_left + candidate_period.claim_time_left
%>
There are currently ${challenge_blocks} blocks (${challenge_time_left.days} days, ${math.floor(challenge_time_left.seconds / 3600)} hours, ${math.floor(challenge_time_left.seconds % 3600 / 60)} minutes, ${challenge_time_left.seconds % 60} seconds) until the end of the challenge period.

The current defender is ${defender_info[0]}.
% if not new_period:
  * Approvals: ${defender_info[2]['approvals']}
  * Rejections: ${defender_info[2]['rejections']}
% endif

The current skeptic is ${defender_info[1]}.
""")
    return template.render(candidate_period = candidate_period, defender_info = defender_info, candidate_text = candidate_text, head = head, new_period = new_period)

