"""
A Casa que Lembra — PyScript GameJam V2
Terror narrativo interativo (botões, sem input/terminal).

Estrutura didática (escola / GameJam):
  CONFIG  → dados fixos do jogo (título, vida, capa, trilha)
  state   → o que muda durante a partida (vida, itens, turnos, flags)
  SCENES  → cada tela: texto, imagem, até 4 opções (texto, nome_da_acao)
  executar_acao() → regras: o que acontece quando o jogador clica
"""

from pyscript import document, window
import json

try:
    from pyodide.ffi import create_proxy
except ImportError:
    def create_proxy(fn):
        return fn

# ---------------------------------------------------------------------------
# CONFIG — constantes do jogo (não mudam durante a partida)
# ---------------------------------------------------------------------------

CONFIG = {
    "titulo": "A Casa que Lembra",
    "subtitulo": "Algo com o seu rosto caminha nos corredores",
    "autor": "lucas lohan",
    "icone": "⌂",
    "capa": "assets/imagens/capa.jpg",
    "trilha_inicial": "assets/audios/trilha_casa.mp3",
    "volume_inicial": 0.45,
    "vida_inicial": 3,
    "pontos_iniciais": 0,
    "cena_inicial": "inicio",
    "max_turnos": 15,
}

SAVE_KEY = "casa_que_lembra_save"
RANK_KEY = "casa_que_lembra_ranking"

SFX = {
    "click": "assets/audios/sfx_click.mp3",
    "porta": "assets/audios/sfx_porta.mp3",
    "passos": "assets/audios/sfx_passos.mp3",
    "tv": "assets/audios/sfx_tv.mp3",
    "dano": "assets/audios/sfx_dano.mp3",
}

# Finais conhecidos (para ranking e para não forçar “atrasado”)
FINAIS = {
    "fim_fuga",
    "fim_verdade",
    "fim_eco",
    "fim_ritual",
    "fim_ruim",
    "fim_atrasado",
}

# ---------------------------------------------------------------------------
# STATE — inventário, vida, turnos e flags da história
# ---------------------------------------------------------------------------

state = {}


def _estado_inicial():
    """Cria um estado novo de partida (usado em Novo jogo / Reiniciar)."""
    return {
        "vida": CONFIG["vida_inicial"],
        "pontos": CONFIG["pontos_iniciais"],
        "inventario": [],
        "turnos": 0,
        "cena_atual": None,
        "flags": {
            "ouviu_fita": False,
            "viu_foto": False,
            "viu_tv": False,
            "leu_bilhete": False,
            "abriu_porao": False,
            "conheceu_eco": False,
            "resolveu_enigma": False,
            "falou_eco": False,
            "achou_pedra": False,
            "leu_pais": False,
        },
    }


state = _estado_inicial()
_js_proxies = []


# ---------------------------------------------------------------------------
# HELPERS DO FRAMEWORK (HUD, itens, áudio, save, ranking)
# ---------------------------------------------------------------------------

def atualizar_status():
    """Atualiza vida, pontos, turnos e inventário na barra de status."""
    document.querySelector("#stat-vida").innerText = str(state["vida"])
    document.querySelector("#stat-pontos").innerText = str(state["pontos"])
    max_t = CONFIG["max_turnos"]
    document.querySelector("#stat-turnos").innerText = f"{state['turnos']}/{max_t}"
    inv = state["inventario"]
    document.querySelector("#stat-inv").innerText = ", ".join(inv) if inv else "nada"


def adicionar_item(item, pontos=0):
    if item not in state["inventario"]:
        state["inventario"].append(item)
    if pontos:
        ganhar_pontos(pontos)
    atualizar_status()


def possui_item(item):
    return item in state["inventario"]


def remover_item(item):
    if item in state["inventario"]:
        state["inventario"].remove(item)
    atualizar_status()


def ganhar_pontos(n):
    state["pontos"] += n
    atualizar_status()


def tocar_sfx(chave_ou_caminho):
    """Toca efeito sonoro curto via JavaScript (não corta a trilha)."""
    src = SFX.get(chave_ou_caminho, chave_ou_caminho)
    try:
        window.tocarSfx(src)
    except Exception:
        pass


def perder_vida(n=1):
    tocar_sfx("dano")
    state["vida"] -= n
    if state["vida"] < 0:
        state["vida"] = 0
    atualizar_status()
    if state["vida"] <= 0:
        mostrar_cena("fim_ruim")
        _ao_chegar_final("fim_ruim")
        return True
    return False


def trocar_audio(caminho):
    player = document.querySelector("#audio-player")
    if not caminho:
        return
    if player.getAttribute("src") == caminho and not player.paused:
        return
    player.src = caminho
    player.volume = CONFIG.get("volume_inicial", 0.5)
    try:
        player.play()
    except Exception:
        pass


def parar_audio():
    player = document.querySelector("#audio-player")
    try:
        player.pause()
        player.currentTime = 0
    except Exception:
        pass
    player.removeAttribute("src")


def _esconder_opcoes():
    for i in range(4):
        btn = document.querySelector(f"#opt-{i}")
        btn.classList.add("hidden")
        btn.innerText = ""
        btn.setAttribute("data-acao", "")


def _eh_final(nome):
    return nome in FINAIS or (nome and nome.startswith("fim_"))


def salvar_jogo():
    """Grava a partida atual no localStorage do navegador."""
    if _eh_final(state.get("cena_atual")):
        apagar_save()
        return
    payload = {
        "vida": state["vida"],
        "pontos": state["pontos"],
        "inventario": list(state["inventario"]),
        "turnos": state["turnos"],
        "cena_atual": state["cena_atual"],
        "flags": dict(state["flags"]),
    }
    try:
        window.localStorage.setItem(SAVE_KEY, json.dumps(payload))
    except Exception:
        pass
    _atualizar_botao_continuar()


def apagar_save():
    try:
        window.localStorage.removeItem(SAVE_KEY)
    except Exception:
        pass
    _atualizar_botao_continuar()


