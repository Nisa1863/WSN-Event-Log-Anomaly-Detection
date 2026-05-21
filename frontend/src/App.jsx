import { useState, useEffect, useCallback } from 'react'
import Dashboard from './components/Dashboard'
import { api } from './api'

function App() {
  const [logs, setLogs] = useState([])
  const [anomalies, setAnomalies] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [active, setActive] = useState(false)

  const loadData = useCallback(async () => {
    try {
      const [logsData, anomaliesData, statsData] = await Promise.all([
        api.getLogs(),
        api.getAnomalies(),
        api.getStats(),
      ])
      setLogs(logsData)
      setAnomalies(anomaliesData)
      setStats(statsData)
      if (logsData.length > 0) setActive(true)
    } catch {
      setMessage('Backend bağlantısı kurulamadı. npm run dev ile başlatın.')
    }
  }, [])

  useEffect(() => {
    loadData()
  }, [loadData])

  const startSimulation = async () => {
    setLoading(true)
    setMessage('')
    setActive(true)
    try {
      const res = await api.startSimulation()
      if (!res.success) throw new Error(res.message)
      setMessage(res.message)
      await loadData()
    } catch (e) {
      setMessage(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dashboard
      logs={logs}
      anomalies={anomalies}
      stats={stats}
      loading={loading}
      message={message}
      active={active}
      onStart={startSimulation}
    />
  )
}

export default App
