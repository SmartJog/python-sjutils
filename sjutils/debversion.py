import re


class DebianVersion:
    """
    Class to compare Debian package version number format
    """

    pattern = re.compile(
        r"^(?:(\d+):)?" "(\d[0-9a-zA-Z.+:~-]*?)" "(?:-([0-9a-zA-Z+.~]+))?$"
    )

    def __init__(self, str_version):
        matches = DebianVersion.pattern.findall(str_version)
        if not matches:
            raise Exception("%s doesn't look like a version string")
        else:
            matches = matches[0]
        self.epoch = int(matches[0] if matches[0] else 0)
        self.upstream = str(matches[1])
        self.debian = str(matches[2])

    def __cmp__(self, other):
        # compare epoch
        rv = self.epoch.__cmp__(other.epoch)
        if rv != 0:
            return rv
        # compare upstream
        rv = vercmp(self.upstream, other.upstream)
        if rv != 0:
            return rv
        # compare debian
        return vercmp(self.debian, other.debian)


def vercmp(lhs, rhs):
    """
    Compare version according to sorting algorithm (see 'man deb-version')
    """
    digitregex = re.compile(r"^([0-9]*)(.*)$")
    nondigitregex = re.compile(r"^([^0-9]*)(.*)$")

    digits = True
    while lhs or rhs:
        pattern = digitregex if digits else nondigitregex
        sub_lhs, lhs = pattern.findall(lhs)[0]
        sub_rhs, rhs = pattern.findall(rhs)[0]

        if digits:
            sub_lhs = int(sub_lhs if sub_lhs else 0)
            sub_rhs = int(sub_rhs if sub_rhs else 0)
            rv = sub_lhs.__cmp__(sub_rhs)
            if rv != 0:
                return rv
        else:
            rv = strvercmp(sub_lhs, sub_rhs)
            if rv != 0:
                return rv

        digits = not digits
    return 0


def strvercmp(lhs, rhs):
    """
    Compare string part of a version number
    """
    size = max(len(lhs), len(rhs))
    lhs_array = debver_array(lhs, size)
    rhs_array = debver_array(rhs, size)
    if lhs_array > rhs_array:
        return 1
    elif lhs_array < rhs_array:
        return -1
    else:
        return 0


def debver_array(str_version, size):
    """
    Turns a string into an array of numeric values kind-of corresponding to
    the ASCII numeric values of the characters in the string.  I say 'kind-of'
    because any character which is not an alphabetic character will be
    it's ASCII value + 256, and the tilde (~) character will have the value
    -1.

    Additionally, the +size+ parameter specifies how long the array needs to
    be; any elements in the array beyond the length of the string will be 0.

    This method has massive ASCII assumptions. Use with caution.
    """
    a = [0] * size
    for i, char in enumerate(str_version):
        char = ord(char)
        if (char >= ord("a") and char <= ord("z")) or (
            char >= ord("A") and char <= ord("Z")
        ):
            a[i] = char
        elif char == ord("~"):
            a[i] = -1
        else:
            a[i] = char + 256
    return a