def carregar_save_dict():
    try:
        raw = window.localStorage.getItem(SAVE_KEY)
        if not raw:
            return None
        return json.loads(str(raw))
    except Exception:
        return None


def _atualizar_botao_continuar():
    btn = document.querySelector("#btn-continuar")
    if not btn:
        return
    if carregar_save_dict():
        btn.classList.remove("hidden")
    else:
        btn.classList.add("hidden")


def registrar_ranking(final_id):
    """Guarda top 5 pontuações (pontos + nome do final) no localStorage."""
    nomes = {
        "fim_fuga": "Fuga",
        "fim_verdade": "Verdade",
        "fim_eco": "O Eco sai",
        "fim_ritual": "Ritual secreto",
        "fim_ruim": "Morte",
        "fim_atrasado": "Atrasado",
    }
    entrada = {
        "pontos": state["pontos"],
        "final": nomes.get(final_id, final_id),
        "turnos": state["turnos"],
    }
    lista = []
    try:
        raw = window.localStorage.getItem(RANK_KEY)
        if raw:
            lista = json.loads(str(raw))
    except Exception:
        lista = []
    lista.append(entrada)
    lista.sort(key=lambda x: x.get("pontos", 0), reverse=True)
    lista = lista[:5]
    try:
        window.localStorage.setItem(RANK_KEY, json.dumps(lista))
    except Exception:
        pass
    atualizar_ranking_ui()


def atualizar_ranking_ui():
    ol = document.querySelector("#ranking-lista")
    if not ol:
        return
    ol.innerHTML = ""
    lista = []
    try:
        raw = window.localStorage.getItem(RANK_KEY)
        if raw:
            lista = json.loads(str(raw))
    except Exception:
        lista = []
    if not lista:
        li = document.createElement("li")
        li.innerText = "Nenhuma partida ainda"
        ol.appendChild(li)
        return
    for item in lista:
        li = document.createElement("li")
        li.innerText = f"{item.get('pontos', 0)} pts — {item.get('final', '?')} ({item.get('turnos', '?')} turnos)"
        ol.appendChild(li)


def _ao_chegar_final(nome):
    """Chamado quando a partida termina: ranking + apaga save."""
    apagar_save()
    registrar_ranking(nome)


def mostrar_cena(nome):
    """Mostra título, texto, mídia e até 4 botões da cena pedida."""
    if nome not in SCENES:
        window.console.error(f"Cena desconhecida: {nome}")
        return

    cena = SCENES[nome]
    state["cena_atual"] = nome
    atualizar_status()

    document.querySelector("#cena-titulo").innerText = cena.get("title", "")
    document.querySelector("#cena-texto").innerText = cena.get("text", "")

    # Fade + troca de mídia via helper JS (evita proxies temporários no setTimeout)
    try:
        payload = {
            "video": cena.get("video") or "",
            "video_autoplay": bool(cena.get("video_autoplay")),
            "image": cena.get("image") or CONFIG.get("capa") or "",
        }
        window.aplicarMidiaCena(payload)
    except Exception:
        img = document.querySelector("#cena-imagem")
        vid = document.querySelector("#cena-video")
        if cena.get("video"):
            img.classList.add("hidden")
            vid.classList.remove("hidden")
            vid.src = cena["video"]
        else:
            vid.classList.add("hidden")
            vid.removeAttribute("src")
            img.classList.remove("hidden")
            img.src = cena.get("image") or CONFIG.get("capa") or ""

    if cena.get("sfx"):
        tocar_sfx(cena["sfx"])

    if cena.get("stop_audio"):
        parar_audio()
    elif cena.get("audio"):
        trocar_audio(cena["audio"])

    _esconder_opcoes()
    opcoes = cena.get("options") or []
    for i, (texto, acao) in enumerate(opcoes[:4]):
        btn = document.querySelector(f"#opt-{i}")
        btn.innerText = texto
        btn.setAttribute("data-acao", acao)
        btn.classList.remove("hidden")

    if _eh_final(nome):
        # Evita salvar finais; ranking já registrado em _ao_chegar_final quando aplicável
        pass
    else:
        salvar_jogo()


def reiniciar_aventura(event=None):
    """Zera o estado e começa do quarto (Novo jogo / Reiniciar)."""
    global state
    state = _estado_inicial()
    apagar_save()
    atualizar_status()
    if CONFIG.get("trilha_inicial"):
        trocar_audio(CONFIG["trilha_inicial"])
    mostrar_cena(CONFIG["cena_inicial"])


def iniciar_jogo(event=None):
    """Esconde a tela de boot e inicia partida nova."""
    document.querySelector("#boot").classList.add("hidden")
    document.querySelector("#app").classList.add("visible")
    reiniciar_aventura()


def continuar_jogo(event=None):
    """Carrega save do localStorage e retoma a cena salva."""
    global state
    data = carregar_save_dict()
    if not data:
        iniciar_jogo()
        return
    state = _estado_inicial()
    state["vida"] = data.get("vida", CONFIG["vida_inicial"])
    state["pontos"] = data.get("pontos", 0)
    state["inventario"] = list(data.get("inventario") or [])
    state["turnos"] = data.get("turnos", 0)
    flags = data.get("flags") or {}
    for k in state["flags"]:
        if k in flags:
            state["flags"][k] = bool(flags[k])
    cena = data.get("cena_atual") or CONFIG["cena_inicial"]
    document.querySelector("#boot").classList.add("hidden")
    document.querySelector("#app").classList.add("visible")
    atualizar_status()
    if CONFIG.get("trilha_inicial"):
        trocar_audio(CONFIG["trilha_inicial"])
    if cena in SCENES:
        mostrar_cena(cena)
    else:
        mostrar_cena(CONFIG["cena_inicial"])


def _finalizar(nome_cena, pontos_extra=0):
    """Mostra um final, soma pontos opcionais e registra ranking."""
    if pontos_extra:
        ganhar_pontos(pontos_extra)
    mostrar_cena(nome_cena)
    _ao_chegar_final(nome_cena)


