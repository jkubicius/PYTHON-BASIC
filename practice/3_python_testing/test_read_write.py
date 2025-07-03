"""
Write tests for 2_python_part_2/task_read_write.py task.
To write files during tests use temporary files:
https://docs.python.org/3/library/tempfile.html
https://docs.pytest.org/en/6.2.x/tmpdir.html
"""

import importlib

read_write_module = importlib.import_module('practice.2_python_part_2.task_read_write')

read_files = read_write_module.read_files
write_to_file = read_write_module.write_to_file

CONTENT = ["1", "2", "3"]
RESULT = "result.txt"


def test_read_and_write(tmp_path):
    temp_dir = tmp_path / "test_dir"
    temp_dir.mkdir()

    for value in CONTENT:
        file_path = temp_dir / f"file_{value}.txt"
        file_path.write_text(value)

    file_paths = [str(temp_dir / f"file_{value}.txt") for value in CONTENT]
    read_values = read_files(file_paths)

    result_file_path = temp_dir / RESULT
    write_to_file(str(result_file_path), read_values)

    expected = ", ".join(CONTENT)
    actual = result_file_path.read_text()
    assert actual == expected