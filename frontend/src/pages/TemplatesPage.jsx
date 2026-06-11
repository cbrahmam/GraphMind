import { useState, useEffect } from 'react'
import { Play, Trash2 } from 'lucide-react'
import { api } from '../api/client'

export default function TemplatesPage() {
  const [templates, setTemplates] = useState([])
  const [selectedTemplate, setSelectedTemplate] = useState(null)
  const [params, setParams] = useState({})
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    api.queryTemplates().then(setTemplates).catch(() => {})
  }, [])

  const selectTemplate = (t) => {
    setSelectedTemplate(t)
    setParams({ ...t.parameters })
    setResult(null)
  }

  const runTemplate = async () => {
    if (!selectedTemplate) return
    setLoading(true)
    setResult(null)
    try {
      const data = await api.runTemplate(selectedTemplate.id, params)
      setResult(data)
    } catch (e) {
      setResult({ error: e.message })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 max-w-5xl space-y-6">
      <h2 className="text-2xl font-bold text-white">Query Templates</h2>

      <div className="grid grid-cols-3 gap-4">
        <div className="col-span-1 space-y-2">
          {templates.map(t => (
            <button key={t.id} onClick={() => selectTemplate(t)} className={`w-full text-left p-3 rounded-lg border transition-colors ${selectedTemplate?.id === t.id ? 'bg-purple-500/10 border-purple-500/30 text-purple-400' : 'bg-[#161b22] border-[#30363d] text-gray-300 hover:border-[#484f58]'}`}>
              <div className="text-sm font-medium">{t.name}</div>
              <div className="text-xs text-gray-500 mt-0.5">{t.description}</div>
              {t.category && <span className="text-xs text-gray-600 mt-1 inline-block">{t.category}</span>}
            </button>
          ))}
        </div>

        <div className="col-span-2 space-y-4">
          {selectedTemplate ? (
            <>
              <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4">
                <h3 className="text-sm font-medium text-white mb-2">{selectedTemplate.name}</h3>
                <pre className="text-xs text-green-400 font-mono bg-[#0d1117] rounded-lg p-3 overflow-x-auto">{selectedTemplate.cypher}</pre>
                {Object.keys(params).length > 0 && (
                  <div className="mt-3 space-y-2">
                    <h4 className="text-xs text-gray-500 uppercase">Parameters</h4>
                    {Object.entries(params).map(([key, value]) => (
                      <div key={key} className="flex items-center gap-2">
                        <label className="text-xs text-gray-400 w-20">${key}</label>
                        <input value={value} onChange={e => setParams(prev => ({...prev, [key]: e.target.value}))} className="flex-1 bg-[#0d1117] border border-[#30363d] rounded px-2 py-1 text-sm text-gray-200 outline-none" />
                      </div>
                    ))}
                  </div>
                )}
                <button onClick={runTemplate} disabled={loading} className="mt-3 flex items-center gap-1.5 px-3 py-1.5 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 rounded-lg text-white text-sm">
                  <Play className="w-3.5 h-3.5" /> {loading ? 'Running...' : 'Run'}
                </button>
              </div>

              {result && !result.error && (
                <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4">
                  <h4 className="text-xs text-gray-500 uppercase mb-2">Results ({result.result_count})</h4>
                  <pre className="text-xs text-gray-300 font-mono overflow-auto max-h-80">{JSON.stringify(result.results, null, 2)}</pre>
                </div>
              )}
              {result?.error && (
                <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 text-red-400 text-sm">{result.error}</div>
              )}
            </>
          ) : (
            <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-8 text-center">
              <p className="text-gray-500 text-sm">Select a template to run</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
