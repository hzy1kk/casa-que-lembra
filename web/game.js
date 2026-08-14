/* A Casa que Lembra — engine web */

const MAX_TURNOS = 15;
const REDUCE_MOTION = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

const ITEM_NOME = {
  fosforos: "fósforos",
  chave_enferrujada: "chave enferrujada",
  fita_cassete: "fita cassete",
  vela: "vela",
  foto_rasgada: "foto rasgada",
};

const SCENE_ART = {
  inicio: "art/scene-inicio.jpg",
  corredor: "art/scene-corredor.jpg",
  cozinha: "art/scene-cozinha.jpg",
  sala: "art/scene-sala.jpg",
  sotao: "art/scene-sotao.jpg",
  porao: "art/scene-porao.jpg",
  espelho: "art/scene-espelho.jpg",
  fim_fuga: "art/scene-fim-fuga.jpg",
  fim_verdade: "art/scene-fim-verdade.jpg",
  fim_eco: "art/scene-fim-eco.jpg",
  fim_ritual: "art/scene-fim-ritual.jpg",
  fim_morte: "art/scene-fim-morte.jpg",
  fim_atrasado: "art/scene-fim-atrasado.jpg",
};

let currentSceneArt = SCENE_ART.inicio;

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
  vidaWrap: document.getElementById("stat-vida-wrap"),
  turnos: document.getElementById("stat-turnos"),
  turnBar: document.getElementById("turn-bar"),
  sceneImg: document.getElementById("scene-img"),
  stageArt: document.getElementById("stage-art"),
  sceneLoc: document.getElementById("scene-loc"),
  boot: document.getElementById("boot"),
  bootBar: document.getElementById("boot-bar"),
  bootLine: document.getElementById("boot-line"),
  btnStart: document.getElementById("btn-start"),
  btnMute: document.getElementById("btn-mute"),
  fade: document.getElementById("fx-fade"),
};

let skipType = false;
let typing = false;

function sleep(ms) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

function pegar(item) {
  if (!state.inv.includes(item)) {
    state.inv.push(item);
    if (window.AudioFx) AudioFx.item();
    atualizarHud();
  }
}

function tem(item) {
  return state.inv.includes(item);
}

function perderVida(n = 1) {
  state.vida -= n;
  document.body.classList.remove("is-hurt");
  void document.body.offsetWidth;
  document.body.classList.add("is-hurt");
  window.setTimeout(() => document.body.classList.remove("is-hurt"), 450);
  if (window.AudioFx) AudioFx.hurt();
  atualizarHud();
  return state.vida <= 0;
}

function atualizarHud() {
  const hearts = "♥".repeat(Math.max(0, state.vida)) + "♡".repeat(Math.max(0, 3 - state.vida));
  el.vida.textContent = hearts || "—";
  el.vida.setAttribute("aria-label", `${state.vida} de vida`);
  if (el.vidaWrap) el.vidaWrap.dataset.low = state.vida <= 1 ? "1" : "0";
  el.turnos.textContent = `${state.turnos}/${MAX_TURNOS}`;
  document.body.dataset.hp = String(Math.max(0, state.vida));
  if (el.turnBar) {
    el.turnBar.style.width = `${(state.turnos / MAX_TURNOS) * 100}%`;
    el.turnBar.parentElement.classList.toggle("is-late", state.turnos >= 12);
  }
  if (window.AudioFx) AudioFx.heartbeat(state.vida === 1);
  if (!el.inv) return;
  el.inv.innerHTML = "";
  if (!state.inv.length) {
    const empty = document.createElement("span");
    empty.className = "inv-empty";
    empty.textContent = "nada";
    el.inv.appendChild(empty);
    return;
  }
  state.inv.forEach((id) => {
    const chip = document.createElement("span");
    chip.className = "inv-chip";
    chip.textContent = ITEM_NOME[id] || id;
    el.inv.appendChild(chip);
  });
}

function showArt(src, cena) {
  if (el.sceneImg.getAttribute("src") !== src) {
    el.sceneImg.src = src;
  }
  if (cena && el.stageArt) el.stageArt.dataset.scene = cena;
  if (cena && el.sceneLoc) el.sceneLoc.textContent = SCENE_LABEL[cena] || cena.toUpperCase();
}

