import { useState, useEffect } from 'react'
import { Eye, Bell, Trash2, Plus } from 'lucide-react'
import { api } from '../api/client'

export default function WatchlistPage() {
  const [watches, setWatches] = useState([])
  const [alerts, setAlerts] = useState([])
  const [pattern, setPattern] = useState('')
  const [tab, setTab] = useState('watches')

  const refresh = () => {
    api.getWatchlist().then(setWatches).catch(() => {})
    api.getAlerts().then(setAlerts).catch(() => {})
  }

  useEffect(refresh, [])

  const addWatch = async () => {
    if (!pattern.trim()) return
    await api.addWatch(pattern)
    setPattern('')
    refresh()
  }

  const removeWatch = async (id) => {
    await api.removeWatch(id)
    refresh()
  }

  const markRead = async (id) => {
    await api.markAlertRead(id)
    refresh()
  }

  const unreadCount = alerts.filter(a => !a.read).length

  return (
    <div className="p-6 max-w-3xl space-y-6">
      <h2 className="text-2xl font-bold text-white">Watchlist & Alerts</h2>

      <div className="flex gap-2">
        <button onClick={() => setTab('watches')} className={`px-3 py-1.5 rounded-lg text-sm flex items-center gap-1.5 ${tab === 'watches' ? 'bg-purple-500/10 text-purple-400' : 'text-gray-400'}`}>
          <Eye className="w-3.5 h-3.5" /> Watches
        </button>
        <button onClick={() => setTab('alerts')} className={`px-3 py-1.5 rounded-lg text-sm flex items-center gap-1.5 ${tab === 'alerts' ? 'bg-purple-500/10 text-purple-400' : 'text-gray-400'}`}>
          <Bell className="w-3.5 h-3.5" /> Alerts {unreadCount > 0 && <span className="bg-red-500 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center">{unreadCount}</span>}
        </button>
      </div>

      {tab === 'watches' && (
        <div className="space-y-4">
          <div className="flex gap-2">
            <input value={pattern} onChange={e => setPattern(e.target.value)} onKeyDown={e => e.key === 'Enter' && addWatch()} placeholder="Entity name pattern to watch..." className="flex-1 bg-[#161b22] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-gray-200 outline-none focus:border-purple-500/50" />
            <button onClick={addWatch} className="px-3 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-white text-sm"><Plus className="w-4 h-4" /></button>
          </div>
          <div className="space-y-2">
            {watches.map(w => (
              <div key={w.id} className="bg-[#161b22] border border-[#30363d] rounded-lg p-3 flex items-center justify-between">
                <div>
                  <span className="text-sm text-gray-200">{w.pattern}</span>
                  {w.label && <span className="ml-2 text-xs text-gray-500">{w.label}</span>}
                </div>
                <button onClick={() => removeWatch(w.id)} className="text-gray-500 hover:text-red-400"><Trash2 className="w-3.5 h-3.5" /></button>
              </div>
            ))}
            {!watches.length && <p className="text-gray-500 text-sm text-center py-4">No watches yet.</p>}
          </div>
        </div>
      )}

      {tab === 'alerts' && (
        <div className="space-y-2">
          {alerts.map(a => (
            <div key={a.id} className={`bg-[#161b22] border rounded-lg p-3 flex items-center justify-between ${a.read ? 'border-[#30363d]' : 'border-yellow-500/30'}`}>
              <div>
                <span className="text-sm text-gray-200">{a.entity_name}</span>
                <span className="ml-2 text-xs text-gray-500">matched "{a.pattern}"</span>
                <span className="ml-2 text-xs text-gray-600">{new Date(a.timestamp).toLocaleString()}</span>
              </div>
              {!a.read && <button onClick={() => markRead(a.id)} className="text-xs text-purple-400 hover:text-purple-300">Mark read</button>}
            </div>
          ))}
          {!alerts.length && <p className="text-gray-500 text-sm text-center py-4">No alerts yet.</p>}
        </div>
      )}
    </div>
  )
}
