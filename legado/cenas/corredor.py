"""Hub central: o corredor."""

from state import state, tem, perder_vida
from utils import narrar, escolher


def corredor() -> str:
    if state["vida"] <= 0:
        return "fim_morte"

    narrar(
        "O corredor é estreito demais para uma casa. As paredes "
        "parecem ter se aproximado com os anos.",
        "Uma lâmpada amarela treme no teto. Longe, passos imitam "
        "os seus com meio segundo de atraso — clic… clic.",
        "À esquerda: a cozinha. À direita: a sala. No fundo, "
        "uma escada sobe para o sótão e desce para o porão.",
    )

    op = escolher(
        "1) Cozinha\n"
        "2) Sala\n"
        "3) Sótão\n"
        "4) Porão\n"
        "5) Chamar quem está aí\n"
        "> ",
        ["1", "2", "3", "4", "5"],
    )

    if op == "1":
        return "cozinha"
    if op == "2":
        return "sala"
    if op == "3":
        return "sotao"
    if op == "4":
        return _tentar_porao()
    return _chamar()


def _tentar_porao() -> str:
    if tem("chave_enferrujada"):
        if not state["abriu_porao"]:
            state["abriu_porao"] = True
            narrar(
                "A chave enferrujada gira com um queixume metálico. "
                "O ar que sobe do porão é úmido, doce e podre — "
                "como fruta esquecida no escuro.",
            )
        return "porao"

    narrar(
        "A porta do porão está trancada. A fechadura é antiga, "
        "coberta de ferrugem em forma de unha.",
    )
    op = escolher(
        "1) Forçar a porta\n"
        "2) Desistir e voltar\n"
        "> ",
        ["1", "2"],
    )
    if op == "1":
        state["forcou_porao"] = True
        narrar(
            "Você empurra com o ombro. A madeira geme, mas não cede. "
            "Algo do outro lado empurra de volta — no mesmo ritmo. "
            "Uma lasca corta sua palma.",
        )
        if perder_vida(1):
            return "fim_morte"
        narrar("Você recua, ofegante. O corredor espera.")
        return "corredor"

    narrar("Você se afasta. Os passos atrasados continuam, pacientes.")
    return "corredor"


def _chamar() -> str:
    narrar(
        'Você engole seco e grita: "Tem alguém aí?"',
        "O silêncio engorda. Então, do fundo do corredor, a sua "
        "própria voz responde — um pouco mais baixa, um pouco "
        "mais alegre:",
        '"Tem alguém aí?"',
        "Os passos atrasados aceleram. Algo frio roça sua nuca.",
    )
    state["conheceu_eco"] = True
    if perder_vida(1):
        return "fim_morte"
    narrar(
        "Quando você se vira, não há ninguém. Só a lâmpada "
        "tremendo mais forte.",
    )
    return "corredor"
