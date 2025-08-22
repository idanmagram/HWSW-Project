"""Generic (shallow and deep) copying operations.

Interface summary:

        import copy

        x = copy.copy(y)        # make a shallow copy of y
        x = copy.deepcopy(y)    # make a deep copy of y

For module specific errors, copy.Error is raised.

The difference between shallow and deep copying is only relevant for
compound objects (objects that contain other objects, like lists or
class instances).

- A shallow copy constructs a new compound object and then (to the
  extent possible) inserts *the same objects* into it that the
  original contains.

- A deep copy constructs a new compound object and then, recursively,
  inserts *copies* into it of the objects found in the original.

Two problems often exist with deep copy operations that don't exist
with shallow copy operations:

 a) recursive objects (compound objects that, directly or indirectly,
    contain a reference to themselves) may cause a recursive loop

 b) because deep copy copies *everything* it may copy too much, e.g.
    administrative data structures that should be shared even between
    copies

Python's deep copy operation avoids these problems by:

 a) keeping a table of objects already copied during the current
    copying pass

 b) letting user-defined classes override the copying operation or the
    set of components copied

This version does not copy types like module, class, function, method,
nor stack trace, stack frame, nor file, socket, window, nor any
similar types.

Classes can use the same interfaces to control copying that they use
to control pickling: they can define methods called __getinitargs__(),
__getstate__() and __setstate__().  See the documentation for module
"pickle" for information on these methods.
"""

import types
import weakref
from copyreg import dispatch_table

class Error(Exception):
    pass
error = Error   # backward compatibility

try:
    from org.python.core import PyStringMap
except ImportError:
    PyStringMap = None

__all__ = ["Error", "copy", "deepcopy"]

def copy(x):
    """Shallow copy operation on arbitrary Python objects.

    See the module's __doc__ string for more info.
    """

    cls = type(x)
    #if cls in _atomic_types:
    #    return x

    copier = _copy_dispatch.get(cls)
    if copier:
        return copier(x)

    if issubclass(cls, type):
        # treat it as a regular class:
        return _copy_immutable(x)

    copier = getattr(cls, "__copy__", None)
    if copier is not None:
        return copier(x)

    reductor = dispatch_table.get(cls)
    if reductor is not None:
        rv = reductor(x)
    else:
        reductor = getattr(x, "__reduce_ex__", None)
        if reductor is not None:
            rv = reductor(4)
        else:
            reductor = getattr(x, "__reduce__", None)
            if reductor:
                rv = reductor()
            else:
                raise Error("un(shallow)copyable object of type %s" % cls)

    if isinstance(rv, str):
        return x
    return _reconstruct(x, None, *rv)


_copy_dispatch = d = {}

def _copy_immutable(x):
    return x
for t in (type(None), int, float, bool, complex, str, tuple,
          bytes, frozenset, type, range, slice, property,
          types.BuiltinFunctionType, type(Ellipsis), type(NotImplemented),
          types.FunctionType, weakref.ref):
    d[t] = _copy_immutable
t = getattr(types, "CodeType", None)
if t is not None:
    d[t] = _copy_immutable

d[list] = list.copy
d[dict] = dict.copy
d[set] = set.copy
d[bytearray] = bytearray.copy

if PyStringMap is not None:
    d[PyStringMap] = PyStringMap.copy

del d, t

def deepcopy(x, memo=None, _nil=[]):
    """Deep copy operation on arbitrary Python objects.

    See the module's __doc__ string for more info.
    """

    if memo is None:
        deepcopy._last_id = None
        deepcopy._last_obj = None
        memo = {}

    d = id(x)

    if deepcopy._last_id == d:
        return deepcopy._last_obj


    y = memo.get(d, _nil)
    if y is not _nil:
        deepcopy._last_id = d
        deepcopy._last_obj = y
        return y

    cls = type(x)

    copier = _deepcopy_dispatch.get(cls)
    if copier is not None:
        y = copier(x, memo)
    else:
        if issubclass(cls, type):
            y = _deepcopy_atomic(x, memo)
        else:
            copier = getattr(x, "__deepcopy__", None)
            if copier is not None:
                y = copier(memo)
            else:
                reductor = dispatch_table.get(cls)
                if reductor:
                    rv = reductor(x)
                else:
                    reductor = getattr(x, "__reduce_ex__", None)
                    if reductor is not None:
                        rv = reductor(4)
                    else:
                        reductor = getattr(x, "__reduce__", None)
                        if reductor:
                            rv = reductor()
                        else:
                            raise Error(
                                "un(deep)copyable object of type %s" % cls)
                if isinstance(rv, str):
                    y = x
                else:
                    y = _reconstruct(x, memo, *rv)

    # If is its own copy, don't memoize.
    if y is not x:
        memo[d] = y
        _keep_alive(x, memo) # Make sure x lives at least as long as d

    deepcopy._last_id = d
    deepcopy._last_obj = y
    return y

