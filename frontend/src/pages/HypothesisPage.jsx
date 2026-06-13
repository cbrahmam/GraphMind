import { useState } from 'react'
import { FlaskConical, CheckCircle, XCircle, HelpCircle } from 'lucide-react'

export default function HypothesisPage() {
  const [tab, setTab] = useState('connection')
  const [entityA, setEntityA] = useState('')
  const [entityB, setEntityB] = useState('')
  const [via, setVia] = useState('')
  const [question, setQuestion] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const testConnection = async () => {
    if (!entityA.trim() || !entityB.trim()) return
    setLoading(true)
    try {
      let url = `/api/hypothesis/test?entity_a=${encodeURIComponent(entityA)}&entity_b=${encodeURIComponent(entityB)}`
      if (via.trim()) url += `&via=${encodeURIComponent(via)}`
      const res = await fetch(url)
      setResult(await res.json())
    } catch (e) { console.error(e) } finally { setLoading(false) }
  }

  const testNL = async () => {
    if (!question.trim()) return
    setLoading(true)
    try {
      const res = await fetch('/api/hypothesis/natural', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      })
      setResult(await res.json())
    } catch (e) { console.error(e) } finally { setLoading(false) }
  }

  const icon = result?.result === 'confirmed' || result?.answer === 'yes'
    ? <CheckCircle className="w-5 h-5 text-green-400" />
    : result?.result === 'not_confirmed' || result?.answer === 'no'
    ? <XCircle className="w-5 h-5 text-red-400" />
    : <HelpCircle className="w-5 h-5 text-yellow-400" />

  return (
    <div className="p-6 max-w-5xl">
      <h1 className="text-xl font-bold text-white flex items-center gap-2 mb-6">
        <FlaskConical className="w-5 h-5 text-emerald-400" /> Hypothesis Testing
      </h1>

      <div className="flex gap-2 mb-6">
        <button onClick={() => setTab('connection')}
          className={`px-3 py-1.5 rounded-lg text-xs ${tab === 'connection' ? 'bg-emerald-500/10 text-emerald-400' : 'text-gray-400 bg-[#161b22]'}`}>
          Connection Test
        </button>
        <button onClick={() => setTab('natural')}
          className={`px-3 py-1.5 rounded-lg text-xs ${tab === 'natural' ? 'bg-emerald-500/10 text-emerald-400' : 'text-gray-400 bg-[#161b22]'}`}>
          Natural Language
        </button>
      </div>

      {tab === 'connection' && (
        <div className="space-y-2 mb-6">
          <div className="flex gap-2">
            <input value={entityA} onChange={e => setEntityA(e.target.value)} placeholder="Entity A"
              className="flex-1 bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-gray-200" />
            <input value={entityB} onChange={e => setEntityB(e.target.value)} placeholder="Entity B"
              className="flex-1 bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-gray-200" />
          </div>
          <input value={via} onChange={e => setVia(e.target.value)} placeholder="Through entity (optional)"
            className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-gray-200" />
          <button onClick={testConnection} disabled={loading}
            className="px-4 py-2 bg-emerald-500/10 text-emerald-400 rounded-lg hover:bg-emerald-500/20">
            {loading ? 'Testing...' : 'Test Hypothesis'}
          </button>
        </div>
      )}

      {tab === 'natural' && (
        <div className="space-y-2 mb-6">
          <textarea value={question} onChange={e => setQuestion(e.target.value)} rows={3}
            placeholder="Ask a question about your knowledge graph..."
            className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-gray-200" />
          <button onClick={testNL} disabled={loading}
            className="px-4 py-2 bg-emerald-500/10 text-emerald-400 rounded-lg hover:bg-emerald-500/20">
            {loading ? 'Analyzing...' : 'Test'}
          </button>
        </div>
      )}

      {result && (
        <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            {icon}
            <span className="text-white font-medium">{result.result || result.answer || 'Result'}</span>
            <span className="text-sm text-gray-500 ml-auto">
              Confidence: {Math.round((result.confidence || 0) * 100)}%
            </span>
          </div>
          {result.explanation && <p className="text-sm text-gray-300 mb-2">{result.explanation}</p>}
          {result.paths?.length > 0 && (
            <div className="mt-2">
              <div className="text-xs text-gray-500 mb-1">Paths found: {result.paths_found}</div>
              {result.paths.map((p, i) => (
                <div key={i} className="text-xs text-gray-400">{p.nodes?.join(' → ')}</div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
