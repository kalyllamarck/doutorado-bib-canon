"""ABCs ValidadorBase + FixerBase + dataclasses auxiliares (CORE-04, CORE-05).

Este modulo define os contratos que validadores (M2-M4) e fixers (M5-M7)
implementam. ABCs forcam TypeError em instanciacao quando metodos abstratos
nao sao implementados (RESEARCH Pattern 8).

Convencoes locked (CONTEXT.md):
    D-05 abc.ABC + @abstractmethod (NAO Protocol)
    D-08 typing.ClassVar em todos atributos de classe
    D-19 cache class-level via cls.__dict__.get (RESEARCH Pitfall 2)
    D-21 carregar_regras e abstract; helper _carregar_json_simples cobre 90%
    D-26 ContextoFixer com eq=False (RESEARCH Pitfall 4)
    D-28 from __future__ import annotations
"""

from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod  # noqa: F401  (used in T-04-02-03)
from collections.abc import Mapping
from dataclasses import dataclass  # noqa: F401  (used in T-04-02-04)
from pathlib import Path
from typing import Any, ClassVar  # noqa: F401  (ClassVar used in T-04-02-03)

from biblio_validador.core.dataclasses import (  # noqa: F401  (T-04-02-03/04)
    Patch,
    Violacao,
)
from biblio_validador.core.enums import (  # noqa: F401  (T-04-02-03/04)
    ModoFixer,
    Scope,
)
from biblio_validador.parser.types import Paragrafo  # noqa: F401  (T-04-02-03)


def _canonical_root() -> Path:
    """Resolve a raiz da biblioteca canonica (D-09).

    Sobe N niveis a partir deste arquivo ate encontrar o diretorio
    biblioteca_canonica/. Subclasses concretas (M2+) usam:

        JSON_SOURCE = (
            _canonical_root()
            / "02_escrita/termos_proibidos"
            / "04_construcoes_sintaticas_proibidas.json"
        )

    Layout: src/biblio_validador/core/contracts.py
            parents[0] = core/
            parents[1] = biblio_validador/
            parents[2] = src/
            parents[3] = biblioteca_canonica/  <- target
    """
    return Path(__file__).resolve().parents[3]


def _carregar_json_simples(
    json_source: Path,
) -> Mapping[str, re.Pattern[str]]:
    """Carrega JSON-fonte e compila regex 1x (D-21, D-22).

    Schema heterogeneo (RESEARCH Pattern 5):
        - regex_deteccao: str               -> compila como unico padrao
        - regex_deteccao: list[str]         -> compila alternativas via "|"
        - regex_deteccao_aproximada: str    -> chave alternativa (cst_011)

    Erros propagam (D-22):
        - FileNotFoundError: JSON_SOURCE invalido
        - json.JSONDecodeError: JSON malformado
        - re.error: regex invalido (mensagem inclui regra_id)

    Sem flag IGNORECASE (RESEARCH §6: 23/23 regex existentes funcionam sem ela).

    Returns:
        Mapping[regra_id -> compiled re.Pattern]
    """
    data: Any = json.loads(json_source.read_text(encoding="utf-8"))
    compiladas: dict[str, re.Pattern[str]] = {}
    for entrada in data["entradas"]:
        rid = entrada["id"]
        # Normalizar schema heterogeneo em list[str] de forma uniforme.
        # Aceita regex_deteccao OR regex_deteccao_aproximada; cada um pode
        # ser str ou list[str] (cst_011 usa key alternativa com list).
        raw = entrada.get("regex_deteccao") or entrada.get(
            "regex_deteccao_aproximada"
        )
        if raw is None:
            # Entrada sem regex (ex.: cst_005 com so exemplos_proibidos).
            # M2 decide se ignora ou erra — Phase 4 helper apenas pula.
            continue
        padroes = [raw] if isinstance(raw, str) else list(raw)
        # Compilar: 1 padrao -> direto; N padroes -> alternativa com (?:...)
        # para evitar bugs de precedencia da alternacao em padroes do JSON.
        try:
            if len(padroes) == 1:
                compiladas[rid] = re.compile(padroes[0])
            else:
                compiladas[rid] = re.compile(
                    "|".join(f"(?:{p})" for p in padroes)
                )
        except re.error as e:  # noqa: PERF203
            raise re.error(f"regra {rid}: {e}") from e
    return compiladas
