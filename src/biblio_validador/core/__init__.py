"""Core domain types — Violacao, Patch, Severidade, EstadoPatch."""

from biblio_validador.core.dataclasses import Patch, Violacao
from biblio_validador.core.enums import EstadoPatch, Severidade

__all__ = ["EstadoPatch", "Patch", "Severidade", "Violacao"]
