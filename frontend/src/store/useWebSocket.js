import { useEffect, useRef, useCallback } from 'react'
import useStore from './useStore'

export default function useWebSocket() {
  const wsRef = useRef(null)
  const fetchStats = useStore(s => s.fetchStats)
  const fetchGraph = useStore(s => s.fetchGraph)

  const connect = useCallback(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws`)

    ws.onmessage = (event) => {
      try {
        const { event: eventType } = JSON.parse(event.data)
        if (eventType === 'extraction_complete' || eventType === 'graph_updated') {
          fetchStats()
          fetchGraph()
        }
      } catch {}
    }

    ws.onclose = () => {
      setTimeout(connect, 3000)
    }

    wsRef.current = ws
  }, [fetchStats, fetchGraph])

  useEffect(() => {
    connect()
    return () => wsRef.current?.close()
  }, [connect])

  return wsRef
}
