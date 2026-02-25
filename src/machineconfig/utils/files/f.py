
from typing import Literal, TypeAlias, get_args
from enum import Enum
T1: TypeAlias = Literal["r", "w", "a", "x", "rb", "wb", "ab", "xb"]

class T1Enum(Enum):
    r = "r"
    w = "w"
    a = "a"
    x = "x"
    rb = "rb"
    wb = "wb"
    ab = "ab"
    xb = "xb"

a: T1 = "r"

def func(arg1: T1) -> T1:
    print(arg1)
    return arg1

b = func(arg1=a)

all_t1 = get_args(T1)
all_t1_enum = [e.value for e in T1Enum]
