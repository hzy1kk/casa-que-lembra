/**
 * Ranking global da competição — Vercel Serverless
 *
 * GET  /api/ranking  → top 30 (público)
 * POST /api/ranking  → { nome, pontos, final, acoes }
 *
 * Precisa de Upstash Redis / Vercel KV:
 *   UPSTASH_REDIS_REST_URL + UPSTASH_REDIS_REST_TOKEN
 *   (ou KV_REST_API_URL + KV_REST_API_TOKEN)
 */

const KEY = "casa_que_lembra:ranking_v1";
const MAX = 30;
const MAX_PONTOS = 800;

const FINAIS_OK = new Set([
  "Fuga",
  "Verdade",
  "O Eco sai",
  "Ritual secreto",
  "Morte",
  "Fuga falhou",
  "Sem lembrar",
]);

function redisEnv() {
  const url =
    process.env.UPSTASH_REDIS_REST_URL ||
    process.env.KV_REST_API_URL ||
    "";
  const token =
    process.env.UPSTASH_REDIS_REST_TOKEN ||
    process.env.KV_REST_API_TOKEN ||
    "";
  return { url, token };
}

async function redis(command) {
  const { url, token } = redisEnv();
  if (!url || !token) {
    const err = new Error("Ranking não configurado (faltam variáveis Redis/KV).");
    err.code = "NO_REDIS";
    throw err;
  }
  const res = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(command),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Redis error ${res.status}: ${text.slice(0, 200)}`);
  }
  return res.json();
}

async function lerLista() {
  const data = await redis(["GET", KEY]);
  const raw = data && data.result;
  if (!raw) return [];
  try {
    const lista = JSON.parse(raw);
    return Array.isArray(lista) ? lista : [];
  } catch (_) {
    return [];
  }
}

async function salvarLista(lista) {
  await redis(["SET", KEY, JSON.stringify(lista)]);
}

function limparNome(nome) {
  return String(nome || "")
    .normalize("NFKC")
    .replace(/[^\p{L}\p{N} _.\-]/gu, "")
    .trim()
    .slice(0, 16);
}

function cors(res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  res.setHeader("Cache-Control", "no-store");
}

module.exports = async function handler(req, res) {
  cors(res);
  if (req.method === "OPTIONS") {
    res.status(204).end();
    return;
  }

  try {
    if (req.method === "GET") {
      const lista = await lerLista();
      lista.sort((a, b) => (b.pontos || 0) - (a.pontos || 0));
      res.status(200).json({
        ok: true,
        global: true,
        ranking: lista.slice(0, MAX),
      });
      return;
    }

    if (req.method === "POST") {
      const body = typeof req.body === "string" ? JSON.parse(req.body || "{}") : req.body || {};
      const nome = limparNome(body.nome);
      const pontos = Number(body.pontos);
      const finalNome = String(body.final || "").slice(0, 40);
      const acoes = Math.max(0, Math.min(9999, Number(body.acoes) || 0));

      if (nome.length < 2) {
        res.status(400).json({ ok: false, error: "Apelido inválido (mín. 2 caracteres)." });
        return;
      }
      if (!Number.isFinite(pontos) || pontos < 0 || pontos > MAX_PONTOS) {
        res.status(400).json({ ok: false, error: "Pontuação inválida." });
        return;
      }
      if (!FINAIS_OK.has(finalNome)) {
        res.status(400).json({ ok: false, error: "Final inválido." });
        return;
      }

      const entrada = {
        nome,
        pontos: Math.floor(pontos),
        final: finalNome,
        acoes,
        em: new Date().toISOString(),
      };

      const lista = await lerLista();
      lista.push(entrada);
      lista.sort((a, b) => (b.pontos || 0) - (a.pontos || 0));
      const top = lista.slice(0, MAX);
      await salvarLista(top);

      const posicao = top.findIndex(
        (x) =>
          x.nome === entrada.nome &&
          x.pontos === entrada.pontos &&
          x.em === entrada.em
      );

      res.status(200).json({
        ok: true,
        posicao: posicao >= 0 ? posicao + 1 : null,
        ranking: top,
      });
      return;
    }

    res.status(405).json({ ok: false, error: "Método não permitido." });
  } catch (err) {
    const status = err && err.code === "NO_REDIS" ? 503 : 500;
    res.status(status).json({
      ok: false,
      error: err.message || "Erro no ranking",
      setup:
        status === 503
          ? "Crie um Redis Upstash no projeto Vercel e defina UPSTASH_REDIS_REST_URL + UPSTASH_REDIS_REST_TOKEN."
          : undefined,
    });
  }
};
