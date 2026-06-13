import { useState, useEffect } from 'react'
import { Bell, Check, Trash2 } from 'lucide-react'

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState([])
  const [unreadCount, setUnreadCount] = useState(0)

  useEffect(() => { load() }, [])

  const load = async () => {
    try {
      const [nRes, cRes] = await Promise.all([
        fetch('/api/notifications/').then(r => r.json()),
        fetch('/api/notifications/unread-count').then(r => r.json()),
      ])
      setNotifications(nRes.notifications || [])
      setUnreadCount(cRes.count || 0)
    } catch (e) { console.error(e) }
  }

  const markRead = async (id) => {
    await fetch(`/api/notifications/${id}/read`, { method: 'PUT' })
    load()
  }

  const markAllRead = async () => {
    await fetch('/api/notifications/read-all', { method: 'PUT' })
    load()
  }

  const remove = async (id) => {
    await fetch(`/api/notifications/${id}`, { method: 'DELETE' })
    load()
  }

  const catColor = (c) => ({
    info: 'text-blue-400', warning: 'text-yellow-400', error: 'text-red-400', success: 'text-green-400',
  }[c] || 'text-gray-400')

  return (
    <div className="p-6 max-w-5xl">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <Bell className="w-5 h-5 text-blue-400" /> Notifications
          {unreadCount > 0 && <span className="text-xs bg-blue-500 text-white px-2 py-0.5 rounded-full">{unreadCount}</span>}
        </h1>
        {unreadCount > 0 && (
          <button onClick={markAllRead} className="text-xs text-blue-400 hover:text-blue-300">
            <Check className="w-3.5 h-3.5 inline mr-1" /> Mark all read
          </button>
        )}
      </div>

      <div className="space-y-1">
        {notifications.map(n => (
          <div key={n.id} className={`bg-[#161b22] border rounded-lg p-3 flex items-start gap-3 ${
            n.read ? 'border-[#30363d]' : 'border-blue-500/30'
          }`}>
            <div className={`w-2 h-2 rounded-full mt-1.5 ${n.read ? 'bg-gray-600' : 'bg-blue-400'}`} />
            <div className="flex-1">
              <div className="text-sm text-gray-200">{n.title}</div>
              <div className="text-xs text-gray-500">{n.message}</div>
              <div className="text-xs text-gray-600 mt-1 flex gap-2">
                <span className={catColor(n.category)}>{n.category}</span>
                <span>{n.created_at?.slice(0, 19)}</span>
              </div>
            </div>
            <div className="flex gap-1">
              {!n.read && (
                <button onClick={() => markRead(n.id)} className="text-gray-500 hover:text-blue-400">
                  <Check className="w-3.5 h-3.5" />
                </button>
              )}
              <button onClick={() => remove(n.id)} className="text-gray-500 hover:text-red-400">
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {notifications.length === 0 && <p className="text-center text-gray-500 py-10">No notifications</p>}
    </div>
  )
}
