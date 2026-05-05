"""Sub-pacote parser — segmentação de .md/.tex em list[Paragrafo]."""

from biblio_validador.parser.markdown import ParserMd
from biblio_validador.parser.types import Paragrafo, TipoSecao

__all__ = ["ParserMd", "Paragrafo", "TipoSecao"]
