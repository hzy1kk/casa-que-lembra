# A Casa que Lembra

Terror narrativo interativo no framework **PyScript GameJam V2**.

Você (adulto) voltou à casa da infância, vazia há 12 anos. Quando criança, prometeu que não a deixaria sozinha — e deixou um **eco** no seu lugar. Explore a casa, junte provas e enfrente o espelho do porão. **Sem limite de turnos:** jogue até um final — ou até morrer.

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
assets/videos/      — cenas animadas e fita
docs/mapa-cenas.md — mapa de cômodos, itens e finais
legado/             — versão anterior (terminal + web 8-bit)
backups/            — backup .tar.gz do jogo funcional
```

## Mecânicas

- **3 vidas**, inventário e pontuação — **sem relógio / sem máximo de turnos**
- Erros perigosos custam vida (escuro sem fósforos, forçar porta, chamar o eco…)
- Com **0 vidas** → final de morte; senão explore até o espelho e escolha um final
- Decisões condicionadas a itens (porão, quarto dos pais, verdade, ritual)
- **Fuga** exige a **chave** (fósforos são luz / ritual, não abrem a porta)
- **Casinha** só pelo jardim ou bilhete da mãe
- **Save / Continuar** e **ranking** no `localStorage` do navegador
- SFX curtos + trilhas por cena; vídeos ambientados em cenas-chave
- Até **4 opções** por cena (só botões — sem `input()`)

## Finais (resumo)

| Final | Como | Resultado |
|-------|------|-----------|
| Fuga | Correr com a chave | Você livre; eco na casa |
| Verdade | Fita + foto | Eco some; você livre |
| Troca | Aceitar trocar | Eco vive sua vida; você preso |
| Libertação | Vela + fósforos + fita + Casinha | Eco liberto; melhor saída |
| Sem prova / fuga falhou | Sem pistas ou sem chave | Eco vence / você preso |
| Morte | Vida chega a zero | A casa fica com você |

Mapa completo: [`docs/mapa-cenas.md`](docs/mapa-cenas.md)

## Entrega escolar

1. Suba a pasta no GitHub (ou use o ZIP de entrega).
2. Conecte o repositório na Vercel (build estático; `vercel.json` já incluso).
3. Para apresentar offline: rode `python3 -m http.server 8000` ou o `.bat`.
