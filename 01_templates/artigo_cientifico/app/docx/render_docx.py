#!/usr/bin/env python3
"""render_docx.py — Gera .docx ABNT a partir dos JSONs canônicos.

Lê os JSONs de `../../caracteristicas/` (campo `formato_word`) e
o snapshot `_abnt_internals/` (estilos, margens, sectPr do docx-modelo)
e emite o `.docx` final via lsa-componentes (recompor + lib_ooxml).

Uso:
    python3 render_docx.py --conteudo artigo.json --out saida.docx
    python3 render_docx.py --conteudo artigo.json --out saida.docx --validar

O `artigo.json` é um dict com as seções do artigo. Veja SCHEMA abaixo.

Dependência: lsa-componentes instalado no venv de bib-extrator-componentes-docx.
    Ative com: source ~/projetos/bib-extrator-componentes-docx/.venv/bin/activate
    Ou instale: pip install -e ~/projetos/bib-extrator-componentes-docx
"""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from copy import deepcopy
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Caminhos canônicos
# ---------------------------------------------------------------------------

_THIS_DIR = Path(__file__).parent
_INTERNALS_DIR = _THIS_DIR / "_abnt_internals"
_CARACTERISTICAS_DIR = (
    _THIS_DIR / ".." / ".." / "caracteristicas"
).resolve()

# ---------------------------------------------------------------------------
# SCHEMA esperado em artigo.json
# ---------------------------------------------------------------------------

SCHEMA_EXEMPLO: dict[str, Any] = {
    "titulo_pt": "Título do artigo em português",
    "titulo_en": "Article title in English",
    "autores": [
        {
            "nome": "Kalyl Lamarck Silvério Pereira",
            "nota": (
                "Doutor em Direito pela UNIFOR. "
                "Professor do PPGD/Unifor."
            ),
        }
    ],
    "resumo": "Texto do resumo em português (150-250 palavras).",
    "palavras_chave": [
        "direito constitucional",
        "doutorado",
        "ABNT",
    ],
    "abstract": "Abstract text in English.",
    "keywords": ["constitutional law", "doctorate", "ABNT"],
    "sumario": [],   # opcional; omitir para gerar automaticamente
    "secoes": [
        {
            "nivel": 1,
            "numero": "1",
            "titulo": "INTRODUÇÃO",
            "paragrafos": ["Texto do parágrafo 1.", "Texto do parágrafo 2."],
        },
        {
            "nivel": 2,
            "numero": "1.1",
            "titulo": "Subseção exemplo",
            "paragrafos": ["Texto."],
        },
    ],
    "referencias": [
        "SILVA, José. Título do livro. Fortaleza: Editora, 2024.",
    ],
}

# ---------------------------------------------------------------------------
# Importa lxml (dep de lsa-componentes)
# ---------------------------------------------------------------------------

try:
    from lxml import etree
except ImportError as exc:
    print(
        "[ERRO] lxml não encontrado. "
        "Ative o venv: source ~/projetos/"
        "bib-extrator-componentes-docx/.venv/bin/activate",
        file=sys.stderr,
    )
    raise SystemExit(1) from exc

# ---------------------------------------------------------------------------
# Importa lib_ooxml de lsa-componentes
# ---------------------------------------------------------------------------

try:
    from lsa_componentes.lib_ooxml import (
        dict_to_xml,
        dict_to_xml_bytes,
        reconstruir_docx_do_zero,
    )
except ImportError as exc:
    print(
        "[ERRO] lsa_componentes não encontrado. "
        "Instale com: pip install -e "
        "~/projetos/bib-extrator-componentes-docx",
        file=sys.stderr,
    )
    raise SystemExit(1) from exc

# ---------------------------------------------------------------------------
# Namespaces OOXML
# ---------------------------------------------------------------------------

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"


def _w(tag: str) -> str:
    return f"{W}{tag}"


# ---------------------------------------------------------------------------
# Funções de montagem de parágrafos
# ---------------------------------------------------------------------------

