import math
BASE_WIDTH = 0
BASE_HEIGHT = 0
NUMBERS = "1234567890"
TRIGON_FUNCS = {"SIN": math.sin, "COS": math.cos, "TG": math.tan, "RAD": math.radians}


def outer_split(cond: str, char: str) -> tuple[str, str, str]:
    def find_cond(text: str) -> tuple[int, int] | tuple[None, None]:
        if text.find("(") == -1:
            return None, None
        else:
            i1 = text.find("(")
            i2 = text.find(")")
            return i1, i2

    i1 = 0
    i2 = len(cond)-1
    l_side = ""
    center_side = ""
    r_side = ""
    condition_ind1, condition_ind2 = 0, 0

    if find_cond(cond) is not None:
        condition_ind1, condition_ind2 = find_cond(cond)

    # Left side
    while cond[i1] != char:
        i1 += 1
    l_side = cond[:i1]

    if condition_ind1 is not None:
        while cond[condition_ind1] != char:
            condition_ind1 -= 1
        while condition_ind2 != len(cond) and cond[condition_ind2] != char:
            condition_ind2 += 1
    else:
        while cond[i2] != char:
            i2 -= 1

    if condition_ind2 is not None:
        if condition_ind2 == len(cond):
            center_side = cond[i1+1:condition_ind1]
            r_side = cond[condition_ind1+1:]
        else:
            center_side = cond[i1+1:condition_ind2]
            r_side = cond[condition_ind2+1:]
    else:
        center_side = cond[i1+1:i2]
        r_side = cond[i2+1:]

    return l_side, center_side, r_side

