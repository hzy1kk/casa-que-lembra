"""Cena da sala."""

from state import state, tem, pegar
from utils import narrar, escolher


def sala() -> str:
    narrar(
        "A sala está coberta. O sofá usa um lençol branco manchado "
        "de amarelo. Relógios parados. Poeira em camadas.",
        "A TV de tubo olha para você com a tela morta — um olho "
        "cinza, opaco.",
    )

    if state["ouviu_fita"]:
        narrar(
            "A TV liga sozinha. Estática. No meio do ruído branco, "
            "um rosto se forma — o seu, mais novo, sorrindo sem "
            "chegar aos olhos.",
        )

    opcoes = ["1", "2", "3"]
    prompt = (
        "1) Abrir a gaveta da estante\n"
        "2) Examinar a TV\n"
        "3) Voltar ao corredor\n"
    )
    if state["ouviu_fita"] and state["viu_foto"]:
        prompt += "4) Seguir o rosto na estática (para o espelho)\n"
        opcoes.append("4")

    op = escolher(prompt + "> ", opcoes)

    if op == "1":
        return _gaveta()
    if op == "2":
        return _tv()
    if op == "4":
        narrar(
            "O rosto na estática inclina a cabeça. A tela estala. "
            "Você sente um puxão atrás dos olhos — e o mundo "
            "vira escuro úmido. Quando a visão volta, você está "
            "diante de um espelho coberto por um pano.",
        )
        return "espelho"

    narrar("Você deixa a sala. O lençol do sofá se mexe sem vento.")
    return "corredor"


def _gaveta() -> str:
    if tem("chave_enferrujada"):
        narrar("A gaveta está vazia. A chave já está com você.")
        return "sala"

    narrar(
        "A gaveta range. Dentro: uma chave enferrujada, quente "
        "ao toque, como se alguém a tivesse segurado agora há pouco. "
        "Na alça, um pedaço de fita isolante com a palavra PORÃO.",
    )
    pegar("chave_enferrujada")
    narrar("Você guarda a chave. Ela esfria na sua mão aos poucos.")
    return "sala"


def _tv() -> str:
    state["viu_tv"] = True
    if state["ouviu_fita"]:
        narrar(
            "Você se aproxima da tela. O rosto de criança abre "
            "a boca. Não sai som — sai um sopro frio pela fresta "
            "do painel. A estática sussurra:",
            '"Você deixou alguém no seu lugar."',
            "A coragem sobe na garganta como náusea. Agora você "
            "sabe: precisa ver o espelho de verdade.",
        )
    else:
        narrar(
            "Você liga a TV. Só estática. No chiado, quase dá "
            "para ouvir alguém contar: um… dois… três… "
            "Você desliga antes de chegar a quinze.",
        )
    return "sala"
