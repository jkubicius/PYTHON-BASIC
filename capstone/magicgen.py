import argparse
import configparser
import logging
import os
import random
import sys
import time
import uuid
import json
from typing import Any
from multiprocessing import Pool, cpu_count

VALID_DATA_TYPES = frozenset({'str', 'int', 'timestamp'})


def load_defaults_from_config() -> dict:
    cfg = configparser.ConfigParser()
    cfg.read('default.ini')
    d = cfg['DEFAULT']
    return {
        'files_count': int(d.get('files_count', '1')),
        'file_name': d.get('file_name', 'data'),
        'file_prefix': d.get('file_prefix', 'uuid'),
        'data_lines': int(d.get('data_lines', '1000')),
        'multiprocessing': int(d.get('multiprocessing', '1')),
    }


def create_parser() -> argparse.ArgumentParser:
    defaults = load_defaults_from_config()
    parser = argparse.ArgumentParser(
        prog='magicgenerator',
        description='Generate random JSON data based on provided schema.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        'path_to_save_files',
        help='Directory where files will be saved (relative or absolute path).'
    )
    parser.add_argument(
        '--files_count', '-n',
        type=int,
        default=defaults['files_count'],
        help='How many JSON files to generate; 0 = print to console.'
    )
    parser.add_argument(
        '--file_name', '-f',
        default=defaults['file_name'],
        help='Base name for generated files.'
    )
    parser.add_argument(
        '--file_prefix', '-p',
        choices=['count', 'random', 'uuid'],
        default=defaults['file_prefix'],
        help='Filename prefix mode when generating multiple files.'
    )
    parser.add_argument(
        '--data_schema', '-s',
        required=True,
        help='JSON schema string or path to .json file.'
    )
    parser.add_argument(
        '--data_lines', '-l',
        type=int,
        default=defaults['data_lines'],
        help='Number of JSON records per file.'
    )
    parser.add_argument(
        '--clear_path', '-c',
        action='store_true',
        help='If set, clear existing files in output directory before generating.'
    )
    parser.add_argument(
        '--multiprocessing', '-m',
        type=int,
        default=defaults['multiprocessing'],
        help='Number of parallel processes to use.'
    )
    return parser


