"""Utilitários de narrativa e escolha do jogador."""

from state import state, status_linha


def narrar(*paragrafos: str) -> None:
    print()
    for p in paragrafos:
        print(p)
        print()


def escolher(msg: str, opcoes: list[str]) -> str:
    """Lê uma escolha válida e conta como uma interação."""
    opcoes_norm = [o.strip().lower() for o in opcoes]
    while True:
        print(status_linha())
        try:
            r = input(msg).strip().lower()
        except EOFError:
            print("\n(Entrada encerrada.)")
            state["turnos"] += 1
            return opcoes_norm[0]
        if r in opcoes_norm:
            state["turnos"] += 1
            return r
        print("Opção inválida. Tente de novo.")
