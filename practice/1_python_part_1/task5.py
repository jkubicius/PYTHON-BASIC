"""
Write function which receives line of space sepparated words.
Remove all duplicated words from line.
Restriction:
Examples:
    >>> remove_duplicated_words('cat cat dog 1 dog 2')
    'cat dog 1 2'
    >>> remove_duplicated_words('cat cat cat')
    'cat'
    >>> remove_duplicated_words('1 2 3')
    '1 2 3'
"""


def remove_duplicated_words(line: str) -> str:
    seen = set() # there will be stored all seen words
    result = [] #final array for unique words
    for word in line.split():
        if word not in seen:
            seen.add(word) #if not seen in set seen - add
            result.append(word)
    return ' '.join(result)

print(remove_duplicated_words('cat cat dog 1 dog 2'))
print(remove_duplicated_words('cat cat cat'))
print(remove_duplicated_words('1 2 3'))