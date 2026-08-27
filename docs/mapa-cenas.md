# Mapa de cenas — A Casa que Lembra

## Hub e exploração

| Cena | Onde leva |
|------|-----------|
| `inicio` | Quarto — bilhete ou corredor |
| `corredor` | Cozinha, sala, escadas, **mais caminhos** |
| `corredor_mais` | Jardim ou chamar o eco |
| `escadas` | Sótão ou porão |
| `cozinha` | Fósforos |
| `sala` | Chave, TV, quarto dos pais |
| `sotao` | Fita cassete, vela |
| `porao` | Foto rasgada, espelho (precisa chave + fósforos) |
| `jardim` | Pedra do jardim (apelido **Casinha**) |
| `quarto_pais` | Bilhete dos pais + enigma (precisa chave) |
| `enigma` | Flag do ritual / bônus de pontos |
| `dialogo_eco` | Antes do confronto no espelho |
| `espelho` | Escolha do final |

## Itens

| Item | Onde | Para quê |
|------|------|----------|
| fósforos | Cozinha | Luz no sótão/porão; ajuda na fuga |
| chave enferrujada | Sala | Abre porão e quarto dos pais |
| fita cassete | Sótão | Final Verdade / Ritual |
| vela | Sótão | Ritual secreto |
| foto rasgada | Porão | Final Verdade |
| pedra do jardim | Jardim | Bônus no enigma / ritual |

## Finais

| Final | Como chegar |
|-------|-------------|
| **Fuga** | No espelho, correr com chave ou fósforos |
| **Verdade** | Confrontar com fita + foto |
| **O Eco sai** | Aceitar trocar de lugar |
| **Ritual (secreto)** | Vela + fósforos + fita (enigma/pedra dão bônus) |
| **Morte** | Vida 0, espelho sem pistas, fuga/verdade falhas |
| **Atrasado** | 15 turnos sem fechar um final |

## Enigma (ordem certa)

1. Fósforos (o que acende)  
2. Fita (memória)  
3. Casinha (apelido)

## Regras rápidas

- Cada escolha gasta **1 turno** (máx. 15).
- Consequências ruins usam cenas próprias (`porta_falha`, `eco_responde`, `enigma_falha`, etc.).
- Save e ranking ficam no navegador (`localStorage`).