# ---------------------------------------------------------------------------
# SCENES — cada chave é uma tela do jogo
# options: lista de (texto_do_botão, nome_da_ação) — máximo 4
# ---------------------------------------------------------------------------

SCENES = {
    "inicio": {
        "title": "O quarto",
        "image": "assets/imagens/inicio.jpg",
        "video": "assets/videos/introducao.mp4",
        "video_autoplay": False,
        "text": (
            "Você acorda suando frio.\n\n"
            "O papel de parede floral está descascado nas bordas. "
            "O colchão cheira a mofo e a sabão em pó antigo — o cheiro da infância.\n\n"
            "No espelho rachado do guarda-roupa, o reflexo pisca um segundo depois de você.\n\n"
            "Na mesinha, um bilhete na sua letra:\n"
            "\"Não abra a porta se ela já estiver aberta.\"\n\n"
            "A porta do quarto já está aberta."
        ),
        "options": [
            ("Levantar e ir ao corredor", "ir_corredor"),
            ("Olhar o bilhete de novo", "ler_bilhete"),
        ],
    },
    "bilhete": {
        "title": "O verso do bilhete",
        "image": "assets/imagens/inicio.jpg",
        "text": (
            "O papel está úmido, como se tivesse acabado de ser escrito.\n\n"
            "No verso, em letra menor, trêmula:\n"
            "\"Ela conta até quinze. Depois, a casa escolhe por você.\"\n\n"
            "O reflexo no espelho rachado agora está imóvel — demais.\n\n"
            "Você larga o bilhete e atravessa a porta."
        ),
        "options": [
            ("Seguir para o corredor", "corredor"),
        ],
    },
    "corredor": {
        "title": "O corredor",
        "image": "assets/imagens/corredor.jpg",
        "sfx": "passos",
        "text": (
            "O corredor é estreito demais para uma casa. "
            "As paredes parecem ter se aproximado com os anos.\n\n"
            "Uma lâmpada amarela treme no teto. Longe, passos imitam os seus "
            "com meio segundo de atraso — clic… clic.\n\n"
            "À esquerda: a cozinha. À direita: a sala.\n"
            "No fundo, escadas. A porta dos fundos leva ao jardim."
        ),
        "options": [
            ("Ir à cozinha", "cozinha"),
            ("Ir à sala", "sala"),
            ("Usar as escadas", "escadas"),
            ("Mais caminhos…", "corredor_mais"),
        ],
    },
    "corredor_mais": {
        "title": "Outros caminhos",
        "image": "assets/imagens/corredor.jpg",
        "text": (
            "A porta dos fundos range com o vento.\n"
            "No escuro do corredor, alguém espera ser chamado pelo nome."
        ),
        "options": [
            ("Ir ao jardim", "jardim"),
            ("Chamar quem está aí", "chamar_eco"),
            ("Voltar", "corredor"),
        ],
    },
    "escadas": {
        "title": "As escadas",
        "image": "assets/imagens/corredor.jpg",
        "sfx": "passos",
        "text": (
            "A escada sobe para o sótão empoeirado.\n"
            "A escada desce para a porta enferrujada do porão.\n\n"
            "Os passos atrasados esperam a sua escolha."
        ),
        "options": [
            ("Subir ao sótão", "sotao"),
            ("Descer ao porão", "tentar_porao"),
            ("Voltar ao corredor", "corredor"),
        ],
    },
    "eco_responde": {
        "title": "Sua voz responde",
        "image": "assets/imagens/eco_responde.jpg",
        "text": (
            "Você engole seco e grita: \"Tem alguém aí?\"\n\n"
            "O silêncio engorda. Então, do fundo do corredor, "
            "a sua própria voz responde — um pouco mais baixa, um pouco mais alegre:\n\n"
            "\"Tem alguém aí?\"\n\n"
            "Os passos atrasados aceleram. Algo frio roça sua nuca.\n\n"
            "Você perdeu uma vida."
        ),
        "options": [
            ("Voltar ao corredor", "corredor"),
        ],
    },
    "jardim": {
        "title": "O jardim",
        "image": "assets/imagens/jardim.jpg",
        "sfx": "passos",
        "text": (
            "O quintal está morto, mas a terra ainda cheira a chuva de infância.\n\n"
            "Sob a roseira seca, uma pedra lisa com um apelido riscato a unha:\n"
            "\"CASINHA\".\n\n"
            "É o nome que você dava à casa quando tinha medo de dormir sozinho."
        ),
        "options": [
            ("Pegar a pedra do jardim", "pegar_pedra"),
            ("Voltar ao corredor", "corredor"),
        ],
    },
    "item_pedra": {
        "title": "Pedra do jardim",
        "image": "assets/imagens/jardim.jpg",
        "text": (
            "Você guarda a pedra. O apelido queima na palma como se ainda estivesse quente.\n\n"
            "A casa parece ter ouvido o próprio nome."
        ),
        "options": [
            ("Ficar no jardim", "jardim"),
            ("Voltar ao corredor", "corredor"),
        ],
    },
    "cozinha": {
        "title": "A cozinha",
        "image": "assets/imagens/cozinha.jpg",
        "text": (
            "A cozinha cheira a gás antigo e laranja podre.\n\n"
            "Na pia, um prato com comida ainda quente. "
            "Ninguém mora aqui há doze anos.\n\n"
            "Na parede, riscos profundos: CONTANDO ATÉ QUINZE.\n\n"
            "Na gaveta da esquerda, uma caixa de fósforos."
        ),
        "options": [
            ("Pegar os fósforos", "pegar_fosforos"),
            ("Tocar a comida quente", "tocar_comida"),
            ("Voltar ao corredor", "corredor"),
        ],
    },
    "cozinha_vazia": {
        "title": "A cozinha",
        "image": "assets/imagens/cozinha.jpg",
        "text": (
            "A gaveta da esquerda está aberta e vazia. "
            "Você já pegou os fósforos.\n\n"
            "O vapor da comida ainda sobe em espirais lentas."
        ),
        "options": [
            ("Voltar ao corredor", "corredor"),
        ],
    },
    "comida_quente": {
        "title": "A segunda mão",
        "image": "assets/imagens/cozinha.jpg",
        "text": (
            "Você encosta o dedo no arroz. Escaldante.\n\n"
            "Por um instante, vê uma segunda mão — a sua, mais nova — "
            "fazendo o mesmo gesto do outro lado do vapor.\n\n"
            "A visão some. O prato continua lá."
        ),
        "options": [
            ("Pegar os fósforos agora", "pegar_fosforos"),
            ("Voltar sem eles", "corredor"),
        ],
    },
    "item_fosforos": {
        "title": "Três chances",
        "image": "assets/imagens/cozinha.jpg",
        "text": (
            "Você guarda os fósforos. A caixa é leve demais — quase vazia.\n\n"
            "Dentro, restam três palitos. Três chances."
        ),
        "options": [
            ("Voltar ao corredor", "corredor"),
        ],
    },
    "sala": {
        "title": "A sala",
        "image": "assets/imagens/sala.jpg",
        "text": (
            "A sala está coberta. O sofá usa um lençol branco manchado de amarelo. "
            "Relógios parados. Poeira em camadas.\n\n"
            "A TV de tubo olha para você com a tela morta — um olho cinza, opaco.\n\n"
            "Na estante, uma gaveta entreaberta. "
            "No corredor lateral, a porta do quarto dos pais."
        ),
        "options": [
            ("Abrir a gaveta da estante", "pegar_chave"),
            ("Examinar a TV", "examinar_tv"),
            ("Ir ao quarto dos pais", "quarto_pais"),
            ("Voltar ao corredor", "corredor"),
        ],
    },
    "sala_pista": {
        "title": "A sala — o rosto",
        "image": "assets/imagens/tv_estatica.jpg",
        "text": (
            "A TV liga sozinha. Estática.\n\n"
            "No meio do ruído branco, um rosto se forma — o seu, mais novo, "
            "sorrindo sem chegar aos olhos.\n\n"
            "A gaveta ainda espera. O quarto dos pais também. "
            "E o rosto na estática parece puxar você para o espelho."
        ),
        "options": [
            ("Abrir a gaveta", "pegar_chave"),
            ("Ir ao quarto dos pais", "quarto_pais"),
            ("Seguir o rosto (espelho)", "ir_espelho"),
            ("Voltar ao corredor", "corredor"),
        ],
    },
    "quarto_pais": {
        "title": "Quarto dos pais",
        "image": "assets/imagens/quarto_pais.jpg",
        "sfx": "porta",
        "text": (
            "A porta cede com a chave enferrujada. O quarto cheira a perfume velho.\n\n"
            "Na cômoda, um bilhete dos pais:\n"
            "\"Se ele acordar de novo, diga o apelido. Conte na ordem certa.\"\n\n"
            "Ao lado, um envelope lacrado com um enigma desenhado à mão."
        ),
        "options": [
            ("Ler o bilhete com cuidado", "ler_pais"),
            ("Abrir o envelope (enigma)", "enigma"),
            ("Voltar à sala", "voltar_sala"),
        ],
    },
    "quarto_pais_trancado": {
        "title": "Porta trancada",
        "image": "assets/imagens/quarto_pais.jpg",
        "sfx": "porta",
        "text": (
            "A porta do quarto dos pais não abre.\n"
            "A fechadura pede a mesma chave do porão."
        ),
        "options": [
            ("Voltar à sala", "voltar_sala"),
        ],
    },
    "bilhete_pais": {
        "title": "O apelido",
        "image": "assets/imagens/quarto_pais.jpg",
        "text": (
            "No verso do bilhete, a letra da sua mãe:\n"
            "\"Casinha. Sempre foi Casinha.\"\n\n"
            "Você lembra do jardim. Da pedra. Do medo que pedia nomes."
        ),
        "options": [
            ("Abrir o envelope (enigma)", "enigma"),
            ("Voltar à sala", "voltar_sala"),
        ],
    },
    "enigma": {
        "title": "O enigma",
        "image": "assets/imagens/enigma.jpg",
        "text": (
            "No papel: três linhas.\n\n"
            "1) O que acende sem ser luz.\n"
            "2) O que guarda a memória sem ser cabeça.\n"
            "3) O apelido da casa.\n\n"
            "Você precisa escolher a ordem certa — ou improvisar."
        ),
        "options": [
            ("Fósforos → fita → Casinha", "enigma_certo"),
            ("Chave → foto → eco", "enigma_errado"),
            ("Vela → pedra → quinze", "enigma_errado"),
            ("Desistir por agora", "voltar_sala"),
        ],
    },
    "enigma_ok": {
        "title": "A casa reconhece",
        "image": "assets/imagens/enigma.jpg",
        "text": (
            "O envelope aquece e solta um cheiro de cera.\n\n"
            "Você acertou a ordem. A casa suspira — um assoalho rangendo longe.\n"
            "O ritual, se um dia for preciso, agora tem caminho."
        ),
        "options": [
            ("Voltar à sala", "voltar_sala"),
            ("Ir ao corredor", "corredor"),
        ],
    },
    "enigma_falha": {
        "title": "Ordem errada",
        "image": "assets/imagens/enigma.jpg",
        "text": (
            "O papel queima nas bordas sem chama.\n\n"
            "Uma dor seca sobe pelo braço. A casa não gosta de mentiras.\n\n"
            "Você perdeu uma vida."
        ),
        "options": [
            ("Tentar de novo", "enigma"),
            ("Voltar à sala", "voltar_sala"),
        ],
    },
    "item_chave": {
        "title": "Chave enferrujada",
        "image": "assets/imagens/sala.jpg",
        "text": (
            "A gaveta range. Dentro: uma chave enferrujada, quente ao toque.\n\n"
            "Na alça, um pedaço de fita isolante com a palavra PORÃO.\n\n"
            "Você guarda a chave. Ela esfria na sua mão aos poucos."
        ),
        "options": [
            ("Continuar na sala", "voltar_sala"),
            ("Ir ao corredor", "corredor"),
        ],
    },
    "tv_estatica": {
        "title": "Estática",
        "image": "assets/imagens/tv_estatica.jpg",
        "sfx": "tv",
        "text": (
            "Você liga a TV. Só estática.\n\n"
            "No chiado, quase dá para ouvir alguém contar: "
            "um… dois… três…\n\n"
            "Você desliga antes de chegar a quinze."
        ),
        "options": [
            ("Continuar na sala", "voltar_sala"),
        ],
    },
    "tv_aviso": {
        "title": "Você deixou alguém",
        "image": "assets/imagens/tv_estatica.jpg",
        "sfx": "tv",
        "text": (
            "Você se aproxima da tela. O rosto de criança abre a boca.\n\n"
            "Não sai som — sai um sopro frio. A estática sussurra:\n"
            "\"Você deixou alguém no seu lugar.\"\n\n"
            "Agora você sabe: precisa ver o espelho de verdade."
        ),
        "options": [
            ("Continuar na sala", "voltar_sala"),
            ("Ir ao espelho", "ir_espelho"),
        ],
    },
    "sotao_escuro": {
        "title": "Sótão sem luz",
        "image": "assets/imagens/sotao.jpg",
        "text": (
            "Está escuro demais. Suas mãos encontram arestas, teias, "
            "algo macio que pode ser um casaco… ou não.\n\n"
            "Sem fósforos, o sótão guarda seus segredos."
        ),
        "options": [
            ("Insistir no escuro", "sotao_queda"),
            ("Descer ao corredor", "corredor"),
        ],
    },
    "sotao_queda": {
        "title": "Queda no escuro",
        "image": "assets/imagens/sotao.jpg",
        "text": (
            "Você avança. O pé encontra o vazio entre duas tábuas.\n\n"
            "Você cai de joelho. Algo — uma unha? um fio? — raspa seu tornozelo.\n\n"
            "Você perdeu uma vida."
        ),
        "options": [
            ("Descer ao corredor", "corredor"),
        ],
    },
    "sotao": {
        "title": "O sótão",
        "image": "assets/imagens/sotao.jpg",
        "text": (
            "Você risca um fósforo. A chama treme e revela o sótão em pedaços laranja:\n"
            "caixas, um gravador de fita cassete, uma vela branca sem usar."
        ),
        "options": [
            ("Examinar o gravador / a fita", "ouvir_fita"),
            ("Pegar a vela", "pegar_vela"),
            ("Descer ao corredor", "corredor"),
        ],
    },
    "sotao_pista": {
        "title": "O sótão — eco da fita",
        "image": "assets/imagens/sotao.jpg",
        "text": (
            "A voz da criança na fita ainda parece ecoar pelas vigas.\n\n"
            "Você pode descer seguindo o eco — até o espelho — "
            "ou continuar vasculhando."
        ),
        "options": [
            ("Ouvir a fita de novo", "ouvir_fita"),
            ("Pegar a vela", "pegar_vela"),
            ("Seguir o eco (espelho)", "ir_espelho"),
            ("Descer ao corredor", "corredor"),
        ],
    },
    "fita_memoria": {
        "title": "EU / OUTRO",
        "image": "assets/imagens/fita.jpg",
        "video": "assets/videos/fita_memoria.mp4",
        "video_autoplay": False,
        "text": (
            "Você aperta play. Chiado. Então uma voz de criança — a sua — sussurra:\n\n"
            "\"Quando eu crescer, vou deixar alguém no meu lugar.\"\n\n"
            "Pausa. Respiração. Depois, mais baixo:\n"
            "\"Pra casa não ficar sozinha.\"\n\n"
            "A fita termina. O gravador continua quente."
        ),
        "options": [
            ("Continuar no sótão", "voltar_sotao"),
            ("Descer ao corredor", "corredor"),
        ],
    },
    "item_vela": {
        "title": "A vela",
        "image": "assets/imagens/sotao.jpg",
        "text": (
            "Você guarda a vela. A cera está fria, mas o pavio cheira a fumaça recente — "
            "como se alguém tivesse apagado agora."
        ),
        "options": [
            ("Continuar no sótão", "voltar_sotao"),
            ("Descer ao corredor", "corredor"),
        ],
    },
    "porta_trancada": {
        "title": "Porão trancado",
        "image": "assets/imagens/porta_falha.jpg",
        "sfx": "porta",
        "text": (
            "A porta do porão está trancada. "
            "A fechadura é antiga, coberta de ferrugem em forma de unha.\n\n"
            "Sem a chave, só resta forçar… ou desistir."
        ),
        "options": [
            ("Forçar a porta", "forcar_porao"),
            ("Desistir e voltar", "corredor"),
        ],
    },
    "porta_falha": {
        "title": "A porta reage",
        "image": "assets/imagens/porta_falha.jpg",
        "sfx": "porta",
        "text": (
            "Você empurra com o ombro. A madeira geme, mas não cede.\n\n"
            "Algo do outro lado empurra de volta — no mesmo ritmo.\n"
            "Uma lasca corta sua palma.\n\n"
            "Você perdeu uma vida."
        ),
        "options": [
            ("Voltar ao corredor", "corredor"),
        ],
    },
    "porao_escuro": {
        "title": "Porão sem luz",
        "image": "assets/imagens/porao.jpg",
        "text": (
            "Sem luz, o chão some. Você tropeça numa caixa. "
            "O joelho bate no concreto.\n\n"
            "Você perdeu uma vida.\n\n"
            "Dedos encontram um pano grosso sobre algo liso — vidro. "
            "Sem luz, você não ousa puxar o pano."
        ),
        "options": [
            ("Subir ao corredor", "corredor"),
        ],
    },
    "porao": {
        "title": "O porão",
        "image": "assets/imagens/porao.jpg",
        "text": (
            "Você risca um fósforo. A chama mostra a inscrição nas paredes:\n"
            "o seu nome, repetido, e abaixo: \"ELE FICOU.\"\n\n"
            "No chão, uma foto rasgada.\n"
            "No fundo, uma porta baixa coberta por um pano escuro — "
            "o formato de um espelho de corpo inteiro."
        ),
        "options": [
            ("Pegar a foto rasgada", "pegar_foto"),
            ("Puxar o pano do espelho", "ir_espelho"),
            ("Subir ao corredor", "corredor"),
        ],
    },
    "item_foto": {
        "title": "A foto rasgada",
        "image": "assets/imagens/porao.jpg",
        "text": (
            "A foto mostra a casa intacta, ensolarada.\n\n"
            "No jardim, uma criança — você — sorri. "
            "Atrás dela, uma sombra com o mesmo sorriso, atrasada um passo.\n\n"
            "A borda da foto está queimada."
        ),
        "options": [
            ("Continuar no porão", "porao"),
            ("Puxar o pano do espelho", "ir_espelho"),
            ("Subir ao corredor", "corredor"),
        ],
    },
    "dialogo_eco": {
        "title": "Diálogo com o eco",
        "image": "assets/imagens/dialogo_eco.jpg",
        "audio": "assets/audios/trilha_espelho.mp3",
        "text": (
            "Antes do confronto, o vidro embacia.\n\n"
            "O eco inclina a cabeça — o seu gesto, atrasado — e pergunta:\n"
            "\"Você veio me buscar… ou veio se despedir?\"\n\n"
            "A resposta muda o peso do que vem depois."
        ),
        "options": [
            ("\"Vim me lembrar de quem eu sou\"", "eco_lembrar"),
            ("\"Vim acabar com isso\"", "eco_acabar"),
            ("\"Vim te ouvir\"", "eco_ouvir"),
            ("Ficar em silêncio", "eco_silencio"),
        ],
    },
    "espelho": {
        "title": "O espelho",
        "image": "assets/imagens/espelho.jpg",
        "audio": "assets/audios/trilha_espelho.mp3",
        "text": (
            "O doppelgänger está do outro lado do vidro, sorrindo com o seu sorriso.\n\n"
            "Ele fala primeiro — com a sua voz, meio segundo atrasada:\n"
            "\"Eu esperei doze anos. A casa estava com saudade.\"\n\n"
            "O ar cheira a chuva de infância e a ferrugem."
        ),
        "options": [
            ("Correr para a porta da frente", "escolher_fuga"),
            ("Confrontar: \"Você não é eu\"", "escolher_verdade"),
            ("Aceitar trocar de lugar", "fim_eco"),
            ("Acender a vela (ritual)", "escolher_ritual"),
        ],
    },
    "espelho_sem_pista": {
        "title": "Sem lembrar",
        "image": "assets/imagens/espelho.jpg",
        "audio": "assets/audios/trilha_espelho.mp3",
        "text": (
            "O espelho te engole com a própria imagem.\n\n"
            "Sem lembrar por que veio, você só vê o sorriso atrasado. "
            "Mãos iguais às suas atravessam o vidro e puxam."
        ),
        "options": [],
    },
    "fuga_falha": {
        "title": "A porta não cede",
        "image": "assets/imagens/corredor.jpg",
        "text": (
            "Você corre. Sem chave, sem luz.\n\n"
            "A porta da frente está trancada por dentro. "
            "Atrasado, o eco chega e põe a mão no seu ombro — a mesma mão."
        ),
        "options": [],
    },
    "verdade_falha": {
        "title": "A frase sem peso",
        "image": "assets/imagens/espelho.jpg",
        "text": (
            "Você grita: \"Você não é eu!\"\n\n"
            "O eco ri com a sua garganta. Sem a fita e a foto, a frase não tem peso.\n"
            "O vidro não quebra. Você quebra."
        ),
        "options": [],
    },
    "ritual_falha": {
        "title": "Falta algo",
        "image": "assets/imagens/espelho.jpg",
        "text": (
            "Você tenta o ritual, mas falta a vela, os fósforos ou a memória da fita.\n\n"
            "O eco sorri. A casa não perdoa improvisos."
        ),
        "options": [
            ("Enfrentar de outro modo", "espelho"),
        ],
    },
    "fim_fuga": {
        "title": "FINAL — FUGA AMBÍGUA",
        "image": "assets/imagens/fim_fuga.jpg",
        "audio": "assets/audios/trilha_casa.mp3",
        "text": (
            "Você corre. A porta da frente cede. A noite lá fora é real.\n\n"
            "Você olha para trás. A casa está quieta. Então, no seu antigo quarto, "
            "a luz acende sozinha.\n\n"
            "Alguém passa atrás da cortina com o seu jeito de andar. "
            "Meio segundo atrasado.\n\n"
            "Você escapou. Talvez."
        ),
        "options": [],
    },
    "fim_verdade": {
        "title": "FINAL — VERDADE",
        "image": "assets/imagens/fim_verdade.jpg",
        "audio": "assets/audios/trilha_amanhecer.mp3",
        "text": (
            "Você segura a foto e a memória da fita.\n"
            "\"Você não é eu. Você é o que eu deixei.\"\n\n"
            "O sorriso do eco trinca. Você golpeia o espelho. "
            "O vidro soluça e estilhaça.\n\n"
            "Quando amanhece, você está no jardim. "
            "Não há passos atrasados. Só o seu coração, no tempo certo."
        ),
        "options": [],
    },
    "fim_eco": {
        "title": "FINAL — O ECO SAI",
        "image": "assets/imagens/fim_eco.jpg",
        "stop_audio": True,
        "text": (
            "Você encosta a mão no vidro. O eco encosta a dele.\n\n"
            "O frio passa. O calor fica do outro lado. Não há recuo.\n\n"
            "Do lado de fora, alguém com o seu rosto abre a porta da frente "
            "e sorri no tempo certo.\n\n"
            "A casa não está mais sozinha. Você está."
        ),
        "options": [],
    },
    "fim_ritual": {
        "title": "FINAL SECRETO — RITUAL",
        "image": "assets/imagens/fim_ritual.jpg",
        "audio": "assets/audios/trilha_amanhecer.mp3",
        "text": (
            "Você risca o fósforo. A vela acende.\n\n"
            "A chama mostra o eco como ele é: pequeno, assustado, "
            "uma criança que prometeu não deixar a casa vazia.\n\n"
            "Você diz o apelido da casa — Casinha.\n"
            "O eco encolhe. Vira menino de novo. Você apaga a vela com os dedos.\n\n"
            "No quintal, queima a fita. A casa, pela primeira vez em doze anos, "
            "não responde."
        ),
        "options": [],
    },
    "fim_ruim": {
        "title": "FINAL — MORTE",
        "image": "assets/imagens/fim_morte.jpg",
        "stop_audio": True,
        "text": (
            "A escuridão fecha como uma boca.\n\n"
            "Os passos atrasados — clic… clic — param.\n"
            "Não porque foram embora.\n"
            "Porque agora estão sincronizados com os seus.\n\n"
            "A casa lembra. E você, enfim, também."
        ),
        "options": [],
    },
    "fim_atrasado": {
        "title": "FINAL — A CASA ESCOLHE",
        "image": "assets/imagens/fim_atrasado.jpg",
        "stop_audio": True,
        "text": (
            "Quinze.\n\n"
            "O bilhete não mentia. A contagem termina e a casa decide por você.\n\n"
            "Os passos atrasados alcançam o seu ritmo. "
            "O corredor encolhe. O espelho já não precisa de você do lado de cá.\n\n"
            "Alguém com o seu rosto apaga a luz."
        ),
        "options": [],
    },
}


