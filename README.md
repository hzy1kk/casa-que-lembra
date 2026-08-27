# A Casa que Lembra

Terror narrativo interativo no framework **PyScript GameJam V2**.

Você acorda no quarto de infância. A casa está vazia há 12 anos. Algo com o seu rosto caminha nos corredores.

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

- **Vida**, inventário, pontuação e **turnos (máx. 15)**
- Cada clique de escolha gasta 1 turno; aos 15 a casa escolhe (`fim_atrasado`)
- Decisões condicionadas a itens (porão, quarto dos pais, verdade, ritual)
- **Save / Continuar** e **ranking** no `localStorage` do navegador
- SFX curtos (porta, passos, TV, dano) + trilhas por cena
- Até **4 opções** por cena (só botões — sem `input()`)
- Reiniciar aventura / Novo jogo

## Finais (resumo)

| Final | Como |
|-------|------|
| Fuga | No espelho, correr com chave ou fósforos |
| Verdade | Confrontar com fita + foto |
| O Eco sai | Aceitar trocar de lugar |
| Ritual (secreto) | Vela + fósforos + fita (enigma/pedra dão bônus) |
| Morte | Vida 0 ou confronto sem pistas |
| Atrasado | 15 turnos sem fechar um final |

Mapa completo: [`docs/mapa-cenas.md`](docs/mapa-cenas.md)

## Entrega escolar

1. Suba a pasta no GitHub (ou use o ZIP de entrega).
2. Conecte o repositório na Vercel (build estático; `vercel.json` já incluso).
3. Para apresentar offline: rode `python3 -m http.server 8000` ou o `.bat`.
