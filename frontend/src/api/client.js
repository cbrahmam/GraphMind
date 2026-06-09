const BASE = '/api';

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || res.statusText);
  }
  return res.json();
}

export const api = {
  health: () => request('/health'),

  // Ingest
  ingestDocument: (file) => {
    const form = new FormData();
    form.append('file', file);
    return fetch(`${BASE}/ingest/document`, { method: 'POST', body: form }).then(r => r.json());
  },
  ingestUrl: (url) => request('/ingest/url', { method: 'POST', body: JSON.stringify({ url }) }),
  ingestText: (text, title) => request('/ingest/text', { method: 'POST', body: JSON.stringify({ text, title }) }),
  ingestCsv: (file) => {
    const form = new FormData();
    form.append('file', file);
    return fetch(`${BASE}/ingest/csv`, { method: 'POST', body: form }).then(r => r.json());
  },
  ingestHistory: () => request('/ingest/history'),

  // Extract
  extractPipeline: (docId) => request(`/extract/pipeline/${docId}`, { method: 'POST' }),
  csvImport: (docId, mapping) => request(`/extract/csv/import?document_id=${docId}`, { method: 'POST', body: JSON.stringify(mapping) }),

  // Graph
  graphStats: () => request('/graph/stats'),
  graphSchema: () => request('/graph/schema'),
  graphFull: (limit = 500) => request(`/graph/full?limit=${limit}`),
  graphNodes: (label, search) => {
    const params = new URLSearchParams();
    if (label) params.set('label', label);
    if (search) params.set('search', search);
    return request(`/graph/nodes?${params}`);
  },
  graphNode: (id) => request(`/graph/node/${id}`),
  graphNeighbors: (id, depth = 1) => request(`/graph/neighbors/${id}?depth=${depth}`),

  // Query
  askQuestion: (question) => request('/query', { method: 'POST', body: JSON.stringify({ question }) }),
  runCypher: (cypher, parameters = {}) => request('/query/cypher', { method: 'POST', body: JSON.stringify({ cypher, parameters }) }),
  querySuggestions: () => request('/query/suggestions'),
  queryHistory: () => request('/query/history'),
  findPath: (from_entity, to_entity, max_depth = 5) => request('/query/path', { method: 'POST', body: JSON.stringify({ from_entity, to_entity, max_depth }) }),

  // Schema
  getSchema: () => request('/schema'),
  updateSchema: (schema) => request('/schema', { method: 'PUT', body: JSON.stringify(schema) }),
  getPresets: () => request('/schema/presets'),
  loadPreset: (name) => request(`/schema/presets/${name}`, { method: 'POST' }),
};
