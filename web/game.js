/* A Casa que Lembra — engine web 8-bit */

const MAX_TURNOS = 15;

const SCENE_ART = {
  inicio: "art/house-night.png",
  corredor: "art/hallway.png",
  cozinha: "art/hallway.png",
  sala: "art/hallway.png",
  sotao: "art/house-night.png",
  porao: "art/mirror-echo.png",
  espelho: "art/mirror-echo.png",
  fim_fuga: "art/house-night.png",
  fim_verdade: "art/mirror-echo.png",
  fim_eco: "art/mirror-echo.png",
  fim_ritual: "art/house-night.png",
  fim_morte: "art/hallway.png",
  fim_atrasado: "art/house-night.png",
};

const SCENE_LABEL = {
  inicio: "QUARTO",
  corredor: "CORREDOR",
  cozinha: "COZINHA",
  sala: "SALA",
  sotao: "SOTAO",
  porao: "PORAO",
  espelho: "ESPELHO",
  fim_fuga: "RUA",
  fim_verdade: "AMANHECER",
  fim_eco: "ESPELHO",
  fim_ritual: "QUINTAL",
  fim_morte: "ESCURIDAO",
  fim_atrasado: "QUARTO",
};

let choiceResolver = null;

function estadoInicial() {
  return {
    vida: 3,
    inv: [],
    turnos: 0,
    ouviu_fita: false,
    viu_foto: false,
    abriu_porao: false,
    apagou_vela: false,
    conheceu_eco: false,
    leu_bilhete: false,
    viu_tv: false,
    forcou_porao: false,
  };
}

let state = estadoInicial();

const el = {
  log: document.getElementById("log"),
  choices: document.getElementById("choices"),
  inv: document.getElementById("inv"),
  vida: document.getElementById("stat-vida"),
  turnos: document.getElementById("stat-turnos"),
  sceneImg: document.getElementById("scene-img"),
  stageArt: document.getElementById("stage-art"),
  sceneLoc: document.getElementById("scene-loc"),
  boot: document.getElementById("boot"),
  bootBar: document.getElementById("boot-bar"),
  bootLine: document.getElementById("boot-line"),
  btnStart: document.getElementById("btn-start"),
};

function pegar(item) {
  if (!state.inv.includes(item)) state.inv.push(item);
}

function tem(item) {
  return state.inv.includes(item);
}

function perderVida(n = 1) {
  state.vida -= n;
  return state.vida <= 0;
}

function atualizarHud() {
  const hearts = "♥".repeat(Math.max(0, state.vida)) + "♡".repeat(Math.max(0, 3 - state.vida));
  el.vida.textContent = hearts || "—";
  el.vida.setAttribute("aria-label", `${state.vida} de vida`);
  el.turnos.textContent = `${state.turnos}/${MAX_TURNOS}`;
  el.inv.textContent = state.inv.length ? state.inv.join(", ") : "nada";
}

function setArt(cena) {
  const src = SCENE_ART[cena] || SCENE_ART.inicio;
  if (el.sceneImg.getAttribute("src") !== src) {
    el.sceneImg.src = src;
  }
  if (el.stageArt) el.stageArt.dataset.scene = cena;
  if (el.sceneLoc) el.sceneLoc.textContent = SCENE_LABEL[cena] || cena.toUpperCase();
}

function narrar(paragrafos, cls) {
  for (const p of paragrafos) {
    const node = document.createElement("p");
    if (cls) node.className = cls;
    node.textContent = p;
    el.log.appendChild(node);
  }
  el.log.scrollTop = el.log.scrollHeight;
}

function limparLog() {
  el.log.innerHTML = "";
}

function limparEscolhas() {
  choiceResolver = null;
  el.choices.innerHTML = "";
}

