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


from unittest.mock import patch, Mock
from task_5 import make_request

@patch('task_5.request.urlopen')
def test_successful_request(mock_urlopen):
    mock_resp = Mock()
    mock_resp.getcode.return_value = 200  #
    mock_resp.read.return_value = b'some text'

    mock_urlopen.return_value = mock_resp
    status, content = make_request('http://fakeurl.com')

    assert status == 200
    assert content == 'some text'
