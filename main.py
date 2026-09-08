"""
A Casa que Lembra — PyScript GameJam V2
Terror narrativo interativo (botões, sem input/terminal).

Estrutura didática (escola / GameJam):
  CONFIG  → dados fixos do jogo (título, vida, capa, trilha)
  state   → o que muda durante a partida (vida, itens, ações, flags)
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
    "subtitulo": "Você deixou alguém no seu lugar. Explore até o espelho — ou até a casa te levar.",
    "icone": "⌂",
    "capa": "/assets/imagens/capa.jpg",
    "trilha_inicial": "/assets/audios/trilha_casa.mp3",
    "volume_inicial": 0.55,
    "vida_inicial": 3,
    "pontos_iniciais": 0,
    "cena_inicial": "inicio",
}

SAVE_KEY = "casa_que_lembra_save"
RANK_KEY = "casa_que_lembra_ranking"

SFX = {
    "click": "/assets/audios/sfx_click.mp3",
    "porta": "/assets/audios/sfx_porta.mp3",
    "passos": "/assets/audios/sfx_passos.mp3",
    "tv": "/assets/audios/sfx_tv.mp3",
    "dano": "/assets/audios/sfx_dano.mp3",
}

# Finais conhecidos (ranking). Sem limite de tempo: a partida acaba no
# espelho (escolha) ou quando a vida chega a zero (fim_ruim).
FINAIS = {
    "fim_fuga",
    "fim_verdade",
    "fim_eco",
    "fim_ritual",
    "fim_ruim",
    "fuga_falha",
    "espelho_sem_pista",
}

# ---------------------------------------------------------------------------
# STATE — inventário, vida, ações e flags da história
# ---------------------------------------------------------------------------

state = {}


def _estado_inicial():
    """Cria um estado novo de partida (usado em Novo jogo / Reiniciar)."""
    return {
        "vida": CONFIG["vida_inicial"],
        "pontos": CONFIG["pontos_iniciais"],
        "inventario": [],
        "acoes": 0,  # contagem só para ranking (sem limite)
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



def asset(path):
    """Normaliza caminho de mídia para URL absoluta (evita quebrar no mobile/Vercel)."""
    if not path:
        return path
    path = str(path).strip()
    if path.startswith("http://") or path.startswith("https://") or path.startswith("/"):
        return path
    path = path.lstrip("./")
    return "/" + path

state = _estado_inicial()
_js_proxies = []


# ---------------------------------------------------------------------------
# HELPERS DO FRAMEWORK (HUD, itens, áudio, save, ranking)
# ---------------------------------------------------------------------------

def atualizar_status():
    """Atualiza vida, pontos e inventário na HUD (sem relógio/limite)."""
    document.querySelector("#stat-vida").innerText = str(state["vida"])
    document.querySelector("#stat-pontos").innerText = str(state["pontos"])
    inv = state["inventario"]
    inv_el = document.querySelector("#stat-inv")
    if inv_el:
        inv_el.innerText = ", ".join(inv) if inv else "nada"

    # Chips de inventário + alerta de vida baixa
    try:
        window.atualizarInventarioUI(json.dumps(list(inv)))
    except Exception:
        pass
    vida_pill = document.querySelector(".stat-pill.vida")
    if vida_pill:
        if state["vida"] <= 1:
            vida_pill.classList.add("low")
        else:
            vida_pill.classList.remove("low")


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
        window.tocarSfx(asset(src))
    except Exception:
        pass


def perder_vida(n=1):
    tocar_sfx("dano")
    try:
        window.flashDano()
    except Exception:
        pass
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
    """Troca a trilha de fundo via JS (respeita gesto do usuário / autoplay)."""
    if not caminho:
        return
    try:
        window.tocarTrilha(asset(caminho), CONFIG.get("volume_inicial", 0.55))
    except Exception:
        # fallback direto no elemento
        player = document.querySelector("#audio-player")
        if not player:
            return
        player.src = caminho
        player.volume = CONFIG.get("volume_inicial", 0.48)
        try:
            player.play()
        except Exception:
            pass


def parar_audio():
    try:
        window.pararTrilha()
    except Exception:
        player = document.querySelector("#audio-player")
        if not player:
            return
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
        btn.classList.remove("show")
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
        "acoes": state.get("acoes", state.get("turnos", 0)),
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
    """Registra pontuação local e abre o envio ao ranking global da competição."""
    nomes = {
        "fim_fuga": "Fuga",
        "fim_verdade": "Verdade",
        "fim_eco": "O Eco sai",
        "fim_ritual": "Ritual secreto",
        "fim_ruim": "Morte",
        "fuga_falha": "Fuga falhou",
        "espelho_sem_pista": "Sem lembrar",
    }
    final_nome = nomes.get(final_id, final_id)
    entrada = {
        "nome": "Você",
        "pontos": state["pontos"],
        "final": final_nome,
        "acoes": state.get("acoes", state.get("turnos", 0)),
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
    lista = lista[:8]
    try:
        window.localStorage.setItem(RANK_KEY, json.dumps(lista))
    except Exception:
        pass

    # Modal JS → POST /api/ranking (placar global na web)
    try:
        window.abrirModalRanking(
            json.dumps(
                {
                    "pontos": int(state["pontos"]),
                    "final": final_nome,
                    "acoes": int(state.get("acoes", 0)),
                }
            )
        )
    except Exception:
        pass
    atualizar_ranking_ui()


def atualizar_ranking_ui():
    """Preferê o placar global; se falhar, mostra o ranking local."""
    try:
        # JS preenche #ranking-lista com o top global
        window.carregarRankingGlobal()
        return
    except Exception:
        pass
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
    for i, item in enumerate(lista[:8]):
        li = document.createElement("li")
        nome = item.get("nome") or "Você"
        li.innerText = (
            f"{i + 1}º · {item.get('pontos', 0)} pts — {nome} · "
            f"{item.get('final', '?')}"
        )
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
        video = asset(cena.get("video") or "")
        image = asset(cena.get("image") or CONFIG.get("capa") or "")
        autoplay = bool(cena.get("video_autoplay"))
        window.aplicarMidiaCena(video, image, autoplay)
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
        btn.classList.remove("show")

    try:
        window.animarPainel()
        window.mostrarOpcoesAnimadas()
    except Exception:
        pass

    if _eh_final(nome):
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
    state["acoes"] = data.get("acoes", data.get("turnos", 0))
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
#
# História (o que precisa fazer sentido):
# Aos 8 anos você prometeu à casa que não a deixaria sozinha.
# Aos 18, foi embora. A casa ficou com um "eco": uma cópia sua, atrasada.
# Doze anos depois você (adulto) volta e acorda no quarto.
# Sem relógio: explore, junte provas, enfrente o espelho — ou morra (0 vidas).
# Identidade: VOCÊ = adulto que voltou; ECO = o menino/cópia que ficou.
# ---------------------------------------------------------------------------

SCENES = {
    "inicio": {
        "title": "O quarto de infância",
        "image": "/assets/imagens/inicio.jpg",
        "video": "/assets/videos/cena_inicio.mp4",
        "video_autoplay": True,
        "text": (
            "Você voltou para a casa onde cresceu. Está vazia há doze anos — "
            "desde o dia em que você saiu e não olhou para trás.\n\n"
            "Acordou no seu antigo quarto. O colchão cheira a mofo e a sabão em pó.\n\n"
            "No guarda-roupa, o reflexo é o seu — adulto — mas pisca meio segundo depois.\n\n"
            "Na mesinha, um bilhete na sua letra de criança:\n"
            "\"Não deixe a casa sozinha. Se for embora, deixe alguém no seu lugar.\"\n\n"
            "Do corredor, passos imitam os seus — atrasados. O eco ainda mora aqui."
        ),
        "options": [
            ("Ler o verso do bilhete", "ler_bilhete"),
            ("Ir ao corredor agora", "ir_corredor"),
        ],
    },
    "bilhete": {
        "title": "O verso",
        "image": "/assets/imagens/inicio.jpg",
        "video": "/assets/videos/cena_inicio.mp4",
        "video_autoplay": True,
        "text": (
            "No verso, a letra treme:\n"
            "\"Cada erro te aproxima dele. Se a casa te cansar, o que ficou no seu lugar vira você.\"\n\n"
            "Você lembra: aos oito anos, com medo de dormir sozinho, "
            "prometeu à casa que nunca iria embora.\n\n"
            "Aos dezoito, foi. Um eco — a sua cópia atrasada — ficou.\n\n"
            "Objetivo: juntar provas, descer ao porão e enfrentar o espelho. "
            "Não há relógio. Há três vidas. Explore até o fim — ou até a casa te levar."
        ),
        "options": [
            ("Ir ao corredor", "corredor"),
        ],
    },
    "corredor": {
        "title": "O corredor",
        "image": "/assets/imagens/corredor.jpg",
        "video": "/assets/videos/cena_corredor.mp4",
        "video_autoplay": True,
        "sfx": "passos",
        "text": (
            "O corredor é o centro da casa. Os passos atrasados ecoam no fundo.\n\n"
            "Cozinha: luz (fósforos).\n"
            "Sala: chave do porão.\n"
            "Escadas: sótão (memória) e porão (o espelho).\n"
            "Jardim e outros caminhos ficam mais adiante."
        ),
        "options": [
            ("Ir à cozinha (fósforos)", "cozinha"),
            ("Ir à sala (chave)", "sala"),
            ("Usar as escadas", "escadas"),
            ("Jardim e outros caminhos", "corredor_mais"),
        ],
    },
    "corredor_mais": {
        "title": "Outros caminhos",
        "image": "/assets/imagens/corredor.jpg",
        "video": "/assets/videos/cena_corredor.mp4",
        "video_autoplay": True,
        "text": (
            "A porta dos fundos leva ao jardim — o apelido da casa está lá.\n\n"
            "Chamar quem anda atrasado é perigoso: o eco responde com a sua voz."
        ),
        "options": [
            ("Ir ao jardim (apelido)", "jardim"),
            ("Chamar quem está aí", "chamar_eco"),
            ("Voltar ao corredor", "corredor"),
        ],
    },
    "escadas": {
        "title": "As escadas",
        "image": "/assets/imagens/corredor.jpg",
        "video": "/assets/videos/cena_corredor.mp4",
        "video_autoplay": True,
        "sfx": "passos",
        "text": (
            "Para cima: o sótão. Lá está a fita que você gravou criança — "
            "a prova da promessa. Também há uma vela.\n\n"
            "Para baixo: o porão. A porta pede a chave da sala. "
            "No fundo, o espelho onde o eco espera."
        ),
        "options": [
            ("Subir ao sótão", "sotao"),
            ("Descer ao porão", "tentar_porao"),
            ("Voltar ao corredor", "corredor"),
        ],
    },
    "eco_responde": {
        "title": "O eco responde",
        "image": "/assets/imagens/eco_responde.jpg",
        "video": "/assets/videos/cena_eco_responde.mp4",
        "video_autoplay": True,
        "text": (
            "Você grita: \"Tem alguém aí?\"\n\n"
            "Do fundo do corredor a sua voz volta, um pouco mais alegre:\n"
            "\"Tem alguém aí?\"\n\n"
            "O eco se aproxima. Frio na nuca. Ele não gosta de ser chamado sem nome.\n\n"
            "Você perdeu uma vida."
        ),
        "options": [
            ("Voltar ao corredor", "corredor"),
        ],
    },
    "jardim": {
        "title": "O jardim",
        "image": "/assets/imagens/jardim.jpg",
        "video": "/assets/videos/cena_jardim.mp4",
        "video_autoplay": True,
        "sfx": "passos",
        "text": (
            "O quintal está morto, mas a terra ainda cheira a chuva.\n\n"
            "Sob a roseira, uma pedra com o apelido que você dava à casa:\n"
            "CASINHA.\n\n"
            "Era assim que você acalmava o medo: dizia o nome em voz alta. "
            "Se for libertar o eco, vai precisar desse nome."
        ),
        "options": [
            ("Pegar a pedra com o apelido", "pegar_pedra"),
            ("Voltar ao corredor", "corredor"),
        ],
    },
    "item_pedra": {
        "title": "O apelido",
        "image": "/assets/imagens/jardim.jpg",
        "video": "/assets/videos/cena_jardim.mp4",
        "video_autoplay": True,
        "text": (
            "Você guarda a pedra. CASINHA.\n\n"
            "A casa parece ter ouvido. O vento no quintal para um segundo.\n\n"
            "Agora você tem o nome verdadeiro — peça do ritual de libertação."
        ),
        "options": [
            ("Voltar ao corredor", "corredor"),
        ],
    },
    "cozinha": {
        "title": "A cozinha",
        "image": "/assets/imagens/cozinha.jpg",
        "video": "/assets/videos/cena_cozinha.mp4",
        "video_autoplay": True,
        "text": (
            "Na parede, riscos: dias, anos — o eco marcou o tempo sozinho.\n\n"
            "Na pia, um prato ainda quente. Ninguém mora aqui. "
            "O eco cozinha no seu horário, atrasado.\n\n"
            "Na gaveta: fósforos. Sem eles o sótão e o porão ficam escuros demais "
            "(e cada queda custa uma vida)."
        ),
        "options": [
            ("Pegar os fósforos", "pegar_fosforos"),
            ("Tocar a comida quente", "tocar_comida"),
            ("Voltar ao corredor", "corredor"),
        ],
    },
    "cozinha_vazia": {
        "title": "A cozinha",
        "image": "/assets/imagens/cozinha.jpg",
        "video": "/assets/videos/cena_cozinha.mp4",
        "video_autoplay": True,
        "text": (
            "Você já pegou os fósforos. O vapor da comida ainda sobe.\n\n"
            "Na parede, o risco do número avança sozinho."
        ),
        "options": [
            ("Voltar ao corredor", "corredor"),
        ],
    },
    "comida_quente": {
        "title": "A segunda mão",
        "image": "/assets/imagens/cozinha.jpg",
        "video": "/assets/videos/cena_cozinha.mp4",
        "video_autoplay": True,
        "text": (
            "O arroz queima o dedo. Do outro lado do vapor, "
            "uma mão igual à sua — mais nova — faz o mesmo gesto.\n\n"
            "O eco está na casa. Ele come, anda, espera.\n\n"
            "Os fósforos ainda estão na gaveta."
        ),
        "options": [
            ("Pegar os fósforos agora", "pegar_fosforos"),
            ("Voltar sem eles", "corredor"),
        ],
    },
    "item_fosforos": {
        "title": "Fósforos",
        "image": "/assets/imagens/cozinha.jpg",
        "video": "/assets/videos/cena_cozinha.mp4",
        "video_autoplay": True,
        "text": (
            "Três palitos. Luz para o sótão e o porão. "
            "Também servem para acender a vela no ritual, ou para ver a porta da frente na fuga."
        ),
        "options": [
            ("Voltar ao corredor", "corredor"),
        ],
    },
    "sala": {
        "title": "A sala",
        "image": "/assets/imagens/sala.jpg",
        "video": "/assets/videos/cena_sala.mp4",
        "video_autoplay": True,
        "text": (
            "Sofá coberto. Relógios parados. A TV de tubo está morta.\n\n"
            "Na estante, a gaveta da chave do porão.\n"
            "Ao lado, o quarto dos pais — também abre com essa chave.\n\n"
            "A TV às vezes mostra o eco. Vale ligar."
        ),
        "options": [
            ("Pegar a chave do porão", "pegar_chave"),
            ("Ligar a TV", "examinar_tv"),
            ("Ir ao quarto dos pais", "quarto_pais"),
            ("Voltar ao corredor", "corredor"),
        ],
    },
    "sala_pista": {
        "title": "A sala — o recado",
        "image": "/assets/imagens/tv_estatica.jpg",
        "video": "/assets/videos/cena_tv.mp4",
        "video_autoplay": True,
        "text": (
            "A TV liga sozinha. No meio da estática, o seu rosto de criança.\n\n"
            "Ele aponta para baixo — para o porão, para o espelho.\n\n"
            "Você já ouviu a fita. Agora falta descer e ver o eco de frente."
        ),
        "options": [
            ("Pegar a chave", "pegar_chave"),
            ("Ir ao quarto dos pais", "quarto_pais"),
            ("Ir ao espelho do porão", "ir_espelho"),
            ("Voltar ao corredor", "corredor"),
        ],
    },
    "quarto_pais": {
        "title": "Quarto dos pais",
        "image": "/assets/imagens/quarto_pais.jpg",
        "video": "/assets/videos/cena_quarto_pais.mp4",
        "video_autoplay": True,
        "sfx": "porta",
        "text": (
            "A chave abre. Cheiro de perfume velho.\n\n"
            "Sua mãe escreveu: se o menino que ficou acordar, "
            "diga o apelido da casa e acenda a vela — não grite, não fuja sem olhar.\n\n"
            "Há um envelope com um enigma: a ordem do ritual."
        ),
        "options": [
            ("Ler o bilhete até o fim", "ler_pais"),
            ("Abrir o envelope do ritual", "enigma"),
            ("Voltar à sala", "voltar_sala"),
        ],
    },
    "quarto_pais_trancado": {
        "title": "Porta trancada",
        "image": "/assets/imagens/quarto_pais.jpg",
        "video": "/assets/videos/cena_quarto_pais.mp4",
        "video_autoplay": True,
        "sfx": "porta",
        "text": (
            "O quarto dos pais não abre sem a chave da sala — "
            "a mesma que abre o porão."
        ),
        "options": [
            ("Voltar à sala", "voltar_sala"),
        ],
    },
    "bilhete_pais": {
        "title": "O que a mãe sabia",
        "image": "/assets/imagens/quarto_pais.jpg",
        "video": "/assets/videos/cena_quarto_pais.mp4",
        "video_autoplay": True,
        "text": (
            "No verso: \"O apelido é Casinha. Sempre foi.\"\n\n"
            "Sua mãe percebeu o eco. Tentou ensinar o nome certo. "
            "Você foi embora antes de aprender.\n\n"
            "Agora você sabe: o ritual precisa de vela, fósforo, fita e o nome Casinha."
        ),
        "options": [
            ("Abrir o envelope do ritual", "enigma"),
            ("Voltar à sala", "voltar_sala"),
        ],
    },
    "enigma": {
        "title": "A ordem do ritual",
        "image": "/assets/imagens/enigma.jpg",
        "video": "/assets/videos/cena_enigma.mp4",
        "video_autoplay": True,
        "text": (
            "Três passos, nesta ordem:\n\n"
            "1) O que faz fogo (cozinha).\n"
            "2) O que guarda a voz da criança (sótão).\n"
            "3) O apelido da casa (jardim / bilhete da mãe).\n\n"
            "Escolha a sequência certa. Errar dói."
        ),
        "options": [
            ("Fogo → fita → Casinha", "enigma_certo"),
            ("Chave → foto → eco", "enigma_errado"),
            ("Vela → pedra → chave", "enigma_errado"),
            ("Deixar para depois", "voltar_sala"),
        ],
    },
    "enigma_cego": {
        "title": "Ainda falta lembrar",
        "image": "/assets/imagens/enigma.jpg",
        "video": "/assets/videos/cena_enigma.mp4",
        "video_autoplay": True,
        "text": (
            "O papel não faz sentido ainda.\n\n"
            "Você precisa achar o apelido (jardim ou bilhete da mãe) "
            "ou ouvir a fita do sótão. Sem isso, o enigma é só risco."
        ),
        "options": [
            ("Voltar à sala", "voltar_sala"),
            ("Ir ao corredor", "corredor"),
        ],
    },
    "enigma_ok": {
        "title": "A ordem certa",
        "image": "/assets/imagens/enigma.jpg",
        "video": "/assets/videos/cena_enigma.mp4",
        "video_autoplay": True,
        "text": (
            "Fogo. Memória. Nome.\n\n"
            "A casa reconhece a ordem. Se você chegar ao espelho com vela, "
            "fósforos e fita, poderá libertar o menino em vez de destruí-lo."
        ),
        "options": [
            ("Voltar à sala", "voltar_sala"),
            ("Ir ao corredor", "corredor"),
        ],
    },
    "enigma_falha": {
        "title": "Ordem errada",
        "image": "/assets/imagens/enigma.jpg",
        "video": "/assets/videos/cena_enigma.mp4",
        "video_autoplay": True,
        "text": (
            "A casa não aceita a sequência. Uma dor sobe pelo braço.\n\n"
            "Você perdeu uma vida. Pode tentar de novo, ou ir atrás das pistas."
        ),
        "options": [
            ("Tentar de novo", "enigma"),
            ("Voltar à sala", "voltar_sala"),
        ],
    },
    "item_chave": {
        "title": "Chave do porão",
        "image": "/assets/imagens/sala.jpg",
        "video": "/assets/videos/cena_sala.mp4",
        "video_autoplay": True,
        "text": (
            "Na alça: PORÃO. Também abre o quarto dos pais.\n\n"
            "Sem essa chave você não chega ao espelho — "
            "e na fuga ela destranca a porta da frente."
        ),
        "options": [
            ("Continuar na sala", "voltar_sala"),
            ("Ir ao corredor", "corredor"),
        ],
    },
    "tv_estatica": {
        "title": "A TV",
        "image": "/assets/imagens/tv_estatica.jpg",
        "video": "/assets/videos/cena_tv.mp4",
        "video_autoplay": True,
        "sfx": "tv",
        "text": (
            "Estática. No chiado, alguém conta: um… dois… três…\n\n"
            "Um rosto de criança — o seu — aparece e some.\n\n"
            "Ainda falta a fita do sótão para entender o que ele quer dizer."
        ),
        "options": [
            ("Continuar na sala", "voltar_sala"),
        ],
    },
    "tv_aviso": {
        "title": "O recado da TV",
        "image": "/assets/imagens/tv_estatica.jpg",
        "video": "/assets/videos/cena_tv.mp4",
        "video_autoplay": True,
        "sfx": "tv",
        "text": (
            "Com a fita ainda na cabeça, a estática fica clara:\n"
            "\"Você deixou alguém no seu lugar. Ele está no porão.\"\n\n"
            "É o eco. Caminho: chave, fósforos, descer."
        ),
        "options": [
            ("Continuar na sala", "voltar_sala"),
            ("Ir ao espelho do porão", "ir_espelho"),
        ],
    },
    "sotao_escuro": {
        "title": "Sótão sem luz",
        "image": "/assets/imagens/sotao.jpg",
        "video": "/assets/videos/cena_sotao.mp4",
        "video_autoplay": True,
        "text": (
            "Escuro demais. A fita e a vela estão aqui, mas sem fósforos "
            "você não vê o chão.\n\n"
            "Volte à cozinha, pegue os fósforos, suba de novo."
        ),
        "options": [
            ("Insistir no escuro", "sotao_queda"),
            ("Descer buscar fósforos", "corredor"),
        ],
    },
    "sotao_queda": {
        "title": "Queda no escuro",
        "image": "/assets/imagens/sotao.jpg",
        "video": "/assets/videos/cena_sotao.mp4",
        "video_autoplay": True,
        "text": (
            "O pé encontra o vazio entre as tábuas. Você cai. Algo raspa o tornozelo.\n\n"
            "Você perdeu uma vida. Ainda precisa dos fósforos."
        ),
        "options": [
            ("Descer ao corredor", "corredor"),
        ],
    },
    "sotao": {
        "title": "O sótão",
        "image": "/assets/imagens/sotao.jpg",
        "video": "/assets/videos/cena_sotao.mp4",
        "video_autoplay": True,
        "text": (
            "O fósforo acende. Há um gravador e uma vela branca.\n\n"
            "A fita é a sua voz de criança prometendo deixar alguém no lugar.\n"
            "A vela é o que a mãe queria que você usasse para libertar o eco."
        ),
        "options": [
            ("Ouvir a fita (prova)", "ouvir_fita"),
            ("Pegar a vela (ritual)", "pegar_vela"),
            ("Descer ao corredor", "corredor"),
        ],
    },
    "sotao_pista": {
        "title": "O sótão — a prova",
        "image": "/assets/imagens/sotao.jpg",
        "video": "/assets/videos/cena_sotao.mp4",
        "video_autoplay": True,
        "text": (
            "Você já ouviu a fita. Sabe o que prometeu.\n\n"
            "Pode descer ao espelho, pegar a vela se ainda não pegou, "
            "ou continuar procurando a foto no porão."
        ),
        "options": [
            ("Ouvir a fita de novo", "ouvir_fita"),
            ("Pegar a vela", "pegar_vela"),
            ("Ir ao espelho", "ir_espelho"),
            ("Descer ao corredor", "corredor"),
        ],
    },
    "fita_memoria": {
        "title": "A promessa",
        "image": "/assets/imagens/fita.jpg",
        "video": "/assets/videos/cena_fita.mp4",
        "video_autoplay": True,
        "text": (
            "Sua voz de criança:\n"
            "\"Quando eu crescer, vou deixar alguém no meu lugar. "
            "Pra casa não ficar sozinha.\"\n\n"
            "Foi isso. Você prometeu. O eco nasceu dessa frase.\n\n"
            "Com a fita, no espelho você pode dizer a verdade. "
            "Para o ritual, ainda precisa da vela, dos fósforos e do nome Casinha."
        ),
        "options": [
            ("Continuar no sótão", "voltar_sotao"),
            ("Descer ao corredor", "corredor"),
        ],
    },
    "item_vela": {
        "title": "A vela",
        "image": "/assets/imagens/sotao.jpg",
        "video": "/assets/videos/cena_sotao.mp4",
        "video_autoplay": True,
        "text": (
            "A vela cheira a fumaça recente. Alguém — o eco, ou a memória da mãe — "
            "já tentou o ritual.\n\n"
            "Com fósforos, fita e o apelido Casinha, ela liberta. Sem isso, não acenda no espelho."
        ),
        "options": [
            ("Continuar no sótão", "voltar_sotao"),
            ("Descer ao corredor", "corredor"),
        ],
    },
    "porta_trancada": {
        "title": "Porão trancado",
        "image": "/assets/imagens/porta_falha.jpg",
        "video": "/assets/videos/cena_porta.mp4",
        "video_autoplay": True,
        "sfx": "porta",
        "text": (
            "A porta do porão pede a chave da sala.\n\n"
            "Forçar é perigoso: o eco empurra do outro lado."
        ),
        "options": [
            ("Forçar a porta", "forcar_porao"),
            ("Voltar buscar a chave", "corredor"),
        ],
    },
    "porta_falha": {
        "title": "A porta reage",
        "image": "/assets/imagens/porta_falha.jpg",
        "video": "/assets/videos/cena_porta.mp4",
        "video_autoplay": True,
        "sfx": "porta",
        "text": (
            "Você empurra. Algo empurra de volta no mesmo ritmo. Uma lasca corta a palma.\n\n"
            "Você perdeu uma vida. Pegue a chave na sala."
        ),
        "options": [
            ("Voltar ao corredor", "corredor"),
        ],
    },
    "porao_escuro": {
        "title": "Porão sem luz",
        "image": "/assets/imagens/porao.jpg",
        "video": "/assets/videos/cena_porao.mp4",
        "video_autoplay": True,
        "text": (
            "Sem fósforos o chão some. Você tropeça. O joelho bate no concreto.\n\n"
            "Você perdeu uma vida. Há um pano sobre um espelho, mas você não ousa puxar no escuro.\n\n"
            "Suba, pegue fósforos na cozinha, desça de novo."
        ),
        "options": [
            ("Subir ao corredor", "corredor"),
        ],
    },
    "porao": {
        "title": "O porão",
        "image": "/assets/imagens/porao.jpg",
        "video": "/assets/videos/cena_porao.mp4",
        "video_autoplay": True,
        "text": (
            "Nas paredes: o seu nome, e abaixo: ELE FICOU.\n\n"
            "No chão, uma foto rasgada — você criança, e atrás uma sombra com o mesmo sorriso.\n\n"
            "No fundo, o espelho coberto. É aqui que o eco espera. "
            "Se chegar sem fita nem foto, ele te puxa."
        ),
        "options": [
            ("Pegar a foto (prova)", "pegar_foto"),
            ("Puxar o pano do espelho", "ir_espelho"),
            ("Subir ao corredor", "corredor"),
        ],
    },
    "item_foto": {
        "title": "A foto rasgada",
        "image": "/assets/imagens/porao.jpg",
        "video": "/assets/videos/cena_porao.mp4",
        "video_autoplay": True,
        "text": (
            "Você no jardim, sorrindo. Atrás, o eco — mesmo sorriso, um passo atrasado.\n\n"
            "Junto com a fita, esta foto prova que você deixou alguém. "
            "No espelho, isso vira a verdade: ele não é você, é o que ficou."
        ),
        "options": [
            ("Puxar o pano do espelho", "ir_espelho"),
            ("Subir ao corredor", "corredor"),
        ],
    },
    "dialogo_eco": {
        "title": "O eco fala",
        "image": "/assets/imagens/dialogo_eco.jpg",
        "video": "/assets/videos/cena_espelho.mp4",
        "video_autoplay": True,
        "audio": "/assets/audios/trilha_espelho.mp3",
        "text": (
            "Do outro lado do vidro, o seu rosto atrasado pergunta:\n"
            "\"Você veio me buscar… ou veio se despedir?\"\n\n"
            "Ele é a criança que você abandonou na promessa. "
            "A resposta não fecha o jogo — só muda o peso do confronto."
        ),
        "options": [
            ("\"Vim me lembrar de quem eu sou\"", "eco_lembrar"),
            ("\"Vim acabar com isso\"", "eco_acabar"),
            ("\"Vim te ouvir\"", "eco_ouvir"),
            ("Ficar em silêncio", "eco_silencio"),
        ],
    },
    "espelho": {
        "title": "O confronto",
        "image": "/assets/imagens/espelho.jpg",
        "video": "/assets/videos/cena_espelho.mp4",
        "video_autoplay": True,
        "audio": "/assets/audios/trilha_espelho.mp3",
        "text": (
            "O eco — o menino que você deixou — sorri com o seu sorriso.\n"
            "\"Eu esperei doze anos. A casa estava com saudade.\"\n\n"
            "Escolha o que fazer:\n"
            "• Fugir — você sai vivo; o eco continua na casa. Precisa da chave.\n"
            "• Dizer a verdade — você prova que ele não é você (fita + foto) "
            "e o eco some.\n"
            "• Trocar de lugar — você aceita ficar no espelho; o eco sai "
            "vivendo a sua vida.\n"
            "• Ritual — liberta o menino em paz "
            "(vela + fósforos + fita + o nome Casinha)."
        ),
        "options": [
            ("Fugir (precisa da chave)", "escolher_fuga"),
            ("Dizer a verdade (fita + foto)", "escolher_verdade"),
            ("Trocar de lugar com o eco", "fim_eco"),
            ("Ritual (vela+fósforo+fita+Casinha)", "escolher_ritual"),
        ],
    },
    "espelho_sem_pista": {
        "title": "FINAL — SEM PROVA",
        "image": "/assets/imagens/espelho.jpg",
        "video": "/assets/videos/cena_espelho.mp4",
        "video_autoplay": True,
        "audio": "/assets/audios/trilha_espelho.mp3",
        "text": (
            "Você puxou o pano do espelho sem saber quem era o eco.\n\n"
            "Sem a fita e sem a foto, você não tem como provar a diferença "
            "entre você e ele. Para a casa, os dois são a mesma pessoa.\n\n"
            "Mãos iguais às suas atravessam o vidro e puxam você para dentro.\n\n"
            "Resultado: você e o eco viram um só. Ninguém sai. "
            "A casa fica com os dois."
        ),
        "options": [],
    },
    "fuga_falha": {
        "title": "FINAL — FUGA FALHOU",
        "image": "/assets/imagens/corredor.jpg",
        "video": "/assets/videos/cena_corredor.mp4",
        "video_autoplay": True,
        "text": (
            "Você tentou fugir sem a chave. A porta da frente não abre.\n\n"
            "Enquanto você puxa a maçaneta, o eco chega atrasado, "
            "põe a mão no seu ombro e empurra você de volta para dentro.\n\n"
            "Ele passa por você, abre a porta (a casa deixa o eco sair) "
            "e vai embora com o seu rosto.\n\n"
            "Resultado: o eco vive a sua vida lá fora. Você fica preso na casa."
        ),
        "options": [],
    },
    "verdade_falha": {
        "title": "A frase sem prova",
        "image": "/assets/imagens/espelho.jpg",
        "video": "/assets/videos/cena_espelho.mp4",
        "video_autoplay": True,
        "text": (
            "Você grita: \"Você não é eu!\"\n\n"
            "Mas sem a fita (sótão) e a foto (porão), o eco ri: "
            "a casa não acredita só em palavras. O espelho não quebra.\n\n"
            "Ainda dá para voltar, pegar as provas e tentar de novo."
        ),
        "options": [
            ("Continuar o confronto", "espelho"),
            ("Subir buscar provas", "corredor"),
        ],
    },
    "ritual_falha": {
        "title": "O ritual incompleto",
        "image": "/assets/imagens/espelho.jpg",
        "video": "/assets/videos/cena_espelho.mp4",
        "video_autoplay": True,
        "text": (
            "O ritual não completa. Falta pelo menos uma peça:\n"
            "vela (sótão), fósforos (cozinha), fita (sótão) "
            "ou o apelido Casinha (jardim ou bilhete da mãe).\n\n"
            "O eco espera. Você pode escolher outro final agora, "
            "ou sair e juntar o que falta."
        ),
        "options": [
            ("Enfrentar de outro modo", "espelho"),
        ],
    },
    "fim_fuga": {
        "title": "FINAL — FUGA",
        "image": "/assets/imagens/fim_fuga.jpg",
        "video": "/assets/videos/cena_fim_fuga.mp4",
        "video_autoplay": True,
        "audio": "/assets/audios/trilha_casa.mp3",
        "text": (
            "Você usa a chave, abre a porta da frente e corre para a rua.\n\n"
            "Você escapou com vida. Mas não enfrentou o eco.\n\n"
            "Olhando para trás: a luz do seu quarto acende. "
            "O eco continua lá dentro, andando no seu ritmo, "
            "meio segundo atrasado — a casa não ficou sozinha.\n\n"
            "Resultado: você livre. O eco preso na casa. A promessa continua."
        ),
        "options": [],
    },
    "fim_verdade": {
        "title": "FINAL — VERDADE",
        "image": "/assets/imagens/fim_verdade.jpg",
        "video": "/assets/videos/cena_fim_verdade.mp4",
        "video_autoplay": True,
        "audio": "/assets/audios/trilha_amanhecer.mp3",
        "text": (
            "Você mostra a fita e a foto ao eco.\n"
            "\"Você não é eu. Você é o que eu deixei quando fui embora.\"\n\n"
            "Com as provas, a casa aceita a verdade. "
            "O espelho quebra. O eco some — a promessa se desfaz.\n\n"
            "De manhã a casa está vazia de verdade. Só você sobrou, "
            "no tempo certo, sem cópia atrasada.\n\n"
            "Resultado: o eco acaba. Você sai livre. A casa para de responder."
        ),
        "options": [],
    },
    "fim_eco": {
        "title": "FINAL — A TROCA",
        "image": "/assets/imagens/fim_eco.jpg",
        "video": "/assets/videos/cena_fim_eco.mp4",
        "video_autoplay": True,
        "stop_audio": True,
        "text": (
            "Você aceita trocar de lugar com o eco.\n\n"
            "Encosta a mão no vidro. Ele encosta a dele. "
            "Vocês trocam: o eco sai do espelho com o seu corpo adulto "
            "e sobe as escadas. Você fica do lado de dentro — "
            "no porão, atrasado, no lugar dele.\n\n"
            "Lá fora, o eco abre a porta da frente e vai viver a sua vida "
            "(trabalho, rua, gente) como se fosse você.\n\n"
            "Resultado: o eco fica livre no mundo. Você fica preso na casa. "
            "A promessa de \"deixar alguém no lugar\" se cumpriu — "
            "só que o alguém agora é você."
        ),
        "options": [],
    },
    "fim_ritual": {
        "title": "FINAL — LIBERTAÇÃO",
        "image": "/assets/imagens/fim_ritual.jpg",
        "video": "/assets/videos/cena_fim_ritual.mp4",
        "video_autoplay": True,
        "audio": "/assets/audios/trilha_amanhecer.mp3",
        "text": (
            "Você acende a vela com o fósforo, põe a fita perto do espelho "
            "e diz o nome certo: Casinha.\n\n"
            "A chama mostra o eco como ele é: um menino com medo "
            "de a casa ficar sozinha — não um monstro.\n\n"
            "Você apaga a vela. Ele some em paz (despedido, não destruído). "
            "A fita queima no quintal. A casa, pela primeira vez em doze anos, "
            "fica em silêncio.\n\n"
            "Resultado: o eco é libertado. Você pode ir embora "
            "sem deixar ninguém no seu lugar. Melhor final."
        ),
        "options": [],
    },
    "fim_ruim": {
        "title": "FINAL — MORTE",
        "image": "/assets/imagens/fim_morte.jpg",
        "video": "/assets/videos/cena_fim_morte.mp4",
        "video_autoplay": True,
        "stop_audio": True,
        "text": (
            "Suas três vidas acabaram. Você errou demais "
            "(escuro sem fósforos, porta, eco, enigma…).\n\n"
            "A casa não deixa você sair. Os passos do eco "
            "sincronizam com os seus até não dar mais para saber "
            "quem é o original.\n\n"
            "Resultado: você morre para o mundo de fora. "
            "A casa fica com o que sobrou de você e do eco — um só morador."
        ),
        "options": [],
    },
}


# ---------------------------------------------------------------------------
# REGRAS / AÇÕES — o que cada clique faz (itens, flags, cena seguinte)
# ---------------------------------------------------------------------------

def executar_acao(acao):
    """Aplica a regra da ação escolhida. Contagem de ações fica no bridge JS."""
    flags = state["flags"]

    def conhece_casinha():
        # Só pelo jardim ou pelo bilhete da mãe — o enigma não "ensina" o nome.
        return (
            flags["achou_pedra"]
            or flags["leu_pais"]
            or possui_item("pedra do jardim")
        )

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
        if not (flags["leu_pais"] or flags["achou_pedra"] or flags["ouviu_fita"]):
            mostrar_cena("enigma_cego")
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
            _finalizar("espelho_sem_pista")
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
        if possui_item("chave enferrujada"):
            _finalizar("fim_fuga", 20)
        else:
            _finalizar("fuga_falha")
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
            # Falha recuperável: não encerra a partida
            mostrar_cena("verdade_falha")
        return

    if acao == "escolher_ritual":
        base_ok = (
            possui_item("vela")
            and possui_item("fósforos")
            and (flags["ouviu_fita"] or possui_item("fita cassete"))
            and conhece_casinha()
        )
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
    Conta ações só para ranking. Sem limite de tempo:
    a partida acaba no final escolhido ou quando a vida chega a zero.
    """
    acao = str(acao).strip() if acao is not None else ""
    if not acao or acao == "None" or acao == "undefined":
        return

    # Partida já encerrada: ignora cliques / chamadas extras
    if _eh_final(state.get("cena_atual")):
        return

    state["acoes"] = state.get("acoes", 0) + 1
    atualizar_status()

    executar_acao(acao)

    cena = state.get("cena_atual")
    if not _eh_final(cena):
        salvar_jogo()


# ---------------------------------------------------------------------------
# BOOT DA INTERFACE
# ---------------------------------------------------------------------------

def configurar_interface():
    """Preenche a tela inicial e liga o Python ao JavaScript dos botões."""
    document.querySelector("#boot-title").innerText = CONFIG["titulo"]
    document.querySelector("#boot-sub").innerText = CONFIG.get("subtitulo", "")
    boot_author = document.querySelector("#boot-author")
    if boot_author is not None:
        boot_author.innerText = ""
    document.querySelector("#boot-icon").innerText = CONFIG.get("icone", "")
    document.querySelector("#titulo-jogo").innerText = CONFIG["titulo"]
    autor_el = document.querySelector("#autor-jogo")
    if autor_el is not None:
        autor_el.innerText = ""

    # Capa de boot agora é CSS full-bleed (#boot-bg); só atualiza se o elemento existir
    cover = document.querySelector("#boot-cover")
    capa = CONFIG.get("capa")
    if cover is not None and capa:
        cover.src = capa
        cover.classList.remove("hidden")

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
