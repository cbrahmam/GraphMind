import { useState, useEffect } from 'react'
import { Brain, Download, RefreshCw } from 'lucide-react'
import { api } from '../api/client'

export default function InsightsPage() {
  const [insights, setInsights] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch('/api/insights/latest').then(r => r.ok ? r.json() : null).then(setInsights).catch(() => {})
  }, [])

  const generate = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await fetch('/api/insights/generate', { method: 'POST' }).then(r => r.json())
      setInsights(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const exportGraph = async (format) => {
    window.open(`/api/export/${format}`, '_blank')
  }

  return (
    <div className="p-6 max-w-5xl space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">Insights & Export</h2>
        <div className="flex gap-2">
          <button onClick={generate} disabled={loading} className="flex items-center gap-1.5 px-3 py-1.5 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 rounded-lg text-white text-sm transition-colors">
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> {loading ? 'Generating...' : 'Generate Insights'}
          </button>
        </div>
      </div>

      {error && <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-red-400 text-sm">{error}</div>}

      {insights && (
        <div className="space-y-4">
          {insights.summary && (
            <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-5">
              <div className="flex items-start gap-3">
                <Brain className="w-5 h-5 text-purple-400 mt-0.5 shrink-0" />
                <p className="text-gray-200 text-sm leading-relaxed">{insights.summary}</p>
              </div>
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            {insights.key_entities?.length > 0 && (
              <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4">
                <h3 className="text-sm font-medium text-gray-400 mb-3">Key Entities</h3>
                <div className="space-y-2">
                  {insights.key_entities.map((e, i) => (
                    <div key={i} className="flex items-start gap-2">
                      <span className="text-xs text-purple-400 bg-purple-500/10 rounded-full w-5 h-5 flex items-center justify-center shrink-0">{i + 1}</span>
                      <div>
                        <span className="text-sm text-white font-medium">{e.name}</span>
                        <p className="text-xs text-gray-500">{e.why}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {insights.knowledge_gaps?.length > 0 && (
              <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4">
                <h3 className="text-sm font-medium text-gray-400 mb-3">Knowledge Gaps</h3>
                <div className="space-y-1">
                  {insights.knowledge_gaps.map((gap, i) => (
                    <div key={i} className="text-sm text-yellow-400 bg-yellow-500/5 rounded-lg px-3 py-1.5">
                      {gap}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {insights.insights?.length > 0 && (
            <div className="space-y-2">
              <h3 className="text-sm font-medium text-gray-400">AI Insights</h3>
              {insights.insights.map((insight, i) => (
                <div key={i} className="bg-[#161b22] border border-[#30363d] rounded-xl p-4">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      insight.priority === 'high' ? 'bg-red-500/10 text-red-400' :
                      insight.priority === 'medium' ? 'bg-yellow-500/10 text-yellow-400' :
                      'bg-gray-500/10 text-gray-400'
                    }`}>{insight.priority}</span>
                    <span className="text-xs text-gray-500">{insight.insight_type}</span>
                  </div>
                  <h4 className="text-sm font-medium text-white">{insight.title}</h4>
                  <p className="text-xs text-gray-400 mt-1">{insight.description}</p>
                </div>
              ))}
            </div>
          )}

          {insights.questions_to_explore?.length > 0 && (
            <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4">
              <h3 className="text-sm font-medium text-gray-400 mb-3">Questions to Explore</h3>
              <div className="flex flex-wrap gap-2">
                {insights.questions_to_explore.map((q, i) => (
                  <span key={i} className="px-3 py-1 bg-[#0d1117] border border-[#30363d] rounded-full text-xs text-gray-300">{q}</span>
                ))}
              </div>
            </div>
          )}

          {insights.health && (
            <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4">
              <h3 className="text-sm font-medium text-gray-400 mb-3">Graph Health</h3>
              <div className="grid grid-cols-4 gap-4 text-center">
                <div><div className="text-lg font-bold text-white">{insights.health.total_nodes}</div><div className="text-xs text-gray-500">Nodes</div></div>
                <div><div className="text-lg font-bold text-white">{insights.health.total_relationships}</div><div className="text-xs text-gray-500">Relationships</div></div>
                <div><div className="text-lg font-bold text-white">{insights.health.avg_connections}</div><div className="text-xs text-gray-500">Avg Connections</div></div>
                <div><div className="text-lg font-bold text-white">{insights.health.isolated_nodes}</div><div className="text-xs text-gray-500">Isolated Nodes</div></div>
              </div>
            </div>
          )}
        </div>
      )}

      <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4">
        <h3 className="text-sm font-medium text-gray-400 mb-3">Export Graph</h3>
        <div className="flex flex-wrap gap-2">
          {['json', 'csv', 'graphml', 'cypher', 'markdown'].map(fmt => (
            <button key={fmt} onClick={() => exportGraph(fmt)} className="flex items-center gap-1.5 px-3 py-1.5 bg-[#0d1117] border border-[#30363d] rounded-lg text-sm text-gray-300 hover:border-purple-500/50 hover:text-purple-400 transition-colors">
              <Download className="w-3.5 h-3.5" /> {fmt.toUpperCase()}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