# ---------------------------------------------------------------------------
# REGRAS / AÇÕES — o que cada clique faz (itens, flags, cena seguinte)
# ---------------------------------------------------------------------------

def executar_acao(acao):
    """Aplica a regra da ação escolhida. Não conta turno (isso é no bridge JS)."""
    flags = state["flags"]

    if acao == "ir_corredor":
        ganhar_pontos(1)
        mostrar_cena("corredor")
        return

    if acao == "ler_bilhete":
        flags["leu_bilhete"] = True
        ganhar_pontos(5)
        mostrar_cena("bilhete")
        return

    if acao == "corredor":
        mostrar_cena("corredor")
        return

    if acao == "corredor_mais":
        mostrar_cena("corredor_mais")
        return

    if acao == "escadas":
        mostrar_cena("escadas")
        return

    if acao == "jardim":
        mostrar_cena("jardim")
        return

    if acao == "pegar_pedra":
        if possui_item("pedra do jardim"):
            mostrar_cena("jardim")
            return
        adicionar_item("pedra do jardim", pontos=12)
        flags["achou_pedra"] = True
        mostrar_cena("item_pedra")
        return

    if acao == "chamar_eco":
        flags["conheceu_eco"] = True
        morreu = perder_vida(1)
        if not morreu:
            mostrar_cena("eco_responde")
        return

    if acao == "cozinha":
        if possui_item("fósforos"):
            mostrar_cena("cozinha_vazia")
        else:
            mostrar_cena("cozinha")
        return

    if acao == "pegar_fosforos":
        adicionar_item("fósforos", pontos=10)
        mostrar_cena("item_fosforos")
        return

    if acao == "tocar_comida":
        ganhar_pontos(2)
        mostrar_cena("comida_quente")
        return

    if acao in ("sala", "voltar_sala"):
        if flags["ouviu_fita"]:
            mostrar_cena("sala_pista")
        else:
            mostrar_cena("sala")
        return

    if acao == "quarto_pais":
        if not possui_item("chave enferrujada"):
            mostrar_cena("quarto_pais_trancado")
            return
        mostrar_cena("quarto_pais")
        return

    if acao == "ler_pais":
        flags["leu_pais"] = True
        ganhar_pontos(8)
        mostrar_cena("bilhete_pais")
        return

    if acao == "enigma":
        if flags["resolveu_enigma"]:
            mostrar_cena("enigma_ok")
            return
        mostrar_cena("enigma")
        return

    if acao == "enigma_certo":
        flags["resolveu_enigma"] = True
        bonus = 25
        if possui_item("pedra do jardim") or flags["achou_pedra"] or flags["leu_pais"]:
            bonus += 10
        ganhar_pontos(bonus)
        mostrar_cena("enigma_ok")
        return

    if acao == "enigma_errado":
        morreu = perder_vida(1)
        if not morreu:
            mostrar_cena("enigma_falha")
        return

    if acao == "pegar_chave":
        if possui_item("chave enferrujada"):
            executar_acao("voltar_sala")
            return
        adicionar_item("chave enferrujada", pontos=10)
        mostrar_cena("item_chave")
        return

    if acao == "examinar_tv":
        flags["viu_tv"] = True
        ganhar_pontos(3)
        if flags["ouviu_fita"]:
            mostrar_cena("tv_aviso")
        else:
            mostrar_cena("tv_estatica")
        return

    if acao in ("sotao", "voltar_sotao"):
        if not possui_item("fósforos"):
            mostrar_cena("sotao_escuro")
            return
        if flags["ouviu_fita"] and (flags["viu_foto"] or flags["viu_tv"]):
            mostrar_cena("sotao_pista")
        else:
            mostrar_cena("sotao")
        return

    if acao == "sotao_queda":
        morreu = perder_vida(1)
        if not morreu:
            mostrar_cena("sotao_queda")
        return

    if acao == "ouvir_fita":
        adicionar_item("fita cassete", pontos=15)
        flags["ouviu_fita"] = True
        mostrar_cena("fita_memoria")
        return

    if acao == "pegar_vela":
        if possui_item("vela"):
            executar_acao("voltar_sotao")
            return
        adicionar_item("vela", pontos=10)
        mostrar_cena("item_vela")
        return

    if acao == "tentar_porao":
        if possui_item("chave enferrujada"):
            flags["abriu_porao"] = True
            ganhar_pontos(5)
            executar_acao("porao")
        else:
            mostrar_cena("porta_trancada")
        return

    if acao == "forcar_porao":
        morreu = perder_vida(1)
        if not morreu:
            mostrar_cena("porta_falha")
        return

    if acao == "porao":
        if not possui_item("fósforos"):
            morreu = perder_vida(1)
            if not morreu:
                mostrar_cena("porao_escuro")
            return
        mostrar_cena("porao")
        return

    if acao == "pegar_foto":
        adicionar_item("foto rasgada", pontos=15)
        flags["viu_foto"] = True
        mostrar_cena("item_foto")
        return

    if acao == "ir_espelho":
        tem_pista = (
            flags["ouviu_fita"]
            or flags["viu_foto"]
            or possui_item("fita cassete")
            or possui_item("foto rasgada")
        )
        ganhar_pontos(5)
        if not tem_pista:
            _finalizar("fim_ruim")
            return
        flags["conheceu_eco"] = True
        if not flags["falou_eco"]:
            mostrar_cena("dialogo_eco")
        else:
            mostrar_cena("espelho")
        return

    if acao == "eco_lembrar":
        flags["falou_eco"] = True
        ganhar_pontos(15)
        mostrar_cena("espelho")
        return

    if acao == "eco_acabar":
        flags["falou_eco"] = True
        ganhar_pontos(5)
        # tom agressivo: leve risco narrativo — só pontos
        mostrar_cena("espelho")
        return

    if acao == "eco_ouvir":
        flags["falou_eco"] = True
        ganhar_pontos(20)
        mostrar_cena("espelho")
        return

    if acao == "eco_silencio":
        flags["falou_eco"] = True
        ganhar_pontos(2)
        # Silêncio: o eco se aproxima e tira uma vida
        morreu = perder_vida(1)
        if not morreu:
            mostrar_cena("espelho")
        return

    if acao == "escolher_fuga":
        if possui_item("chave enferrujada") or possui_item("fósforos"):
            _finalizar("fim_fuga", 20)
        else:
            _finalizar("fim_ruim")
        return

    if acao == "escolher_verdade":
        tem_fita = flags["ouviu_fita"] or possui_item("fita cassete")
        tem_foto = flags["viu_foto"] or possui_item("foto rasgada")
        if tem_fita and tem_foto:
            bonus = 40
            if flags["leu_pais"] or flags["falou_eco"]:
                bonus += 10
            _finalizar("fim_verdade", bonus)
        else:
            _finalizar("fim_ruim")
        return

    if acao == "escolher_ritual":
        base_ok = (
            possui_item("vela")
            and possui_item("fósforos")
            and (flags["ouviu_fita"] or possui_item("fita cassete"))
        )
        # Enigma ou pedra ajudam, mas ritual clássico ainda funciona sem eles
        if base_ok:
            bonus = 60
            if flags["resolveu_enigma"]:
                bonus += 20
            if possui_item("pedra do jardim"):
                bonus += 10
            _finalizar("fim_ritual", bonus)
        else:
            mostrar_cena("ritual_falha")
        return

    if acao == "fim_eco":
        _finalizar("fim_eco", 10)
        return

    if acao == "espelho":
        mostrar_cena("espelho")
        return

    if acao in SCENES:
        mostrar_cena(acao)
        return

    window.console.warn(f"Ação sem tratamento: {acao}")


