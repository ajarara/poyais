

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
