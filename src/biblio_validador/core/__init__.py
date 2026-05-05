"""Pacote core — tipos, contratos e utilitarios compartilhados.

Phase 3 (Dataclasses Core): Violacao, Patch, EstadoPatch, Severidade.
Phase 4 (Contratos ABC): ValidadorBase, FixerBase, AplicacaoResultado,
ContextoFixer, Scope, ModoFixer.
"""

from biblio_validador.core.contracts import (
    AplicacaoResultado,
    ContextoFixer,
    FixerBase,
    ValidadorBase,
)
from biblio_validador.core.dataclasses import Patch, Violacao
from biblio_validador.core.enums import (
    EstadoPatch,
    ModoFixer,
    Scope,
    Severidade,
)

__all__ = [
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
]