def _make_p(
    texto: str,
    pstyle: str | None = None,
    negrito: bool = False,
    italico: bool = False,
    tamanho_pt: int | None = None,
    alinhamento: str | None = None,
    recuo_cm: float = 0.0,
    espaco_antes_pt: int = 0,
    espaco_depois_pt: int = 0,
    keep_next: bool = False,
) -> etree._Element:
    """Cria <w:p> com formatação explícita via rPr/pPr."""
    p = etree.Element(_w("p"))
    pPr = etree.SubElement(p, _w("pPr"))

    if pstyle:
        ps = etree.SubElement(pPr, _w("pStyle"))
        ps.set(_w("val"), pstyle)

    if alinhamento:
        jc = etree.SubElement(pPr, _w("jc"))
        _val_map = {
            "centralizado": "center",
            "center": "center",
            "justificado": "both",
            "both": "both",
            "direita": "right",
            "right": "right",
            "esquerda": "left",
            "left": "left",
        }
        jc.set(_w("val"), _val_map.get(alinhamento, alinhamento))

    if recuo_cm > 0:
        # 1 cm ≈ 567 twips
        twips = int(recuo_cm * 567)
        ind = etree.SubElement(pPr, _w("ind"))
        ind.set(_w("firstLine"), str(twips))

    if espaco_antes_pt or espaco_depois_pt:
        spc = etree.SubElement(pPr, _w("spacing"))
        if espaco_antes_pt:
            spc.set(_w("before"), str(espaco_antes_pt * 20))
        if espaco_depois_pt:
            spc.set(_w("after"), str(espaco_depois_pt * 20))

    if keep_next:
        knxt = etree.SubElement(pPr, _w("keepNext"))

    if not texto:
        return p

    r = etree.SubElement(p, _w("r"))

    if negrito or italico or tamanho_pt:
        rPr = etree.SubElement(r, _w("rPr"))
        if negrito:
            etree.SubElement(rPr, _w("b"))
        if italico:
            etree.SubElement(rPr, _w("i"))
        if tamanho_pt:
            sz = etree.SubElement(rPr, _w("sz"))
            sz.set(_w("val"), str(tamanho_pt * 2))
            szCs = etree.SubElement(rPr, _w("szCs"))
            szCs.set(_w("val"), str(tamanho_pt * 2))

    t = etree.SubElement(r, _w("t"))
    t.set(XML_SPACE, "preserve")
    t.text = texto
    return p


def _p_vazio() -> etree._Element:
    """Parágrafo vazio (linha em branco)."""
    return _make_p("")


# ---------------------------------------------------------------------------
# Carrega sectPr do snapshot
# ---------------------------------------------------------------------------

def _carregar_sect_pr() -> etree._Element | None:
    sect_json = _INTERNALS_DIR / "section_properties.json"
    if not sect_json.exists():
        return None
    d = json.loads(sect_json.read_text(encoding="utf-8"))
    return dict_to_xml(d)


# ---------------------------------------------------------------------------
# Constrói o body do documento
# ---------------------------------------------------------------------------

