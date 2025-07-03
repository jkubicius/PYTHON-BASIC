"""
Write tests for 2_python_part_2/task_read_write_2.py task.
To write files during tests use temporary files:
https://docs.python.org/3/library/tempfile.html
https://docs.pytest.org/en/6.2.x/tmpdir.html
"""
import importlib
import pytest

module = importlib.import_module('practice.2_python_part_2.task_read_write_2')

write_to_file = module.write_to_file

@pytest.fixture
def sample_words():
    return ['abc', 'def', 'xyz']

def test_write_utf8_file(tmp_path, sample_words):
    file_path = tmp_path / 'file1.txt'

    write_to_file(str(file_path), sample_words, encoding='UTF-8', sep='\n') # using str() to be compatible with pathlib.Path

    assert file_path.read_text(encoding='UTF-8') == "abc\ndef\nxyz"

def test_write_cp1252_file_reversed(tmp_path, sample_words):
    file_path = tmp_path / 'file2.txt'

    write_to_file(str(file_path), sample_words[::-1], encoding='cp1252', sep=',')

    assert file_path.read_text(encoding='cp1252') == "xyz,def,abc"