async function setArt(cena) {
  const src = SCENE_ART[cena] || SCENE_ART.inicio;
  const changed = currentSceneArt !== src || (el.stageArt && el.stageArt.dataset.scene !== cena);
  if (changed && el.stageArt) {
    el.stageArt.classList.add("is-fade");
    if (!REDUCE_MOTION) await sleep(160);
  }
  currentSceneArt = src;
  showArt(src, cena);
  document.body.dataset.scene = cena;
  const ending = typeof FINAIS !== "undefined" && FINAIS.has(cena);
  document.body.classList.toggle("is-ending", ending);
  if (ending) document.body.dataset.ending = cena.replace("fim_", "");
  else delete document.body.dataset.ending;
  if (el.stageArt) {
    el.stageArt.classList.remove("is-fade");
    el.stageArt.classList.remove("is-live");
    void el.stageArt.offsetWidth;
    el.stageArt.classList.add("is-live");
  }
  if (window.AudioFx) AudioFx.room(cena);
}

async function typeLine(node, text) {
  if (REDUCE_MOTION) {
    node.textContent = text;
    return;
  }
  node.textContent = "";
  for (let i = 0; i < text.length; i += 1) {
    if (skipType) {
      node.textContent = text;
      return;
    }
    node.textContent += text[i];
    el.log.scrollTop = el.log.scrollHeight;
    const ch = text[i];
    let wait = 17;
    if (ch === "," || ch === ";") wait = 55;
    if (ch === "." || ch === "!" || ch === "?" || ch === "…" || ch === "—") wait = 95;
    await sleep(wait);
  }
}

async function narrar(paragrafos, cls) {
  skipType = false;
  typing = true;
  const onSkip = (e) => {
    if (e.type === "keydown" && e.key >= "1" && e.key <= "9") return;
    skipType = true;
  };
  document.addEventListener("pointerdown", onSkip);
  document.addEventListener("keydown", onSkip);
  for (const p of paragrafos) {
    const node = document.createElement("p");
    if (cls) node.className = cls;
    el.log.appendChild(node);
    await typeLine(node, p);
  }
  document.removeEventListener("pointerdown", onSkip);
  document.removeEventListener("keydown", onSkip);
  typing = false;
  el.log.scrollTop = el.log.scrollHeight;
  if (cls === "danger" && window.AudioFx) AudioFx.stinger();
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

    const finish = (opt) => {
      choiceResolver = null;
      if (window.AudioFx) AudioFx.click();
      if (opt.art) showArt(opt.art);
      state.turnos += 1;
      atualizarHud();
      limparEscolhas();
      resolve(opt.value);
    };

    opcoes.forEach((opt, index) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "choice-btn";
      btn.dataset.key = String(index + 1);

      if (opt.art) {
        const img = document.createElement("img");
        img.src = opt.art;
        img.alt = "";
        img.className = "choice-btn__art";
        btn.appendChild(img);
      }

      const label = document.createElement("span");
      label.className = "choice-btn__label";
      label.textContent = opt.label;
      btn.appendChild(label);

      btn.addEventListener("click", () => finish(opt));
      btn.addEventListener("mouseenter", () => {
        if (opt.art) showArt(opt.art);
      });
      btn.addEventListener("focus", () => {
        if (opt.art) showArt(opt.art);
      });
      btn.addEventListener("mouseleave", () => {
        if (choiceResolver) showArt(currentSceneArt);
      });
      el.choices.appendChild(btn);
    });

    choiceResolver = (key) => {
      const i = Number(key) - 1;
      if (i >= 0 && i < opcoes.length) finish(opcoes[i]);
    };
  });
}

