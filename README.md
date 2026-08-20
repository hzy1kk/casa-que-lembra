# A Casa que Lembra

Terror narrativo interativo no framework **PyScript GameJam V2**.

Você acorda no quarto de infância. A casa está vazia há 12 anos. Algo com o seu rosto caminha nos corredores.

## Jogar online

Após o deploy Vercel: [casa-que-lembra.vercel.app](https://casa-que-lembra.vercel.app)

## Executar localmente

```bash
python3 -m http.server 8000
```

Abra http://localhost:8000

No Windows, também pode usar `INICIAR_JOGO.bat`.

Não abra `index.html` por `file://` — use o servidor HTTP.

## Estrutura

```
index.html          — interface PyScript (responsiva)
main.py             — CONFIG, STATE, SCENES, regras
assets/imagens/     — capas e cenas
assets/audios/      — trilhas
assets/videos/      — introdução e fita
legado/             — versão anterior (terminal + web 8-bit)
backups/            — backup .tar.gz do jogo funcional
```

## Mecânicas

- Vida, inventário e pontuação
- Decisões condicionadas a itens (porão, verdade, ritual)
- Múltiplos finais + final secreto (ritual com vela + fósforos + fita)
- Troca de trilha no espelho / amanhecer
- Vídeos na introdução e na fita
- Até 4 opções por cena (botões)
- Reiniciar aventura

## Autor

lucas lohan
