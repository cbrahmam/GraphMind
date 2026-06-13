import { useState, useEffect } from 'react'
import { HardDrive, Plus, RotateCcw, Trash2 } from 'lucide-react'

export default function BackupsPage() {
  const [backups, setBackups] = useState([])
  const [name, setName] = useState('')

  useEffect(() => { loadBackups() }, [])

  const loadBackups = async () => {
    try {
      const res = await fetch('/api/backups/')
      const data = await res.json()
      setBackups(data.backups || [])
    } catch (e) { console.error(e) }
  }

  const createBackup = async () => {
    try {
      await fetch('/api/backups/', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name }),
      })
      setName('')
      loadBackups()
    } catch (e) { console.error(e) }
  }

  const restore = async (backupName) => {
    if (!confirm(`Restore from "${backupName}"? This will replace the current graph.`)) return
    try {
      await fetch(`/api/backups/${backupName}/restore`, { method: 'POST' })
      alert('Restored successfully')
    } catch (e) { console.error(e) }
  }

  const deleteBackup = async (backupName) => {
    await fetch(`/api/backups/${backupName}`, { method: 'DELETE' })
    loadBackups()
  }

  return (
    <div className="p-6 max-w-5xl">
      <h1 className="text-xl font-bold text-white flex items-center gap-2 mb-6">
        <HardDrive className="w-5 h-5 text-teal-400" /> Backup & Restore
      </h1>

      <div className="flex gap-2 mb-6">
        <input value={name} onChange={e => setName(e.target.value)} placeholder="Backup name (optional)"
          className="flex-1 bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-gray-200" />
        <button onClick={createBackup}
          className="flex items-center gap-1.5 px-4 py-2 bg-teal-500/10 text-teal-400 rounded-lg hover:bg-teal-500/20">
          <Plus className="w-3.5 h-3.5" /> Create Backup
        </button>
      </div>

      <div className="space-y-2">
        {backups.map((b, i) => (
          <div key={i} className="bg-[#161b22] border border-[#30363d] rounded-lg p-3 flex items-center gap-3">
            <HardDrive className="w-4 h-4 text-teal-400" />
            <div className="flex-1">
              <div className="text-sm text-gray-200">{b.name}</div>
              <div className="text-xs text-gray-500">
                {b.created_at?.slice(0, 19)} — {b.node_count || '?'} nodes, {b.relationship_count || '?'} relationships
              </div>
            </div>
            <button onClick={() => restore(b.name)}
              className="flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300">
              <RotateCcw className="w-3 h-3" /> Restore
            </button>
            <button onClick={() => deleteBackup(b.name)}
              className="flex items-center gap-1 text-xs text-red-400 hover:text-red-300">
              <Trash2 className="w-3 h-3" />
            </button>
          </div>
        ))}
      </div>

      {backups.length === 0 && <p className="text-center text-gray-500 py-10">No backups yet</p>}
    </div>
  )
}
