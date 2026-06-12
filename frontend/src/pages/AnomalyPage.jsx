import { useState } from 'react'
import { AlertTriangle, Shield, RefreshCw } from 'lucide-react'

export default function AnomalyPage() {
  const [audit, setAudit] = useState(null)
  const [loading, setLoading] = useState(false)

  const runAudit = async () => {
    setLoading(true)
    try {
      const res = await fetch('/api/anomaly/audit')
      const data = await res.json()
      setAudit(data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const severityColor = (s) => ({ high: 'text-red-400 bg-red-400/10', medium: 'text-yellow-400 bg-yellow-400/10', low: 'text-blue-400 bg-blue-400/10' }[s] || 'text-gray-400')

  return (
    <div className="p-6 max-w-5xl">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-yellow-400" /> Anomaly Detection
          </h1>
          <p className="text-sm text-gray-500 mt-1">Find contradictions, outliers, and structural issues</p>
        </div>
        <button onClick={runAudit} disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-yellow-500/10 text-yellow-400 rounded-lg hover:bg-yellow-500/20 disabled:opacity-50">
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          {loading ? 'Scanning...' : 'Run Full Audit'}
        </button>
      </div>

      {audit && (
        <>
          <div className="grid grid-cols-4 gap-3 mb-6">
            {[
              { label: 'Total', value: audit.total_anomalies, color: 'text-white' },
              { label: 'High', value: audit.by_severity?.high || 0, color: 'text-red-400' },
              { label: 'Medium', value: audit.by_severity?.medium || 0, color: 'text-yellow-400' },
              { label: 'Low', value: audit.by_severity?.low || 0, color: 'text-blue-400' },
            ].map(s => (
              <div key={s.label} className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 text-center">
                <div className={`text-2xl font-bold ${s.color}`}>{s.value}</div>
                <div className="text-xs text-gray-500">{s.label}</div>
              </div>
            ))}
          </div>

          <div className="space-y-2">
            {audit.anomalies?.map((a, i) => (
              <div key={i} className="bg-[#161b22] border border-[#30363d] rounded-lg p-3 flex items-start gap-3">
                <span className={`text-xs px-2 py-0.5 rounded-full ${severityColor(a.severity)}`}>{a.severity}</span>
                <div className="flex-1">
                  <div className="text-sm text-gray-200">{a.description}</div>
                  <div className="text-xs text-gray-500 mt-1">{a.type}</div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {!audit && !loading && (
        <div className="text-center py-20 text-gray-500">
          <Shield className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p>Click "Run Full Audit" to scan your graph for anomalies</p>
        </div>
      )}
    </div>
  )
}
