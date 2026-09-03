# A Casa que Lembra

Terror narrativo interativo no framework **PyScript GameJam V2**.

Você voltou à casa da infância, vazia há 12 anos. Quando criança, prometeu que não a deixaria sozinha — e deixou um **eco** no seu lugar. A casa conta até 15. Junte provas e enfrente o espelho do porão.

**Autor:** lucas lohan

## Jogar online

Após o deploy Vercel: [casa-que-lembra.vercel.app](https://casa-que-lembra.vercel.app)

## Executar localmente

```bash
python3 -m http.server 8000
```

Abra http://localhost:8000

No Windows, também pode usar `INICIAR_JOGO.bat`.

Não abra `index.html` por `file://` — use o servidor HTTP (o PyScript precisa disso).

## Estrutura

```
index.html          — interface PyScript (responsiva, botões)
main.py             — CONFIG, STATE, SCENES, regras (executar_acao)
assets/imagens/     — capa e artes das cenas
assets/audios/      — trilhas + SFX
assets/videos/      — introdução e fita
docs/mapa-cenas.md — mapa de cômodos, itens e finais
legado/             — versão anterior (terminal + web 8-bit)
backups/            — backup .tar.gz do jogo funcional
```

## Mecânicas

- **Vida**, inventário, pontuação e **turnos (máx. 15 explorando)**
- Cada clique de escolha gasta 1 turno; aos 15 fora do espelho a casa escolhe (`fim_atrasado`)
- No confronto do espelho você ainda pode fechar um final
- Decisões condicionadas a itens (porão, quarto dos pais, verdade, ritual)
- **Save / Continuar** e **ranking** no `localStorage` do navegador
- SFX curtos (porta, passos, TV, dano) + trilhas por cena
- Até **4 opções** por cena (só botões — sem `input()`)
- Reiniciar aventura / Novo jogo

## Finais (resumo)

| Final | Como |
|-------|------|
| Fuga | Correr com chave ou fósforos — o eco fica |
| Verdade | Fita + foto: você nomeia o eco |
| Troca | Aceitar trocar de lugar |
| Libertação | Vela + fósforos + fita + apelido Casinha |
| Sem prova / falhas | Espelho sem pistas, fuga ou verdade incompletas |
| Quinze | 15 turnos sem fechar um final |

Mapa completo: [`docs/mapa-cenas.md`](docs/mapa-cenas.md)

## Entrega escolar

1. Suba a pasta no GitHub (ou use o ZIP de entrega).
2. Conecte o repositório na Vercel (build estático; `vercel.json` já incluso).
3. Para apresentar offline: rode `python3 -m http.server 8000` ou o `.bat`.
