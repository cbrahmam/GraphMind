import { useState } from 'react'
import { FileText, Download, Code, Globe } from 'lucide-react'

export default function ReportsPage() {
  const [preview, setPreview] = useState(null)
  const [format, setFormat] = useState(null)

  const loadReport = async (fmt) => {
    setFormat(fmt)
    try {
      const res = await fetch(`/api/reports/${fmt}`)
      if (fmt === 'json') {
        const data = await res.json()
        setPreview(JSON.stringify(data, null, 2))
      } else {
        const text = await res.text()
        setPreview(text)
      }
    } catch (e) {
      console.error(e)
      setPreview('Error loading report')
    }
  }

  const downloadReport = (fmt) => {
    const extensions = { text: 'txt', json: 'json', html: 'html' }
    const blob = new Blob([preview], { type: fmt === 'json' ? 'application/json' : fmt === 'html' ? 'text/html' : 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `graphmind-report.${extensions[fmt]}`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="p-6 max-w-5xl">
      <h1 className="text-xl font-bold text-white flex items-center gap-2 mb-2">
        <FileText className="w-5 h-5 text-green-400" /> Reports
      </h1>
      <p className="text-sm text-gray-500 mb-6">Generate and download knowledge graph reports</p>

      <div className="grid grid-cols-3 gap-3 mb-6">
        {[
          { fmt: 'text', label: 'Text Report', icon: FileText, desc: 'Plain text summary' },
          { fmt: 'json', label: 'JSON Report', icon: Code, desc: 'Machine-readable data' },
          { fmt: 'html', label: 'HTML Report', icon: Globe, desc: 'Styled web report' },
        ].map(r => (
          <button key={r.fmt} onClick={() => loadReport(r.fmt)}
            className={`bg-[#161b22] border rounded-lg p-4 text-left hover:bg-[#1c2128] transition-colors ${
              format === r.fmt ? 'border-green-500/50' : 'border-[#30363d]'
            }`}>
            <r.icon className="w-5 h-5 text-green-400 mb-2" />
            <div className="text-sm text-gray-200">{r.label}</div>
            <div className="text-xs text-gray-500">{r.desc}</div>
          </button>
        ))}
      </div>

      {preview && (
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Preview</span>
            <button onClick={() => downloadReport(format)}
              className="flex items-center gap-1.5 text-xs text-green-400 hover:text-green-300">
              <Download className="w-3.5 h-3.5" /> Download
            </button>
          </div>
          {format === 'html' ? (
            <iframe srcDoc={preview} className="w-full h-[500px] rounded-lg border border-[#30363d]" />
          ) : (
            <pre className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 text-xs text-gray-300 overflow-auto max-h-[500px] whitespace-pre-wrap">
              {preview}
            </pre>
          )}
        </div>
      )}
    </div>
  )
}
