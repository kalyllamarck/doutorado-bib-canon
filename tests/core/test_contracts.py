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

import json
import re
from collections.abc import Mapping
from dataclasses import FrozenInstanceError
from pathlib import Path
from typing import ClassVar

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


# ============================================================================
# Success criterion #2: carregar_regras() compila regex 1x (cache class-level)
# ============================================================================


class _ValidadorComCache(ValidadorBase):
    """Subclasse concreta usando o pattern cache via cls.__dict__.get."""

    JSON_SOURCE: ClassVar[Path] = FIXT / "regras_fake.json"
    SCOPE: ClassVar[Scope] = Scope.PARAGRAFO

    @classmethod
    def carregar_regras(cls) -> Mapping[str, re.Pattern[str]]:
        cached = cls.__dict__.get("_regras_compiladas")
        if cached is not None:
            return cached  # type: ignore[no-any-return]
        result = _carregar_json_simples(cls.JSON_SOURCE)
        cls._regras_compiladas = result
        return result

    def validar(self, paragrafos: list[Paragrafo]) -> list[Violacao]:
        return []


class _ValidadorSubA(_ValidadorComCache):
    """Cache per-subclass — JSON_SOURCE_A."""

    JSON_SOURCE: ClassVar[Path] = FIXT / "regras_fake.json"


class _ValidadorSubB(_ValidadorComCache):
    """Cache per-subclass — JSON_SOURCE_B (str_e_lista)."""

    JSON_SOURCE: ClassVar[Path] = FIXT / "regras_str_e_lista.json"


def test_carregar_regras_cache_hit() -> None:
    """Chamar carregar_regras() 2x retorna o mesmo objeto (id() identico)."""
    # Limpar cache de outros testes
    _ValidadorComCache._regras_compiladas = None
    r1 = _ValidadorComCache.carregar_regras()
    r2 = _ValidadorComCache.carregar_regras()
    assert id(r1) == id(r2), "cache miss — recompilou"


def test_carregar_regras_per_subclass_isolation() -> None:
    """Subclasses A e B com JSON_SOURCE distintos NAO compartilham cache.

    RESEARCH Pitfall 2: getattr(cls, '_x') traversaria MRO; cls.__dict__.get
    e' per-subclass.
    """
    # Limpar caches herdados
    for kls in (_ValidadorComCache, _ValidadorSubA, _ValidadorSubB):
        kls._regras_compiladas = None
    rA = _ValidadorSubA.carregar_regras()
    rB = _ValidadorSubB.carregar_regras()
    assert id(rA) != id(rB), "Sub A e B compartilharam cache (Pitfall 2)"
    # rA tem cst_999 (regras_fake); rB tem cst_str/cst_lista/cst_alt_key
    assert "cst_999" in rA
    assert {"cst_str", "cst_lista", "cst_alt_key"}.issubset(rB.keys())


# ============================================================================
# Cobertura de erros (D-22, D-33)
# ============================================================================


