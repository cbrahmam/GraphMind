import { useState } from 'react'
import { Upload, Globe, Type, Table } from 'lucide-react'
import { api } from '../api/client'
import useStore from '../store/useStore'

const TABS = [
  { key: 'document', label: 'Upload Document', icon: Upload },
  { key: 'url', label: 'Import URL', icon: Globe },
  { key: 'text', label: 'Paste Text', icon: Type },
  { key: 'csv', label: 'Import CSV', icon: Table },
]

export default function IngestPage() {
  const [tab, setTab] = useState('document')
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [progress, setProgress] = useState([])
  const fetchStats = useStore(s => s.fetchStats)
  const fetchIngestions = useStore(s => s.fetchIngestions)

  // Document upload
  const [file, setFile] = useState(null)

  // URL
  const [url, setUrl] = useState('')

  // Text
  const [text, setText] = useState('')
  const [title, setTitle] = useState('')

  // CSV
  const [csvFile, setCsvFile] = useState(null)
  const [csvDoc, setCsvDoc] = useState(null)
  const [csvMapping, setCsvMapping] = useState({ entity_column: '', entity_label: 'Organization', property_columns: [], relationship_columns: [] })

  const addProgress = (msg) => setProgress(prev => [...prev, msg])

  const runPipeline = async (docId) => {
    addProgress('Running extraction pipeline...')
    try {
      const result = await api.extractPipeline(docId)
      addProgress(`Extracted ${result.entities_extracted} entities and ${result.relationships_extracted} relationships`)
      if (result.resolved_entities !== undefined) {
        addProgress(`Resolved to ${result.resolved_entities} unique entities (${result.merges} merges)`)
      }
      if (result.graph_result) {
        addProgress(`Graph: ${result.graph_result.nodes_created} nodes created, ${result.graph_result.relationships_created} relationships created`)
      }
      addProgress('Done!')
      setStatus('success')
      fetchStats()
      fetchIngestions()
    } catch (e) {
      addProgress(`Pipeline error: ${e.message}`)
      setStatus('error')
    }
  }

  const handleDocument = async () => {
    if (!file) return
    setLoading(true)
    setError(null)
    setProgress([])
    setStatus(null)
    addProgress(`Uploading ${file.name}...`)
    try {
      const doc = await api.ingestDocument(file)
      addProgress(`Parsed: ${doc.total_characters} characters, ${doc.total_chunks} chunks`)
      await runPipeline(doc.document_id)
    } catch (e) {
      setError(e.message)
      setStatus('error')
    } finally {
      setLoading(false)
    }
  }

  const handleUrl = async () => {
    if (!url.trim()) return
    setLoading(true)
    setError(null)
    setProgress([])
    setStatus(null)
    addProgress(`Fetching ${url}...`)
    try {
      const doc = await api.ingestUrl(url)
      addProgress(`Parsed: ${doc.total_characters} characters, ${doc.total_chunks} chunks`)
      await runPipeline(doc.document_id)
    } catch (e) {
      setError(e.message)
      setStatus('error')
    } finally {
      setLoading(false)
    }
  }

  const handleText = async () => {
    if (!text.trim()) return
    setLoading(true)
    setError(null)
    setProgress([])
    setStatus(null)
    addProgress('Processing text...')
    try {
      const doc = await api.ingestText(text, title || 'Pasted Text')
      addProgress(`Parsed: ${doc.total_characters} characters, ${doc.total_chunks} chunks`)
      await runPipeline(doc.document_id)
    } catch (e) {
      setError(e.message)
      setStatus('error')
    } finally {
      setLoading(false)
    }
  }

  const handleCsvUpload = async () => {
    if (!csvFile) return
    setLoading(true)
    setError(null)
    setProgress([])
    addProgress(`Uploading ${csvFile.name}...`)
    try {
      const doc = await api.ingestCsv(csvFile)
      setCsvDoc(doc)
      addProgress(`CSV parsed: ${doc.columns?.length || 0} columns detected`)
      if (doc.columns?.length) {
        setCsvMapping(prev => ({ ...prev, entity_column: doc.columns[0].name || doc.columns[0] }))
      }
      setStatus('csv_ready')
    } catch (e) {
      setError(e.message)
      setStatus('error')
    } finally {
      setLoading(false)
    }
  }

  const handleCsvImport = async () => {
    if (!csvDoc) return
    setLoading(true)
    addProgress('Importing CSV to graph...')
    try {
      const result = await api.csvImport(csvDoc.document_id, csvMapping)
      const gr = result.graph_result
      addProgress(`Imported: ${gr.nodes_created} nodes, ${gr.relationships_created} relationships`)
      addProgress('Done!')
      setStatus('success')
      fetchStats()
      fetchIngestions()
    } catch (e) {
      addProgress(`Import error: ${e.message}`)
      setStatus('error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 max-w-3xl space-y-6">
      <h2 className="text-2xl font-bold text-white">Ingest Data</h2>

      <div className="flex gap-1 bg-[#161b22] rounded-lg p-1 border border-[#30363d]">
        {TABS.map(({ key, label, icon: Icon }) => (
          <button key={key} onClick={() => { setTab(key); setStatus(null); setProgress([]); setError(null) }} className={`flex items-center gap-1.5 px-3 py-2 rounded-md text-sm transition-colors flex-1 justify-center ${tab === key ? 'bg-purple-500/10 text-purple-400' : 'text-gray-400 hover:text-gray-200'}`}>
            <Icon className="w-3.5 h-3.5" /> {label}
          </button>
        ))}
      </div>

      <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-5 space-y-4">
        {tab === 'document' && (
          <>
            <div className="border-2 border-dashed border-[#30363d] rounded-lg p-8 text-center">
              <input type="file" onChange={e => setFile(e.target.files?.[0])} accept=".pdf,.docx,.txt,.md,.html,.json" className="hidden" id="file-upload" />
              <label htmlFor="file-upload" className="cursor-pointer">
                <Upload className="w-8 h-8 text-gray-500 mx-auto mb-2" />
                <p className="text-sm text-gray-400">{file ? file.name : 'Click to upload (PDF, DOCX, TXT, MD, HTML, JSON)'}</p>
              </label>
            </div>
            <button onClick={handleDocument} disabled={!file || loading} className="w-full py-2 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 rounded-lg text-white text-sm transition-colors">
              {loading ? 'Processing...' : 'Upload & Extract'}
            </button>
          </>
        )}

        {tab === 'url' && (
          <>
            <input value={url} onChange={e => setUrl(e.target.value)} placeholder="https://example.com/article" className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg px-4 py-2.5 text-sm text-gray-200 outline-none focus:border-purple-500/50" />
            <button onClick={handleUrl} disabled={!url.trim() || loading} className="w-full py-2 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 rounded-lg text-white text-sm transition-colors">
              {loading ? 'Processing...' : 'Fetch & Extract'}
            </button>
          </>
        )}

        {tab === 'text' && (
          <>
            <input value={title} onChange={e => setTitle(e.target.value)} placeholder="Title (optional)" className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg px-4 py-2.5 text-sm text-gray-200 outline-none focus:border-purple-500/50" />
            <textarea value={text} onChange={e => setText(e.target.value)} placeholder="Paste your text here..." rows={6} className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg px-4 py-2.5 text-sm text-gray-200 outline-none focus:border-purple-500/50" />
            <button onClick={handleText} disabled={!text.trim() || loading} className="w-full py-2 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 rounded-lg text-white text-sm transition-colors">
              {loading ? 'Processing...' : 'Extract'}
            </button>
          </>
        )}

        {tab === 'csv' && (
          <>
            <div className="border-2 border-dashed border-[#30363d] rounded-lg p-8 text-center">
              <input type="file" onChange={e => setCsvFile(e.target.files?.[0])} accept=".csv" className="hidden" id="csv-upload" />
              <label htmlFor="csv-upload" className="cursor-pointer">
                <Table className="w-8 h-8 text-gray-500 mx-auto mb-2" />
                <p className="text-sm text-gray-400">{csvFile ? csvFile.name : 'Click to upload CSV'}</p>
              </label>
            </div>
            {!csvDoc && (
              <button onClick={handleCsvUpload} disabled={!csvFile || loading} className="w-full py-2 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 rounded-lg text-white text-sm transition-colors">
                Upload CSV
              </button>
            )}
            {csvDoc && (
              <div className="space-y-3">
                <h4 className="text-sm text-gray-400">Column Mapping</h4>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs text-gray-500">Entity Column</label>
                    <select value={csvMapping.entity_column} onChange={e => setCsvMapping(prev => ({...prev, entity_column: e.target.value}))} className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-gray-200 mt-1">
                      {(csvDoc.columns || []).map(c => <option key={c.name || c} value={c.name || c}>{c.name || c}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="text-xs text-gray-500">Entity Label</label>
                    <input value={csvMapping.entity_label} onChange={e => setCsvMapping(prev => ({...prev, entity_label: e.target.value}))} className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-gray-200 mt-1" />
                  </div>
                </div>
                <button onClick={handleCsvImport} disabled={loading} className="w-full py-2 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 rounded-lg text-white text-sm transition-colors">
                  {loading ? 'Importing...' : 'Import to Graph'}
                </button>
              </div>
            )}
          </>
        )}
      </div>

      {error && <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-red-400 text-sm">{error}</div>}

      {progress.length > 0 && (
        <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4 space-y-1">
          {progress.map((msg, i) => (
            <div key={i} className="flex items-start gap-2 text-sm">
              <span className={`mt-1 w-1.5 h-1.5 rounded-full shrink-0 ${i === progress.length - 1 && status !== 'success' ? 'bg-yellow-400 animate-pulse' : 'bg-green-400'}`} />
              <span className="text-gray-300">{msg}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
