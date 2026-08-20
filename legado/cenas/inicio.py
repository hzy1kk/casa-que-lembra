"""Cena inicial: o quarto de infância."""

from state import state
from utils import narrar, escolher


def inicio() -> str:
    narrar(
        "Você acorda suando frio.",
        "O papel de parede floral está descascado nas bordas, "
        "como se alguém tivesse arrancado pétalas com as unhas. "
        "O colchão cheira a mofo e a sabão em pó antigo — o mesmo "
        "cheiro da sua infância.",
        "No espelho rachado do guarda-roupa, o reflexo pisca "
        "um segundo depois de você. Só um segundo. Mas o bastante "
        "para o estômago apertar.",
        "Na mesinha de cabeceira, um bilhete na sua letra:",
        '"Não abra a porta se ela já estiver aberta."',
        "A porta do quarto já está aberta. Além dela, o corredor "
        "respira uma luz amarela fraca.",
    )

    op = escolher(
        "1) Levantar e ir ao corredor\n"
        "2) Olhar o bilhete de novo\n"
        "> ",
        ["1", "2"],
    )

    if op == "2":
        state["leu_bilhete"] = True
        narrar(
            "Você pega o bilhete. O papel está úmido, como se "
            "tivesse acabado de ser escrito. No verso, em letra "
            "menor, trêmula:",
            '"Ela conta até quinze. Depois, a casa escolhe por você."',
            "O reflexo no espelho rachado agora está imóvel — "
            "demais. Você larga o bilhete e atravessa a porta.",
        )
    else:
        narrar(
            "Você se levanta. O piso range sob o pé esquerdo, "
            "depois — meio segundo depois — range de novo, sozinho. "
            "Você atravessa a porta aberta.",
        )

    return "corredor"
