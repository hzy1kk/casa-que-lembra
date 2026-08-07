"""Cena do porão."""

from state import state, tem, pegar, perder_vida
from utils import narrar, escolher


def porao() -> str:
    narrar(
        "O porão engole o som. Umidade cola na pele. Nas paredes, "
        "marcas de unha formam o seu nome — letra por letra, "
        "profundas demais para uma brincadeira.",
    )

    if not tem("fosforos"):
        narrar(
            "Sem luz, o chão some. Você tropeça numa caixa. "
            "O joelho bate no concreto.",
        )
        if perder_vida(1):
            return "fim_morte"
        narrar(
            "Você engatinha até a escada, guiado só pelo cheiro "
            "menos podre de cima.",
        )
        op = escolher(
            "1) Subir ao corredor\n"
            "2) Tentar de novo no escuro\n"
            "> ",
            ["1", "2"],
        )
        if op == "1":
            return "corredor"
        narrar(
            "Você insiste. Dedos encontram um pano grosso sobre "
            "algo liso — vidro. Um espelho. Sem luz, você não "
            "ousa puxar o pano.",
        )
        if perder_vida(1):
            return "fim_morte"
        return "corredor"

    return _com_luz()


def _com_luz() -> str:
    narrar(
        "Você risca um fósforo. A chama mostra a inscrição "
        "completa nas paredes: o seu nome, repetido, e abaixo:",
        '"ELE FICOU."',
        "No chão, uma foto rasgada. No fundo, uma porta baixa "
        "coberta por um pano escuro — o formato de um espelho "
        "de corpo inteiro.",
    )

    while True:
        opcoes = ["1", "2", "3"]
        prompt = ""
        if not tem("foto_rasgada"):
            prompt += "1) Pegar a foto rasgada\n"
        else:
            prompt += "1) (Você já tem a foto)\n"
        prompt += (
            "2) Puxar o pano do espelho\n"
            "3) Subir ao corredor\n"
        )

        op = escolher(prompt + "> ", opcoes)

        if op == "1":
            if not tem("foto_rasgada"):
                pegar("foto_rasgada")
                state["viu_foto"] = True
                narrar(
                    "A foto mostra a casa intacta, ensolarada. "
                    "No jardim, uma criança — você — sorri. "
                    "Atrás dela, uma sombra com o mesmo sorriso, "
                    "atrasada um passo. A borda da foto está "
                    "queimada.",
                )
            else:
                narrar("Você já guarda a foto. O sorriso da sombra não muda.")
            continue

        if op == "2":
            narrar(
                "Você puxa o pano. O tecido cai como pele morta. "
                "O espelho não mostra o porão — mostra o corredor "
                "de cima, vazio… e alguém com o seu rosto "
                "já te esperando do outro lado, sorrindo.",
            )
            state["conheceu_eco"] = True
            return "espelho"

        narrar("Você sobe. O fósforo morre entre os dedos.")
        return "corredor"
