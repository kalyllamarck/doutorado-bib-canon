"""Tipos parser-internal: Paragrafo + TipoSecao."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class TipoSecao(Enum):
    """Vocabulário fechado de tipos de seção/parágrafo (D-03)."""

    TITULO = "titulo"
    AUTORES = "autores"
    RESUMO = "resumo"
    PALAVRAS_CHAVE = "palavras_chave"
    ABSTRACT = "abstract"
    KEYWORDS = "keywords"
    SUMARIO = "sumario"
    INTRODUCAO = "introducao"
    SECAO = "secao"
    CONCLUSAO = "conclusao"
    REFERENCIAS = "referencias"
    NOTA_RODAPE = "nota_rodape"
    CORPO = "corpo"
    DESCONHECIDO = "desconhecido"


@dataclass(frozen=True, slots=True)
class Paragrafo:
    """Bloco de texto identificável linha a linha (D-02).

    Offsets relativos ao source UTF-8 NFC.
    """

    arquivo: Path
    indice: int  # 0-based, ordem topológica
    tipo: TipoSecao
    nivel_heading: int | None  # 1-6 se heading; None se corpo
    texto: str  # slice raw NFC, com markup preservado
    linha_inicio: int  # 1-based
    linha_fim: int  # 1-based, inclusivo
    offset_bytes: int  # absoluto em UTF-8 NFC
    len_bytes: int  # bytes UTF-8 NFC
    ref_nota: str | None  # label da footnote ("a", "1", ...)
    paragrafo_pai_idx: int | None  # idx do parágrafo que cita [^ref_nota]