def load_schema(data_schema: str) -> dict:
    if os.path.isfile(data_schema):
        logging.info(f"Loading schema from file: {data_schema}")
        try:
            with open(data_schema, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logging.error("Invalid JSON schema file.")
            sys.exit(1)

    logging.info("Parsing schema from command-line string")
    try:
        return json.loads(data_schema)
    except json.JSONDecodeError:
        logging.error("Invalid JSON schema.")
        sys.exit(1)


def validate_path(path: str) -> str:
    if path == '.':
        path = os.getcwd()
    elif not os.path.isabs(path):
        path = os.path.abspath(path)

    if os.path.exists(path) and not os.path.isdir(path):
        logging.error(f"'{path}' exists but is not a directory.")
        sys.exit(1)
    if not os.path.exists(path):
        logging.info(f"Creating directory: {path}")
        os.makedirs(path, exist_ok=True)
    if not os.access(path, os.W_OK):
        logging.error(f"No write permission for directory: {path}")
        sys.exit(1)
    return path


def clear_output_files(path: str, base: str):
    logging.info(f"Clearing files in {path} with prefix '{base}_'")
    for fname in os.listdir(path):
        if fname.startswith(base + '_') and fname.endswith('.json'):
            fp = os.path.join(path, fname)
            try:
                os.remove(fp)
                logging.info(f"Deleted: {fp}")
            except Exception as e:
                logging.error(f"Cannot remove {fp}: {e}")


def validate_schema(schema: dict[str, str]) -> None:

    for key, val in schema.items():
        if ':' not in val:
            logging.error(f"Missing ':' in schema value for key '{key}'")
            sys.exit(1)
        dtype, instr = map(str.strip, val.split(':', 1))
        if dtype not in VALID_DATA_TYPES:
            logging.error(f"Unsupported data type '{dtype}' in key '{key}'")
            sys.exit(1)
        if dtype == 'timestamp':
            if instr:
                logging.warning(f"Ignoring '{instr}' for timestamp key '{key}'")
            continue
        if dtype == 'str':
            if instr == '':
                continue
            if instr == 'rand':
                continue
            if instr.startswith('[') and instr.endswith(']'):
                try:
                    opts = json.loads(instr.replace("'", '"'))
                    if not all(isinstance(x, str) for x in opts):
                        raise ValueError
                except Exception:
                    logging.error(f"Invalid string list in key '{key}': {instr}")
                    sys.exit(1)
                continue
            if instr.startswith('rand(') and instr.endswith(')'):
                logging.error(f"rand(range) not supported for str in key '{key}': {instr}")
                sys.exit(1)
            continue
        if instr == '':
            continue
        if instr == 'rand':
            continue
        if instr.startswith('rand(') and instr.endswith(')'):
            try:
                a, b = map(int, instr[5:-1].split(','))
                if a > b:
                    raise ValueError
            except Exception:
                logging.error(f"Invalid rand(a,b) in key '{key}': {instr}")
                sys.exit(1)
            continue
        if instr.startswith('[') and instr.endswith(']'):
            try:
                opts = json.loads(instr.replace("'", '"'))
                if not all(isinstance(x, int) for x in opts):
                    raise ValueError
            except Exception:
                logging.error(f"Invalid int list in key '{key}': {instr}")
                sys.exit(1)
            continue
        try:
            int(instr)
        except Exception:
            logging.error(f"Invalid int constant in key '{key}': {instr}")
            sys.exit(1)
    logging.info("Schema validation passed")


def parse_field(type_val: str, field: str) -> Any:
    dtype, raw = map(str.strip, type_val.split(':', 1))
    if dtype == 'timestamp':
        return time.time()
    if dtype == 'str':
        if raw == 'rand':
            return str(uuid.uuid4())
        if raw.startswith('[') and raw.endswith(']'):
            opts = json.loads(raw.replace("'", '"'))
            return random.choice(opts)
        return raw
    if raw == 'rand':
        return random.randint(0, 10000)
    if raw.startswith('rand(') and raw.endswith(')'):
        a, b = map(int, raw[5:-1].split(','))
        return random.randint(a, b)
    if raw.startswith('[') and raw.endswith(']'):
        opts = json.loads(raw.replace("'", '"'))
        return random.choice(opts)
    if raw == '':
        return None
    return int(raw)


def generate_line(schema: dict[str, str]) -> dict:
    return {k: parse_field(v, k) for k, v in schema.items()}


def generate_data_lines(schema: dict[str, str], count: int) -> list[dict]:
    return [generate_line(schema) for _ in range(count)]


def make_filename(base: str, mode: str, idx: int) -> str:
    if mode == 'count':
        suffix = str(idx)
    elif mode == 'random':
        suffix = str(random.randint(1000, 9999))
    else:
        suffix = str(uuid.uuid4())
    return f"{base}_{suffix}.json"


def write_file(path: str, filename: str, data: list[dict]):
    fp = os.path.join(path, filename)
    logging.info(f"Writing file: {fp}")
    with open(fp, 'w') as f:
        for rec in data:
            f.write(json.dumps(rec) + '\n')
    logging.info(f"Wrote: {fp}")


def generate_worker(args):
    idx, path, base, prefix, schema, lines = args
    data = generate_data_lines(schema, lines)
    fname = make_filename(base, prefix, idx)
    write_file(path, fname, data)


def validate_all_arguments(args: argparse.Namespace) -> dict:
    path = validate_path(args.path_to_save_files)
    if args.files_count < 0:
        logging.error("files_count must be >= 0")
        sys.exit(1)
    if args.data_lines <= 0:
        logging.error("data_lines must be > 0")
        sys.exit(1)
    if args.multiprocessing < 0:
        logging.error("multiprocessing must be >= 0")
        sys.exit(1)
    if args.multiprocessing > cpu_count():
        logging.warning(f"multiprocessing > CPU count; using {cpu_count()}")
        args.multiprocessing = cpu_count()

    schema = load_schema(args.data_schema)
    validate_schema(schema)

    return {
        'path': path,
        'file_name': args.file_name,
        'file_prefix': args.file_prefix,
        'files_count': args.files_count,
        'data_lines': args.data_lines,
        'schema': schema,
        'clear_path': args.clear_path,
        'multiprocessing': args.multiprocessing,
    }


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    parser = create_parser()
    args = parser.parse_args()
    cfg = validate_all_arguments(args)

    if cfg['clear_path']:
        clear_output_files(cfg['path'], cfg['file_name'])

    if cfg['files_count'] == 0:
        logging.info("Generating to console (JSON Lines)...")
        for rec in generate_data_lines(cfg['schema'], cfg['data_lines']):
            print(json.dumps(rec))
        return

    logging.info(
        f"Starting generation of {cfg['files_count']} file(s) "
        f"({cfg['data_lines']} lines each) "
        f"using {cfg['multiprocessing']} process(es)"
    )
    jobs = [
        (i, cfg['path'], cfg['file_name'], cfg['file_prefix'], cfg['schema'], cfg['data_lines'])
        for i in range(cfg['files_count'])
    ]

    if cfg['multiprocessing'] > 1:
        with Pool(cfg['multiprocessing']) as pool:
            pool.map(generate_worker, jobs)
    else:
        for job in jobs:
            generate_worker(job)

    logging.info("Data generation complete.")


if __name__ == '__main__':
    main()