"""Estado global do jogo: vida, inventário, turnos e flags."""

MAX_TURNOS = 15

state = {
    "vida": 3,
    "inv": [],
    "turnos": 0,
    "ouviu_fita": False,
    "viu_foto": False,
    "abriu_porao": False,
    "apagou_vela": False,
    "conheceu_eco": False,
    "leu_bilhete": False,
    "viu_tv": False,
    "forcou_porao": False,
}


def pegar(item: str) -> None:
    if item not in state["inv"]:
        state["inv"].append(item)


def tem(item: str) -> bool:
    return item in state["inv"]


def perder_vida(n: int = 1) -> bool:
    """Reduz vida. Retorna True se a vida chegou a zero ou menos."""
    state["vida"] -= n
    return state["vida"] <= 0


def status_linha() -> str:
    itens = ", ".join(state["inv"]) if state["inv"] else "nada"
    return (
        f"[vida: {state['vida']} | turnos: {state['turnos']}/{MAX_TURNOS} "
        f"| inventário: {itens}]"
    )
