"""Clímax: confronto no espelho."""

from state import state, tem
from utils import narrar, escolher


def espelho() -> str:
    if state["vida"] <= 0:
        return "fim_morte"

    tem_pista = state["ouviu_fita"] or state["viu_foto"] or tem("fita_cassete") or tem("foto_rasgada")

    if not tem_pista:
        narrar(
            "O espelho te engole com a própria imagem. Sem "
            "lembrar por que veio, você só vê o sorriso atrasado. "
            "Mãos iguais às suas atravessam o vidro e puxam.",
        )
        return "fim_morte"

    narrar(
        "O doppelgänger está do outro lado do vidro, sorrindo "
        "com o seu sorriso. Ele fala primeiro — com a sua voz, "
        "meio segundo atrasada:",
        '"Eu esperei doze anos. A casa estava com saudade."',
        "O ar cheira a chuva de infância e a ferrugem.",
    )
    state["conheceu_eco"] = True

    opcoes = ["1", "2", "3"]
    prompt = (
        "1) Correr para a porta da frente\n"
        '2) Confrontar: "Você não é eu"\n'
        "3) Aceitar trocar de lugar\n"
    )
    if tem("vela") and tem("fosforos") and (
        state["ouviu_fita"] or tem("fita_cassete")
    ):
        prompt += "4) Acender a vela e dizer o nome do bilhete\n"
        opcoes.append("4")

    op = escolher(prompt + "> ", opcoes)

    if op == "1":
        if tem("chave_enferrujada") or tem("fosforos"):
            return "fim_fuga"
        narrar(
            "Você corre. Sem chave, sem luz. A porta da frente "
            "está trancada por dentro. Atrasado, o eco chega "
            "e põe a mão no seu ombro — a mesma mão.",
        )
        return "fim_morte"

    if op == "2":
        if (state["ouviu_fita"] or tem("fita_cassete")) and (
            state["viu_foto"] or tem("foto_rasgada")
        ):
            return "fim_verdade"
        narrar(
            'Você grita: "Você não é eu!" O eco ri com a sua '
            "garganta. Sem a fita e a foto, a frase não tem peso. "
            "O vidro não quebra. Você quebra.",
        )
        return "fim_morte"

    if op == "3":
        return "fim_eco"

    # ritual
    if tem("vela") and tem("fosforos") and (
        state["ouviu_fita"] or tem("fita_cassete")
    ):
        state["apagou_vela"] = True
        return "fim_ritual"

    return "fim_morte"
