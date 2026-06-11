import { useState, useEffect } from 'react'
import { Clock, GitBranch } from 'lucide-react'
import { api } from '../api/client'

export default function TimelinePage() {
  const [timeline, setTimeline] = useState([])
  const [feed, setFeed] = useState([])
  const [tab, setTab] = useState('timeline')

  useEffect(() => {
    api.timeline().then(setTimeline).catch(() => {})
    api.changeFeed(50).then(setFeed).catch(() => {})
  }, [])

  let cumulativeNodes = 0
  let cumulativeRels = 0
  const enriched = timeline.map(t => {
    cumulativeNodes += t.entities
    cumulativeRels += t.relationships
    return { ...t, cumulativeNodes, cumulativeRels }
  })
  const maxNodes = Math.max(1, ...enriched.map(t => t.cumulativeNodes))

  return (
    <div className="p-6 max-w-4xl space-y-6">
      <h2 className="text-2xl font-bold text-white">Timeline & Activity</h2>

      <div className="flex gap-2">
        {['timeline', 'feed'].map(t => (
          <button key={t} onClick={() => setTab(t)} className={`px-3 py-1.5 rounded-lg text-sm capitalize ${tab === t ? 'bg-purple-500/10 text-purple-400' : 'text-gray-400 hover:text-gray-200'}`}>
            {t}
          </button>
        ))}
      </div>

      {tab === 'timeline' && (
        <div className="space-y-3">
          {enriched.length === 0 && (
            <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-8 text-center">
              <Clock className="w-8 h-8 text-gray-600 mx-auto mb-2" />
              <p className="text-gray-500 text-sm">No extraction events yet.</p>
            </div>
          )}
          {enriched.map((t, i) => (
            <div key={i} className="bg-[#161b22] border border-[#30363d] rounded-xl p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-200">{t.document}</span>
                <span className="text-xs text-gray-500">{new Date(t.timestamp).toLocaleString()}</span>
              </div>
              <div className="flex items-center gap-4 text-xs text-gray-400 mb-2">
                <span>+{t.entities} entities</span>
                <span>+{t.relationships} relationships</span>
                <span className="text-gray-500">Total: {t.cumulativeNodes} nodes, {t.cumulativeRels} rels</span>
              </div>
              <div className="h-2 bg-[#0d1117] rounded-full overflow-hidden">
                <div className="h-full bg-purple-500 rounded-full transition-all" style={{ width: `${(t.cumulativeNodes / maxNodes) * 100}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}

      {tab === 'feed' && (
        <div className="space-y-1">
          {feed.length === 0 && <p className="text-gray-500 text-sm text-center py-8">No activity yet.</p>}
          {feed.map((entry, i) => (
            <div key={i} className="flex items-start gap-3 py-2 px-3 bg-[#161b22] border border-[#30363d] rounded-lg">
              <GitBranch className="w-3.5 h-3.5 text-gray-500 mt-0.5 shrink-0" />
              <div className="flex-1">
                <span className={`text-xs px-1.5 py-0.5 rounded mr-2 ${
                  entry.type?.includes('created') ? 'bg-green-500/10 text-green-400' :
                  entry.type?.includes('updated') ? 'bg-blue-500/10 text-blue-400' :
                  'bg-gray-500/10 text-gray-400'
                }`}>{entry.type}</span>
                <span className="text-xs text-gray-300">
                  {entry.name || entry.document || entry.from || ''} {entry.label ? `(${entry.label})` : ''}
                </span>
              </div>
              <span className="text-xs text-gray-600 shrink-0">{new Date(entry.timestamp).toLocaleTimeString()}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
