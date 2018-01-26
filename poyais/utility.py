from collections import namedtuple
import re


def memoize(fun):
    cache = {}

    def memoized(*args, **kwargs):
        hashable_params = (
            args,
            frozenset(kwargs.items()))
        if hashable_params not in cache:
            out = fun(*args, **kwargs)
            cache[hashable_params] = out
            return out
        else:
            return cache[hashable_params]
    return memoized


def node_from_iterable(it):
    got = reversed(it)
    here = None
    for thing in got:
        here = Node(thing, here)
    return here


class Node:
    def __init__(self, value, link=None):
        self.value = value
        assert link is None or isinstance(link, Node)
        self.link = link

    def __iter__(self):
        here = self
        while here is not None:
            yield here.value
            here = here.link

    # @memoize
    def __len__(self):
        return len(self.value) + (
            len(self.link) if self.link else 0)


@memoize
def what_is_linum_of_idx(program_string, absolute_idx):
    line_map = build_idx_line_map(program_string)
    if not line_map:
        return Linum(1, absolute_idx)
    line_num = _search(line_map, absolute_idx)
    if line_num == 0:
        chars_consumed = 0
    else:
        chars_consumed = line_map[line_num]
    
    return Linum(1 + line_num, absolute_idx - chars_consumed)


# mapping is implicit, the index of the match is the line number it is on.
def build_idx_line_map(program_string):
    newline_reg = re.compile("\n")
    return sorted(x.start() for x in newline_reg.finditer(program_string))


Linum = namedtuple('Linum', ('line', 'relative_idx'))


def _search(listing, absolute_idx):
    """
    Assuming the idx is in the string that generated the listing, find
    the line that it was on.
    """
    if not listing:
        return 0
    if len(listing) == 1:
        return 0 if absolute_idx <= listing[0] else 1

    lower = 0
    for idx, num in enumerate(listing):
        if num < absolute_idx:
            lower = num
        if num >= absolute_idx:
            return lower
