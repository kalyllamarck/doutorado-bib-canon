"""CLI entry point — esqueleto Phase 1.

Comandos reais (`validar`, `corrigir`, `auditar`) virão em phases futuras
(M1 piloto Phase 8 + M8 orchestrator Phase 52).
"""

import typer

app = typer.Typer(
    help="Validador acadêmico — biblioteca canônica PPGD/Unifor",
)


@app.callback()
def main() -> None:
    """Comandos virão em phases futuras (validar, corrigir, auditar)."""
    pass