function escolher(opcoes) {
  return new Promise((resolve) => {
    limparEscolhas();
    choiceResolver = null;

    const finish = (value) => {
      choiceResolver = null;
      state.turnos += 1;
      atualizarHud();
      limparEscolhas();
      resolve(value);
    };

    opcoes.forEach((opt, index) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "choice-btn";
      btn.dataset.key = String(index + 1);
      btn.textContent = opt.label;
      btn.addEventListener("click", () => finish(opt.value));
      el.choices.appendChild(btn);
    });

    const hint = document.createElement("p");
    hint.className = "hint-keys";
    hint.textContent = "TECLAS 1-9 TAMBEM FUNCIONAM";
    el.choices.appendChild(hint);

    choiceResolver = (key) => {
      const i = Number(key) - 1;
      if (i >= 0 && i < opcoes.length) finish(opcoes[i].value);
    };
  });
}

document.addEventListener("keydown", (e) => {
  if (!choiceResolver) return;
  if (e.key >= "1" && e.key <= "9") {
    e.preventDefault();
    choiceResolver(e.key);
  }
});

const FINAIS = new Set([
  "fim_fuga",
  "fim_verdade",
  "fim_eco",
  "fim_ritual",
  "fim_morte",
  "fim_atrasado",
]);

async function cenaInicio() {
  setArt("inicio");
  limparLog();
  narrar([
    "Você acorda suando frio.",
    "O papel de parede floral está descascado nas bordas, como se alguém tivesse arrancado pétalas com as unhas. O colchão cheira a mofo e a sabão em pó antigo — o mesmo cheiro da sua infância.",
    "No espelho rachado do guarda-roupa, o reflexo pisca um segundo depois de você. Só um segundo. Mas o bastante para o estômago apertar.",
    "Na mesinha de cabeceira, um bilhete na sua letra:",
    '"Não abra a porta se ela já estiver aberta."',
    "A porta do quarto já está aberta. Além dela, o corredor respira uma luz amarela fraca.",
  ]);
  const op = await escolher([
    { value: "1", label: "1) Levantar e ir ao corredor" },
    { value: "2", label: "2) Olhar o bilhete de novo" },
  ]);
  if (op === "2") {
    state.leu_bilhete = true;
    narrar(
      [
        "Você pega o bilhete. O papel está úmido, como se tivesse acabado de ser escrito. No verso, em letra menor, trêmula:",
        '"Ela conta até quinze. Depois, a casa escolhe por você."',
        "O reflexo no espelho rachado agora está imóvel — demais. Você larga o bilhete e atravessa a porta.",
      ],
      "flavor",
    );
  } else {
    narrar(
      [
        "Você se levanta. O piso range sob o pé esquerdo, depois — meio segundo depois — range de novo, sozinho. Você atravessa a porta aberta.",
      ],
      "flavor",
    );
  }
  return "corredor";
}

async function cenaCorredor() {
  if (state.vida <= 0) return "fim_morte";
  setArt("corredor");
  limparLog();
  narrar([
    "O corredor é estreito demais para uma casa. As paredes parecem ter se aproximado com os anos.",
    "Uma lâmpada amarela treme no teto. Longe, passos imitam os seus com meio segundo de atraso — clic… clic.",
    "À esquerda: a cozinha. À direita: a sala. No fundo, uma escada sobe para o sótão e desce para o porão.",
  ]);
  const op = await escolher([
    { value: "1", label: "1) Cozinha" },
    { value: "2", label: "2) Sala" },
    { value: "3", label: "3) Sótão" },
    { value: "4", label: "4) Porão" },
    { value: "5", label: "5) Chamar quem está aí" },
  ]);
  if (op === "1") return "cozinha";
  if (op === "2") return "sala";
  if (op === "3") return "sotao";
  if (op === "4") return tentarPorao();
  return chamar();
}

