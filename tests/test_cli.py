"""Smoke tests Phase 1 — valida 4 success criteria de CORE-12."""

import tomllib
from pathlib import Path

from typer.testing import CliRunner

import biblio_validador
from biblio_validador.cli import app

runner = CliRunner()


def test_validar_help_exit_zero() -> None:
    """Criterion #2: `validar --help` retorna exit 0 + nome canônico."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "biblioteca canônica" in result.output


def test_version_exposed() -> None:
    """Criterion #3: `biblio_validador.__version__` == '0.1.0'."""
    assert biblio_validador.__version__ == "0.1.0"


def test_pyproject_declares_m1_deps() -> None:
    """Criterion #4: pyproject.toml declara as 6 deps M1."""
    pyproject = Path(__file__).parent.parent / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    deps = " ".join(data["project"]["dependencies"])
    for required in (
        "markdown-it-py",
        "mdit-py-plugins",
        "pylatexenc",
        "typer",
        "rich",
        "loguru",
    ):
        assert required in deps, f"M1 dep ausente: {required}"