def _construir_body(artigo: dict[str, Any]) -> list[etree._Element]:
    """Monta todos os elementos do body na ordem canônica ABNT."""
    elementos: list[etree._Element] = []

    # ------------------------------------------------------------------
    # 1. Título PT (negrito, centralizado, TNR 12)
    # ------------------------------------------------------------------
    titulo_pt = artigo.get("titulo_pt", "")
    if titulo_pt:
        elementos.append(
            _make_p(
                titulo_pt,
                negrito=True,
                alinhamento="center",
                tamanho_pt=12,
            )
        )
        elementos.append(_p_vazio())

    # ------------------------------------------------------------------
    # 2. Título EN (itálico, centralizado, TNR 12)
    # ------------------------------------------------------------------
    titulo_en = artigo.get("titulo_en", "")
    if titulo_en:
        elementos.append(
            _make_p(
                titulo_en,
                italico=True,
                alinhamento="center",
                tamanho_pt=12,
            )
        )
        elementos.append(_p_vazio())

    # ------------------------------------------------------------------
    # 3. Autores (alinhamento direita, TNR 12)
    # ------------------------------------------------------------------
    autores = artigo.get("autores", [])
    for idx, autor in enumerate(autores, start=1):
        nome = autor.get("nome", "")
        marcador = f"{''.join(['¹²³⁴⁵⁶⁷⁸⁹'][idx - 1:idx])}"
        elementos.append(
            _make_p(
                f"{nome}{marcador}",
                alinhamento="right",
                tamanho_pt=12,
            )
        )
    if autores:
        elementos.append(_p_vazio())

    # ------------------------------------------------------------------
    # 4. RESUMO
    # ------------------------------------------------------------------
    resumo = artigo.get("resumo", "")
    if resumo:
        elementos.append(
            _make_p("Resumo", negrito=True, tamanho_pt=12)
        )
        elementos.append(
            _make_p(
                resumo,
                alinhamento="both",
                tamanho_pt=12,
            )
        )
        pcs = artigo.get("palavras_chave", [])
        if pcs:
            pc_texto = "Palavras-chave: " + "; ".join(pcs) + "."
            elementos.append(_make_p(pc_texto, tamanho_pt=12))
        elementos.append(_p_vazio())

    # ------------------------------------------------------------------
    # 5. ABSTRACT
    # ------------------------------------------------------------------
    abstract = artigo.get("abstract", "")
    if abstract:
        elementos.append(
            _make_p("Abstract", negrito=True, italico=True, tamanho_pt=12)
        )
        elementos.append(
            _make_p(
                abstract,
                italico=True,
                alinhamento="both",
                tamanho_pt=12,
            )
        )
        kws = artigo.get("keywords", [])
        if kws:
            kw_texto = "Keywords: " + "; ".join(kws) + "."
            elementos.append(_make_p(kw_texto, italico=True, tamanho_pt=12))
        elementos.append(_p_vazio())

    # ------------------------------------------------------------------
    # 6. Seções de desenvolvimento
    # ------------------------------------------------------------------
    for secao in artigo.get("secoes", []):
        nivel = secao.get("nivel", 1)
        numero = secao.get("numero", "")
        titulo = secao.get("titulo", "")
        titulo_completo = f"{numero} {titulo}".strip() if numero else titulo

        if nivel == 1:
            # Primária: CAIXA ALTA, negrito, espaço antes 18pt, depois 12pt
            elementos.append(
                _make_p(
                    titulo_completo.upper(),
                    negrito=True,
                    tamanho_pt=12,
                    alinhamento="left",
                    espaco_antes_pt=18,
                    espaco_depois_pt=12,
                    keep_next=True,
                )
            )
        else:
            # Secundária: case normal, negrito, espaço antes 12pt, depois 6pt
            elementos.append(
                _make_p(
                    titulo_completo,
                    negrito=True,
                    tamanho_pt=12,
                    alinhamento="left",
                    espaco_antes_pt=12,
                    espaco_depois_pt=6,
                    keep_next=True,
                )
            )

        for paragrafo in secao.get("paragrafos", []):
            elementos.append(
                _make_p(
                    paragrafo,
                    alinhamento="both",
                    tamanho_pt=12,
                    recuo_cm=1.25,
                )
            )

    # ------------------------------------------------------------------
    # 7. REFERÊNCIAS
    # ------------------------------------------------------------------
    refs = artigo.get("referencias", [])
    if refs:
        elementos.append(
            _make_p(
                "REFERÊNCIAS",
                negrito=True,
                tamanho_pt=12,
                alinhamento="left",
                espaco_antes_pt=18,
                espaco_depois_pt=12,
                keep_next=True,
            )
        )
        for ref in refs:
            elementos.append(
                _make_p(
                    ref,
                    alinhamento="left",
                    tamanho_pt=12,
                )
            )

    return elementos