async function tentarPorao() {
  if (tem("chave_enferrujada")) {
    if (!state.abriu_porao) {
      state.abriu_porao = true;
      narrar(
        [
          "A chave enferrujada gira com um queixume metálico. O ar que sobe do porão é úmido, doce e podre — como fruta esquecida no escuro.",
        ],
        "item",
      );
    }
    return "porao";
  }
  narrar([
    "A porta do porão está trancada. A fechadura é antiga, coberta de ferrugem em forma de unha.",
  ]);
  const op = await escolher([
    { value: "1", label: "1) Forçar a porta" },
    { value: "2", label: "2) Desistir e voltar" },
  ]);
  if (op === "1") {
    state.forcou_porao = true;
    narrar(
      [
        "Você empurra com o ombro. A madeira geme, mas não cede. Algo do outro lado empurra de volta — no mesmo ritmo. Uma lasca corta sua palma.",
      ],
      "danger",
    );
    if (perderVida(1)) return "fim_morte";
    narrar(["Você recua, ofegante. O corredor espera."]);
    return "corredor";
  }
  narrar(["Você se afasta. Os passos atrasados continuam, pacientes."]);
  return "corredor";
}

async function chamar() {
  narrar(
    [
      'Você engole seco e grita: "Tem alguém aí?"',
      "O silêncio engorda. Então, do fundo do corredor, a sua própria voz responde — um pouco mais baixa, um pouco mais alegre:",
      '"Tem alguém aí?"',
      "Os passos atrasados aceleram. Algo frio roça sua nuca.",
    ],
    "danger",
  );
  state.conheceu_eco = true;
  if (perderVida(1)) return "fim_morte";
  narrar(["Quando você se vira, não há ninguém. Só a lâmpada tremendo mais forte."]);
  return "corredor";
}

async function cenaCozinha() {
  setArt("cozinha");
  limparLog();
  narrar([
    "A cozinha cheira a gás antigo e laranja podre.",
    "Na pia, um prato com comida ainda quente — arroz, feijão, um pedaço de carne. O vapor sobe em espirais lentas. Ninguém mora aqui há doze anos.",
    "Na parede acima da mesa, riscos profundos formam letras tortas: CONTANDO ATÉ QUINZE.",
  ]);
  if (tem("fosforos")) {
    narrar(["A gaveta da esquerda está aberta e vazia. Você já pegou os fósforos."]);
    await escolher([{ value: "1", label: "1) Voltar ao corredor" }]);
    return "corredor";
  }
  narrar([
    "Na gaveta da esquerda, uma caixa de fósforos. A etiqueta está apagada, mas você lembra da marca — a mesma que seu pai usava para acender o fogão.",
  ]);
  const op = await escolher([
    { value: "1", label: "1) Pegar os fósforos" },
    { value: "2", label: "2) Deixar e voltar ao corredor" },
    { value: "3", label: "3) Tocar a comida quente" },
  ]);
  if (op === "1") {
    pegar("fosforos");
    narrar(
      ["Você guarda os fósforos. A caixa é leve demais — quase vazia. Dentro, restam três palitos. Três chances."],
      "item",
    );
  } else if (op === "3") {
    narrar([
      "Você encosta o dedo no arroz. Escaldante. Quando retira a mão, a comida ainda fumega… e, por um instante, você vê uma segunda mão — a sua, mais nova — fazendo o mesmo gesto do outro lado do vapor.",
      "A visão some. O prato continua lá.",
    ]);
    const op2 = await escolher([
      { value: "1", label: "1) Pegar os fósforos agora" },
      { value: "2", label: "2) Voltar ao corredor sem eles" },
    ]);
    if (op2 === "1") {
      pegar("fosforos");
      narrar(["Você pega os fósforos. A caixa treme na sua mão."], "item");
    } else {
      narrar(["Você deixa a cozinha. O cheiro de laranja te segue."]);
    }
  } else {
    narrar(["Você fecha a gaveta sem pegar nada e volta."]);
  }
  return "corredor";
}

