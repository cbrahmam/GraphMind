import { NavLink } from 'react-router-dom'
import { useEffect } from 'react'
import {
  LayoutDashboard, Network, Box, MessageSquare, FileText, Upload,
  Settings, History, Brain, Clock, Eye, GitCompare, Sliders,
  AlertTriangle, Sparkles, Search, Crown, Rss, FileBarChart,
  Database, Shield, Route, FlaskConical, Shapes, FlaskRound,
  ShieldAlert, Copy, HardDrive, Bell, GitBranch
} from 'lucide-react'
import useStore from '../store/useStore'

const links = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/graph', icon: Network, label: 'Graph 2D' },
  { to: '/graph3d', icon: Box, label: 'Graph 3D' },
  { to: '/query', icon: MessageSquare, label: 'Query' },
  { to: '/templates', icon: FileText, label: 'Templates' },
  { to: '/ingest', icon: Upload, label: 'Ingest Data' },
  { to: '/rss', icon: Rss, label: 'RSS Feeds' },
  { to: '/schema', icon: Sliders, label: 'Schema' },
  { to: '/insights', icon: Brain, label: 'Insights' },
  { to: '/pathfinder', icon: Route, label: 'Path Finder' },
  { to: '/comparison', icon: GitBranch, label: 'Compare' },
  { to: '/hypothesis', icon: FlaskConical, label: 'Hypothesis' },
  { to: '/predictions', icon: Sparkles, label: 'Predictions' },
  { to: '/influence', icon: Crown, label: 'Influence' },
  { to: '/gaps', icon: Search, label: 'Gaps' },
  { to: '/anomaly', icon: AlertTriangle, label: 'Anomalies' },
  { to: '/motifs', icon: Shapes, label: 'Motifs' },
  { to: '/whatif', icon: FlaskRound, label: 'What-If' },
  { to: '/resilience', icon: ShieldAlert, label: 'Resilience' },
  { to: '/duplicates', icon: Copy, label: 'Duplicates' },
  { to: '/vectors', icon: Database, label: 'Vectors' },
  { to: '/timeline', icon: Clock, label: 'Timeline' },
  { to: '/watchlist', icon: Eye, label: 'Watchlist' },
  { to: '/diff', icon: GitCompare, label: 'Graph Diff' },
  { to: '/reports', icon: FileBarChart, label: 'Reports' },
  { to: '/backups', icon: HardDrive, label: 'Backups' },
  { to: '/notifications', icon: Bell, label: 'Notifications' },
  { to: '/audit', icon: Shield, label: 'Audit Log' },
  { to: '/history', icon: History, label: 'History' },
  { to: '/settings', icon: Settings, label: 'Settings' },
]

export default function Sidebar() {
  const stats = useStore(s => s.stats)
  const fetchStats = useStore(s => s.fetchStats)

  useEffect(() => { fetchStats() }, [fetchStats])

  return (
    <aside className="w-56 bg-[#161b22] border-r border-[#30363d] flex flex-col shrink-0">
      <div className="p-4 border-b border-[#30363d]">
        <h1 className="text-lg font-bold text-white flex items-center gap-2">
          <Network className="w-5 h-5 text-purple-400" />
          GraphMind
        </h1>
        <p className="text-xs text-gray-500 mt-0.5">AI Knowledge Graph Builder</p>
      </div>

      <nav className="flex-1 p-2 space-y-0.5 overflow-y-auto">
        {links.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg text-xs transition-colors ${
                isActive
                  ? 'bg-purple-500/10 text-purple-400'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-[#1c2128]'
              }`
            }
          >
            <Icon className="w-3.5 h-3.5" />
            {label}
          </NavLink>
        ))}
      </nav>

      {stats && (
        <div className="p-3 border-t border-[#30363d] text-xs text-gray-500 space-y-0.5">
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