document.addEventListener("keydown", (e) => {
  if (typing) {
    if (e.key === " " || e.key === "Enter") e.preventDefault();
    return;
  }
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
  await setArt("inicio");
  limparLog();
  await narrar([
    "Você acorda suando frio.",
    "O papel de parede floral está descascado nas bordas, como se alguém tivesse arrancado pétalas com as unhas. O colchão cheira a mofo e a sabão em pó antigo — o mesmo cheiro da sua infância.",
    "No espelho rachado do guarda-roupa, o reflexo pisca um segundo depois de você. Só um segundo. Mas o bastante para o estômago apertar.",
    "Na mesinha de cabeceira, um bilhete na sua letra:",
    '"Não abra a porta se ela já estiver aberta."',
    "A porta do quarto já está aberta. Além dela, o corredor respira uma luz amarela fraca.",
  ]);
  const op = await escolher([
    { value: "1", label: "1) Levantar e ir ao corredor", art: "art/choice-inicio-1.jpg" },
    { value: "2", label: "2) Olhar o bilhete de novo", art: "art/choice-inicio-2.jpg" },
  ]);
  if (op === "2") {
    state.leu_bilhete = true;
    await narrar(
      [
        "Você pega o bilhete. O papel está úmido, como se tivesse acabado de ser escrito. No verso, em letra menor, trêmula:",
        '"Ela conta até quinze. Depois, a casa escolhe por você."',
        "O reflexo no espelho rachado agora está imóvel — demais. Você larga o bilhete e atravessa a porta.",
      ],
      "flavor",
    );
  } else {
    await narrar(
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
  await setArt("corredor");
  limparLog();
  await narrar([
    "O corredor é estreito demais para uma casa. As paredes parecem ter se aproximado com os anos.",
    "Uma lâmpada amarela treme no teto. Longe, passos imitam os seus com meio segundo de atraso — clic… clic.",
    "À esquerda: a cozinha. À direita: a sala. No fundo, uma escada sobe para o sótão e desce para o porão.",
  ]);
  const op = await escolher([
    { value: "1", label: "1) Cozinha", art: "art/choice-corredor-1.jpg" },
    { value: "2", label: "2) Sala", art: "art/choice-corredor-2.jpg" },
    { value: "3", label: "3) Sótão", art: "art/choice-corredor-3.jpg" },
    { value: "4", label: "4) Porão", art: "art/choice-corredor-4.jpg" },
    { value: "5", label: "5) Chamar quem está aí", art: "art/choice-corredor-5.jpg" },
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
      await narrar(
        [
          "A chave enferrujada gira com um queixume metálico. O ar que sobe do porão é úmido, doce e podre — como fruta esquecida no escuro.",
        ],
        "item",
      );
    }
    return "porao";
  }
  await narrar([
    "A porta do porão está trancada. A fechadura é antiga, coberta de ferrugem em forma de unha.",
  ]);
  const op = await escolher([
    { value: "1", label: "1) Forçar a porta", art: "art/choice-porao-forcar.jpg" },
    { value: "2", label: "2) Desistir e voltar", art: "art/choice-porao-desistir.jpg" },
  ]);
  if (op === "1") {
    state.forcou_porao = true;
    await narrar(
      [
        "Você empurra com o ombro. A madeira geme, mas não cede. Algo do outro lado empurra de volta — no mesmo ritmo. Uma lasca corta sua palma.",
      ],
      "danger",
    );
    if (perderVida(1)) return "fim_morte";
    await narrar(["Você recua, ofegante. O corredor espera."]);
    return "corredor";
  }
  await narrar(["Você se afasta. Os passos atrasados continuam, pacientes."]);
  return "corredor";
}

async function chamar() {
  await narrar(
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
  await narrar(["Quando você se vira, não há ninguém. Só a lâmpada tremendo mais forte."]);
  return "corredor";
}

async function cenaCozinha() {
  await setArt("cozinha");
  limparLog();
  await narrar([
    "A cozinha cheira a gás antigo e laranja podre.",
    "Na pia, um prato com comida ainda quente — arroz, feijão, um pedaço de carne. O vapor sobe em espirais lentas. Ninguém mora aqui há doze anos.",
    "Na parede acima da mesa, riscos profundos formam letras tortas: CONTANDO ATÉ QUINZE.",
  ]);
  if (tem("fosforos")) {
    await narrar(["A gaveta da esquerda está aberta e vazia. Você já pegou os fósforos."]);
    await escolher([{ value: "1", label: "1) Voltar ao corredor", art: "art/choice-cozinha-voltar.jpg" }]);
    return "corredor";
  }
  await narrar([
    "Na gaveta da esquerda, uma caixa de fósforos. A etiqueta está apagada, mas você lembra da marca — a mesma que seu pai usava para acender o fogão.",
  ]);
  const op = await escolher([
    { value: "1", label: "1) Pegar os fósforos", art: "art/choice-cozinha-1.jpg" },
    { value: "2", label: "2) Deixar e voltar ao corredor", art: "art/choice-cozinha-2.jpg" },
    { value: "3", label: "3) Tocar a comida quente", art: "art/choice-cozinha-3.jpg" },
  ]);
  if (op === "1") {
    pegar("fosforos");
    await narrar(
      ["Você guarda os fósforos. A caixa é leve demais — quase vazia. Dentro, restam três palitos. Três chances."],
      "item",
    );
  } else if (op === "3") {
    await narrar([
      "Você encosta o dedo no arroz. Escaldante. Quando retira a mão, a comida ainda fumega… e, por um instante, você vê uma segunda mão — a sua, mais nova — fazendo o mesmo gesto do outro lado do vapor.",
      "A visão some. O prato continua lá.",
    ]);
    const op2 = await escolher([
      { value: "1", label: "1) Pegar os fósforos agora", art: "art/choice-cozinha-1.jpg" },
      { value: "2", label: "2) Voltar ao corredor sem eles", art: "art/choice-cozinha-2.jpg" },
    ]);
    if (op2 === "1") {
      pegar("fosforos");
      await narrar(["Você pega os fósforos. A caixa treme na sua mão."], "item");
    } else {
      await narrar(["Você deixa a cozinha. O cheiro de laranja te segue."]);
    }
  } else {
    await narrar(["Você fecha a gaveta sem pegar nada e volta."]);
  }
  return "corredor";
}

async function cenaSala() {
  await setArt("sala");
  limparLog();
  await narrar([
    "A sala está coberta. O sofá usa um lençol branco manchado de amarelo. Relógios parados. Poeira em camadas.",
    "A TV de tubo olha para você com a tela morta — um olho cinza, opaco.",
  ]);
  if (state.ouviu_fita) {
    if (window.AudioFx) AudioFx.staticBurst();
    await narrar([
      "A TV liga sozinha. Estática. No meio do ruído branco, um rosto se forma — o seu, mais novo, sorrindo sem chegar aos olhos.",
    ]);
  }
  const opcoes = [
    { value: "1", label: "1) Abrir a gaveta da estante", art: "art/choice-sala-1.jpg" },
    { value: "2", label: "2) Examinar a TV", art: "art/choice-sala-2.jpg" },
    { value: "3", label: "3) Voltar ao corredor", art: "art/choice-sala-3.jpg" },
  ];
  if (state.ouviu_fita && state.viu_foto) {
    opcoes.push({
      value: "4",
      label: "4) Seguir o rosto na estática (para o espelho)",
      art: "art/choice-sala-4.jpg",
    });
  }
  const op = await escolher(opcoes);
  if (op === "1") {
    if (tem("chave_enferrujada")) {
      await narrar(["A gaveta está vazia. A chave já está com você."]);
    } else {
      await narrar(
        [
          "A gaveta range. Dentro: uma chave enferrujada, quente ao toque, como se alguém a tivesse segurado agora há pouco. Na alça, um pedaço de fita isolante com a palavra PORÃO.",
        ],
        "item",
      );
      pegar("chave_enferrujada");
      await narrar(["Você guarda a chave. Ela esfria na sua mão aos poucos."]);
    }
    return "sala";
  }
  if (op === "2") {
    state.viu_tv = true;
    if (window.AudioFx) AudioFx.staticBurst();
    if (state.ouviu_fita) {
      await narrar([
        "Você se aproxima da tela. O rosto de criança abre a boca. Não sai som — sai um sopro frio pela fresta do painel. A estática sussurra:",
        '"Você deixou alguém no seu lugar."',
        "A coragem sobe na garganta como náusea. Agora você sabe: precisa ver o espelho de verdade.",
      ]);
    } else {
      await narrar([
        "Você liga a TV. Só estática. No chiado, quase dá para ouvir alguém contar: um… dois… três… Você desliga antes de chegar a quinze.",
      ]);
    }
    return "sala";
  }
  if (op === "4") {
    await narrar([
      "O rosto na estática inclina a cabeça. A tela estala. Você sente um puxão atrás dos olhos — e o mundo vira escuro úmido. Quando a visão volta, você está diante de um espelho coberto por um pano.",
    ]);
    return "espelho";
  }
  await narrar(["Você deixa a sala. O lençol do sofá se mexe sem vento."]);
  return "corredor";
}

async function cenaSotao() {
  await setArt("sotao");
  limparLog();
  await narrar([
    "A escada range a cada degrau. O sótão cheira a poeira quente e a madeira velha. Caixas empilhadas. Um baú de brinquedos cobertos por lençol.",
  ]);
  if (!tem("fosforos")) {
    await narrar(["Está escuro demais. Suas mãos encontram arestas, teias, algo macio que pode ser um casaco… ou não."]);
    const op = await escolher([
      { value: "1", label: "1) Insistir no escuro", art: "art/choice-sotao-escuro-1.jpg" },
      { value: "2", label: "2) Descer ao corredor", art: "art/choice-sotao-escuro-2.jpg" },
    ]);
    if (op === "2") {
      await narrar(["Você desce. A escuridão do sótão parece aliviada."]);
      return "corredor";
    }
    await narrar(
      [
        "Você avança. O pé encontra o vazio entre duas tábuas. Você cai de joelho. Algo — uma unha? um fio? — raspa seu tornozelo.",
      ],
      "danger",
    );
    if (perderVida(1)) return "fim_morte";
    await narrar(["Você engatinha de volta à escada, o coração batendo atrasado, como os passos do corredor."]);
    return "corredor";
  }

  await narrar([
    "Você risca um fósforo. A chama treme e revela o sótão em pedaços laranja: caixas, um gravador de fita cassete, uma vela branca sem usar.",
  ]);

  while (true) {
    const opcoes = [
      { value: "1", label: "1) Examinar o gravador / a fita", art: "art/choice-sotao-1.jpg" },
      {
        value: "2",
        label: tem("vela") ? "2) (Você já tem a vela)" : "2) Pegar a vela",
        art: "art/choice-sotao-2.jpg",
      },
      { value: "3", label: "3) Descer ao corredor", art: "art/choice-sotao-3.jpg" },
    ];
    if (state.ouviu_fita && (state.viu_foto || state.viu_tv)) {
      opcoes.push({
        value: "4",
        label: "4) Seguir o eco da fita (para o espelho)",
        art: "art/choice-sotao-4.jpg",
      });
    }
    const op = await escolher(opcoes);
    if (op === "1") {
      if (!tem("fita_cassete")) {
        pegar("fita_cassete");
        await narrar(
          ["Você puxa a fita do gravador. A etiqueta, na sua letra de criança: EU / OUTRO."],
          "item",
        );
      }
      await narrar([
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
        await narrar(
          [
            "Você guarda a vela. A cera está fria, mas o pavio cheira a fumaça recente — como se alguém tivesse apagado agora.",
          ],
          "item",
        );
      } else {
        await narrar(["A vela já está com você."]);
      }
      continue;
    }
    if (op === "4") {
      await narrar([
        "A voz da criança na fita parece vir de baixo. Você segue o som escada abaixo, atravessa o corredor sem olhar, e desce ao porão — até um espelho coberto por pano.",
      ]);
      return "espelho";
    }
    await narrar(["Você desce. O fósforo se apaga no último degrau."]);
    return "corredor";
  }
}

async function cenaPorao() {
  await setArt("porao");
  limparLog();
  await narrar([
    "O porão engole o som. Umidade cola na pele. Nas paredes, marcas de unha formam o seu nome — letra por letra, profundas demais para uma brincadeira.",
  ]);
  if (!tem("fosforos")) {
    await narrar(["Sem luz, o chão some. Você tropeça numa caixa. O joelho bate no concreto."], "danger");
    if (perderVida(1)) return "fim_morte";
    await narrar(["Você engatinha até a escada, guiado só pelo cheiro menos podre de cima."]);
    const op = await escolher([
      { value: "1", label: "1) Subir ao corredor", art: "art/choice-porao-escuro-1.jpg" },
      { value: "2", label: "2) Tentar de novo no escuro", art: "art/choice-porao-escuro-2.jpg" },
    ]);
    if (op === "1") return "corredor";
    await narrar(
      [
        "Você insiste. Dedos encontram um pano grosso sobre algo liso — vidro. Um espelho. Sem luz, você não ousa puxar o pano.",
      ],
      "danger",
    );
    if (perderVida(1)) return "fim_morte";
    return "corredor";
  }

  await narrar([
    "Você risca um fósforo. A chama mostra a inscrição completa nas paredes: o seu nome, repetido, e abaixo:",
    '"ELE FICOU."',
    "No chão, uma foto rasgada. No fundo, uma porta baixa coberta por um pano escuro — o formato de um espelho de corpo inteiro.",
  ]);

  while (true) {
    const op = await escolher([
      {
        value: "1",
        label: tem("foto_rasgada") ? "1) (Você já tem a foto)" : "1) Pegar a foto rasgada",
        art: "art/choice-porao-1.jpg",
      },
      { value: "2", label: "2) Puxar o pano do espelho", art: "art/choice-porao-2.jpg" },
      { value: "3", label: "3) Subir ao corredor", art: "art/choice-porao-3.jpg" },
    ]);
    if (op === "1") {
      if (!tem("foto_rasgada")) {
        pegar("foto_rasgada");
        state.viu_foto = true;
        await narrar(
          [
            "A foto mostra a casa intacta, ensolarada. No jardim, uma criança — você — sorri. Atrás dela, uma sombra com o mesmo sorriso, atrasada um passo. A borda da foto está queimada.",
          ],
          "item",
        );
      } else {
        await narrar(["Você já guarda a foto. O sorriso da sombra não muda."]);
      }
      continue;
    }
    if (op === "2") {
      await narrar([
        "Você puxa o pano. O tecido cai como pele morta. O espelho não mostra o porão — mostra o corredor de cima, vazio… e alguém com o seu rosto já te esperando do outro lado, sorrindo.",
      ]);
      state.conheceu_eco = true;
      return "espelho";
    }
    await narrar(["Você sobe. O fósforo morre entre os dedos."]);
    return "corredor";
  }
}

async function cenaEspelho() {
  if (state.vida <= 0) return "fim_morte";
  await setArt("espelho");
  limparLog();
  const temPista =
    state.ouviu_fita || state.viu_foto || tem("fita_cassete") || tem("foto_rasgada");
  if (!temPista) {
    await narrar(
      [
        "O espelho te engole com a própria imagem. Sem lembrar por que veio, você só vê o sorriso atrasado. Mãos iguais às suas atravessam o vidro e puxam.",
      ],
      "danger",
    );
    return "fim_morte";
  }
  await narrar([
    "O doppelgänger está do outro lado do vidro, sorrindo com o seu sorriso. Ele fala primeiro — com a sua voz, meio segundo atrasada:",
    '"Eu esperei doze anos. A casa estava com saudade."',
    "O ar cheira a chuva de infância e a ferrugem.",
  ]);
  state.conheceu_eco = true;
  const opcoes = [
    { value: "1", label: "1) Correr para a porta da frente", art: "art/choice-espelho-1.jpg" },
    { value: "2", label: '2) Confrontar: "Você não é eu"', art: "art/choice-espelho-2.jpg" },
    { value: "3", label: "3) Aceitar trocar de lugar", art: "art/choice-espelho-3.jpg" },
  ];
  if (tem("vela") && tem("fosforos") && (state.ouviu_fita || tem("fita_cassete"))) {
    opcoes.push({
      value: "4",
      label: "4) Acender a vela e dizer o nome do bilhete",
      art: "art/choice-espelho-4.jpg",
    });
  }
  const op = await escolher(opcoes);
  if (op === "1") {
    if (tem("chave_enferrujada") || tem("fosforos")) return "fim_fuga";
    await narrar(
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
    await narrar(
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
  if (window.AudioFx) AudioFx.ending(titulo);
  atualizarHud();
}

async function fimFuga() {
  await setArt("fim_fuga");
  limparLog();
  await narrar([
    "Você corre. A porta da frente cede — chave ou luz, não importa. A noite lá fora é real: vento, rua, o cheiro de asfalto molhado.",
    "Você olha para trás. A casa está quieta. Então, no seu antigo quarto, a luz acende sozinha.",
    "Alguém passa atrás da cortina com o seu jeito de andar. Meio segundo atrasado.",
    "Você escapou. Talvez.",
  ]);
  resumo("FUGA AMBÍGUA");
  return "fim";
}

async function fimVerdade() {
  await setArt("fim_verdade");
  limparLog();
  await narrar([
    'Você segura a foto e a memória da fita. "Você não é eu. Você é o que eu deixei."',
    "O sorriso do eco trinca. Você golpeia o espelho. O vidro soluça — um som úmido, humano — e estilhaça.",
    "A casa inteira respira fundo, como quem larga um segredo. Poeira sobe. A luz amarela morre.",
    "Quando amanhece, você está no jardim. A porta está fechada. Não há passos atrasados. Só o seu coração, no tempo certo.",
  ]);
  resumo("VERDADE");
  return "fim";
}

async function fimEco() {
  await setArt("fim_eco");
  limparLog();
  await narrar([
    "Você encosta a mão no vidro. O eco encosta a dele. O frio passa. O calor fica do outro lado.",
    "Você tenta recuar. Não há recuo. O porão — ou a sala, ou o quarto — agora é o lado de dentro do espelho.",
    "Do lado de fora, alguém com o seu rosto abre a porta da frente, inspira a noite e sorri no tempo certo.",
    "A casa não está mais sozinha. Você está.",
  ]);
  resumo("O ECO SAI");
  return "fim";
}

async function fimRitual() {
  await setArt("fim_ritual");
  limparLog();
  await narrar([
    "Você risca o fósforo. A vela acende. A chama mostra o eco como ele é: pequeno, assustado, uma criança que prometeu não deixar a casa vazia.",
    "Você diz o que o bilhete escondia — não um nome de pessoa, mas o nome da casa, o apelido que só vocês dois usavam quando era tarde demais para dormir.",
    "O eco encolhe. Vira menino de novo. A vela tremula. Você apaga com os dedos.",
    "De manhã, você tranca cada porta. No quintal, queima a fita. A fumaça sobe reta. A casa, pela primeira vez em doze anos, não responde.",
  ]);
  resumo("RITUAL — FINAL SECRETO");
  return "fim";
}

async function fimMorte() {
  await setArt("fim_morte");
  limparLog();
  await narrar(
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
  await setArt("fim_atrasado");
  limparLog();
  await narrar([
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
  document.body.classList.remove("is-ending");
  delete document.body.dataset.ending;
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
  again.textContent = "acordar de novo";
  again.addEventListener("click", () => {
    state = estadoInicial();
    document.body.classList.remove("is-ending", "is-hurt");
    delete document.body.dataset.ending;
    atualizarHud();
    limparLog();
    limparEscolhas();
    loop();
  });
  el.choices.appendChild(again);
}

function syncMuteButton() {
  if (!el.btnMute || !window.AudioFx) return;
  const muted = AudioFx.isMuted();
  el.btnMute.setAttribute("aria-pressed", muted ? "true" : "false");
  el.btnMute.textContent = muted ? "mudo" : "som";
}

function boot() {
  const lines = [
    "O reflexo ainda não chegou…",
    "Passos com meio segundo de atraso.",
    "A casa conta até quinze.",
    "Ela está com saudade.",
  ];
  let i = 0;
  const tick = setInterval(() => {
    const pct = Math.min(100, ((i + 1) / lines.length) * 100);
    el.bootBar.style.width = `${pct}%`;
    el.bootLine.textContent = lines[i] || lines[lines.length - 1];
    i += 1;
    if (i >= lines.length) {
      clearInterval(tick);
      el.btnStart.hidden = false;
    }
  }, 700);

  syncMuteButton();
  if (el.btnMute) {
    el.btnMute.addEventListener("click", () => {
      if (!window.AudioFx) return;
      AudioFx.ensure();
      AudioFx.setMuted(!AudioFx.isMuted());
      syncMuteButton();
    });
  }

  el.btnStart.addEventListener("click", () => {
    if (window.AudioFx) {
      AudioFx.ensure();
      AudioFx.startDrone();
    }
    el.boot.classList.add("is-done");
    document.body.dataset.scene = "inicio";
    loop();
  });
}

boot();
