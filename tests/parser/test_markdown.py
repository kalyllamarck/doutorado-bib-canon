"""Smoke tests Phase 2 — parser CommonMark + footnotes (D-26)."""

import unicodedata
from pathlib import Path

import pytest

from biblio_validador.parser import ParserMd, Paragrafo, TipoSecao

EOLICA_FIXTURE = Path(__file__).parent / "fixtures" / "eolica_first_30.md"


@pytest.fixture
def parser() -> ParserMd:
    return ParserMd()


def test_paragrafo_simples_um_so_paragrafo(
    tmp_path: Path, parser: ParserMd
) -> None:
    """D-26.1: arquivo com 1 parágrafo simples."""
    f = tmp_path / "simples.md"
    f.write_text("Texto simples.\n", encoding="utf-8")
    paragrafos = parser.parsear(f)
    assert len(paragrafos) == 1
    p = paragrafos[0]
    assert p.linha_inicio == 1
    assert p.linha_fim == 1  # Pitfall 2 — half-open → 1-based inclusivo
    assert p.offset_bytes == 0
    assert p.tipo == TipoSecao.DESCONHECIDO
    assert p.texto == "Texto simples."  # Pitfall 3 — sem trailing \n
    assert p.nivel_heading is None
    assert p.ref_nota is None


def test_heading_classificacao_e_heranca(
    tmp_path: Path, parser: ParserMd
) -> None:
    """D-26.2: 3 headings canônicos com herança de tipo (D-05/D-06/D-07)."""
    src = (
        "# Título do Artigo\n"
        "\n"
        "## RESUMO\n"
        "\n"
        "Parágrafo do resumo.\n"
        "\n"
        "## INTRODUÇÃO\n"
        "\n"
        "Parágrafo da intro.\n"
    )
    f = tmp_path / "headings.md"
    f.write_text(src, encoding="utf-8")
    paragrafos = parser.parsear(f)

    tipos = [(p.tipo, p.nivel_heading, p.texto[:20]) for p in paragrafos]
    assert tipos[0] == (TipoSecao.TITULO, 1, "# Título do Artigo")
    assert tipos[1] == (TipoSecao.RESUMO, 2, "## RESUMO")
    assert tipos[2] == (TipoSecao.RESUMO, None, "Parágrafo do resumo.")
    assert tipos[3] == (TipoSecao.INTRODUCAO, 2, "## INTRODUÇÃO")
    assert tipos[4][0] == TipoSecao.INTRODUCAO


def test_normalizacao_nfc(tmp_path: Path, parser: ParserMd) -> None:
    """D-26.3: NFD → NFC normalization (CORE-11)."""
    nfd = "cafe\u0301"  # NFD: e + combining acute (U+0301)
    src = f"Texto com {nfd}.\n"
    f = tmp_path / "nfd.md"
    f.write_bytes(src.encode("utf-8"))
    paragrafos = parser.parsear(f)
    assert len(paragrafos) == 1
    # NFC composed: "caf" + precomposed e-acute (U+00E9)
    assert "café" in paragrafos[0].texto
    # Inverse check: combining acute MUST NOT survive NFC (Pitfall 4)
    assert "\u0301" not in paragrafos[0].texto


def test_footnote_separa_e_linka(
    tmp_path: Path, parser: ParserMd
) -> None:
    """D-26.4: footnote separation + linkage (D-14/D-15/D-16)."""
    src = (
        "Parágrafo com referência[^1].\n"
        "\n"
        "[^1]: Corpo da nota.\n"
    )
    f = tmp_path / "fn.md"
    f.write_text(src, encoding="utf-8")
    paragrafos = parser.parsear(f)

    notas = [p for p in paragrafos if p.tipo == TipoSecao.NOTA_RODAPE]
    corpos = [p for p in paragrafos if p.tipo != TipoSecao.NOTA_RODAPE]
    assert len(notas) == 1
    nota = notas[0]
    assert nota.ref_nota == "1"
    assert nota.texto == "Corpo da nota."
    pai = corpos[0]
    assert "[^1]" in pai.texto
    assert nota.paragrafo_pai_idx == pai.indice


def test_artigo_eolica_excerpt(parser: ParserMd) -> None:
    """D-26.5: artigo Eólica real (integration sub-fixture)."""
    if not EOLICA_FIXTURE.exists():
        pytest.skip("fixture não disponível")
    paragrafos = parser.parsear(EOLICA_FIXTURE)
    assert len(paragrafos) >= 5

    # Primeiro parágrafo: heading h1 = TITULO
    p0 = paragrafos[0]
    assert p0.linha_inicio == 1
    assert p0.tipo == TipoSecao.TITULO
    assert p0.nivel_heading == 1
    assert "Correntes eólicas" in p0.texto

    # heading "## RESUMO" na linha 9 do fixture
    resumos = [p for p in paragrafos
               if p.tipo == TipoSecao.RESUMO
               and p.nivel_heading == 2]
    assert len(resumos) == 1
    assert resumos[0].linha_inicio == 9

    # parágrafo do resumo na linha 11 herda RESUMO
    paragrafos_resumo = [p for p in paragrafos
                         if p.tipo == TipoSecao.RESUMO
                         and p.nivel_heading is None]
    assert len(paragrafos_resumo) == 1
    assert paragrafos_resumo[0].linha_inicio == 11
    assert "Investiga-se" in paragrafos_resumo[0].texto


def test_round_trip_offset_bytes(
    tmp_path: Path, parser: ParserMd
) -> None:
    """Property: src_bytes_nfc[offset:offset+len_bytes] == texto.encode().

    Pin do invariante byte-exact (Phase 5 PatchAplicador depende).
    Catches Pitfalls 2, 3, 4, 6 simultaneously.
    """
    src = (
        "# Title\n\nFirst para with é.\n\nSecond para[^1].\n\n"
        "[^1]: nota com **bold**.\n"
    )
    f = tmp_path / "rt.md"
    f.write_text(src, encoding="utf-8")
    paragrafos = parser.parsear(f)

    raw = f.read_bytes()
    nfc = unicodedata.normalize(
        "NFC", raw.decode("utf-8")
    ).encode("utf-8")

    for p in paragrafos:
        chunk = nfc[p.offset_bytes:p.offset_bytes + p.len_bytes]
        assert chunk.decode("utf-8") == p.texto, (
            f"round-trip falhou para {p.indice}: "
            f"chunk={chunk!r} texto={p.texto!r}"
        )
