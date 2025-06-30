"""
Create virtual environment and install Faker package only for this venv.
Write command line tool which will receive int as a first argument and one or more named arguments
 and generates defined number of dicts separated by new line.
Exec format:
`$python task_4.py NUMBER --FIELD=PROVIDER [--FIELD=PROVIDER...]`
where:
NUMBER - positive number of generated instances
FIELD - key used in generated dict
PROVIDER - name of Faker provider
Example:
`$python task_4.py 2 --fake-address=address --some_name=name`
{"some_name": "Chad Baird", "fake-address": "62323 Hobbs Green\nMaryshire, WY 48636"}
{"some_name": "Courtney Duncan", "fake-address": "8107 Nicole Orchard Suite 762\nJosephchester, WI 05981"}
"""
import argparse
from faker import Faker
import sys

def print_name_address(args: argparse.Namespace) -> None:
    fake = Faker()
    for _ in range(args.number):
        result = {}
        for key, provider in vars(args).items():
            if key == "number":
                continue
            result[key] = getattr(fake, provider)()
        print(result)

def parse_args():
    parser = argparse.ArgumentParser(
        usage="%(prog)s [-h] [--FIELD=PROVIDER FIELD=PROVIDER [FIELD=PROVIDER ...]] NUMBER"
    )
    parser.add_argument(
        "number",
        type=int,
        metavar="NUMBER")

    args, unknown = parser.parse_known_args()
    field_map = {}
    for arg in unknown:
        if arg.startswith("--") and "=" in arg:
            key, value = arg[2:].split("=", 1)
            field_map[key] = value
        else:
            print(f"Ignored invalid argument: {arg}", file=sys.stderr)

    return args.number, field_map

def main():
    number, fields = parse_args()
    args = argparse.Namespace(number=number, **fields)
    print_name_address(args)

if __name__ == "__main__":
    main()

"""
Write test for print_name_address function
Use Mock for mocking args argument https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock
Example:
    >>> m = Mock()
    >>> m.method.return_value = 123
    >>> m.method()
    123
"""