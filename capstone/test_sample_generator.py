import argparse
import configparser
import json
import os
import sys
import stat
import random
import uuid
import pytest

import magicgen


class TestParseFieldTypes:
    @pytest.mark.parametrize("field_spec,expected_type", [
        ("str:rand", str),
        ("str:['foo','bar']", str),
        ("str:hello", str),
        ("int:rand", int),
        ("int:rand(5,10)", int),
        ("int:[1,2,3]", int),
        ("int:-7", int),
        ("int:", type(None)),
        ("timestamp:", float),
    ])
    def test_parse_field_returns_correct_type(self, field_spec, expected_type):
        val = magicgen.parse_field(field_spec, "dummy")
        assert isinstance(val, expected_type)


class TestValidateSchema:
    @pytest.mark.parametrize("good_schema", [
        {"n": "str:"},
        {"n": "str:rand"},
        {"n": "str:['a','b']"},
        {"i": "int:rand"},
        {"i": "int:rand(1,2)"},
        {"i": "int:[1,2,3]"},
        {"i": "int:42"},
        {"t": "timestamp:"},
    ])
    def test_validate_schema_accepts_valid(self, good_schema):
        magicgen.validate_schema(good_schema)

    @pytest.mark.parametrize("bad_schema", [
        {"x": "foo"},
        {"x": "bool:rand"},
        {"s": "str:rand(1,2)"},
        {"i": "int:rand(a,b)"},
        {"i": "int:[1,'2']"},
        {"i": "int:abc"},
    ])
    def test_validate_schema_rejects_invalid(self, bad_schema):
        with pytest.raises(SystemExit):
            magicgen.validate_schema(bad_schema)


class TestLoadSchema:
    def test_load_schema_from_file(self, tmp_path):
        data = {"a": "int:1", "b": "str:hello"}
        p = tmp_path / "schema.json"
        p.write_text(json.dumps(data))
        assert magicgen.load_schema(str(p)) == data

    def test_load_schema_from_bad_file_exits(self, tmp_path):
        p = tmp_path / "bad.json"
        p.write_text("{not: valid}")
        with pytest.raises(SystemExit):
            magicgen.load_schema(str(p))

    def test_load_schema_from_string(self):
        s = '{"x": "int:rand", "y": "timestamp:"}'
        out = magicgen.load_schema(s)
        assert out == {"x": "int:rand", "y": "timestamp:"}


class TestCreateParser:
    def test_parser_contains_expected_args(self):
        parser = magicgen.create_parser()
        help_str = parser.format_help()
        for opt in ["files_count", "file_name", "file_prefix",
                    "data_schema", "data_lines",
                    "clear_path", "multiprocessing",
                    "path_to_save_files"]:
            assert opt in help_str


