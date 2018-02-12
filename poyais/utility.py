from collections import namedtuple
import operator
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
        here = LanguageNode(thing, here)
    return here


# idx would be useful for compile errors.
# but since this is a PoC, leave it for now.
LanguageToken = namedtuple('LanguageToken', ('tag', 'match'))

# mostly for empty matches
UtilityToken = namedtuple('UtilityToken', ('tag', 'match'))


class LanguageNode:
    def __init__(self, value, link=None):
        self.value = value
        assert link is None or isinstance(link, LanguageNode)
        self.link = link

    def __iter__(self):
        here = self
        while here is not None:
            yield here.value
            here = here.link

    def __str__(self):
        return "".join(str(token.match) for token in iter_traverse(self))

    def __len__(self):
        got = iter_traverse(self)
        return sum(len(token.match) for token in got)

    def __repr__(self):
        return "LanguageNode({}{})".format(
            # self.value is calling __str__ here
            self.value, ', ...' if self.link is not None else '')


def len_of_token_or_node(language_obj):
    if isinstance(language_obj, (LanguageToken, UtilityToken)):
        return len(language_obj.match)
    elif isinstance(language_obj, LanguageNode):
        return len(language_obj)
    else:
        raise AssertionError('Unsupported obj passed to len_of_token_or_node!')


def traverse(language_node):
    return iter_traverse(language_node)


def recursive_traverse(language_node):
    """
    Depth first traversal of the language node, returning a mutable
    list of only language tokens.
    """
    if language_node is None:
        return []
    if isinstance(language_node.value, LanguageNode):
        here = traverse(language_node.value)
    elif isinstance(language_node.value, LanguageToken):
        here = [language_node.value]

    return here + traverse(language_node.link)


def iter_traverse(language_node):
    """
    Half way point between an iterative and a recursive solution
    """
    out = []
    for element in language_node:
        if isinstance(element, LanguageNode):
            out.extend(iter_traverse(element))
        elif isinstance(element, LanguageToken):
            out.append(element)
    return out


def node_str(language_node):
    return "".join(str(token.match) for token in traverse(language_node))


def node_len(language_node):
    return operator.add(len(token.match) for token in traverse(language_node))


def what_is_linum_of_idx(program_string, absolute_idx):
    line_map = build_idx_line_map(program_string)
    if not line_map:
        return Linum(1, absolute_idx)
    line_num = _search(line_map, absolute_idx)
    if line_num == 0:
        chars_consumed = 0
    else:
        chars_consumed = line_map[line_num - 1]

    return Linum(1 + line_num, absolute_idx - chars_consumed)


# mapping is implicit, the index of the match is the line number it is on.
@memoize
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

    for idx, line_break_idx in enumerate(listing):
        if line_break_idx >= absolute_idx:
            return idx