_deepcopy_dispatch = d = {}

def _deepcopy_atomic(x, memo):
    return x
d[type(None)] = _deepcopy_atomic
d[type(Ellipsis)] = _deepcopy_atomic
d[type(NotImplemented)] = _deepcopy_atomic
d[int] = _deepcopy_atomic
d[float] = _deepcopy_atomic
d[bool] = _deepcopy_atomic
d[complex] = _deepcopy_atomic
d[bytes] = _deepcopy_atomic
d[str] = _deepcopy_atomic
d[types.CodeType] = _deepcopy_atomic
d[type] = _deepcopy_atomic
d[range] = _deepcopy_atomic
d[types.BuiltinFunctionType] = _deepcopy_atomic
d[types.FunctionType] = _deepcopy_atomic
d[weakref.ref] = _deepcopy_atomic
d[property] = _deepcopy_atomic

def _deepcopy_list(x, memo, deepcopy=deepcopy):
    y = [None] * len(x)  # Preallocate list
    memo[id(x)] = y

    for i, a in enumerate(x):
        y[i] = deepcopy(a, memo)

    return y
d[list] = _deepcopy_list

def _deepcopy_tuple(x, memo, deepcopy=deepcopy):
    y = [deepcopy(a, memo) for a in x]
    # We're not going to put the tuple in the memo, but it's still important we
    # check for it, in case the tuple contains recursive mutable structures.
    try:
        return memo[id(x)]
    except KeyError:
        pass
    for k, j in zip(x, y):
        if k is not j:
            y = tuple(y)
            break
    else:
        y = x
    return y
d[tuple] = _deepcopy_tuple
_IMMUTABLE_KEY_TYPES = (int, float, str, bytes, frozenset, type(None))

def _deepcopy_dict(x, memo, deepcopy=deepcopy):
    y = {}
    memo[id(x)] = y
    x_items = x.items()
    for key, value in x_items:
        # Immutable types do not need   deepcopy
        if isinstance(key, _IMMUTABLE_KEY_TYPES):
            key_copy = key
        else:
            key_copy = deepcopy(key, memo)
        if isinstance(value, _IMMUTABLE_KEY_TYPES):
            value_copy = value
        else:
            value_copy = deepcopy(value, memo)
        y[key_copy] = value_copy
    return y

d[dict] = _deepcopy_dict
if PyStringMap is not None:
    d[PyStringMap] = _deepcopy_dict

def _deepcopy_method(x, memo): # Copy instance methods
    return type(x)(x.__func__, deepcopy(x.__self__, memo))
d[types.MethodType] = _deepcopy_method

del d

def _keep_alive(x, memo):
    """Keeps a reference to the object x in the memo.

    Because we remember objects by their id, we have
    to assure that possibly temporary objects are kept
    alive by referencing them.
    We store a reference at the id of the memo, which should
    normally not be used unless someone tries to deepcopy
    the memo itself...
    """
    try:
        memo[id(memo)].append(x)
    except KeyError:
        # aha, this is the first one :-)
        memo[id(memo)]=[x]

def _reconstruct(x, memo, func, args,
                 state=None, listiter=None, dictiter=None,
                 deepcopy=deepcopy):
    deep = memo is not None

    # Copy args if deep; * will build a tuple anyway, so do it explicitly once
    if deep and args:
        args = tuple(deepcopy(arg, memo) for arg in args)

    # Construct object
    y = func(*args)
    if deep:
        memo[id(x)] = y

    # Apply state
    if state is not None:
        if deep:
            state = deepcopy(state, memo)

        setstate = getattr(y, '__setstate__', None)
        if setstate is not None:
            setstate(state)
        else:
            # Fast-path common shapes:
            # 1) dict state
            if isinstance(state, dict):
                y.__dict__.update(state)
            else:
                # 2) (state, slotstate) tuple
                slotstate = None
                if isinstance(state, tuple) and len(state) == 2:
                    state, slotstate = state

                if state is not None:
                    if isinstance(state, dict):
                        y.__dict__.update(state)
                    else:
                        # Very uncommon: assign via setattr for sequence of pairs
                        for k, v in state:
                            setattr(y, k, v)

                if slotstate is not None:
                    # slotstate is always a dict in pickle protocol
                    for key, value in slotstate.items():
                        setattr(y, key, value)

    # Populate list elements
    if listiter is not None:
        if deep:
            y.extend(deepcopy(item, memo) for item in listiter)
        else:
            y.extend(listiter)

    # Populate dict items
    if dictiter is not None:
        if deep:
            y.update({deepcopy(k, memo): deepcopy(v, memo) for (k, v) in dictiter})
        else:
            y.update(dictiter)

    return y

del types, weakref, PyStringMap
