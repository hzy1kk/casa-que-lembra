"""Finais do jogo."""

from state import state, status_linha
from utils import narrar


def fim_fuga() -> str:
    narrar(
        "Você corre. A porta da frente cede — chave ou luz, "
        "não importa. A noite lá fora é real: vento, rua, "
        "o cheiro de asfalto molhado.",
        "Você olha para trás. A casa está quieta. Então, "
        "no seu antigo quarto, a luz acende sozinha.",
        "Alguém passa atrás da cortina com o seu jeito de andar. "
        "Meio segundo atrasado.",
        "Você escapou. Talvez.",
    )
    _resumo("FUGA AMBÍGUA")
    return "fim"


def fim_verdade() -> str:
    narrar(
        'Você segura a foto e a memória da fita. "Você não é eu. '
        'Você é o que eu deixei."',
        "O sorriso do eco trinca. Você golpeia o espelho. "
        "O vidro soluça — um som úmido, humano — e estilhaça.",
        "A casa inteira respira fundo, como quem larga um "
        "segredo. Poeira sobe. A luz amarela morre.",
        "Quando amanhece, você está no jardim. A porta está "
        "fechada. Não há passos atrasados. Só o seu coração, "
        "no tempo certo.",
    )
    _resumo("VERDADE")
    return "fim"


def fim_eco() -> str:
    narrar(
        "Você encosta a mão no vidro. O eco encosta a dele. "
        "O frio passa. O calor fica do outro lado.",
        "Você tenta recuar. Não há recuo. O porão — ou a sala, "
        "ou o quarto — agora é o lado de dentro do espelho.",
        "Do lado de fora, alguém com o seu rosto abre a porta "
        "da frente, inspira a noite e sorri no tempo certo.",
        "A casa não está mais sozinha. Você está.",
    )
    _resumo("O ECO SAI")
    return "fim"


def fim_ritual() -> str:
    narrar(
        "Você risca o fósforo. A vela acende. A chama mostra "
        "o eco como ele é: pequeno, assustado, uma criança "
        "que prometeu não deixar a casa vazia.",
        "Você diz o que o bilhete escondia — não um nome de "
        "pessoa, mas o nome da casa, o apelido que só vocês "
        "dois usavam quando era tarde demais para dormir.",
        "O eco encolhe. Vira menino de novo. A vela tremula. "
        "Você apaga com os dedos.",
        "De manhã, você tranca cada porta. No quintal, queima "
        "a fita. A fumaça sobe reta. A casa, pela primeira vez "
        "em doze anos, não responde.",
    )
    _resumo("RITUAL — FINAL SECRETO")
    return "fim"


def fim_morte() -> str:
    narrar(
        "A escuridão fecha como uma boca.",
        "Os passos atrasados — clic… clic — param.",
        "Não porque foram embora.",
        "Porque agora estão sincronizados com os seus.",
        "A casa lembra. E você, enfim, também.",
    )
    _resumo("MORTE")
    return "fim"


def fim_atrasado() -> str:
    narrar(
        "Quinze. A casa completa a contagem por você.",
        "Do corredor vem a sua voz, paciente, quase carinhosa:",
        '"Não abra a porta se ela já estiver aberta."',
        "A porta do quarto — aquela que você deixou para trás — "
        "fecha por dentro. A chave gira sozinha.",
        "O eco completa a frase do bilhete no seu ouvido:",
        '"Agora eu abro."',
        "Não há mais escolhas. Só a casa, lembrando.",
    )
    _resumo("ATRASADO DEMAIS")
    return "fim"


def _resumo(titulo: str) -> None:
    print("---")
    print(f"Final: {titulo}")
    print(status_linha())
    print("---")
