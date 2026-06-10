import { NavLink } from 'react-router-dom'
import { useEffect } from 'react'
import { LayoutDashboard, Network, MessageSquare, Upload, Settings, History, Brain } from 'lucide-react'
import useStore from '../store/useStore'

const links = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/graph', icon: Network, label: 'Graph Explorer' },
  { to: '/query', icon: MessageSquare, label: 'Query' },
  { to: '/ingest', icon: Upload, label: 'Ingest Data' },
  { to: '/schema', icon: Settings, label: 'Schema' },
  { to: '/insights', icon: Brain, label: 'Insights' },
  { to: '/history', icon: History, label: 'History' },
]

export default function Sidebar() {
  const stats = useStore(s => s.stats)
  const fetchStats = useStore(s => s.fetchStats)

  useEffect(() => { fetchStats() }, [fetchStats])

  return (
    <aside className="w-64 bg-[#161b22] border-r border-[#30363d] flex flex-col shrink-0">
      <div className="p-5 border-b border-[#30363d]">
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <Network className="w-6 h-6 text-purple-400" />
          GraphMind
        </h1>
        <p className="text-xs text-gray-500 mt-1">AI Knowledge Graph Builder</p>
      </div>

      <nav className="flex-1 p-3 space-y-1">
        {links.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                isActive
                  ? 'bg-purple-500/10 text-purple-400'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-[#1c2128]'
              }`
            }
          >
            <Icon className="w-4 h-4" />
            {label}
          </NavLink>
        ))}
      </nav>

      {stats && (
        <div className="p-4 border-t border-[#30363d] text-xs text-gray-500 space-y-1">
          <div className="flex justify-between">
            <span>Nodes</span>
            <span className="text-gray-300">{stats.total_nodes ?? 0}</span>
          </div>
          <div className="flex justify-between">
            <span>Relationships</span>
            <span className="text-gray-300">{stats.total_relationships ?? 0}</span>
          </div>
        </div>
      )}
    </aside>
  )
}
