"""
A Casa que Lembra — PyScript GameJam V2
Terror narrativo interativo (botões, sem input/terminal).
"""

from pyscript import document, window

try:
    from pyodide.ffi import create_proxy
except ImportError:
    def create_proxy(fn):
        return fn

# ---------------------------------------------------------------------------
# CONFIG
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
}

# ---------------------------------------------------------------------------
# STATE
# ---------------------------------------------------------------------------

state = {
    "vida": CONFIG["vida_inicial"],
    "pontos": CONFIG["pontos_iniciais"],
    "inventario": [],
    "cena_atual": None,
    "flags": {
        "ouviu_fita": False,
        "viu_foto": False,
        "viu_tv": False,
        "leu_bilhete": False,
        "abriu_porao": False,
        "conheceu_eco": False,
    },
}


def _estado_inicial():
    return {
        "vida": CONFIG["vida_inicial"],
        "pontos": CONFIG["pontos_iniciais"],
        "inventario": [],
        "cena_atual": None,
        "flags": {
            "ouviu_fita": False,
            "viu_foto": False,
            "viu_tv": False,
            "leu_bilhete": False,
            "abriu_porao": False,
            "conheceu_eco": False,
        },
    }


# ---------------------------------------------------------------------------
# HELPERS DO FRAMEWORK
# ---------------------------------------------------------------------------

def atualizar_status():
    document.querySelector("#stat-vida").innerText = str(state["vida"])
    document.querySelector("#stat-pontos").innerText = str(state["pontos"])
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


def perder_vida(n=1):
    state["vida"] -= n
    if state["vida"] < 0:
        state["vida"] = 0
    atualizar_status()
    if state["vida"] <= 0:
        mostrar_cena("fim_ruim")
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


def mostrar_cena(nome):
    if nome not in SCENES:
        window.console.error(f"Cena desconhecida: {nome}")
        return

    cena = SCENES[nome]
    state["cena_atual"] = nome
    atualizar_status()

    document.querySelector("#cena-titulo").innerText = cena.get("title", "")
    document.querySelector("#cena-texto").innerText = cena.get("text", "")

    img = document.querySelector("#cena-imagem")
    vid = document.querySelector("#cena-video")

    if cena.get("video"):
        img.classList.add("hidden")
        vid.classList.remove("hidden")
        vid.src = cena["video"]
        if cena.get("video_autoplay"):
            try:
                vid.play()
            except Exception:
                pass
        else:
            try:
                vid.pause()
            except Exception:
                pass
    else:
        vid.classList.add("hidden")
        try:
            vid.pause()
        except Exception:
            pass
        vid.removeAttribute("src")
        img.classList.remove("hidden")
        img.src = cena.get("image") or CONFIG.get("capa") or ""

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


def reiniciar_aventura(event=None):
    global state
    state = _estado_inicial()
    atualizar_status()
    if CONFIG.get("trilha_inicial"):
        trocar_audio(CONFIG["trilha_inicial"])
    mostrar_cena(CONFIG["cena_inicial"])


def iniciar_jogo(event=None):
    document.querySelector("#boot").classList.add("hidden")
    document.querySelector("#app").classList.add("visible")
    reiniciar_aventura()


def ao_clicar_opcao(event):
    btn = event.currentTarget
    acao = btn.getAttribute("data-acao")
    if not acao:
        return
    executar_acao(acao)


# ---------------------------------------------------------------------------
# SCENES — A Casa que Lembra
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
        "text": (
            "O corredor é estreito demais para uma casa. "
            "As paredes parecem ter se aproximado com os anos.\n\n"
            "Uma lâmpada amarela treme no teto. Longe, passos imitam os seus "
            "com meio segundo de atraso — clic… clic.\n\n"
            "À esquerda: a cozinha. À direita: a sala.\n"
            "No fundo, escadas sobem ao sótão e descem ao porão."
        ),
        "options": [
            ("Ir à cozinha", "cozinha"),
            ("Ir à sala", "sala"),
            ("Usar as escadas", "escadas"),
            ("Chamar quem está aí", "chamar_eco"),
        ],
    },
    "escadas": {
        "title": "As escadas",
        "image": "assets/imagens/corredor.jpg",
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
            "Na estante, uma gaveta entreaberta."
        ),
        "options": [
            ("Abrir a gaveta da estante", "pegar_chave"),
            ("Examinar a TV", "examinar_tv"),
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
            "Na estante, a gaveta ainda espera. "
            "E o rosto na estática parece puxar você para o espelho."
        ),
        "options": [
            ("Abrir a gaveta", "pegar_chave"),
            ("Examinar a TV", "examinar_tv"),
            ("Seguir o rosto (espelho)", "ir_espelho"),
            ("Voltar ao corredor", "corredor"),
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
            "Você diz o apelido da casa — o que o bilhete escondia.\n"
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
}


# ---------------------------------------------------------------------------
# REGRAS / AÇÕES
# ---------------------------------------------------------------------------

def executar_acao(acao):
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

    if acao == "escadas":
        mostrar_cena("escadas")
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
            mostrar_cena("fim_ruim")
            return
        flags["conheceu_eco"] = True
        mostrar_cena("espelho")
        return

    if acao == "escolher_fuga":
        if possui_item("chave enferrujada") or possui_item("fósforos"):
            ganhar_pontos(20)
            mostrar_cena("fim_fuga")
        else:
            mostrar_cena("fim_ruim")
        return

    if acao == "escolher_verdade":
        tem_fita = flags["ouviu_fita"] or possui_item("fita cassete")
        tem_foto = flags["viu_foto"] or possui_item("foto rasgada")
        if tem_fita and tem_foto:
            ganhar_pontos(40)
            mostrar_cena("fim_verdade")
        else:
            mostrar_cena("fim_ruim")
        return

    if acao == "escolher_ritual":
        if (
            possui_item("vela")
            and possui_item("fósforos")
            and (flags["ouviu_fita"] or possui_item("fita cassete"))
        ):
            ganhar_pontos(60)
            mostrar_cena("fim_ritual")
        else:
            mostrar_cena("ritual_falha")
        return

    if acao == "fim_eco":
        ganhar_pontos(10)
        mostrar_cena("fim_eco")
        return

    if acao in SCENES:
        mostrar_cena(acao)
        return

    window.console.warn(f"Ação sem tratamento: {acao}")


# ---------------------------------------------------------------------------
# BOOT DA INTERFACE
# ---------------------------------------------------------------------------

def configurar_interface():
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

    # Expõe funções para o JavaScript da página (cliques reais no mouse)
    window.iniciar_jogo = create_proxy(iniciar_jogo)
    window.reiniciar_aventura = create_proxy(reiniciar_aventura)
    window.executar_acao_js = create_proxy(executar_acao)

    document.querySelector("#loading").classList.add("hidden")
    document.querySelector("#btn-iniciar").disabled = False
    document.querySelector("#btn-iniciar").innerText = "▶ INICIAR JOGO"


configurar_interface()
