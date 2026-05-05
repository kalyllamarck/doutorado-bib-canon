"""Dataclasses core: Violacao + Patch + helper _normalize_for_json.

CRITICAL: módulo se chama `dataclasses.py` mas importa do stdlib
`dataclasses`. SEMPRE usar `from dataclasses import dataclass, asdict`
(NUNCA `import dataclasses` bare — causaria self-import recursivo).
"""

from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, cast

from biblio_validador.core.enums import EstadoPatch, Severidade


def _normalize_for_json(obj: Any) -> Any:
    """Converte recursivamente Path/Enum/tuple em str/value/list (D-25).

    Pós-processa a saída de dataclasses.asdict() para que json.dumps()
    funcione sem encoder customizado. Recursivo: desce em dicts, listas
    e tuples para normalizar estruturas aninhadas (RESEARCH Pattern 5).
    """
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, tuple):
        return [_normalize_for_json(x) for x in obj]
    if isinstance(obj, list):
        return [_normalize_for_json(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _normalize_for_json(v) for k, v in obj.items()}
    return obj


@dataclass(frozen=True, slots=True)
class Violacao:
    """Violação de regra canônica detectada por um validador (CORE-02).

    Imutável após construção (frozen=True, D-05). Coleções são tuple
    (D-07: tuple[str, ...] em vez de list[str] — frozen só impede
    reatribuir o atributo, tuple fecha o buraco da imutabilidade).

    Convenção col half-open (D-10):
        col_inicio = primeiro caractere violador (1-based)
        col_fim    = primeiro caractere NAO violador (1-based, exclusivo)
        Slicing Python: linha[col_inicio - 1 : col_fim - 1]

    Invariante intra-linha (D-22):
        len(trecho_violador) == col_fim - col_inicio
        quando linha_inicio == linha_fim.

    Nota sobre serialização (D-26):
        - dataclasses.asdict(viol) retorna dict ESTRUTURALMENTE CORRETO
          mas com Path/Enum/tuple preservados (json.dumps falha).
        - viol.to_dict() retorna dict JSON-READY (Path->str, Enum->value,
          tuple->list) via _normalize_for_json.
    """

    arquivo: Path
    linha_inicio: int  # 1-based
    linha_fim: int  # 1-based, inclusivo
    col_inicio: int  # 1-based, half-open
    col_fim: int  # 1-based, half-open exclusivo
    trecho_violador: str  # texto exato detectado
    regra_id: str  # ex.: "cst_012", "lex_001", "coc_007"
    regra_nome: str  # nome humanizado lido do JSON-fonte
    severidade: Severidade
    sugestoes: tuple[str, ...] = ()  # D-07: tuple, não list
    principio_canonico_violado: str | None = None  # AGR-02 preenche

    def __post_init__(self) -> None:
        """Valida invariantes (D-22) com mensagem incluindo regra_id."""
        if self.linha_inicio < 1:
            raise ValueError(
                f"linha_inicio < 1 em {self.regra_id}: {self.linha_inicio}"
            )
        if self.linha_fim < self.linha_inicio:
            raise ValueError(
                f"linha_fim < linha_inicio em {self.regra_id}: "
                f"{self.linha_fim} < {self.linha_inicio}"
            )
        if self.col_inicio < 1:
            raise ValueError(
                f"col_inicio < 1 em {self.regra_id}: {self.col_inicio}"
            )
        if self.col_fim < self.col_inicio:
            raise ValueError(
                f"col_fim < col_inicio em {self.regra_id}: "
                f"{self.col_fim} < {self.col_inicio}"
            )
        if not self.regra_id.strip():
            raise ValueError("regra_id vazio")
        if (
            self.linha_inicio == self.linha_fim
            and len(self.trecho_violador) != self.col_fim - self.col_inicio
        ):
            raise ValueError(
                f"trecho_violador len {len(self.trecho_violador)} != "
                f"col_fim - col_inicio "
                f"{self.col_fim - self.col_inicio} em {self.regra_id}"
            )

    def to_dict(self) -> dict[str, Any]:
        """Serialização JSON-ready (D-25)."""
        return cast(dict[str, Any], _normalize_for_json(asdict(self)))


@dataclass(slots=True)
class Patch:
    """Patch proposto por um fixer (CORE-03 / D-17, D-18).

    NAO frozen (D-06): estado e requer_revisao_humana podem ser mutados
    pelo orchestrator (Phase 51) e pelo pos-validador LLM (Phase 48).
    Demais campos sao read-only por convencao (nao enforcado em runtime).

    Single-line (D-18): patch que abrange varias linhas e decomposto em
    multiplos Patch pelo fixer; PatchAplicador (Phase 5) ordena reverso
    por (linha, col_inicio).

    Transicoes validas de `estado` (documentadas, nao enforcadas — D-21):
        PROPOSTO -> ACEITO | REJEITADO | SUPRIMIDO
        ACEITO   -> SUPRIMIDO  (raro: aplicacao falhou byte-exact)
        terminais: REJEITADO, SUPRIMIDO

    Patch e UNHASHABLE (Pitfall 4): Python desabilita __hash__ porque
    dataclass mutavel com eq=True nao pode garantir contrato de hash
    estavel. Para deduplicar use tupla (arquivo, linha, col_inicio).
    """

    arquivo: Path
    linha: int  # 1-based, single-line
    col_inicio: int  # 1-based, half-open
    col_fim: int  # 1-based, half-open exclusivo
    texto_original: str  # bytes que serao substituidos
    texto_substituto: str  # bytes que entram no lugar
    motivo: str  # narrativa da regra-origem
    confianca: float  # 0.0..1.0, SEM default (D-17 anti-hidden-default)
    requer_revisao_humana: bool = False
    estado: EstadoPatch = EstadoPatch.PROPOSTO

    def __post_init__(self) -> None:
        """Valida invariantes (D-23)."""
        if self.linha < 1:
            raise ValueError(f"linha < 1: {self.linha}")
        if self.col_inicio < 1:
            raise ValueError(f"col_inicio < 1: {self.col_inicio}")
        if self.col_fim < self.col_inicio:
            raise ValueError(
                f"col_fim < col_inicio: {self.col_fim} < {self.col_inicio}"
            )
        if not 0.0 <= self.confianca <= 1.0:
            raise ValueError(f"confianca fora de [0,1]: {self.confianca}")
        if not self.texto_original:
            raise ValueError(
                "texto_original vazio (use [] em vez de Patch nulo)"
            )
        if not self.motivo.strip():
            raise ValueError("motivo vazio")

    def to_dict(self) -> dict[str, Any]:
        """Serialização JSON-ready (D-25)."""
        return cast(dict[str, Any], _normalize_for_json(asdict(self)))
