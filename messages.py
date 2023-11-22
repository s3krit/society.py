from mako.template import Template

# Formats a list as a markdown bulleted list
def format_list(list):
    response = ""
    for item in list:
        response += "* {}\n".format(item)
    return response

def new_period_message(blocks_left, defender_info, candidates, head, new_period: True):
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

% if len(candidates) > 0:
The current candidates are:
${format_list(candidates)}
% else:
There are no candidates for this period.
% endif
""")
    return template.render(blocks_left = blocks_left, defender_info = defender_info, candidates = candidates, head = head, new_period = new_period)