async function cenaSala() {
  setArt("sala");
  limparLog();
  narrar([
    "A sala está coberta. O sofá usa um lençol branco manchado de amarelo. Relógios parados. Poeira em camadas.",
    "A TV de tubo olha para você com a tela morta — um olho cinza, opaco.",
  ]);
  if (state.ouviu_fita) {
    narrar([
      "A TV liga sozinha. Estática. No meio do ruído branco, um rosto se forma — o seu, mais novo, sorrindo sem chegar aos olhos.",
    ]);
  }
  const opcoes = [
    { value: "1", label: "1) Abrir a gaveta da estante" },
    { value: "2", label: "2) Examinar a TV" },
    { value: "3", label: "3) Voltar ao corredor" },
  ];
  if (state.ouviu_fita && state.viu_foto) {
    opcoes.push({ value: "4", label: "4) Seguir o rosto na estática (para o espelho)" });
  }
  const op = await escolher(opcoes);
  if (op === "1") {
    if (tem("chave_enferrujada")) {
      narrar(["A gaveta está vazia. A chave já está com você."]);
    } else {
      narrar(
        [
          "A gaveta range. Dentro: uma chave enferrujada, quente ao toque, como se alguém a tivesse segurado agora há pouco. Na alça, um pedaço de fita isolante com a palavra PORÃO.",
        ],
        "item",
      );
      pegar("chave_enferrujada");
      narrar(["Você guarda a chave. Ela esfria na sua mão aos poucos."]);
    }
    return "sala";
  }
  if (op === "2") {
    state.viu_tv = true;
    if (state.ouviu_fita) {
      narrar([
        "Você se aproxima da tela. O rosto de criança abre a boca. Não sai som — sai um sopro frio pela fresta do painel. A estática sussurra:",
        '"Você deixou alguém no seu lugar."',
        "A coragem sobe na garganta como náusea. Agora você sabe: precisa ver o espelho de verdade.",
      ]);
    } else {
      narrar([
        "Você liga a TV. Só estática. No chiado, quase dá para ouvir alguém contar: um… dois… três… Você desliga antes de chegar a quinze.",
      ]);
    }
    return "sala";
  }
  if (op === "4") {
    narrar([
      "O rosto na estática inclina a cabeça. A tela estala. Você sente um puxão atrás dos olhos — e o mundo vira escuro úmido. Quando a visão volta, você está diante de um espelho coberto por um pano.",
    ]);
    return "espelho";
  }
  narrar(["Você deixa a sala. O lençol do sofá se mexe sem vento."]);
  return "corredor";
}

async function cenaSotao() {
  setArt("sotao");
  limparLog();
  narrar([
    "A escada range a cada degrau. O sótão cheira a poeira quente e a madeira velha. Caixas empilhadas. Um baú de brinquedos cobertos por lençol.",
  ]);
  if (!tem("fosforos")) {
    narrar(["Está escuro demais. Suas mãos encontram arestas, teias, algo macio que pode ser um casaco… ou não."]);
    const op = await escolher([
      { value: "1", label: "1) Insistir no escuro" },
      { value: "2", label: "2) Descer ao corredor" },
    ]);
    if (op === "2") {
      narrar(["Você desce. A escuridão do sótão parece aliviada."]);
      return "corredor";
    }
    narrar(
      [
        "Você avança. O pé encontra o vazio entre duas tábuas. Você cai de joelho. Algo — uma unha? um fio? — raspa seu tornozelo.",
      ],
      "danger",
    );
    if (perderVida(1)) return "fim_morte";
    narrar(["Você engatinha de volta à escada, o coração batendo atrasado, como os passos do corredor."]);
    return "corredor";
  }

  narrar([
    "Você risca um fósforo. A chama treme e revela o sótão em pedaços laranja: caixas, um gravador de fita cassete, uma vela branca sem usar.",
  ]);

  while (true) {
    const opcoes = [
      { value: "1", label: "1) Examinar o gravador / a fita" },
      {
        value: "2",
        label: tem("vela") ? "2) (Você já tem a vela)" : "2) Pegar a vela",
      },
      { value: "3", label: "3) Descer ao corredor" },
    ];
    if (state.ouviu_fita && (state.viu_foto || state.viu_tv)) {
      opcoes.push({ value: "4", label: "4) Seguir o eco da fita (para o espelho)" });
    }
    const op = await escolher(opcoes);
    if (op === "1") {
      if (!tem("fita_cassete")) {
        pegar("fita_cassete");
        narrar(
          ["Você puxa a fita do gravador. A etiqueta, na sua letra de criança: EU / OUTRO."],
          "item",
        );
      }
      narrar([
        "Você aperta play. Chiado. Então uma voz de criança — a sua — sussurra perto demais do microfone:",
        '"Quando eu crescer, vou deixar alguém no meu lugar."',
        "Pausa. Respiração. Depois, mais baixo:",
        '"Pra casa não ficar sozinha."',
        "A fita termina. O gravador continua quente.",
      ]);
      state.ouviu_fita = true;
      continue;
    }
    if (op === "2") {
      if (!tem("vela")) {
        pegar("vela");
        narrar(
          [
            "Você guarda a vela. A cera está fria, mas o pavio cheira a fumaça recente — como se alguém tivesse apagado agora.",
          ],
          "item",
        );
      } else {
        narrar(["A vela já está com você."]);
      }
      continue;
    }
    if (op === "4") {
      narrar([
        "A voz da criança na fita parece vir de baixo. Você segue o som escada abaixo, atravessa o corredor sem olhar, e desce ao porão — até um espelho coberto por pano.",
      ]);
      return "espelho";
    }
    narrar(["Você desce. O fósforo se apaga no último degrau."]);
    return "corredor";
  }
}

