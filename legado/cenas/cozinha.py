"""Cena da cozinha."""

from state import tem, pegar
from utils import narrar, escolher


def cozinha() -> str:
    narrar(
        "A cozinha cheira a gás antigo e laranja podre.",
        "Na pia, um prato com comida ainda quente — arroz, feijão, "
        "um pedaço de carne. O vapor sobe em espirais lentas. "
        "Ninguém mora aqui há doze anos.",
        "Na parede acima da mesa, riscos profundos formam letras "
        "tortas: CONTANDO ATÉ QUINZE.",
    )

    if tem("fosforos"):
        narrar(
            "A gaveta da esquerda está aberta e vazia. Você já "
            "pegou os fósforos.",
        )
        escolher("1) Voltar ao corredor\n> ", ["1"])
        return "corredor"

    narrar(
        "Na gaveta da esquerda, uma caixa de fósforos. A etiqueta "
        "está apagada, mas você lembra da marca — a mesma que "
        "seu pai usava para acender o fogão.",
    )

    op = escolher(
        "1) Pegar os fósforos\n"
        "2) Deixar e voltar ao corredor\n"
        "3) Tocar a comida quente\n"
        "> ",
        ["1", "2", "3"],
    )

    if op == "1":
        pegar("fosforos")
        narrar(
            "Você guarda os fósforos. A caixa é leve demais — "
            "quase vazia. Dentro, restam três palitos. Três chances.",
        )
    elif op == "3":
        narrar(
            "Você encosta o dedo no arroz. Escaldante. Quando "
            "retira a mão, a comida ainda fumega… e, por um "
            "instante, você vê uma segunda mão — a sua, mais "
            "nova — fazendo o mesmo gesto do outro lado do vapor.",
            "A visão some. O prato continua lá.",
        )
        op2 = escolher(
            "1) Pegar os fósforos agora\n"
            "2) Voltar ao corredor sem eles\n"
            "> ",
            ["1", "2"],
        )
        if op2 == "1":
            pegar("fosforos")
            narrar("Você pega os fósforos. A caixa treme na sua mão.")
        else:
            narrar("Você deixa a cozinha. O cheiro de laranja te segue.")
    else:
        narrar("Você fecha a gaveta sem pegar nada e volta.")

    return "corredor"
