import re
from html.entities import entitydefs


def pretty_size(size, verbose=False):
    """
    Convert an integer to an human-readable file size string.

    @param size The size to convert to an human-readable string.
    @param verbose If True, do not use abbreviations (M -> Mega etc.)
    @return A string representing the size in human readable form.
    """
    import gettext

    gettext.install("python-sjutils")
    base = _("Bytes")
    for unit in ["", "Kilo", "Mega", "Giga", "Tera", "Peta", "Exa", "Zetta", "Yotta"]:
        if verbose:
            final_unit = len(unit) and (unit + base) or base
        else:
            final_unit = len(unit) and (unit[0] + base[0]) or base[0]

        if size < 1024.0:
            import math

            if math.floor(size) == size:
                return "%d %s" % (int(size), final_unit)
            else:
                return "%3.1f %s" % (size, final_unit)

        if unit != "Yotta":
            size /= 1024.0

    return "%3.1f %s" % (size, final_unit)


entitydefs_inverted = {}
for k, v in list(entitydefs.items()):
    entitydefs_inverted[v] = k

_badchars_regex = re.compile("|".join(list(entitydefs.values())))
_been_fixed_regex = re.compile("&\w+;|&#[0-9]+;")


def html_entity_fixer(text, skipchars=[], extra_careful=1):
    # if extra_careful we don't attempt to do anything to
    # the string if it might have been converted already.
    if extra_careful and _been_fixed_regex.findall(text):
        return text

    if type(skipchars) == type("s"):
        skipchars = [skipchars]

    keyholder = []
    for char in _badchars_regex.findall(text):
        if char not in skipchars:
            keyholder.append(char)
    text = text.replace("&", "&amp;")
    text = text.replace("\x80", "&#8364;")
    for each in keyholder:
        if each == "&":
            continue

        better = entitydefs_inverted[each]
        if not better.startswith("&#"):
            better = "&%s;" % entitydefs_inverted[each]

        text = text.replace(each, better)
    return text


def html_escape(text):
    """
    Escape HTML characters / entities in @text.
    """
    # We start by replacing '&'
    text = text.replace("&", "&amp;")

    if isinstance(text, bytes):
        # We use this to avoid UnicodeDecodeError in text.replace()
        convert = lambda x: x.decode("iso-8859-1")
    else:
        convert = lambda x: x

    # We don't want '&' in our dict, as it would mess up any previous
    # replace() we'd done
    entitydefs_inverted = (
        (convert(value), key) for key, value in entitydefs.items() if value != "&"
    )
    for key, value in entitydefs_inverted:
        text = text.replace(key, "&%s;" % value)
    return text


def any(iterable, predicate=bool, *args, **kw):
    """Return True if predicate(x, *args, **kw) is True for any x in the iterable."""
    for elt in iterable:
        if predicate(elt, *args, **kw):
            return True
    return False


def all(iterable, predicate=bool, *args, **kw):
    """Return True if predicate(x, *args, **kw) is True for all values x in the iterable."""
    for elt in iterable:
        if not predicate(elt, *args, **kw):
            return False
    return True


def flatten_dict(dictionary, sep="/"):
    """
    Flatten a Python dictionary, in an iterative way (no stack
    overflow)

    Flattenning a dictionary can be compared to the depth-first
    traversal of a B-tree. We can iterate through the tree's branches
    by keeping a stack (FILO) of the nodes we're traversing.

    @param dictionary The dictionary to flatten
    @param sep A string that will be used to join the keys
    @return The flattened dictionary
    """

    my_stack = list(dictionary.items())
    result = {}

    while my_stack:
        key, value = my_stack.pop()
        if isinstance(value, dict):
            my_stack.extend(
                [
                    (key + sep + inner_key, inner_value)
                    for inner_key, inner_value in value.items()
                ]
            )
        else:
            result[key] = value

    return result


def flatten_list(my_list):
    """
    Flatten a Python list, in an iterative way (no stack
    overflow)

    Flattenning a list can be compared to the depth-first traversal of
    a B-tree. We can iterate through the tree's branches by keeping a
    stack (FILO) of the nodes we're traversing.

    Note: I used collections.deque here in order to avoid using
    multiple calls to list() (to avoid in-place modification of the
    list) and reverse() (to preserve the order in the stack). The only
    beef I have with deque is its input-reversing extendleft() method,
    which forces me to call reversed() on the inner lists.

    Note 2: Currently, we completely collapse empty lists, i.e. they
    will never be part of the returned list.

    @param my_list The list to flatten
    @return The flattened list
    """

    # We use collections.deque for fast pop(0) / insert(0, v)
    from collections import deque

    my_stack = deque(my_list)
    result = []

    while my_stack:
        elt = my_stack.popleft()
        if isinstance(elt, list):
            my_stack.extendleft(reversed(elt))
        else:
            result.append(elt)

    return result


def paginate(iterable, pagesize):
    """
    Pure generator-based paginate operator, from
    http://paste.pocoo.org/show/173972/

    paginate([1,2,3,4,5,6,7], 3) -> [[1,2,3], [4,5,6], [7]]

    This function makes clever use of floor division for the groupby()
    key function, so that the key changes every pagesize items,
    prompting the yield of a new page.
    """

    import itertools

    counter = itertools.count()

    def key_function(_elt):
        return next(counter) // pagesize

    for _key, values in itertools.groupby(iterable, key_function):
        yield values
