"""
Write a function that makes a request to some url
using urllib. Return status code and decoded response data in utf-8
Examples:
     >>> make_request('https://www.google.com')
     200, 'response data'
"""
from urllib.request import urlopen
from typing import Tuple

def make_request(url: str) -> Tuple[int, str]:
    resp = urlopen(url)

    charset = resp.headers.get_content_charset() or "utf-8"
    text = resp.read().decode(charset, errors="replace")
    return resp.getcode(), text

if __name__ == "__main__":
    print(make_request("https://www.google.com"))


"""
Write test for make_request function
Use Mock for mocking request with urlopen https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock
Example:
    >>> m = Mock()
    >>> m.method.return_value = 200
    >>> m.method2.return_value = b'some text'
    >>> m.method()
    200
    >>> m.method2()
    b'some text'
"""
