"""Registro de todas as cenas do jogo."""

from cenas.inicio import inicio
from cenas.corredor import corredor
from cenas.cozinha import cozinha
from cenas.sala import sala
from cenas.sotao import sotao
from cenas.porao import porao
from cenas.espelho import espelho
from cenas.finais import (
    fim_fuga,
    fim_verdade,
    fim_eco,
    fim_ritual,
    fim_morte,
    fim_atrasado,
)

CENAS = {
    "inicio": inicio,
    "corredor": corredor,
    "cozinha": cozinha,
    "sala": sala,
    "sotao": sotao,
    "porao": porao,
    "espelho": espelho,
    "fim_fuga": fim_fuga,
    "fim_verdade": fim_verdade,
    "fim_eco": fim_eco,
    "fim_ritual": fim_ritual,
    "fim_morte": fim_morte,
    "fim_atrasado": fim_atrasado,
}

FINAIS = {
    "fim_fuga",
    "fim_verdade",
    "fim_eco",
    "fim_ritual",
    "fim_morte",
    "fim_atrasado",
}
