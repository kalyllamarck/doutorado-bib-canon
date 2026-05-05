"""Smoke tests Phase 3 — Violacao + Patch + invariantes (D-28/D-29)."""

import json
from dataclasses import FrozenInstanceError, asdict
from pathlib import Path

import pytest

from biblio_validador.core import (
    EstadoPatch,
    Patch,
    Severidade,
    Violacao,
)

# ---------- CORE-02: Violacao success criteria ----------


def _violacao_minima(**overrides: object) -> Violacao:
    """Helper: Violacao com defaults validos, parametrizavel via kwargs."""
    base: dict[str, object] = dict(
        arquivo=Path("a.md"),
        linha_inicio=1,
        linha_fim=1,
        col_inicio=1,
        col_fim=5,
        trecho_violador="abcd",
        regra_id="lex_001",
        regra_nome="X",
        severidade=Severidade.ERRO,
    )
    base.update(overrides)
    return Violacao(**base)  # type: ignore[arg-type]


def test_violacao_instancia_com_frozen_e_slots() -> None:
    """D-28.1: Violacao instancia, e frozen e tem __slots__."""
    v = _violacao_minima()
    assert v.regra_id == "lex_001"
    assert v.sugestoes == ()  # default D-09
    assert v.principio_canonico_violado is None  # default D-09
    assert hasattr(v, "__slots__")
    assert not hasattr(v, "__dict__")


def test_violacao_frozen_raises_on_mutate() -> None:
    """D-28.4: mutar regra_id levanta FrozenInstanceError."""
    v = _violacao_minima()
    with pytest.raises(FrozenInstanceError):
        v.regra_id = "outro"  # type: ignore[misc]


def test_violacao_asdict_estrutural() -> None:
    """D-28.3 parte 1: asdict retorna dict estruturalmente correto."""
    v = _violacao_minima()
    d = asdict(v)
    assert isinstance(d, dict)
    expected_keys = {
        "arquivo",
        "linha_inicio",
        "linha_fim",
        "col_inicio",
        "col_fim",
        "trecho_violador",
        "regra_id",
        "regra_nome",
        "severidade",
        "sugestoes",
        "principio_canonico_violado",
    }
    assert set(d.keys()) == expected_keys
    assert d["regra_id"] == "lex_001"


def test_violacao_to_dict_json_roundtrip() -> None:
    """D-28.3 parte 2: json.dumps(to_dict()) round-trip preserva campos."""
    v = _violacao_minima(sugestoes=("alt1", "alt2"))
    s = json.dumps(v.to_dict())
    parsed = json.loads(s)
    assert parsed["regra_id"] == "lex_001"
    assert parsed["arquivo"] == "a.md"  # Path -> str
    assert parsed["severidade"] == "erro"  # Enum -> value
    assert parsed["sugestoes"] == ["alt1", "alt2"]  # tuple -> list
    assert parsed["principio_canonico_violado"] is None


@pytest.mark.parametrize(
    "overrides, msg_substr",
    [
        (dict(linha_inicio=0), "linha_inicio"),
        (dict(linha_inicio=2, linha_fim=1), "linha_fim"),
        (dict(col_inicio=0), "col_inicio"),
        (dict(col_inicio=5, col_fim=2, trecho_violador="ab"), "col_fim"),
    ],
)
def test_violacao_invariantes_raise(
    overrides: dict[str, object], msg_substr: str
) -> None:
    """D-29: __post_init__ raises ValueError com regra_id no contexto."""
    with pytest.raises(ValueError, match=msg_substr):
        _violacao_minima(**overrides)


# ---------- Severidade.peso() ----------


def test_severidade_peso_monotonica() -> None:
    """D-15/D-16: peso() retorna 0..3 monotonico crescente."""
    pesos = [
        Severidade.INFO.peso(),
        Severidade.ALERTA.peso(),
        Severidade.ERRO.peso(),
        Severidade.CRITICO.peso(),
    ]
    assert pesos == [0, 1, 2, 3]


# ---------- CORE-03: Patch success criteria ----------


def _patch_minimo(**overrides: object) -> Patch:
    """Helper: Patch com defaults validos, parametrizavel via kwargs."""
    base: dict[str, object] = dict(
        arquivo=Path("a.md"),
        linha=1,
        col_inicio=1,
        col_fim=5,
        texto_original="abcd",
        texto_substituto="efgh",
        motivo="cst_012 -> forma direta",
        confianca=1.0,
    )
    base.update(overrides)
    return Patch(**base)  # type: ignore[arg-type]


def test_patch_mutavel_estado() -> None:
    """D-28.2: Patch e mutavel em estado, slots proibe atributo novo."""
    p = _patch_minimo()
    assert p.estado == EstadoPatch.PROPOSTO  # default D-17
    assert p.requer_revisao_humana is False  # default D-17
    p.estado = EstadoPatch.ACEITO  # mutacao OK (nao frozen)
    assert p.estado == EstadoPatch.ACEITO
    with pytest.raises(AttributeError):
        p.atributo_novo = 42  # type: ignore[attr-defined]


