import { create } from 'zustand';
import { api } from '../api/client';

const useStore = create((set, get) => ({
  stats: null,
  graphData: null,
  selectedNode: null,
  suggestions: [],
  history: [],
  ingestions: [],
  loading: false,
  error: null,

  setSelectedNode: (node) => set({ selectedNode: node }),
  setError: (error) => set({ error }),
  clearError: () => set({ error: null }),

  fetchStats: async () => {
    try {
      const stats = await api.graphStats();
      set({ stats });
    } catch {
      set({ stats: { total_nodes: 0, total_relationships: 0, label_counts: {}, relationship_type_counts: {} } });
    }
  },

  fetchGraph: async (limit = 500) => {
    set({ loading: true });
    try {
      const graphData = await api.graphFull(limit);
      set({ graphData, loading: false });
    } catch (e) {
      set({ graphData: { nodes: [], links: [] }, loading: false, error: e.message });
    }
  },

  fetchSuggestions: async () => {
    try {
      const data = await api.querySuggestions();
      set({ suggestions: data.suggestions || [] });
    } catch {
      set({ suggestions: [] });
    }
  },

  fetchHistory: async () => {
    try {
      const history = await api.queryHistory();
      set({ history });
    } catch {
      set({ history: [] });
    }
  },

  fetchIngestions: async () => {
    try {
      const ingestions = await api.ingestHistory();
      set({ ingestions });
    } catch {
      set({ ingestions: [] });
    }
  },
}));

export default useStore;