def test_carregar_regras_file_not_found() -> None:
    """JSON_SOURCE inexistente propaga FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        _carregar_json_simples(Path("/does/not/exist.json"))


def test_carregar_regras_json_decode_error() -> None:
    """JSON malformado propaga json.JSONDecodeError."""
    with pytest.raises(json.JSONDecodeError):
        _carregar_json_simples(FIXT / "regras_malformadas.json")


def test_carregar_regras_regex_error() -> None:
    """Regex invalido propaga re.error com regra_id no message."""
    with pytest.raises(re.error, match="cst_invalido"):
        _carregar_json_simples(FIXT / "regras_regex_invalido.json")


def test_carregar_regras_normalizes_str_and_list() -> None:
    """RESEARCH Pattern 5 + skip-branch: aceita str, list, chave alternativa,
    e PULA entradas sem regex (espelha cst_005 com so exemplos_proibidos).

    Coverage do branch `if raw is None: continue` em _carregar_json_simples.
    """
    result = _carregar_json_simples(FIXT / "regras_str_e_lista.json")
    # cst_str, cst_lista, cst_alt_key compilam; cst_skip e' pulado
    assert set(result.keys()) == {"cst_str", "cst_lista", "cst_alt_key"}
    assert "cst_skip" not in result, "entrada sem regex deveria ser pulada"
    # Cada Pattern e' um re.Pattern compilado
    for rid, pattern in result.items():
        assert isinstance(pattern, re.Pattern), f"{rid} nao e' Pattern"


# ============================================================================
# Success criterion #3: pode_corrigir retorna False fora de VIOLACAO_IDS
# ============================================================================


class _FixerCompleto(FixerBase):
    """Subclasse concreta com VIOLACAO_IDS limitado a {cst_999}."""

    VIOLACAO_IDS: ClassVar[frozenset[str]] = frozenset({"cst_999"})
    MODO: ClassVar[ModoFixer] = ModoFixer.AUTO

    def propor_patches(
        self,
        v: Violacao,
        contexto: ContextoFixer,
    ) -> list[Patch]:
        return []

    def aplicar(
        self,
        patches: list[Patch],
        modo_interativo: bool,
    ) -> AplicacaoResultado:
        return AplicacaoResultado((), (), (), 0)


def test_pode_corrigir_returns_true_for_known_id() -> None:
    """v.regra_id em VIOLACAO_IDS -> True."""
    fixer = _FixerCompleto()
    v = _make_violacao(regra_id="cst_999")
    assert fixer.pode_corrigir(v) is True


def test_pode_corrigir_returns_false_for_unknown_id() -> None:
    """v.regra_id fora de VIOLACAO_IDS -> False (success criterion #3)."""
    fixer = _FixerCompleto()
    v = _make_violacao(regra_id="cst_001")
    assert fixer.pode_corrigir(v) is False


# ============================================================================
# Dataclasses auxiliares: AplicacaoResultado (frozen+slots) +
# ContextoFixer (eq=False)
# ============================================================================


def test_aplicacao_resultado_frozen_slots() -> None:
    """AplicacaoResultado frozen+slots: reatribuir gera FrozenInstanceError."""
    ar = AplicacaoResultado(
        patches_aceitos=(),
        patches_rejeitados=(),
        patches_suprimidos=(),
        bytes_modificados=42,
    )
    assert ar.bytes_modificados == 42
    assert hasattr(AplicacaoResultado, "__slots__")
    with pytest.raises(FrozenInstanceError):
        ar.bytes_modificados = 0  # type: ignore[misc]


def test_contexto_fixer_eq_false_unhashable_safe() -> None:
    """ContextoFixer com eq=False e' instanciavel mesmo com Mapping field.

    RESEARCH Pitfall 4: sem eq=False, frozen+slots+dict-field gera __hash__
    auto que tenta hashear Mapping (dict) -> TypeError em hash() ou em
    qualquer uso como key. Com eq=False:
        - instancia normalmente
        - ContextoFixer.__hash__ e' herdado de object (id-based) OU None
        - eq usa identidade (id())
    """
    paragrafo = _make_paragrafo()
    pat = re.compile(r"\bfake\b")
    ctx = ContextoFixer(
        paragrafo=paragrafo,
        todas_violacoes_paragrafo=(),
        regras_compiladas={"cst_999": pat},
    )
    # Instanciacao bem-sucedida e' a evidencia primaria de Pitfall 4 mitigado
    assert ctx.paragrafo == paragrafo
    assert ctx.regras_compiladas["cst_999"] is pat
    # Nao acessamos hash(ctx) — eq=False com frozen=True pode ainda dar
    # __hash__ herdado de object (id-based) que NAO levanta TypeError.
    # O contrato e': eq=False evita que dataclass tente sintetizar
    # __eq__/__hash__ baseado em fields (que falharia com Mapping).


# ============================================================================
# Smoke test: re-export do core/__init__.py
# ============================================================================


def test_core_reexport_smoke() -> None:
    """Os 10 simbolos da Phase 3 + Phase 4 estao em biblio_validador.core."""
    import biblio_validador.core as core_mod

    expected = {
        "AplicacaoResultado",
        "ContextoFixer",
        "EstadoPatch",
        "FixerBase",
        "ModoFixer",
        "Patch",
        "Scope",
        "Severidade",
        "ValidadorBase",
        "Violacao",
    }
    assert set(core_mod.__all__) == expected
