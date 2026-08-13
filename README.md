# A Casa que Lembra

Jogo de terror em texto. Você acorda no quarto de infância — a casa está vazia há 12 anos. Algo com o seu rosto caminha nos corredores.

## Versão 8-bit dark (navegador)

Interface cinematográfica dark (sangue, cinza, ferrugem), texto datilografado, som procedural e uma arte por fase/escolha.

**Online:** (após deploy Vercel) · **Repo:** https://github.com/hzy1kk/casa-que-lembra

```bash
cd web
python3 -m http.server 8080
```

Abra http://localhost:8080

Arquivos: [`web/index.html`](web/index.html) · [`web/styles.css`](web/styles.css) · [`web/game.js`](web/game.js) · [`web/art/`](web/art/)

Cada **fase** tem ilustração própria. Cada **escolha** mostra miniatura (hover troca a arte). O texto entra letra a letra (clique ou espaço adianta). Há drone, passos atrasados e batimento quando a vida cai.

Botão **som / mudo** no canto.

### Deploy Vercel

O site estático sai da pasta `web/` (`vercel.json`). Importar o repo no [Vercel](https://vercel.com/new) ou:

```bash
npx vercel --prod
```

## Terminal (Python)

```bash
python3 main.py
```

### Google Colab

Abra o notebook [`casa_que_lembra_colab.ipynb`](casa_que_lembra_colab.ipynb) no [Colab](https://colab.research.google.com/) (Arquivo → Fazer upload do notebook). Rode a célula do código e depois `jogar()`.

Cada escolha gasta **1 interação** (máximo **15**). Se o tempo acabar, a casa escolhe por você.

## Objetivo

Explorar a casa, reunir pistas e itens, e enfrentar o eco no espelho. Há vários finais — fuga, verdade, troca, ritual secreto, morte e atraso.

## Itens

| Item | Onde | Para quê |
|------|------|----------|
| Fósforos | Cozinha | Luz no sótão/porão; ajuda na fuga |
| Chave enferrujada | Sala | Abre o porão |
| Fita cassete | Sótão | Pista para o final da verdade / ritual |
| Vela | Sótão (com fósforos) | Ritual secreto no espelho |
| Foto rasgada | Porão (com luz) | Pista para o final da verdade |

## Estrutura

```
main.py / cenas/   — versão terminal
web/               — versão 8-bit dark no navegador
casa_que_lembra_colab.ipynb
```
