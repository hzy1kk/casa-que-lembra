"""A Casa que Lembra — jogo de terror em texto."""

from state import state, MAX_TURNOS
from cenas import CENAS, FINAIS


def main() -> None:
    print("=" * 48)
    print("  A CASA QUE LEMBRA")
    print("  Um jogo de terror em texto")
    print("=" * 48)
    print(
        "\nVocê tem no máximo "
        f"{MAX_TURNOS} interações. Cada escolha conta.\n"
        "A casa está contando junto com você.\n"
    )

    cena = "inicio"
    while cena != "fim":
        if state["turnos"] >= MAX_TURNOS and cena not in FINAIS:
            cena = "fim_atrasado"
            continue
        if cena not in CENAS:
            print(f"Cena desconhecida: {cena}")
            break
        cena = CENAS[cena]()

    print("\nFim.\n")


if __name__ == "__main__":
    main()