def executar_acao_js(acao):
    """
    Entrada dos cliques (JavaScript → Python).
    Conta 1 turno por escolha; aos 15 fora de final, a casa escolhe.
    """
    acao = str(acao).strip() if acao is not None else ""
    if not acao or acao == "None" or acao == "undefined":
        return

    # Não conta turno em reinícios internos sem clique — só cliques passam aqui
    state["turnos"] += 1
    atualizar_status()

    executar_acao(acao)

    cena = state.get("cena_atual")
    if state["turnos"] >= CONFIG["max_turnos"] and not _eh_final(cena):
        _finalizar("fim_atrasado")
        return

    if not _eh_final(cena):
        salvar_jogo()


# ---------------------------------------------------------------------------
# BOOT DA INTERFACE
# ---------------------------------------------------------------------------

def configurar_interface():
    """Preenche a tela inicial e liga o Python ao JavaScript dos botões."""
    document.querySelector("#boot-title").innerText = CONFIG["titulo"]
    document.querySelector("#boot-sub").innerText = CONFIG.get("subtitulo", "")
    document.querySelector("#boot-author").innerText = f"por {CONFIG.get('autor', '')}"
    document.querySelector("#boot-icon").innerText = CONFIG.get("icone", "")
    document.querySelector("#titulo-jogo").innerText = CONFIG["titulo"]
    document.querySelector("#autor-jogo").innerText = CONFIG.get("autor", "")

    capa = CONFIG.get("capa")
    cover = document.querySelector("#boot-cover")
    if capa:
        cover.src = capa
        cover.classList.remove("hidden")
    else:
        cover.classList.add("hidden")

    # Expõe funções para o JavaScript (guarda proxies para o GC não liberar)
    global _js_proxies
    _js_proxies = [
        create_proxy(iniciar_jogo),
        create_proxy(continuar_jogo),
        create_proxy(reiniciar_aventura),
        create_proxy(executar_acao_js),
    ]
    window.iniciar_jogo = _js_proxies[0]
    window.continuar_jogo = _js_proxies[1]
    window.reiniciar_aventura = _js_proxies[2]
    window.executar_acao_js = _js_proxies[3]

    atualizar_ranking_ui()
    _atualizar_botao_continuar()
    atualizar_status()

    document.querySelector("#loading").classList.add("hidden")
    document.querySelector("#btn-iniciar").disabled = False
    document.querySelector("#btn-iniciar").innerText = "▶ NOVO JOGO"


configurar_interface()
