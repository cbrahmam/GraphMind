import { useState, useEffect } from 'react'
import { Shield, BarChart3 } from 'lucide-react'

export default function AuditPage() {
  const [tab, setTab] = useState('logs')
  const [logs, setLogs] = useState([])
  const [stats, setStats] = useState(null)
  const [filter, setFilter] = useState({ action: '', user: '' })

  useEffect(() => { loadLogs() }, [])

  const loadLogs = async () => {
    try {
      const params = new URLSearchParams({ limit: '100' })
      if (filter.action) params.set('action', filter.action)
      if (filter.user) params.set('user', filter.user)
      const res = await fetch(`/api/audit/logs?${params}`)
      const data = await res.json()
      setLogs(data.logs || [])
    } catch (e) { console.error(e) }
  }

  const loadStats = async () => {
    setTab('stats')
    try {
      const res = await fetch('/api/audit/stats')
      setStats(await res.json())
    } catch (e) { console.error(e) }
  }

  return (
    <div className="p-6 max-w-5xl">
      <h1 className="text-xl font-bold text-white flex items-center gap-2 mb-6">
        <Shield className="w-5 h-5 text-green-400" /> Audit Log
      </h1>

      <div className="flex gap-2 mb-4">
        <button onClick={() => { setTab('logs'); loadLogs() }}
          className={`px-3 py-1.5 rounded-lg text-xs ${tab === 'logs' ? 'bg-green-500/10 text-green-400' : 'text-gray-400 bg-[#161b22]'}`}>
          Logs
        </button>
        <button onClick={loadStats}
          className={`px-3 py-1.5 rounded-lg text-xs ${tab === 'stats' ? 'bg-green-500/10 text-green-400' : 'text-gray-400 bg-[#161b22]'}`}>
          <BarChart3 className="w-3.5 h-3.5 inline mr-1" /> Statistics
        </button>
      </div>

      {tab === 'stats' && stats && (
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
            <h3 className="text-sm text-gray-400 mb-2">Total Events</h3>
            <div className="text-2xl font-bold text-green-400">{stats.total_events}</div>
          </div>
          <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
            <h3 className="text-sm text-gray-400 mb-2">Top Actions</h3>
            {Object.entries(stats.actions || {}).slice(0, 5).map(([k, v]) => (
              <div key={k} className="flex justify-between text-xs text-gray-300">
                <span>{k}</span><span className="text-gray-500">{v}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {tab === 'logs' && (
        <div className="space-y-1">
          {logs.map((l, i) => (
            <div key={i} className="bg-[#161b22] border border-[#30363d] rounded-lg p-2.5 flex items-center gap-3 text-xs">
              <span className="text-gray-500 w-36 shrink-0">{l.timestamp?.slice(0, 19)}</span>
              <span className="text-green-400 w-24 shrink-0">{l.action}</span>
              <span className="text-gray-300 flex-1">{l.resource}</span>
              <span className="text-gray-500">{l.user}</span>
            </div>
          ))}
          {logs.length === 0 && <p className="text-center text-gray-500 py-10">No audit log entries yet</p>}
        </div>
      )}
    </div>
  )
}