async function cenaPorao() {
  setArt("porao");
  limparLog();
  narrar([
    "O porão engole o som. Umidade cola na pele. Nas paredes, marcas de unha formam o seu nome — letra por letra, profundas demais para uma brincadeira.",
  ]);
  if (!tem("fosforos")) {
    narrar(["Sem luz, o chão some. Você tropeça numa caixa. O joelho bate no concreto."], "danger");
    if (perderVida(1)) return "fim_morte";
    narrar(["Você engatinha até a escada, guiado só pelo cheiro menos podre de cima."]);
    const op = await escolher([
      { value: "1", label: "1) Subir ao corredor" },
      { value: "2", label: "2) Tentar de novo no escuro" },
    ]);
    if (op === "1") return "corredor";
    narrar(
      [
        "Você insiste. Dedos encontram um pano grosso sobre algo liso — vidro. Um espelho. Sem luz, você não ousa puxar o pano.",
      ],
      "danger",
    );
    if (perderVida(1)) return "fim_morte";
    return "corredor";
  }

  narrar([
    "Você risca um fósforo. A chama mostra a inscrição completa nas paredes: o seu nome, repetido, e abaixo:",
    '"ELE FICOU."',
    "No chão, uma foto rasgada. No fundo, uma porta baixa coberta por um pano escuro — o formato de um espelho de corpo inteiro.",
  ]);

  while (true) {
    const op = await escolher([
      {
        value: "1",
        label: tem("foto_rasgada") ? "1) (Você já tem a foto)" : "1) Pegar a foto rasgada",
      },
      { value: "2", label: "2) Puxar o pano do espelho" },
      { value: "3", label: "3) Subir ao corredor" },
    ]);
    if (op === "1") {
      if (!tem("foto_rasgada")) {
        pegar("foto_rasgada");
        state.viu_foto = true;
        narrar(
          [
            "A foto mostra a casa intacta, ensolarada. No jardim, uma criança — você — sorri. Atrás dela, uma sombra com o mesmo sorriso, atrasada um passo. A borda da foto está queimada.",
          ],
          "item",
        );
      } else {
        narrar(["Você já guarda a foto. O sorriso da sombra não muda."]);
      }
      continue;
    }
    if (op === "2") {
      narrar([
        "Você puxa o pano. O tecido cai como pele morta. O espelho não mostra o porão — mostra o corredor de cima, vazio… e alguém com o seu rosto já te esperando do outro lado, sorrindo.",
      ]);
      state.conheceu_eco = true;
      return "espelho";
    }
    narrar(["Você sobe. O fósforo morre entre os dedos."]);
    return "corredor";
  }
}

