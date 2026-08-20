"""Cena do sótão."""

from state import state, tem, pegar, perder_vida
from utils import narrar, escolher


def sotao() -> str:
    narrar(
        "A escada range a cada degrau. O sótão cheira a poeira "
        "quente e a madeira velha. Caixas empilhadas. Um posto "
        "de brinquedos cobertos por lençol.",
    )

    if not tem("fosforos"):
        return _sem_luz()
    return _com_luz()


def _sem_luz() -> str:
    narrar(
        "Está escuro demais. Suas mãos encontram arestas, "
        "teias, algo macio que pode ser um casaco… ou não.",
    )
    op = escolher(
        "1) Insistir no escuro\n"
        "2) Descer ao corredor\n"
        "> ",
        ["1", "2"],
    )
    if op == "2":
        narrar("Você desce. A escuridão do sótão parece aliviada.")
        return "corredor"

    narrar(
        "Você avança. O pé encontra o vazio entre duas tábuas. "
        "Você cai de joelho. Algo — uma unha? um fio? — "
        "raspa seu tornozelo.",
    )
    if perder_vida(1):
        return "fim_morte"
    narrar(
        "Você engatinha de volta à escada, o coração batendo "
        "atrasado, como os passos do corredor.",
    )
    return "corredor"


def _com_luz() -> str:
    narrar(
        "Você risca um fósforo. A chama treme e revela o sótão "
        "em pedaços laranja: caixas, um gravador de fita cassete, "
        "uma vela branca sem usar.",
    )

    while True:
        opcoes = ["1", "2", "3"]
        prompt = "1) Examinar o gravador / a fita\n"
        if not tem("vela"):
            prompt += "2) Pegar a vela\n"
        else:
            prompt += "2) (Você já tem a vela)\n"
        prompt += "3) Descer ao corredor\n"
        if state["ouviu_fita"] and (state["viu_foto"] or state["viu_tv"]):
            prompt += "4) Seguir o eco da fita (para o espelho)\n"
            opcoes.append("4")

        op = escolher(prompt + "> ", opcoes)

        if op == "1":
            _fita()
            continue
        if op == "2":
            if not tem("vela"):
                pegar("vela")
                narrar(
                    "Você guarda a vela. A cera está fria, mas "
                    "o pavio cheira a fumaça recente — "
                    "como se alguém tivesse apagado agora.",
                )
            else:
                narrar("A vela já está com você.")
            continue
        if op == "4":
            narrar(
                "A voz da criança na fita parece vir de baixo. "
                "Você segue o som escada abaixo, atravessa o "
                "corredor sem olhar, e desce ao porão — "
                "até um espelho coberto por pano.",
            )
            return "espelho"

        narrar("Você desce. O fósforo se apaga no último degrau.")
        return "corredor"


def _fita() -> None:
    if not tem("fita_cassete"):
        pegar("fita_cassete")
        narrar(
            "Você puxa a fita do gravador. A etiqueta, na sua "
            "letra de criança: EU / OUTRO.",
        )

    narrar(
        "Você aperta play. Chiado. Então uma voz de criança — "
        "a sua — sussurra perto demais do microfone:",
        '"Quando eu crescer, vou deixar alguém no meu lugar."',
        "Pausa. Respiração. Depois, mais baixo:",
        '"Pra casa não ficar sozinha."',
        "A fita termina. O gravador continua quente.",
    )
    state["ouviu_fita"] = True