def test_estado_patch_default_proposto() -> None:
    """D-20: EstadoPatch.PROPOSTO eh default e value 'proposto'."""
    p = _patch_minimo()
    assert p.estado is EstadoPatch.PROPOSTO
    assert p.estado.value == "proposto"


@pytest.mark.parametrize(
    "overrides, msg_substr",
    [
        (dict(confianca=1.5), "confianca"),
        (dict(confianca=-0.1), "confianca"),
        (dict(texto_original=""), "texto_original"),
        (dict(motivo=""), "motivo"),
        (dict(motivo="   "), "motivo"),  # whitespace-only
    ],
)
def test_patch_invariantes_raise(
    overrides: dict[str, object], msg_substr: str
) -> None:
    """D-29: __post_init__ raises ValueError em invariantes violadas."""
    with pytest.raises(ValueError, match=msg_substr):
        _patch_minimo(**overrides)


def test_patch_to_dict_json_roundtrip() -> None:
    """CORE-03 contract: json.dumps(patch.to_dict()) preserva campos."""
    p = _patch_minimo()
    s = json.dumps(p.to_dict())
    parsed = json.loads(s)
    assert parsed["motivo"] == "cst_012 -> forma direta"
    assert parsed["arquivo"] == "a.md"  # Path -> str
    assert parsed["estado"] == "proposto"  # Enum -> value
    assert parsed["confianca"] == 1.0


# ---------- Contract tests (RESEARCH "Contract Tests Especificos") ----------


def test_aux_violacao_frozenness_contract() -> None:
    """Contract 1: detecta regressao se alguem remover frozen=True."""
    params = Violacao.__dataclass_params__  # type: ignore[attr-defined]
    assert params.frozen is True


def test_aux_violacao_sugestoes_eh_tuple_nao_list() -> None:
    """Contract 3 + Pitfall 1: sugestoes e tuple, nao list."""
    v = _violacao_minima(sugestoes=("a", "b"))
    assert isinstance(v.sugestoes, tuple)
    assert not isinstance(v.sugestoes, list)


def test_aux_violacao_hashable_patch_unhashable() -> None:
    """Contract 5: Violacao hashable (frozen); Patch unhashable (mutavel)."""
    v1 = _violacao_minima()
    v2 = _violacao_minima()
    assert hash(v1) == hash(v2)  # mesmo conteudo -> mesmo hash
    assert len({v1, v2}) == 1  # set deduplica identicos
    p = _patch_minimo()
    with pytest.raises(TypeError):
        hash(p)  # Patch e unhashable (Pitfall 4)


def test_aux_imports_via_re_export_funcionam() -> None:
    """D-03: __init__.py re-exporta os 4 simbolos publicos."""
    from biblio_validador.core import __all__

    assert set(__all__) == {
        "EstadoPatch",
        "Patch",
        "Severidade",
        "Violacao",
    }


def test_aux_violacao_regra_id_vazio_raises() -> None:
    """D-22: regra_id vazio ou whitespace-only levanta ValueError."""
    with pytest.raises(ValueError, match="regra_id"):
        Violacao(
            arquivo=Path("a.md"),
            linha_inicio=1,
            linha_fim=1,
            col_inicio=1,
            col_fim=1,
            trecho_violador="",
            regra_id="   ",  # whitespace-only
            regra_nome="X",
            severidade=Severidade.ERRO,
        )


def test_aux_violacao_trecho_len_invariante() -> None:
    """D-22: trecho_violador len != col_fim - col_inicio (intra-linha)."""
    with pytest.raises(ValueError, match="trecho_violador"):
        Violacao(
            arquivo=Path("a.md"),
            linha_inicio=1,
            linha_fim=1,
            col_inicio=1,
            col_fim=3,  # span = 2 chars
            trecho_violador="xyz",  # 3 chars — mismatch
            regra_id="lex_001",
            regra_nome="X",
            severidade=Severidade.ERRO,
        )


def test_aux_patch_linha_col_invariantes_raise() -> None:
    """D-23: linha<1, col_inicio<1 e col_fim<col_inicio levantam ValueError."""
    with pytest.raises(ValueError, match="linha"):
        _patch_minimo(linha=0)
    with pytest.raises(ValueError, match="col_inicio"):
        _patch_minimo(col_inicio=0)
    with pytest.raises(ValueError, match="col_fim"):
        _patch_minimo(col_inicio=5, col_fim=3)


def test_aux_normalize_for_json_list_branch() -> None:
    """_normalize_for_json cobre branch list (linha 30 do modulo)."""
    from pathlib import Path as P

    from biblio_validador.core.dataclasses import _normalize_for_json

    result = _normalize_for_json([P("x.md"), "texto"])
    assert result == ["x.md", "texto"]
