"""
Write function which receives filename and reads file line by line and returns min and mix integer from file.
Restriction: filename always valid, each line of file contains valid integer value
Examples:
    # file contains following lines:
        10
        -2
        0
        34
    >>> get_min_max('filename')
    (-2, 34)

Hint:
To read file line-by-line you can use this:
with open(filename) as opened_file:
    for line in opened_file:
        ...
"""
from typing import Tuple


def get_min_max(filename: str) -> Tuple[int, int]:
    with open(filename) as opened_file:
        first_line = next(opened_file)
        min_val = max_val = int(first_line.strip())
        for line in opened_file:
            num = int(line.strip())
            if num < min_val:
                min_val = num
            if num > max_val:
                max_val = num
    return (min_val, max_val)
print(get_min_max('filename.py'))