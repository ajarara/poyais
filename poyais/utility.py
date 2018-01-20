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


# this makes it so that all we need to report parse errors is the
# index at which it occured.
def build_idx_line_map(program_string):
    newline_reg = re.compile("\n")
    # thank you tim sort
    return sorted(x.start() for x in newline_reg.finditer(program_string))
