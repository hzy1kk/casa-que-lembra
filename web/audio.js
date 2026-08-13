/* Som procedural de terror — sem arquivos externos. */
const AudioFx = (() => {
  let ctx = null;
  let master = null;
  let droneGain = null;
  let droneNodes = [];
  let footTimer = null;
  let heartTimer = null;
  let muted = localStorage.getItem("cql-mute") === "1";
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function ensure() {
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return false;
    if (!ctx) {
      ctx = new AC();
      master = ctx.createGain();
      master.gain.value = muted ? 0 : 0.26;
      master.connect(ctx.destination);
    }
    if (ctx.state === "suspended") ctx.resume();
    return true;
  }

  function now() {
    return ctx ? ctx.currentTime : 0;
  }

  function setMuted(value) {
    muted = Boolean(value);
    localStorage.setItem("cql-mute", muted ? "1" : "0");
    if (master) {
      master.gain.cancelScheduledValues(now());
      master.gain.setTargetAtTime(muted ? 0 : 0.26, now(), 0.08);
    }
    if (!muted) {
      ensure();
      startDrone();
    }
  }

  function isMuted() {
    return muted;
  }

  function env(duration, peak) {
    if (!ensure()) return null;
    const g = ctx.createGain();
    const t = ctx.currentTime;
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(Math.max(peak, 0.0002), t + 0.018);
    g.gain.exponentialRampToValueAtTime(0.0001, t + duration);
    g.connect(master);
    return g;
  }

  function tone(freq, type, duration, peak) {
    if (!ensure() || muted) return;
    const o = ctx.createOscillator();
    o.type = type;
    o.frequency.value = freq;
    const g = env(duration, peak);
    if (!g) return;
    o.connect(g);
    o.start();
    o.stop(ctx.currentTime + duration + 0.02);
  }

  function noise(duration, peak, hpFreq) {
    if (!ensure() || muted) return;
    const buffer = ctx.createBuffer(1, Math.floor(ctx.sampleRate * duration), ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < data.length; i += 1) data[i] = Math.random() * 2 - 1;
    const src = ctx.createBufferSource();
    src.buffer = buffer;
    const hp = ctx.createBiquadFilter();
    hp.type = "highpass";
    hp.frequency.value = hpFreq;
    const g = env(duration, peak);
    if (!g) return;
    src.connect(hp);
    hp.connect(g);
    src.start();
  }

  function startDrone() {
    if (!ensure() || droneNodes.length) return;
    droneGain = ctx.createGain();
    droneGain.gain.value = 1;
    droneGain.connect(master);

    const make = (freq, type, vol, lfoRate) => {
      const o = ctx.createOscillator();
      const g = ctx.createGain();
      const lfo = ctx.createOscillator();
      const lg = ctx.createGain();
      o.type = type;
      o.frequency.value = freq;
      g.gain.value = vol;
      lfo.type = "sine";
      lfo.frequency.value = lfoRate;
      lg.gain.value = freq * 0.01;
      lfo.connect(lg);
      lg.connect(o.frequency);
      o.connect(g);
      g.connect(droneGain);
      o.start();
      lfo.start();
      droneNodes.push(o, lfo);
    };

    make(42, "sine", 0.07, 0.06);
    make(63.5, "sine", 0.035, 0.09);
    make(126, "triangle", 0.012, 0.04);
  }

  function footstep() {
    if (muted) return;
    noise(0.07, 0.09, 280);
    tone(84, "sine", 0.11, 0.045);
    window.setTimeout(() => {
      if (muted) return;
      noise(0.06, 0.05, 260);
      tone(78, "sine", 0.1, 0.025);
    }, 430);
  }

  function stopFootsteps() {
    if (footTimer) {
      window.clearTimeout(footTimer);
      footTimer = null;
    }
  }

  function startFootsteps() {
    stopFootsteps();
    if (reduced) return;
    const tick = () => {
      footstep();
      footTimer = window.setTimeout(tick, 2400 + Math.random() * 1600);
    };
    footTimer = window.setTimeout(tick, 900);
  }

  function heartbeat(on) {
    if (heartTimer) {
      window.clearInterval(heartTimer);
      heartTimer = null;
    }
    if (!on || reduced) return;
    const beat = () => {
      tone(48, "sine", 0.14, 0.11);
      window.setTimeout(() => tone(42, "sine", 0.18, 0.07), 130);
    };
    beat();
    heartTimer = window.setInterval(beat, 1040);
  }

  function click() {
    noise(0.025, 0.04, 1800);
    tone(190, "square", 0.04, 0.03);
  }

  function item() {
    tone(392, "sine", 0.16, 0.07);
    window.setTimeout(() => tone(523, "sine", 0.2, 0.045), 90);
  }

  function hurt() {
    noise(0.28, 0.16, 180);
    tone(64, "sawtooth", 0.32, 0.09);
  }

  function stinger() {
    tone(147, "sawtooth", 0.45, 0.07);
    tone(155, "square", 0.4, 0.04);
    noise(0.35, 0.09, 500);
  }

  function staticBurst() {
    noise(0.55, 0.07, 1400);
  }

  function room(cena) {
    startDrone();
    const walking = cena === "corredor" || cena === "porao" || cena === "espelho" || cena === "sotao";
    if (walking && !String(cena).startsWith("fim_")) startFootsteps();
    else stopFootsteps();
  }

  function ending(kind) {
    stopFootsteps();
    if (kind === "MORTE" || kind === "ATRASADO DEMAIS") {
      stinger();
      tone(36, "sine", 1.4, 0.12);
      return;
    }
    if (kind === "VERDADE" || kind.indexOf("RITUAL") !== -1) {
      tone(196, "sine", 0.9, 0.05);
      tone(294, "sine", 1.1, 0.035);
      return;
    }
    tone(98, "sine", 0.9, 0.06);
  }

  return {
    ensure,
    setMuted,
    isMuted,
    startDrone,
    room,
    click,
    item,
    hurt,
    stinger,
    staticBurst,
    heartbeat,
    ending,
  };
})();
