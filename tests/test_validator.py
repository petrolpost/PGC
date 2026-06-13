"""Test PGCValidator: load_and_validate and validate_directory."""

import pytest
import yaml
from pathlib import Path

from pgc_core.validator import PGCValidator, PGCValidationError
from conftest import make_valid_doc, write_yaml


class TestLoadAndValidate:
    """Validator load_and_validate: file loading and error handling."""

    def test_file_not_found(self) -> None:
        with pytest.raises(FileNotFoundError, match="未找到"):
            PGCValidator.load_and_validate("/nonexistent/path/agent.pgc.yaml")

    def test_invalid_yaml_syntax(self, tmp_path: Path) -> None:
        bad_yaml = tmp_path / "bad.pgc.yaml"
        bad_yaml.write_text("personas: [\n  invalid yaml here", encoding="utf-8")
        with pytest.raises(PGCValidationError, match="YAML 解析失败"):
            PGCValidator.load_and_validate(str(bad_yaml))

    def test_non_dict_root(self, tmp_path: Path) -> None:
        non_dict = tmp_path / "list.pgc.yaml"
        non_dict.write_text("- item1\n- item2", encoding="utf-8")
        with pytest.raises(PGCValidationError, match="字典"):
            PGCValidator.load_and_validate(str(non_dict))

    def test_validation_error_formatting(self, tmp_path: Path) -> None:
        # Missing required field: output_target
        data = {
            "personas": [
                {"id": "p1", "name": "P1", "responsibilities": ["r1"]}
            ]
        }
        yaml_path = write_yaml(tmp_path, data)
        with pytest.raises(PGCValidationError, match="验证失败"):
            PGCValidator.load_and_validate(str(yaml_path))

    def test_valid_file_loads(self, tmp_path: Path) -> None:
        data = make_valid_doc()
        yaml_path = write_yaml(tmp_path, data)
        doc = PGCValidator.load_and_validate(str(yaml_path))
        assert doc.personas[0].id == "reviewer"


class TestValidateDirectory:
    """Validator validate_directory: batch scanning of .pgc.yaml files."""

    def test_directory_with_valid_files(self, tmp_path: Path) -> None:
        data = make_valid_doc()
        write_yaml(tmp_path, data, filename="agent.pgc.yaml")
        # Need .pgc.yaml extension for directory scan
        pgc_file = tmp_path / "agent.pgc.yaml"
        pgc_file.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")

        results = PGCValidator.validate_directory(str(tmp_path))
        assert len(results["success"]) == 1
        assert len(results["failed"]) == 0

    def test_directory_with_invalid_file(self, tmp_path: Path) -> None:
        bad_data = {"personas": [{"id": "p1"}]}  # missing required fields
        pgc_file = tmp_path / "bad.pgc.yaml"
        pgc_file.write_text(yaml.dump(bad_data, allow_unicode=True, sort_keys=False), encoding="utf-8")

        results = PGCValidator.validate_directory(str(tmp_path))
        assert len(results["success"]) == 0
        assert len(results["failed"]) == 1

    def test_empty_directory(self, tmp_path: Path) -> None:
        results = PGCValidator.validate_directory(str(tmp_path))
        assert len(results["success"]) == 0
        assert len(results["failed"]) == 0
