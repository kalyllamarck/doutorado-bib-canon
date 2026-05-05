"""biblio_validador/parser/markdown.py — parser CommonMark + footnotes.

Offsets byte-exact sobre source UTF-8 NFC; ver D-09/D-11 do CONTEXT.md.
"""

import dataclasses
import re
import unicodedata
from pathlib import Path

from loguru import logger
from markdown_it import MarkdownIt
from markdown_it.token import Token
from mdit_py_plugins.footnote import footnote_plugin

from biblio_validador.parser.types import Paragrafo, TipoSecao

_REGEX_FOOTNOTE_REF = re.compile(r"\[\^([^\]]+)\]")
_RE_PUNCT = re.compile(r"[^\w\s-]", re.UNICODE)
_RE_SPACES = re.compile(r"\s+")


class ParserMd:
    """Parser CommonMark + footnotes para biblio_validador.

    Offsets são relativos ao source UTF-8 NFC. Arquivos em NFD
    (ex.: macOS) são convertidos silenciosamente. Validadores
    operam sempre em NFC.
    """

    def __init__(self) -> None:
        self._md = MarkdownIt().use(footnote_plugin)
        self._mapa_secao = self._carregar_mapa_secao()

    def parsear(self, path: Path) -> list[Paragrafo]:
        logger.info(f"parsear: {path}")
        try:
            raw = path.read_bytes()
        except FileNotFoundError:
            logger.error(f"arquivo não encontrado: {path}")
            raise

        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            logger.error(f"encoding inválido em {path}")
            raise

        # BOM strip (Pitfall 6 — antes de NFC)
        if text.startswith("\ufeff"):
            text = text[1:]
        # CRLF -> LF (D-20)
        text = text.replace("\r\n", "\n")
        # NFC source-único (D-11, CORE-11)
        text_nfc = unicodedata.normalize("NFC", text)
        if text != text_nfc:
            logger.info(f"source NFD detectado, convertido para NFC: {path}")

        if not text_nfc.strip():
            return []

        src_bytes = text_nfc.encode("utf-8")
        linha_offsets = self._construir_linha_offsets(src_bytes)

        tokens = self._md.parse(text_nfc)
        paragrafos = self._walk(tokens, src_bytes, linha_offsets, path)
        paragrafos = self._resolver_pais(paragrafos)
        logger.info(f"parsear: {len(paragrafos)} parágrafos")
        return paragrafos

    @staticmethod
    def _construir_linha_offsets(src_bytes: bytes) -> list[int]:
        """Tabela cumulativa de offsets de início de cada linha.

        linha_offsets[k] = offset em bytes do início da linha
        (0-indexed). Sentinela final = len(src_bytes) garante que
        slicing do último bloco funcione mesmo sem trailing newline.
        """
        offsets = [0]
        for i, b in enumerate(src_bytes):
            if b == 0x0A:
                offsets.append(i + 1)
        if offsets[-1] != len(src_bytes):
            offsets.append(len(src_bytes))
        return offsets

    @classmethod
    def _carregar_mapa_secao(cls) -> dict[str, TipoSecao]:
        return {
            "resumo": TipoSecao.RESUMO,
            "palavras-chave": TipoSecao.PALAVRAS_CHAVE,
            "palavras chave": TipoSecao.PALAVRAS_CHAVE,
            "palavraschave": TipoSecao.PALAVRAS_CHAVE,
            "abstract": TipoSecao.ABSTRACT,
            "keywords": TipoSecao.KEYWORDS,
            "sumario": TipoSecao.SUMARIO,
            "introducao": TipoSecao.INTRODUCAO,
            "consideracoes finais": TipoSecao.CONCLUSAO,
            "conclusao": TipoSecao.CONCLUSAO,
            "referencias": TipoSecao.REFERENCIAS,
            "notas": TipoSecao.NOTA_RODAPE,
            "notas de rodape": TipoSecao.NOTA_RODAPE,
        }

    def _classificar_heading(
        self, texto: str, nivel: int, is_first_h1: bool
    ) -> TipoSecao:
        # Ordem load-bearing (D-06): is_first_h1 → mapa → SECAO → DESCONHECIDO
        if nivel == 1 and is_first_h1:
            return TipoSecao.TITULO
        chave = self._normalizar_heading(texto)
        if chave in self._mapa_secao:
            return self._mapa_secao[chave]
        if nivel >= 2:
            return TipoSecao.SECAO
        return TipoSecao.DESCONHECIDO

    @staticmethod
    def _normalizar_heading(texto: str) -> str:
        t = unicodedata.normalize("NFKD", texto)
        t = "".join(c for c in t if not unicodedata.combining(c))
        t = t.casefold()
        t = _RE_PUNCT.sub(" ", t)
        t = _RE_SPACES.sub(" ", t).strip()
        return t

    def _build_paragrafo(
        self,
        token: Token,
        src_bytes: bytes,
        linha_offsets: list[int],
        arquivo: Path,
        indice: int,
        tipo: TipoSecao,
        nivel_heading: int | None,
        ref_nota: str | None,
    ) -> Paragrafo:
        # token.map = [start, end] (0-indexed half-open)
        # → linha_inicio = map[0] + 1 ; linha_fim = map[1] (Pitfall 2)
        assert token.map is not None  # mypy strict narrowing (Pitfall 8)
        start, end = token.map
        offset_bytes = linha_offsets[start]
        end_offset = linha_offsets[end]
        # Strip trailing newline do conteúdo, mantendo offset_bytes
        # intacto (Pitfall 3)
        chunk = src_bytes[offset_bytes:end_offset].rstrip(b"\n")
        # Footnote body: pular o prefixo de definição "[^label]: "
        # (sintaxe markdown, não conteúdo). Ajusta offset/len para
        # preservar round-trip byte-exact (Test 6 invariante).
        if tipo == TipoSecao.NOTA_RODAPE and ref_nota is not None:
            prefixo = f"[^{ref_nota}]: ".encode()
            if chunk.startswith(prefixo):
                offset_bytes += len(prefixo)
                chunk = chunk[len(prefixo) :]
        texto = chunk.decode("utf-8")
        return Paragrafo(
            arquivo=arquivo,
            indice=indice,
            tipo=tipo,
            nivel_heading=nivel_heading,
            texto=texto,
            linha_inicio=start + 1,
            linha_fim=end,
            offset_bytes=offset_bytes,
            len_bytes=len(chunk),
            ref_nota=ref_nota,
            paragrafo_pai_idx=None,
        )

    def _walk(
        self,
        tokens: list[Token],
        src_bytes: bytes,
        linha_offsets: list[int],
        arquivo: Path,
    ) -> list[Paragrafo]:
        out: list[Paragrafo] = []
        current_secao = TipoSecao.DESCONHECIDO
        is_first_h1 = True
        in_footnote: str | None = None

        i = 0
        while i < len(tokens):
            t = tokens[i]
            if t.type == "footnote_open":
                in_footnote = t.meta.get("label")
                i += 1
                continue
            if t.type == "footnote_close":
                in_footnote = None
                i += 1
                continue
            if t.type == "heading_open":
                nivel = int(t.tag[1])
                inline = tokens[i + 1]
                secao = self._classificar_heading(
                    inline.content, nivel, is_first_h1
                )
                if nivel == 1 and is_first_h1:
                    is_first_h1 = False
                current_secao = secao
                out.append(
                    self._build_paragrafo(
                        t,
                        src_bytes,
                        linha_offsets,
                        arquivo,
                        indice=len(out),
                        tipo=secao,
                        nivel_heading=nivel,
                        ref_nota=None,
                    )
                )
                i += 3  # heading_open + inline + heading_close
                continue
            if t.type == "paragraph_open":
                # Pitfall 1: paragraph_open dentro de footnote_open
                # tem map; footnote_open tem map=None
                tipo = TipoSecao.NOTA_RODAPE if in_footnote else current_secao
                out.append(
                    self._build_paragrafo(
                        t,
                        src_bytes,
                        linha_offsets,
                        arquivo,
                        indice=len(out),
                        tipo=tipo,
                        nivel_heading=None,
                        ref_nota=in_footnote,
                    )
                )
                i += 1
                continue
            if t.type == "fence":
                out.append(
                    self._build_paragrafo(
                        t,
                        src_bytes,
                        linha_offsets,
                        arquivo,
                        indice=len(out),
                        tipo=TipoSecao.DESCONHECIDO,
                        nivel_heading=None,
                        ref_nota=None,
                    )
                )
                i += 1
                continue
            # Pitfall 7: bullet_list_open / list_item_open /
            # blockquote_open são SILENCIOSAMENTE pulados — seu
            # paragraph_open interno será emitido na próxima iteração
            i += 1
        return out

    @staticmethod
    def _resolver_pais(
        paragrafos: list[Paragrafo],
    ) -> list[Paragrafo]:
        """Pass 2: resolve paragrafo_pai_idx para Paragrafo(NOTA_RODAPE)."""
        label_to_idx: dict[str, int] = {}
        for p in paragrafos:
            if p.tipo == TipoSecao.NOTA_RODAPE:
                continue
            for m in _REGEX_FOOTNOTE_REF.finditer(p.texto):
                label = m.group(1)
                if label not in label_to_idx:
                    label_to_idx[label] = p.indice

        final: list[Paragrafo] = []
        for p in paragrafos:
            if p.tipo == TipoSecao.NOTA_RODAPE and p.ref_nota:
                pai_idx = label_to_idx.get(p.ref_nota)
                if pai_idx is None:
                    logger.warning(
                        f"footnote órfã: [^{p.ref_nota}] sem ref "
                        f"localizável em {p.arquivo}"
                    )
                final.append(dataclasses.replace(p, paragrafo_pai_idx=pai_idx))
            else:
                final.append(p)
        return final
