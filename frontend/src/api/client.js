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
  graphSnapshot: (name = 'latest') => request(`/graph/snapshot?name=${name}`, { method: 'POST' }),
  graphDiff: (before, after) => request(`/graph/diff/${before}/${after}`),

  // Query
  askQuestion: (question) => request('/query', { method: 'POST', body: JSON.stringify({ question }) }),
  runCypher: (cypher, parameters = {}) => request('/query/cypher', { method: 'POST', body: JSON.stringify({ cypher, parameters }) }),
  querySuggestions: () => request('/query/suggestions'),
  queryHistory: () => request('/query/history'),
  findPath: (from_entity, to_entity, max_depth = 5) => request('/query/path', { method: 'POST', body: JSON.stringify({ from_entity, to_entity, max_depth }) }),

  // Conversational query
  conversationalQuery: (question, sessionId = 'default') => request(`/query/conversational?question=${encodeURIComponent(question)}&session_id=${sessionId}`, { method: 'POST' }),
  querySessions: () => request('/query/sessions'),
  querySession: (id) => request(`/query/session/${id}`),
  clearSession: (id) => request(`/query/session/${id}`, { method: 'DELETE' }),

  // Graph RAG
  ragQuery: (question) => request(`/query/rag?question=${encodeURIComponent(question)}`, { method: 'POST' }),

  // Templates
  queryTemplates: () => request('/query/templates'),
  runTemplate: (id, params = {}) => request(`/query/templates/${id}/run`, { method: 'POST', body: JSON.stringify(params) }),
  saveTemplate: (template) => request('/query/templates', { method: 'POST', body: JSON.stringify(template) }),
  deleteTemplate: (id) => request(`/query/templates/${id}`, { method: 'DELETE' }),

  // Schema
  getSchema: () => request('/schema'),
  updateSchema: (schema) => request('/schema', { method: 'PUT', body: JSON.stringify(schema) }),
  getPresets: () => request('/schema/presets'),
  loadPreset: (name) => request(`/schema/presets/${name}`, { method: 'POST' }),

  // Annotations
  getAnnotations: (entity) => request(`/annotations${entity ? `?entity=${encodeURIComponent(entity)}` : ''}`),
  addAnnotation: (entity_name, text, type = 'note') => request(`/annotations?entity_name=${encodeURIComponent(entity_name)}&text=${encodeURIComponent(text)}&annotation_type=${type}`, { method: 'POST' }),
  voteAnnotation: (id, dir = 1) => request(`/annotations/${id}/vote?direction=${dir}`, { method: 'POST' }),
  deleteAnnotation: (id) => request(`/annotations/${id}`, { method: 'DELETE' }),

  // Change feed
  changeFeed: (limit = 100) => request(`/feed?limit=${limit}`),
  timeline: () => request('/feed/timeline'),

  // Watchlist
  getWatchlist: () => request('/watchlist'),
  addWatch: (pattern, label) => request(`/watchlist?entity_pattern=${encodeURIComponent(pattern)}${label ? `&label=${label}` : ''}`, { method: 'POST' }),
  removeWatch: (id) => request(`/watchlist/${id}`, { method: 'DELETE' }),
  getAlerts: (unreadOnly = false) => request(`/watchlist/alerts?unread_only=${unreadOnly}`),
  markAlertRead: (id) => request(`/watchlist/alerts/${id}/read`, { method: 'POST' }),

  // Workspaces
  getWorkspaces: () => request('/workspaces'),
  createWorkspace: (name, desc = '') => request(`/workspaces?name=${encodeURIComponent(name)}&description=${encodeURIComponent(desc)}`, { method: 'POST' }),
  setActiveWorkspace: (id) => request(`/workspaces/active/${id}`, { method: 'POST' }),
  deleteWorkspace: (id) => request(`/workspaces/${id}`, { method: 'DELETE' }),

  // Auth
  register: (username, password, role = 'viewer') => request(`/auth/register?username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}&role=${role}`, { method: 'POST' }),
  login: (username, password) => request(`/auth/login?username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`, { method: 'POST' }),
  logout: (token) => request(`/auth/logout?token=${token}`, { method: 'POST' }),
};
