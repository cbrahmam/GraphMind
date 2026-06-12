import { useState, useEffect } from 'react'
import { Rss, Plus, Trash2, Download } from 'lucide-react'

export default function RSSPage() {
  const [feeds, setFeeds] = useState([])
  const [url, setUrl] = useState('')
  const [name, setName] = useState('')
  const [articles, setArticles] = useState([])

  useEffect(() => { loadFeeds() }, [])

  const loadFeeds = async () => {
    try {
      const res = await fetch('/api/rss/feeds')
      const data = await res.json()
      setFeeds(data.feeds || [])
    } catch (e) { console.error(e) }
  }

  const addFeed = async () => {
    if (!url.trim()) return
    try {
      await fetch('/api/rss/feeds', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, name }),
      })
      setUrl('')
      setName('')
      loadFeeds()
    } catch (e) { console.error(e) }
  }

  const fetchFeed = async (feedId) => {
    try {
      const res = await fetch(`/api/rss/feeds/${feedId}/fetch`, { method: 'POST' })
      const data = await res.json()
      setArticles(data.articles || [])
      loadFeeds()
    } catch (e) { console.error(e) }
  }

  const deleteFeed = async (feedId) => {
    await fetch(`/api/rss/feeds/${feedId}`, { method: 'DELETE' })
    loadFeeds()
  }

  return (
    <div className="p-6 max-w-5xl">
      <h1 className="text-xl font-bold text-white flex items-center gap-2 mb-6">
        <Rss className="w-5 h-5 text-orange-400" /> RSS Feed Ingestion
      </h1>

      <div className="flex gap-2 mb-6">
        <input value={url} onChange={e => setUrl(e.target.value)} placeholder="Feed URL..."
          className="flex-1 bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-gray-200" />
        <input value={name} onChange={e => setName(e.target.value)} placeholder="Name (optional)"
          className="w-48 bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-gray-200" />
        <button onClick={addFeed} className="px-4 py-2 bg-orange-500/10 text-orange-400 rounded-lg hover:bg-orange-500/20">
          <Plus className="w-4 h-4" />
        </button>
      </div>

      <div className="space-y-2 mb-6">
        {feeds.map(f => (
          <div key={f.id} className="bg-[#161b22] border border-[#30363d] rounded-lg p-3 flex items-center gap-3">
            <Rss className="w-4 h-4 text-orange-400" />
            <div className="flex-1">
              <div className="text-sm text-gray-200">{f.name}</div>
              <div className="text-xs text-gray-500">{f.url}</div>
            </div>
            <span className="text-xs text-gray-500">{f.article_count || 0} articles</span>
            <button onClick={() => fetchFeed(f.id)} className="text-xs text-blue-400 hover:text-blue-300">
              <Download className="w-3.5 h-3.5" />
            </button>
            <button onClick={() => deleteFeed(f.id)} className="text-xs text-red-400 hover:text-red-300">
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          </div>
        ))}
      </div>

      {articles.length > 0 && (
        <div>
          <h2 className="text-sm font-medium text-gray-400 mb-3">Fetched Articles ({articles.length})</h2>
          <div className="space-y-2">
            {articles.map((a, i) => (
              <div key={i} className="bg-[#161b22] border border-[#30363d] rounded-lg p-3">
                <div className="text-sm text-gray-200">{a.title}</div>
                <div className="text-xs text-gray-500 mt-1 line-clamp-2">{a.content?.slice(0, 200)}</div>
                {a.published && <div className="text-xs text-gray-600 mt-1">{a.published}</div>}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
