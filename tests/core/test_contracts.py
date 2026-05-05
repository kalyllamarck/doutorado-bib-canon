"""Testes para core/contracts.py: CORE-04 (ValidadorBase) + CORE-05 (FixerBase).

Cobertura mapeada aos 4 success criteria do roadmap Phase 4:
    #1: TypeError em instanciacao de subclasse incompleta — testes
        test_validador_base_abstract_* + test_fixer_base_abstract_*
    #2: carregar_regras() compila regex 1x — test_carregar_regras_cache_hit
    #3: pode_corrigir(v) retorna False fora de VIOLACAO_IDS —
        test_pode_corrigir_*
    #4: testes unitarios passam — esta suite e a evidencia

Convencoes herdadas (Phase 3 D-26):
    - Helper de construcao com **overrides para reduzir duplicacao
    - test_aux_<descricao> autorizado para coverage gap fill
"""

from __future__ import annotations

import json  # noqa: F401  # used in T-04-03-03 (json.JSONDecodeError test)
import re
from collections.abc import Mapping
from dataclasses import FrozenInstanceError  # noqa: F401  # used in T-04-03-04
from pathlib import Path
from typing import ClassVar  # noqa: F401  # used in T-04-03-03/04 subclasses

import pytest

from biblio_validador.core import (
    AplicacaoResultado,
    ContextoFixer,
    EstadoPatch,  # noqa: F401  # used in T-04-03-04 smoke test (re-export)
    FixerBase,
    ModoFixer,
    Patch,
    Scope,
    Severidade,
    ValidadorBase,
    Violacao,
)
from biblio_validador.core.contracts import _carregar_json_simples
from biblio_validador.parser.types import Paragrafo, TipoSecao

FIXT = Path(__file__).parent / "fixtures"


def _make_violacao(**overrides: object) -> Violacao:
    """Builder minimo de Violacao para testes (Phase 3 convention)."""
    base: dict[str, object] = {
        "arquivo": Path("a.md"),
        "linha_inicio": 1,
        "linha_fim": 1,
        "col_inicio": 1,
        "col_fim": 5,
        "trecho_violador": "abcd",
        "regra_id": "cst_999",
        "regra_nome": "fake",
        "severidade": Severidade.ERRO,
    }
    base.update(overrides)
    return Violacao(**base)  # type: ignore[arg-type]


def _make_paragrafo() -> Paragrafo:
    """Builder minimo de Paragrafo para ContextoFixer.

    Campos seguem `src/biblio_validador/parser/types.py` (Phase 2):
        arquivo, indice, tipo, nivel_heading, texto, linha_inicio,
        linha_fim, offset_bytes, len_bytes, ref_nota, paragrafo_pai_idx
    """
    return Paragrafo(
        arquivo=Path("a.md"),
        indice=0,
        tipo=TipoSecao.CORPO,
        nivel_heading=None,
        texto="abcd",
        linha_inicio=1,
        linha_fim=1,
        offset_bytes=0,
        len_bytes=4,
        ref_nota=None,
        paragrafo_pai_idx=None,
    )


# ============================================================================
# Success criterion #1: TypeError em instanciacao de subclasse incompleta
# ============================================================================


def test_validador_base_abstract_validar() -> None:
    """Subclasse omitindo validar() deve levantar TypeError em ()."""

    class _Incomplete(ValidadorBase):
        JSON_SOURCE = FIXT / "regras_fake.json"
        SCOPE = Scope.PARAGRAFO

        @classmethod
        def carregar_regras(cls) -> Mapping[str, re.Pattern[str]]:
            return _carregar_json_simples(cls.JSON_SOURCE)

    with pytest.raises(TypeError, match="abstract"):
        _Incomplete()  # type: ignore[abstract]


def test_validador_base_abstract_carregar_regras() -> None:
    """Subclasse omitindo carregar_regras() deve levantar TypeError."""

    class _Incomplete(ValidadorBase):
        JSON_SOURCE = FIXT / "regras_fake.json"
        SCOPE = Scope.PARAGRAFO

        def validar(self, paragrafos: list[Paragrafo]) -> list[Violacao]:
            return []

    with pytest.raises(TypeError, match="abstract"):
        _Incomplete()  # type: ignore[abstract]


def test_fixer_base_abstract_propor_patches() -> None:
    """Subclasse FixerBase sem propor_patches levanta TypeError."""

    class _Incomplete(FixerBase):
        VIOLACAO_IDS = frozenset({"cst_999"})
        MODO = ModoFixer.AUTO

        def aplicar(
            self,
            patches: list[Patch],
            modo_interativo: bool,
        ) -> AplicacaoResultado:
            return AplicacaoResultado((), (), (), 0)

    with pytest.raises(TypeError, match="abstract"):
        _Incomplete()  # type: ignore[abstract]


def test_fixer_base_abstract_aplicar() -> None:
    """Subclasse de FixerBase omitindo aplicar deve levantar TypeError."""

    class _Incomplete(FixerBase):
        VIOLACAO_IDS = frozenset({"cst_999"})
        MODO = ModoFixer.AUTO

        def propor_patches(
            self,
            v: Violacao,
            contexto: ContextoFixer,
        ) -> list[Patch]:
            return []

    with pytest.raises(TypeError, match="abstract"):
        _Incomplete()  # type: ignore[abstract]
