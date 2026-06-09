import { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { Send, Code, ChevronDown, ChevronUp } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import useStore from '../store/useStore'
import { api } from '../api/client'

export default function QueryPage() {
  const location = useLocation()
  const suggestions = useStore(s => s.suggestions)
  const fetchSuggestions = useStore(s => s.fetchSuggestions)

  const [question, setQuestion] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [showCypher, setShowCypher] = useState(false)
  const [advancedMode, setAdvancedMode] = useState(false)
  const [cypher, setCypher] = useState('')
  const [cypherResult, setCypherResult] = useState(null)

  useEffect(() => { fetchSuggestions() }, [fetchSuggestions])
  useEffect(() => {
    if (location.state?.question) {
      setQuestion(location.state.question)
    }
  }, [location.state])

  const askQuestion = async (q) => {
    const text = q || question
    if (!text.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const data = await api.askQuestion(text)
      setResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const runCypher = async () => {
    if (!cypher.trim()) return
    setLoading(true)
    setError(null)
    setCypherResult(null)
    try {
      const data = await api.runCypher(cypher)
      setCypherResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 max-w-4xl space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">Query</h2>
        <button
          onClick={() => setAdvancedMode(!advancedMode)}
          className={`flex items-center gap-1 text-xs px-3 py-1.5 rounded-lg border transition-colors ${advancedMode ? 'border-purple-500 text-purple-400' : 'border-[#30363d] text-gray-400'}`}
        >
          <Code className="w-3 h-3" /> Advanced Mode
        </button>
      </div>

      {!advancedMode ? (
        <div>
          <div className="flex gap-2">
            <input
              value={question}
              onChange={e => setQuestion(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && askQuestion()}
              placeholder="Ask anything about your knowledge graph..."
              className="flex-1 bg-[#161b22] border border-[#30363d] rounded-lg px-4 py-3 text-gray-200 outline-none focus:border-purple-500/50 text-sm"
            />
            <button onClick={() => askQuestion()} disabled={loading} className="px-4 py-3 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 rounded-lg text-white text-sm transition-colors">
              <Send className="w-4 h-4" />
            </button>
          </div>

          {suggestions.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-3">
              {suggestions.map((q, i) => (
                <button key={i} onClick={() => { setQuestion(q); askQuestion(q) }} className="px-3 py-1 bg-[#161b22] border border-[#30363d] rounded-full text-xs text-gray-400 hover:border-purple-500/50 hover:text-purple-400 transition-colors">
                  {q}
                </button>
              ))}
            </div>
          )}
        </div>
      ) : (
        <div>
          <textarea
            value={cypher}
            onChange={e => setCypher(e.target.value)}
            placeholder="MATCH (n) RETURN n LIMIT 25"
            rows={5}
            className="w-full bg-[#161b22] border border-[#30363d] rounded-lg px-4 py-3 text-gray-200 outline-none focus:border-purple-500/50 text-sm font-mono"
          />
          <button onClick={runCypher} disabled={loading} className="mt-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 rounded-lg text-white text-sm transition-colors">
            Run Query
          </button>
        </div>
      )}

      {loading && <div className="text-center text-gray-400 text-sm py-8">Thinking...</div>}
      {error && <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-red-400 text-sm">{error}</div>}

      {result && (
        <div className="space-y-4">
          <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-5">
            <div className="prose prose-invert prose-sm max-w-none">
              <ReactMarkdown>{result.formatted_answer || 'No answer generated.'}</ReactMarkdown>
            </div>
          </div>

          {result.results?.length > 0 && (
            <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4 overflow-x-auto">
              <h4 className="text-xs text-gray-500 uppercase tracking-wide mb-2">Results ({result.result_count})</h4>
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-[#30363d]">
                    {Object.keys(result.results[0]).map(k => (
                      <th key={k} className="text-left text-gray-400 py-2 px-2 font-medium text-xs">{k}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {result.results.slice(0, 25).map((row, i) => (
                    <tr key={i} className="border-b border-[#30363d]/50">
                      {Object.values(row).map((v, j) => (
                        <td key={j} className="py-1.5 px-2 text-gray-300 text-xs">
                          {typeof v === 'object' ? JSON.stringify(v) : String(v ?? '')}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {result.query?.cypher && (
            <div className="bg-[#161b22] border border-[#30363d] rounded-xl">
              <button onClick={() => setShowCypher(!showCypher)} className="flex items-center justify-between w-full p-3 text-xs text-gray-400 hover:text-gray-300">
                <span>Generated Cypher</span>
                {showCypher ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
              </button>
              {showCypher && (
                <pre className="px-4 pb-3 text-xs text-green-400 font-mono overflow-x-auto">{result.query.cypher}</pre>
              )}
            </div>
          )}
        </div>
      )}

      {cypherResult && (
        <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4 overflow-x-auto">
          <h4 className="text-xs text-gray-500 uppercase tracking-wide mb-2">Results ({cypherResult.result_count})</h4>
          <pre className="text-xs text-gray-300 font-mono whitespace-pre-wrap">{JSON.stringify(cypherResult.results, null, 2)}</pre>
        </div>
      )}
    </div>
  )
}
