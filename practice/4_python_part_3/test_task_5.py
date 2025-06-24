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
from unittest.mock import Mock, patch
from task_5 import make_request

@patch("urllib.request.urlopen")
def test_make_request(mock_urlopen):
    mock_urlopen.return_value.getcode.return_value = 200
    mock_urlopen.return_value.read.return_value = b"some text"

    code, data = make_request("http://example.com")

    assert code == 200
    assert data == "some text"
