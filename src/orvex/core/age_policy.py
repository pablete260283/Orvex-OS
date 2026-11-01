"""Conservative numeric age policy shared by the demo and the persistent catalog."""

import math


def valid_age(value, maximum=21):
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and 0 <= value <= maximum
        and math.isfinite(value)
        and value == int(value)
    )
