import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Clock } from 'lucide-react'
import useStore from '../store/useStore'

export default function HistoryPage() {
  const history = useStore(s => s.history)
  const fetchHistory = useStore(s => s.fetchHistory)
  const navigate = useNavigate()

  useEffect(() => { fetchHistory() }, [fetchHistory])

  return (
    <div className="p-6 max-w-4xl space-y-6">
      <h2 className="text-2xl font-bold text-white">Query History</h2>

      {history.length === 0 ? (
        <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-8 text-center">
          <Clock className="w-8 h-8 text-gray-600 mx-auto mb-2" />
          <p className="text-gray-500 text-sm">No queries yet. Ask a question to get started.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {history.map(item => (
            <div key={item.id} className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 hover:border-[#484f58] transition-colors cursor-pointer" onClick={() => navigate('/query', { state: { question: item.question } })}>
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <p className="text-sm text-gray-200">{item.question}</p>
                  {item.cypher && <p className="text-xs text-gray-500 font-mono mt-1 truncate">{item.cypher}</p>}
                </div>
                <div className="text-right shrink-0">
                  <span className="text-xs text-gray-500">{item.result_count} results</span>
                  <span className="text-xs text-gray-600 ml-2">{item.execution_time_ms}ms</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
