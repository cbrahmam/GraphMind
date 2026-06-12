import { useState } from 'react'
import { Search, AlertCircle, Brain, RefreshCw } from 'lucide-react'

export default function GapsPage() {
  const [tab, setTab] = useState('sparse')
  const [gaps, setGaps] = useState([])
  const [aiAnalysis, setAiAnalysis] = useState(null)
  const [loading, setLoading] = useState(false)

  const loadGaps = async (type) => {
    setLoading(true)
    setTab(type)
    try {
      if (type === 'ai') {
        const res = await fetch('/api/gaps/analysis')
        const data = await res.json()
        setAiAnalysis(data)
        setGaps(data.gaps || [])
      } else {
        const endpoints = { sparse: '/api/gaps/sparse', disconnected: '/api/gaps/disconnected', reciprocals: '/api/gaps/reciprocals' }
        const res = await fetch(endpoints[type])
        const data = await res.json()
        setGaps(data.gaps || [])
        setAiAnalysis(null)
      }
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 max-w-5xl">
      <h1 className="text-xl font-bold text-white flex items-center gap-2 mb-2">
        <Search className="w-5 h-5 text-orange-400" /> Knowledge Gaps
      </h1>
      <p className="text-sm text-gray-500 mb-6">Identify missing information and incomplete areas</p>

      <div className="flex gap-2 mb-6">
        {[
          { key: 'sparse', label: 'Sparse Entities' },
          { key: 'disconnected', label: 'Disconnected' },
          { key: 'reciprocals', label: 'Missing Links' },
          { key: 'ai', label: 'AI Analysis' },
        ].map(t => (
          <button key={t.key} onClick={() => loadGaps(t.key)}
            className={`px-3 py-1.5 rounded-lg text-xs transition-colors ${
              tab === t.key ? 'bg-orange-500/10 text-orange-400' : 'text-gray-400 hover:text-gray-200 bg-[#161b22]'
            }`}>
            {t.label}
          </button>
        ))}
      </div>

      {loading && <p className="text-gray-500 text-sm flex items-center gap-2"><RefreshCw className="w-3.5 h-3.5 animate-spin" /> Analyzing...</p>}

      {aiAnalysis && tab === 'ai' && (
        <div className="mb-4 bg-[#161b22] border border-[#30363d] rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Brain className="w-4 h-4 text-purple-400" />
            <span className="text-sm text-white font-medium">Completeness Score</span>
            <span className="text-purple-400 font-bold">{Math.round((aiAnalysis.completeness_score || 0) * 100)}%</span>
          </div>
          {aiAnalysis.recommended_sources?.length > 0 && (
            <div className="text-xs text-gray-500">
              Recommended sources: {aiAnalysis.recommended_sources.join(', ')}
            </div>
          )}
        </div>
      )}

      <div className="space-y-2">
        {gaps.map((g, i) => (
          <div key={i} className="bg-[#161b22] border border-[#30363d] rounded-lg p-3">
            <div className="flex items-start gap-2">
              <AlertCircle className="w-4 h-4 text-orange-400 mt-0.5 shrink-0" />
              <div>
                <div className="text-sm text-gray-200">{g.suggestion || g.description}</div>
                {g.priority && <span className="text-xs text-gray-500">Priority: {g.priority}</span>}
                {g.area && <span className="text-xs text-gray-500 ml-2">Area: {g.area}</span>}
              </div>
            </div>
          </div>
        ))}
      </div>

      {!loading && gaps.length === 0 && (
        <p className="text-center text-gray-500 py-10">Click a tab to analyze knowledge gaps</p>
      )}
    </div>
  )
}
