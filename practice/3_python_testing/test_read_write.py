"""
Write tests for 2_python_part_2/task_read_write.py task.
To write files during tests use temporary files:
https://docs.python.org/3/library/tempfile.html
https://docs.pytest.org/en/6.2.x/tmpdir.html
"""

import importlib
import pytest

read_write_module = importlib.import_module('practice.2_python_part_2.task_read_write')

read_files = read_write_module.read_files
write_to_file = read_write_module.write_to_file

@pytest.fixture
def mock_files(tmp_path):
    file_1 = tmp_path / "file_1.txt"
    file_2 = tmp_path / "file_2.txt"

    file_1.write_text("Content of file 1")
    file_2.write_text("Content of file 2")

    return [str(file_1), str(file_2)]

def test_read_files(mock_files):
    result = read_files(mock_files)

    assert result == ["Content of file 1", "Content of file 2"]

def test_write_to_file(tmp_path):
    content_to_write = ["Hello", "World"]
    output_file = tmp_path / "output.txt"

    write_to_file(str(output_file), content_to_write)
    written_text = output_file.read_text()

    assert written_text == "Hello,World"