async function cenaEspelho() {
  if (state.vida <= 0) return "fim_morte";
  setArt("espelho");
  limparLog();
  const temPista =
    state.ouviu_fita || state.viu_foto || tem("fita_cassete") || tem("foto_rasgada");
  if (!temPista) {
    narrar(
      [
        "O espelho te engole com a própria imagem. Sem lembrar por que veio, você só vê o sorriso atrasado. Mãos iguais às suas atravessam o vidro e puxam.",
      ],
      "danger",
    );
    return "fim_morte";
  }
  narrar([
    "O doppelgänger está do outro lado do vidro, sorrindo com o seu sorriso. Ele fala primeiro — com a sua voz, meio segundo atrasada:",
    '"Eu esperei doze anos. A casa estava com saudade."',
    "O ar cheira a chuva de infância e a ferrugem.",
  ]);
  state.conheceu_eco = true;
  const opcoes = [
    { value: "1", label: "1) Correr para a porta da frente" },
    { value: '2', label: '2) Confrontar: "Você não é eu"' },
    { value: "3", label: "3) Aceitar trocar de lugar" },
  ];
  if (tem("vela") && tem("fosforos") && (state.ouviu_fita || tem("fita_cassete"))) {
    opcoes.push({ value: "4", label: "4) Acender a vela e dizer o nome do bilhete" });
  }
  const op = await escolher(opcoes);
  if (op === "1") {
    if (tem("chave_enferrujada") || tem("fosforos")) return "fim_fuga";
    narrar(
      [
        "Você corre. Sem chave, sem luz. A porta da frente está trancada por dentro. Atrasado, o eco chega e põe a mão no seu ombro — a mesma mão.",
      ],
      "danger",
    );
    return "fim_morte";
  }
  if (op === "2") {
    if (
      (state.ouviu_fita || tem("fita_cassete")) &&
      (state.viu_foto || tem("foto_rasgada"))
    ) {
      return "fim_verdade";
    }
    narrar(
      [
        'Você grita: "Você não é eu!" O eco ri com a sua garganta. Sem a fita e a foto, a frase não tem peso. O vidro não quebra. Você quebra.',
      ],
      "danger",
    );
    return "fim_morte";
  }
  if (op === "3") return "fim_eco";
  if (tem("vela") && tem("fosforos") && (state.ouviu_fita || tem("fita_cassete"))) {
    state.apagou_vela = true;
    return "fim_ritual";
  }
  return "fim_morte";
}

function resumo(titulo) {
  const banner = document.createElement("div");
  banner.className = "ending-banner";
  banner.textContent = `FINAL: ${titulo}`;
  el.log.appendChild(banner);
  atualizarHud();
}

async function fimFuga() {
  setArt("fim_fuga");
  limparLog();
  narrar([
    "Você corre. A porta da frente cede — chave ou luz, não importa. A noite lá fora é real: vento, rua, o cheiro de asfalto molhado.",
    "Você olha para trás. A casa está quieta. Então, no seu antigo quarto, a luz acende sozinha.",
    "Alguém passa atrás da cortina com o seu jeito de andar. Meio segundo atrasado.",
    "Você escapou. Talvez.",
  ]);
  resumo("FUGA AMBÍGUA");
  return "fim";
}

async function fimVerdade() {
  setArt("fim_verdade");
  limparLog();
  narrar([
    'Você segura a foto e a memória da fita. "Você não é eu. Você é o que eu deixei."',
    "O sorriso do eco trinca. Você golpeia o espelho. O vidro soluça — um som úmido, humano — e estilhaça.",
    "A casa inteira respira fundo, como quem larga um segredo. Poeira sobe. A luz amarela morre.",
    "Quando amanhece, você está no jardim. A porta está fechada. Não há passos atrasados. Só o seu coração, no tempo certo.",
  ]);
  resumo("VERDADE");
  return "fim";
}

