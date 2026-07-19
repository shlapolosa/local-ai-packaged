// One-off seeder: embed capability_map_documents.json via native Ollama (nomic-embed-text)
// and upsert into the Qdrant `capability-maps` collection in the payload shape the
// architecture pipeline's LangChain Qdrant `load` node expects ({content, metadata}).
// Runs INSIDE the n8n container: reaches Ollama at host.docker.internal:11434, Qdrant at qdrant:6333.
const fs = require('fs');
const http = require('http');

const SRC = '/data/shared/knowledge/capability-maps/capability_map_documents.json';
const OLLAMA = { host: 'host.docker.internal', port: 11434 };
const QDRANT = { host: 'qdrant', port: 6333 };
const COLLECTION = 'capability-maps';
const CONC = 8;
const UPSERT_BATCH = 200;

function req(opts, body) {
  return new Promise((resolve, reject) => {
    const data = body != null ? JSON.stringify(body) : null;
    const r = http.request(
      { ...opts, headers: { 'Content-Type': 'application/json', ...(data ? { 'Content-Length': Buffer.byteLength(data) } : {}) } },
      (res) => { let d = ''; res.on('data', (c) => (d += c)); res.on('end', () => { try { resolve({ status: res.statusCode, json: d ? JSON.parse(d) : null }); } catch (e) { resolve({ status: res.statusCode, raw: d }); } }); }
    );
    r.on('error', reject);
    if (data) r.write(data);
    r.end();
  });
}
async function embed(text) {
  const res = await req({ host: OLLAMA.host, port: OLLAMA.port, path: '/api/embeddings', method: 'POST' }, { model: 'nomic-embed-text', prompt: text });
  return res.json && res.json.embedding;
}
const contentOf = (doc) => doc.text || doc.definition || doc.capability || String(doc.id);

async function run() {
  const DOCS = JSON.parse(fs.readFileSync(SRC, 'utf8'));
  console.log('docs to seed:', DOCS.length);
  const points = new Array(DOCS.length);
  let idx = 0, done = 0, fail = 0;
  async function worker() {
    while (true) {
      const i = idx++; if (i >= DOCS.length) break;
      const doc = DOCS[i];
      const text = contentOf(doc);
      let vec = null, tries = 0;
      while (!vec && tries < 3) { try { vec = await embed(text); } catch (e) {} tries++; }
      if (!vec) { fail++; continue; }
      points[i] = { id: i, vector: vec, payload: { doc_id: doc.id, content: text, metadata: Object.assign({}, doc.metadata || {}, { id: doc.id, path: doc.path, capability: doc.capability, level: doc.level }) } };
      if (++done % 250 === 0) console.log('embedded', done);
    }
  }
  await Promise.all(Array.from({ length: CONC }, worker));
  const valid = points.filter(Boolean);
  console.log('embedded total:', valid.length, '| failed:', fail);
  for (let i = 0; i < valid.length; i += UPSERT_BATCH) {
    const slice = valid.slice(i, i + UPSERT_BATCH);
    const res = await req({ host: QDRANT.host, port: QDRANT.port, path: `/collections/${COLLECTION}/points?wait=true`, method: 'PUT' }, { points: slice });
    if (res.status >= 300) console.log('upsert err', res.status, JSON.stringify(res.json || res.raw).slice(0, 200));
  }
  const cnt = await req({ host: QDRANT.host, port: QDRANT.port, path: `/collections/${COLLECTION}`, method: 'GET' });
  console.log('capability-maps points_count:', cnt.json && cnt.json.result && cnt.json.result.points_count);
}
run().catch((e) => { console.error(e); process.exit(1); });
