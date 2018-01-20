

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


# to be used for a quick interval tree
class BSTNode:

    def __init__(self, val, left=None, right=None):
        for arg in (left, right):
            assert(arg is None or isinstance(arg, BSTNode))

        if left and right:
            assert left.val <= right.val
        self.left = left
        self.right = right
        self.val = val

    def insert(self, val):
        if val <= self.val:
            if self.left is None:
                self.left = BSTNode(val)
            else:
                self.left.insert(val)
        elif val > self.val:
            if self.right is None:
                self.right = BSTNode(val)
            else:
                self.right.insert(val)
