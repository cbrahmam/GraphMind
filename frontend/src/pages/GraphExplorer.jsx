import { useEffect, useState, useCallback, useRef } from 'react'
import ForceGraph2D from 'react-force-graph-2d'
import { Search, Filter } from 'lucide-react'
import useStore from '../store/useStore'
import { api } from '../api/client'
import DetailPanel from '../components/DetailPanel'

const COLORS = {
  Person: '#3b82f6', Organization: '#22c55e', Technology: '#a855f7',
  Location: '#f97316', Event: '#ef4444', Concept: '#14b8a6', Product: '#ec4899',
}

export default function GraphExplorer() {
  const graphData = useStore(s => s.graphData)
  const selectedNode = useStore(s => s.selectedNode)
  const setSelectedNode = useStore(s => s.setSelectedNode)
  const fetchGraph = useStore(s => s.fetchGraph)
  const loading = useStore(s => s.loading)

  const [search, setSearch] = useState('')
  const [visibleLabels, setVisibleLabels] = useState(new Set())
  const [visibleRels, setVisibleRels] = useState(new Set())
  const [showFilters, setShowFilters] = useState(false)
  const graphRef = useRef()
  const containerRef = useRef()
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 })

  useEffect(() => { fetchGraph() }, [fetchGraph])

  useEffect(() => {
    if (graphData?.nodes) {
      const labels = new Set(graphData.nodes.map(n => n.label || n._label).filter(Boolean))
      const rels = new Set(graphData.links.map(l => l.type).filter(Boolean))
      setVisibleLabels(labels)
      setVisibleRels(rels)
    }
  }, [graphData])

  useEffect(() => {
    const el = containerRef.current
    if (!el) return
    const obs = new ResizeObserver(([e]) => {
      setDimensions({ width: e.contentRect.width, height: e.contentRect.height })
    })
    obs.observe(el)
    return () => obs.disconnect()
  }, [])

  const filteredData = (() => {
    if (!graphData) return { nodes: [], links: [] }
    const nodes = graphData.nodes.filter(n => {
      const label = n.label || n._label || ''
      if (visibleLabels.size && !visibleLabels.has(label)) return false
      if (search && !n.name?.toLowerCase().includes(search.toLowerCase())) return false
      return true
    })
    const nodeIds = new Set(nodes.map(n => n.id))
    const links = graphData.links.filter(l => {
      const src = typeof l.source === 'object' ? l.source.id : l.source
      const tgt = typeof l.target === 'object' ? l.target.id : l.target
      return nodeIds.has(src) && nodeIds.has(tgt) && (!visibleRels.size || visibleRels.has(l.type))
    })
    return { nodes, links }
  })()

  const handleNodeClick = useCallback((node) => {
    setSelectedNode(node)
    if (graphRef.current) {
      graphRef.current.centerAt(node.x, node.y, 400)
      graphRef.current.zoom(2, 400)
    }
  }, [setSelectedNode])

  const handleSearch = () => {
    if (!search || !graphRef.current) return
    const node = filteredData.nodes.find(n => n.name?.toLowerCase().includes(search.toLowerCase()))
    if (node) {
      setSelectedNode(node)
      graphRef.current.centerAt(node.x, node.y, 400)
      graphRef.current.zoom(2, 400)
    }
  }

  const allLabels = graphData?.nodes ? [...new Set(graphData.nodes.map(n => n.label || n._label).filter(Boolean))] : []
  const allRels = graphData?.links ? [...new Set(graphData.links.map(l => l.type).filter(Boolean))] : []

  const toggleLabel = (label) => {
    setVisibleLabels(prev => {
      const next = new Set(prev)
      next.has(label) ? next.delete(label) : next.add(label)
      return next
    })
  }

  const toggleRel = (rel) => {
    setVisibleRels(prev => {
      const next = new Set(prev)
      next.has(rel) ? next.delete(rel) : next.add(rel)
      return next
    })
  }

  return (
    <div className="flex h-full">
      <div className="flex-1 flex flex-col" ref={containerRef}>
        <div className="flex items-center gap-2 p-3 border-b border-[#30363d] bg-[#161b22]">
          <div className="flex items-center flex-1 bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-1.5">
            <Search className="w-4 h-4 text-gray-500 mr-2" />
            <input
              value={search}
              onChange={e => setSearch(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSearch()}
              placeholder="Search entities..."
              className="bg-transparent text-sm text-gray-300 outline-none flex-1"
            />
          </div>
          <button onClick={() => setShowFilters(!showFilters)} className={`p-2 rounded-lg border transition-colors ${showFilters ? 'border-purple-500 text-purple-400' : 'border-[#30363d] text-gray-400 hover:text-gray-200'}`}>
            <Filter className="w-4 h-4" />
          </button>
        </div>

        {showFilters && (
          <div className="p-3 border-b border-[#30363d] bg-[#161b22] flex gap-6 text-xs">
            <div>
              <span className="text-gray-500 uppercase tracking-wider">Labels</span>
              <div className="flex flex-wrap gap-1 mt-1">
                {allLabels.map(label => (
                  <button key={label} onClick={() => toggleLabel(label)} className={`px-2 py-0.5 rounded-full border transition-colors ${visibleLabels.has(label) ? 'border-purple-500/50 text-purple-400 bg-purple-500/10' : 'border-[#30363d] text-gray-500'}`}>
                    <span className="inline-block w-2 h-2 rounded-full mr-1" style={{ backgroundColor: COLORS[label] || '#6b7280' }} />
                    {label}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <span className="text-gray-500 uppercase tracking-wider">Relationships</span>
              <div className="flex flex-wrap gap-1 mt-1">
                {allRels.map(rel => (
                  <button key={rel} onClick={() => toggleRel(rel)} className={`px-2 py-0.5 rounded-full border transition-colors ${visibleRels.has(rel) ? 'border-blue-500/50 text-blue-400 bg-blue-500/10' : 'border-[#30363d] text-gray-500'}`}>
                    {rel}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        <div className="flex-1 relative">
          {loading && (
            <div className="absolute inset-0 flex items-center justify-center bg-[#0d1117]/80 z-10">
              <div className="text-gray-400 text-sm">Loading graph...</div>
            </div>
          )}
          <ForceGraph2D
            ref={graphRef}
            graphData={filteredData}
            width={dimensions.width}
            height={dimensions.height - 52}
            backgroundColor="#0D1117"
            nodeLabel={n => `${n.name} (${n.label || n._label || ''})`}
            nodeColor={n => COLORS[n.label || n._label] || '#6b7280'}
            nodeRelSize={5}
            nodeVal={n => {
              const links = filteredData.links.filter(l => {
                const src = typeof l.source === 'object' ? l.source.id : l.source
                const tgt = typeof l.target === 'object' ? l.target.id : l.target
                return src === n.id || tgt === n.id
              })
              return Math.max(1, links.length)
            }}
            nodeCanvasObject={(node, ctx, globalScale) => {
              const label = node.name || ''
              const color = COLORS[node.label || node._label] || '#6b7280'
              const size = Math.max(3, Math.sqrt(node.val || 1) * 3)

              ctx.beginPath()
              ctx.arc(node.x, node.y, size, 0, 2 * Math.PI)
              ctx.fillStyle = selectedNode?.id === node.id ? '#fff' : color
              ctx.fill()

              if (globalScale > 1.2) {
                ctx.font = `${Math.max(2, 10 / globalScale)}px sans-serif`
                ctx.textAlign = 'center'
                ctx.fillStyle = '#e6edf3'
                ctx.fillText(label, node.x, node.y + size + 8 / globalScale)
              }
            }}
            linkColor={() => '#30363d'}
            linkWidth={0.5}
            linkDirectionalArrowLength={3}
            linkDirectionalArrowRelPos={1}
            onNodeClick={handleNodeClick}
            onNodeDragEnd={node => { node.fx = node.x; node.fy = node.y }}
            cooldownTicks={100}
          />
        </div>
      </div>

      {selectedNode && <DetailPanel node={selectedNode} onClose={() => setSelectedNode(null)} />}
    </div>
  )
}
