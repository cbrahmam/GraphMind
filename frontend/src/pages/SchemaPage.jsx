import { useState, useEffect } from 'react'
import { api } from '../api/client'

export default function SchemaPage() {
  const [schema, setSchema] = useState(null)
  const [presets, setPresets] = useState({})
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState(null)

  useEffect(() => {
    api.getSchema().then(setSchema).catch(() => {})
    api.getPresets().then(setPresets).catch(() => {})
  }, [])

  const loadPreset = async (name) => {
    setLoading(true)
    try {
      const data = await api.loadPreset(name)
      setSchema(data)
      setMessage(`Loaded "${name}" preset`)
    } catch (e) {
      setMessage(`Error: ${e.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 max-w-4xl space-y-6">
      <h2 className="text-2xl font-bold text-white">Schema</h2>

      <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4">
        <h3 className="text-sm font-medium text-gray-400 mb-3">Schema Presets</h3>
        <div className="flex flex-wrap gap-2">
          {Object.keys(presets).map(name => (
            <button key={name} onClick={() => loadPreset(name)} disabled={loading} className="px-3 py-1.5 bg-[#0d1117] border border-[#30363d] rounded-lg text-sm text-gray-300 hover:border-purple-500/50 hover:text-purple-400 transition-colors disabled:opacity-50">
              {name}
            </button>
          ))}
        </div>
      </div>

      {message && (
        <div className={`p-3 rounded-lg text-sm ${message.startsWith('Error') ? 'bg-red-500/10 text-red-400' : 'bg-green-500/10 text-green-400'}`}>
          {message}
        </div>
      )}

      {schema && (
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4">
            <h3 className="text-sm font-medium text-gray-400 mb-3">Entity Types ({schema.entity_types?.length || 0})</h3>
            <div className="space-y-2">
              {(schema.entity_types || []).map(et => (
                <div key={et.label} className="bg-[#0d1117] rounded-lg p-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-white">{et.label}</span>
                    <span className="text-xs text-gray-500">{et.properties?.length || 0} props</span>
                  </div>
                  {et.description && <p className="text-xs text-gray-500 mt-1">{et.description}</p>}
                  {et.properties?.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {et.properties.map(p => (
                        <span key={p} className="text-xs px-1.5 py-0.5 bg-[#161b22] rounded text-gray-400">{p}</span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4">
            <h3 className="text-sm font-medium text-gray-400 mb-3">Relationship Types ({schema.relationship_types?.length || 0})</h3>
            <div className="space-y-2">
              {(schema.relationship_types || []).map(rt => (
                <div key={rt.type} className="bg-[#0d1117] rounded-lg p-3">
                  <span className="text-sm font-medium text-white">{rt.type}</span>
                  {rt.description && <p className="text-xs text-gray-500 mt-1">{rt.description}</p>}
                  {(rt.from_types || rt.to_types) && (
                    <p className="text-xs text-gray-500 mt-1">
                      {(rt.from_types || []).join(', ')} {'->'} {(rt.to_types || []).join(', ')}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
