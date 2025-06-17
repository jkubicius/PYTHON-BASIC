"""
Use function 'generate_words' to generate random words.
Write them to a new file encoded in UTF-8. Separator - '\n'.
Write second file encoded in CP1252, reverse words order. Separator - ','.

Example:
    Input: ['abc', 'def', 'xyz']

    Output:
        file1.txt (content: "abc\ndef\nxyz", encoding: UTF-8)
        file2.txt (content: "xyz,def,abc", encoding: CP1252)
"""


def generate_words(n=20):
    import string
    import random

    words = list()
    for _ in range(n):
        word = ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 10)))
        words.append(word)

    return words


def write_to_file(filename: str, content: list[str], encoding='UTF-8', sep='\n'):
    with open(filename, 'w', encoding=encoding) as file:
        file.write(sep.join(content)) # Write content with separator

words = generate_words()

write_to_file('file1.txt', words, encoding='UTF-8', sep='\n')
write_to_file('file2.txt', words[::-1], encoding='cp1252', sep=',') # ::-1 means reverse the list