class TestValidatePath:
    def test_dot_expands_to_cwd(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = magicgen.validate_path(".")
        assert path == tmp_path.as_posix()

    def test_relative_to_absolute_and_created(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        rel = "subdir"
        path = magicgen.validate_path(rel)
        assert os.path.isdir(path)
        assert path == (tmp_path / rel).resolve().as_posix()

    def test_file_instead_of_dir_errors(self, tmp_path):
        f = tmp_path / "afile"
        f.write_text("x")
        with pytest.raises(SystemExit):
            magicgen.validate_path(str(f))

    def test_no_write_permission_errors(self, tmp_path, monkeypatch):
        d = tmp_path / "d"
        d.mkdir()
        d.chmod(stat.S_IRUSR | stat.S_IXUSR)
        with pytest.raises(SystemExit):
            magicgen.validate_path(str(d))


class TestClearPathAction:
    @pytest.fixture
    def temp_dir(self, tmp_path):
        d = tmp_path / "out"
        d.mkdir()
        return d

    def test_clear_output_files_only_matching(self, temp_dir):
        (temp_dir / "base_1.json").write_text("x")
        (temp_dir / "base_2.json").write_text("x")
        (temp_dir / "other_3.json").write_text("x")
        magicgen.clear_output_files(temp_dir.as_posix(), "base")
        assert not (temp_dir / "base_1.json").exists()
        assert not (temp_dir / "base_2.json").exists()
        assert (temp_dir / "other_3.json").exists()


class TestSaveFunction:
    @pytest.fixture
    def temp_dir(self, tmp_path):
        d = tmp_path / "out"
        d.mkdir()
        return d

    def test_save_creates_and_writes(self, temp_dir):
        data = {"k": "v"}
        fname = "file.json"
        magicgen.write_file(temp_dir.as_posix(), fname, data)
        full = temp_dir / fname
        assert full.exists()
        loaded = json.loads(full.read_text())
        assert loaded == 'k'


class TestMultiprocessingFileCount:
    @pytest.fixture
    def temp_dir(self, tmp_path):
        d = tmp_path / "out"
        d.mkdir()
        return d

    @pytest.fixture(autouse=True)
    def dummy_schema(self, tmp_path):
        p = tmp_path / "schema.json"
        p.write_text(json.dumps({"a": "int:1"}))
        self.schema_path = str(p)
        return self.schema_path

    @pytest.mark.parametrize("files_count,workers", [
        (2, 1),
        (3, 2),
        (5, 4),
    ])
    def test_main_creates_correct_number_of_files(self, monkeypatch, temp_dir, files_count, workers):
        argv = [
            "magicgen.py",
            "--files_count", str(files_count),
            "--file_name", "out",
            "--file_prefix", "count",
            "--data_schema", self.schema_path,
            "--data_lines", "3",
            "--clear_path",
            "--multiprocessing", str(workers),
            temp_dir.as_posix()
        ]
        monkeypatch.setenv("PYTHONPATH", os.getcwd())
        monkeypatch.setattr(sys, "argv", argv)
        magicgen.main()
        files = sorted(os.listdir(temp_dir))
        assert len(files) == files_count

        for fn in files:
            content = (temp_dir / fn).read_text().splitlines()
            assert len(content) == 3
            for line in content:
                data = json.loads(line)
                assert isinstance(data, dict)


class TestValidateAllArguments:
    @pytest.fixture(autouse=True)
    def dummy_schema_file(self, tmp_path):
        p = tmp_path / "schema.json"
        p.write_text(json.dumps({"a": "int:1"}))
        self.schema_file = str(p)
        return self.schema_file

    def make_args(self, tmp_path):
        ns = argparse.Namespace()
        ns.files_count = 2
        ns.file_name = "f"
        ns.file_prefix = "count"
        ns.data_schema = self.schema_file
        ns.data_lines = 3
        ns.clear_path = False
        ns.multiprocessing = 1
        ns.path_to_save_files = tmp_path.as_posix()
        return ns

    def test_valid_all(self, tmp_path):
        args = self.make_args(tmp_path)
        cfg = magicgen.validate_all_arguments(args)
        assert cfg["path"] == tmp_path.as_posix()
        assert cfg["files_count"] == 2
        assert cfg["data_lines"] == 3
        assert cfg["schema"] == {"a": "int:1"}

    def test_negative_files_count(self, tmp_path):
        args = self.make_args(tmp_path)
        args.files_count = -1
        with pytest.raises(SystemExit):
            magicgen.validate_all_arguments(args)

    def test_zero_data_lines(self, tmp_path):
        args = self.make_args(tmp_path)
        args.data_lines = 0
        with pytest.raises(SystemExit):
            magicgen.validate_all_arguments(args)

    def test_negative_multiprocessing(self, tmp_path):
        args = self.make_args(tmp_path)
        args.multiprocessing = -1
        with pytest.raises(SystemExit):
            magicgen.validate_all_arguments(args)

    def test_too_many_processes(self, tmp_path, monkeypatch):
        args = self.make_args(tmp_path)
        monkeypatch.setattr(magicgen.os, "cpu_count", lambda: 2)
        args.multiprocessing = 5
        cfg = magicgen.validate_all_arguments(args)
        assert cfg["multiprocessing"] == 2

    def test_invalid_path_exits(self, tmp_path):
        args = self.make_args(tmp_path)
        args.path_to_save_files = "/"
        with pytest.raises(SystemExit):
            magicgen.validate_all_arguments(args)


class TestHelperFunctions:
    def test_make_filename_count(self):
        name = magicgen.make_filename("base", "count", 3)
        assert name == "base_3.json"

    def test_make_filename_random(self, monkeypatch):
        monkeypatch.setattr(random, "randint", lambda a, b: 5555)
        name = magicgen.make_filename("base", "random", 1)
        assert name == "base_5555.json"

    def test_make_filename_uuid(self, monkeypatch):
        fake = uuid.UUID("00000000-0000-0000-0000-000000000001")
        monkeypatch.setattr(uuid, "uuid4", lambda: fake)
        name = magicgen.make_filename("base", "uuid", 9)
        assert name.endswith("00000000-0000-0000-0000-000000000001.json")

    def test_make_filename_fallback(self):
        name = magicgen.make_filename("b", "unknown", 1)
        assert name.startswith("b_") and name.endswith(".json")

    def test_generate_line_and_data_lines(self, monkeypatch):
        orig = magicgen.parse_field
        monkeypatch.setattr(magicgen, "parse_field", lambda spec, field: orig(spec, field))

        schema = {"a": "int:1", "b": "str:hi"}
        ln = magicgen.generate_line(schema)
        assert set(ln.keys()) == set(schema.keys())

        lines = magicgen.generate_data_lines(schema, 4)
        assert isinstance(lines, list) and len(lines) == 4
        assert all(isinstance(r, dict) for r in lines)

    def test_generate_worker(self, tmp_path, monkeypatch):
        monkeypatch.setattr(magicgen, "generate_data_lines", lambda s, c: [{"x": 1}, {"x": 2}])
        calls = []
        monkeypatch.setattr(magicgen, "write_file", lambda p, f, d: calls.append((p, f, d)))
        args = (7, tmp_path.as_posix(), "base", "count", {"a": "int:1"}, 2)
        magicgen.generate_worker(args)
        assert len(calls) == 1
        p, fname, data = calls[0]
        assert p == tmp_path.as_posix()
        assert fname == "base_7.json"
        assert data == [{"x": 1}, {"x": 2}]


class TestLoadDefaultsFromConfig:
    def test_defaults_when_no_ini(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        open("default.ini", "w").close()
        d = magicgen.load_defaults_from_config()
        assert d == {
            "files_count": 1,
            "file_name": "data",
            "file_prefix": "uuid",
            "data_lines": 1000,
            "multiprocessing": 1,
        }

    def test_overrides_via_ini(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg = configparser.ConfigParser()
        cfg["DEFAULT"] = {
            "files_count": "7",
            "file_name": "xd",
            "file_prefix": "pfx",
            "data_lines": "99",
            "multiprocessing": "3",
        }
        with open("default.ini", "w") as f:
            cfg.write(f)
        d = magicgen.load_defaults_from_config()
        assert d["files_count"] == 7
        assert d["file_name"] == "xd"
        assert d["file_prefix"] == "pfx"
        assert d["data_lines"] == 99
        assert d["multiprocessing"] == 3