import { useEffect, useState, useRef } from 'react'
import ForceGraph3D from 'react-force-graph-3d'
import { Search } from 'lucide-react'
import useStore from '../store/useStore'
import DetailPanel from '../components/DetailPanel'

const COLORS = {
  Person: '#3b82f6', Organization: '#22c55e', Technology: '#a855f7',
  Location: '#f97316', Event: '#ef4444', Concept: '#14b8a6', Product: '#ec4899',
}

export default function Graph3D() {
  const graphData = useStore(s => s.graphData)
  const selectedNode = useStore(s => s.selectedNode)
  const setSelectedNode = useStore(s => s.setSelectedNode)
  const fetchGraph = useStore(s => s.fetchGraph)
  const loading = useStore(s => s.loading)
  const [search, setSearch] = useState('')
  const graphRef = useRef()
  const containerRef = useRef()
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 })

  useEffect(() => { fetchGraph() }, [fetchGraph])

  useEffect(() => {
    const el = containerRef.current
    if (!el) return
    const obs = new ResizeObserver(([e]) => {
      setDimensions({ width: e.contentRect.width, height: e.contentRect.height })
    })
    obs.observe(el)
    return () => obs.disconnect()
  }, [])

  const data = graphData || { nodes: [], links: [] }

  return (
    <div className="flex h-full">
      <div className="flex-1 flex flex-col" ref={containerRef}>
        <div className="flex items-center gap-2 p-3 border-b border-[#30363d] bg-[#161b22]">
          <div className="flex items-center flex-1 bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-1.5">
            <Search className="w-4 h-4 text-gray-500 mr-2" />
            <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search entities..." className="bg-transparent text-sm text-gray-300 outline-none flex-1" />
          </div>
          <span className="text-xs text-gray-500">{data.nodes.length} nodes, {data.links.length} edges</span>
        </div>
        <div className="flex-1 relative">
          {loading && (
            <div className="absolute inset-0 flex items-center justify-center bg-[#0d1117]/80 z-10">
              <div className="text-gray-400 text-sm">Loading 3D graph...</div>
            </div>
          )}
          <ForceGraph3D
            ref={graphRef}
            graphData={data}
            width={dimensions.width}
            height={dimensions.height - 52}
            backgroundColor="#0D1117"
            nodeLabel={n => `${n.name} (${n.label || n._label || ''})`}
            nodeColor={n => COLORS[n.label || n._label] || '#6b7280'}
            nodeRelSize={4}
            linkColor={() => '#30363d'}
            linkWidth={0.3}
            linkDirectionalArrowLength={3}
            onNodeClick={(node) => setSelectedNode(node)}
          />
        </div>
      </div>
      {selectedNode && <DetailPanel node={selectedNode} onClose={() => setSelectedNode(null)} />}
    </div>
  )
}
