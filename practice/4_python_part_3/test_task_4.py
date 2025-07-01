from task_4 import print_name_address
from unittest.mock import patch
import io
import argparse

@patch('sys.stdout', new_callable=io.StringIO)
def test_print_name_address(mock_stdout):
    test_data = {
        "test1": argparse.Namespace(number=2, fake_address='address', some_name='name'),
        "test2": argparse.Namespace(number=3, fake_company='company', fake_color='color'),
    }

    for test_name, args in test_data.items():
        print_name_address(args)
        output = mock_stdout.getvalue().strip().split('\n')

        assert len(output) == args.number, f"{test_name}: Number of lines mismatch"

        for line in output:
            assert line.startswith('{') and line.endswith('}'), f"{test_name}: Line format error"
            for field in vars(args):
                if field != "number":
                    assert f"'{field}':" in line, f"{test_name}: Missing key {field} in output"

        mock_stdout.truncate(0)
        mock_stdout.seek(0)
