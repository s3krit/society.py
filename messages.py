from mako.template import Template


# Formats a list as a markdown bulleted list
def format_list(list):
    response = ""
    for item in list:
        response += "* {}\n".format(item)
    return response

def candidates_message(candidates):
    DIVISOR = 1000000000000
    template = Template("""\
% if len(candidates) > 0:
The current candidates are:
%   for candidate in candidates:
* ${candidate[0]}
  * Bid: ${candidate[1]['bid']/DIVISOR} KSM
  * Approvals: ${candidate[1]['tally']['approvals']}, Rejections: ${candidate[1]['tally']['rejections']}
%   endfor
% else:
There are no candidates
% endif
""")
    return template.render(candidates = candidates, DIVISOR = DIVISOR)

def new_period_message(blocks_left, defender_info, candidates, head, new_period: True):
    candidate_text = candidates_message(candidates)
    template = Template("""\
% if new_period:
A new period has started. Blocks until next period: ${blocks_left}
% else:
Blocks until next period: ${blocks_left}
% endif

The current head is ${head}.

The current defender is ${defender_info[0]}.
% if not new_period:
They currently have ${defender_info[2]['approvals']} approvals and ${defender_info[2]['rejections']} rejections.
% endif

The current skeptic is ${defender_info[1]}.

${candidate_text}
""")
    return template.render(blocks_left = blocks_left, defender_info = defender_info, candidate_text = candidate_text, head = head, new_period = new_period)

