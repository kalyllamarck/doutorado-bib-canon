"""Enums core: Severidade + EstadoPatch (D-14, D-20)."""

from enum import Enum


class Severidade(Enum):
    """Classificação de severidade de uma Violacao (D-15).

    Ordem de prioridade (peso() crescente):
        INFO < ALERTA < ERRO < CRITICO

    Não usa IntEnum (D-16): IntEnum mistura semântica de ranking com
    representação textual em logs. peso() separa as preocupações.
    Não usa StrEnum (D-14): perde marcador de tipo no repr; quebra a
    convenção herdada de TipoSecao (Phase 2 D-03).
    """

    INFO = "info"
    ALERTA = "alerta"
    ERRO = "erro"
    CRITICO = "critico"

    def peso(self) -> int:
        """Peso para ordenação determinística (0..3, monotônico crescente)."""
        return _PESOS_SEVERIDADE[self]


# Tabela de pesos como módulo-level dict — evita lookup em loop e
# mantém a ordenação canônica em local único (RESEARCH Pattern 3).
_PESOS_SEVERIDADE: dict[Severidade, int] = {
    Severidade.INFO: 0,
    Severidade.ALERTA: 1,
    Severidade.ERRO: 2,
    Severidade.CRITICO: 3,
}


class EstadoPatch(Enum):
    """Ciclo de vida de um Patch (D-20).

    Transições válidas (documentadas, não enforçadas em runtime nesta
    phase — enforcement adiado para Phase 51 ORC-02 se necessário):

        PROPOSTO -> ACEITO | REJEITADO | SUPRIMIDO
        ACEITO   -> SUPRIMIDO  (raro: aplicação falhou byte-exact)
        terminais: REJEITADO, SUPRIMIDO
    """

    PROPOSTO = "proposto"
    ACEITO = "aceito"
    REJEITADO = "rejeitado"
    SUPRIMIDO = "suprimido"
