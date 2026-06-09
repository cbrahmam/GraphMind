import { useEffect, useState } from 'react'
import { X, ExternalLink } from 'lucide-react'
import { api } from '../api/client'

export default function DetailPanel({ node, onClose }) {
  const [details, setDetails] = useState(null)

  useEffect(() => {
    if (node?.id) {
      api.graphNode(node.id).then(setDetails).catch(() => setDetails(null))
    }
  }, [node?.id])

  if (!node) return null

  const props = details || node
  const relationships = details?.relationships || []
  const grouped = {}
  for (const rel of relationships) {
    const key = rel.type + (rel.outgoing ? ' ->' : ' <-')
    if (!grouped[key]) grouped[key] = []
    grouped[key].push(rel)
  }

  return (
    <div className="w-80 bg-[#161b22] border-l border-[#30363d] flex flex-col shrink-0 overflow-auto">
      <div className="flex items-center justify-between p-4 border-b border-[#30363d]">
        <h3 className="font-semibold text-white truncate">{props.name || 'Unknown'}</h3>
        <button onClick={onClose} className="text-gray-500 hover:text-gray-300"><X className="w-4 h-4" /></button>
      </div>

      <div className="p-4 space-y-4 text-sm">
        {props._label && (
          <span className="inline-block px-2 py-0.5 rounded-full text-xs bg-purple-500/10 text-purple-400">
            {props._label || props.label}
          </span>
        )}

        <div>
          <h4 className="text-xs text-gray-500 uppercase tracking-wide mb-2">Properties</h4>
          <div className="space-y-1">
            {Object.entries(props)
              .filter(([k]) => !['id', 'labels', 'relationships', 'name'].includes(k) && !k.startsWith('_'))
              .map(([k, v]) => (
                <div key={k} className="flex justify-between gap-2">
                  <span className="text-gray-500">{k}</span>
                  <span className="text-gray-300 text-right truncate max-w-[160px]">{String(v)}</span>
                </div>
              ))}
          </div>
        </div>

        {Object.keys(grouped).length > 0 && (
          <div>
            <h4 className="text-xs text-gray-500 uppercase tracking-wide mb-2">Relationships</h4>
            <div className="space-y-2">
              {Object.entries(grouped).map(([type, rels]) => (
                <div key={type}>
                  <span className="text-xs text-blue-400">{type}</span>
                  <div className="ml-2 space-y-0.5">
                    {rels.map((r, i) => (
                      <div key={i} className="text-xs text-gray-300">{r.target_name}</div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {props._source && (
          <div>
            <h4 className="text-xs text-gray-500 uppercase tracking-wide mb-2">Source</h4>
            <span className="text-xs text-gray-400">{props._source}</span>
          </div>
        )}
      </div>
    </div>
  )
}