# ---------------------------------------------------------------------------
# Wrap em <w:document>
# ---------------------------------------------------------------------------

def _wrap_document(
    body_elementos: list[etree._Element],
    sectPr: etree._Element | None,
) -> bytes:
    skel_json = _INTERNALS_DIR / "document_root_skeleton.json"
    if skel_json.exists():
        skel = json.loads(skel_json.read_text(encoding="utf-8"))
        nsmap_root = {
            None if k == "" else k: v
            for k, v in skel.get("nsmap", {}).items()
        }
        attrib_root = skel.get("attrib", {})
    else:
        nsmap_root = {
            "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        }
        attrib_root = {}

    document = etree.Element(
        _w("document"), attrib=attrib_root, nsmap=nsmap_root
    )
    body = etree.SubElement(document, _w("body"))
    for el in body_elementos:
        body.append(el)
    if sectPr is not None:
        body.append(deepcopy(sectPr))

    return etree.tostring(
        document, xml_declaration=True, encoding="UTF-8", standalone=True
    )


# ---------------------------------------------------------------------------
# Ponto de entrada principal
# ---------------------------------------------------------------------------

def render(
    artigo: dict[str, Any],
    out_docx: Path,
) -> None:
    """Gera o .docx ABNT a partir do dict `artigo`.

    Args:
        artigo: dict com campos definidos em SCHEMA_EXEMPLO.
        out_docx: caminho de saída do .docx.
    """
    if not _INTERNALS_DIR.exists():
        raise FileNotFoundError(
            f"_abnt_internals/ não encontrado em {_INTERNALS_DIR}. "
            "Execute a extração conforme README.md."
        )

    sectPr = _carregar_sect_pr()
    body_elementos = _construir_body(artigo)
    document_xml = _wrap_document(body_elementos, sectPr)

    if out_docx.exists():
        out_docx.unlink()

    # Usa a pasta _abnt_internals como "componentes_dir" para
    # reconstruir_docx_do_zero — a função espera _docx_internals/ dentro dela.
    # Criamos um pseudo-componentes_dir que aponta para o pai de _abnt_internals.
    componentes_dir = _THIS_DIR
    # reconstruir_docx_do_zero lê componentes_dir/_docx_internals/
    # Porém nosso snapshot está em _abnt_internals/. Criamos um symlink
    # temporário ou passamos o pai. Para manter sem symlinks, criamos
    # a estrutura esperada como um diretório temporário.
    import tempfile, shutil

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        # Cria a estrutura que reconstruir_docx_do_zero espera:
        #   <tmp>/componentes/_docx_internals/ -> cópia do _abnt_internals/
        comp_tmp = tmp_path / "componentes"
        comp_tmp.mkdir()
        shutil.copytree(_INTERNALS_DIR, comp_tmp / "_docx_internals")

        manifesto = reconstruir_docx_do_zero(
            comp_tmp, out_docx, document_xml
        )

    print(f"[OK] {out_docx} gerado ({out_docx.stat().st_size} bytes)")
    print(
        f"     XMLs internos: "
        f"{len(manifesto['arquivos_xml_reconstruidos'])}"
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--conteudo",
        type=Path,
        required=True,
        help="JSON com o conteúdo do artigo (veja SCHEMA_EXEMPLO no código)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("artigo_abnt.docx"),
        help="Caminho do .docx a gerar (default: artigo_abnt.docx)",
    )
    parser.add_argument(
        "--schema",
        action="store_true",
        help="Imprime o schema de exemplo e sai",
    )
    args = parser.parse_args()

    if args.schema:
        print(json.dumps(SCHEMA_EXEMPLO, ensure_ascii=False, indent=2))
        return

    if not args.conteudo.exists():
        print(f"[ERRO] {args.conteudo} não encontrado", file=sys.stderr)
        sys.exit(1)

    artigo = json.loads(args.conteudo.read_text(encoding="utf-8"))
    render(artigo, args.out)


if __name__ == "__main__":
    _cli()