async function fimEco() {
  setArt("fim_eco");
  limparLog();
  narrar([
    "Você encosta a mão no vidro. O eco encosta a dele. O frio passa. O calor fica do outro lado.",
    "Você tenta recuar. Não há recuo. O porão — ou a sala, ou o quarto — agora é o lado de dentro do espelho.",
    "Do lado de fora, alguém com o seu rosto abre a porta da frente, inspira a noite e sorri no tempo certo.",
    "A casa não está mais sozinha. Você está.",
  ]);
  resumo("O ECO SAI");
  return "fim";
}

async function fimRitual() {
  setArt("fim_ritual");
  limparLog();
  narrar([
    "Você risca o fósforo. A vela acende. A chama mostra o eco como ele é: pequeno, assustado, uma criança que prometeu não deixar a casa vazia.",
    "Você diz o que o bilhete escondia — não um nome de pessoa, mas o nome da casa, o apelido que só vocês dois usavam quando era tarde demais para dormir.",
    "O eco encolhe. Vira menino de novo. A vela tremula. Você apaga com os dedos.",
    "De manhã, você tranca cada porta. No quintal, queima a fita. A fumaça sobe reta. A casa, pela primeira vez em doze anos, não responde.",
  ]);
  resumo("RITUAL — FINAL SECRETO");
  return "fim";
}

async function fimMorte() {
  setArt("fim_morte");
  limparLog();
  narrar(
    [
      "A escuridão fecha como uma boca.",
      "Os passos atrasados — clic… clic — param.",
      "Não porque foram embora.",
      "Porque agora estão sincronizados com os seus.",
      "A casa lembra. E você, enfim, também.",
    ],
    "danger",
  );
  resumo("MORTE");
  return "fim";
}

async function fimAtrasado() {
  setArt("fim_atrasado");
  limparLog();
  narrar([
    "Quinze. A casa completa a contagem por você.",
    "Do corredor vem a sua voz, paciente, quase carinhosa:",
    '"Não abra a porta se ela já estiver aberta."',
    "A porta do quarto — aquela que você deixou para trás — fecha por dentro. A chave gira sozinha.",
    "O eco completa a frase do bilhete no seu ouvido:",
    '"Agora eu abro."',
    "Não há mais escolhas. Só a casa, lembrando.",
  ]);
  resumo("ATRASADO DEMAIS");
  return "fim";
}

const CENAS = {
  inicio: cenaInicio,
  corredor: cenaCorredor,
  cozinha: cenaCozinha,
  sala: cenaSala,
  sotao: cenaSotao,
  porao: cenaPorao,
  espelho: cenaEspelho,
  fim_fuga: fimFuga,
  fim_verdade: fimVerdade,
  fim_eco: fimEco,
  fim_ritual: fimRitual,
  fim_morte: fimMorte,
  fim_atrasado: fimAtrasado,
};

async function loop() {
  let cena = "inicio";
  while (cena !== "fim") {
    atualizarHud();
    if (state.turnos >= MAX_TURNOS && !FINAIS.has(cena)) {
      cena = "fim_atrasado";
      continue;
    }
    const fn = CENAS[cena];
    if (!fn) break;
    cena = await fn();
  }
  limparEscolhas();
  const again = document.createElement("button");
  again.type = "button";
  again.className = "bit-btn";
  again.textContent = "▶ JOGAR DE NOVO";
  again.addEventListener("click", () => {
    state = estadoInicial();
    atualizarHud();
    limparLog();
    limparEscolhas();
    loop();
  });
  el.choices.appendChild(again);
}

function boot() {
  const lines = [
    "Sincronizando passos...",
    "O rastro esta vivo...",
    "Contando ate quinze...",
    "Pronto.",
  ];
  let i = 0;
  const tick = setInterval(() => {
    const pct = Math.min(100, ((i + 1) / lines.length) * 100);
    el.bootBar.style.width = `${pct}%`;
    el.bootLine.textContent = lines[i] || "Pronto.";
    i += 1;
    if (i >= lines.length) {
      clearInterval(tick);
      el.btnStart.hidden = false;
    }
  }, 450);

  el.btnStart.addEventListener("click", () => {
    el.boot.classList.add("is-done");
    loop();
  });
}

boot();
