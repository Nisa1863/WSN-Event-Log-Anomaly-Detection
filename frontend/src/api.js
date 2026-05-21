const API = 'http://localhost:5001'

async function get(path, options = {}) {
  const res = await fetch(`${API}${path}`, options)
  const data = await res.json()
  if (!res.ok) throw new Error(data.message || 'Bağlantı hatası')
  return data
}

export const api = {
  startSimulation: () => get('/start-simulation', { method: 'POST' }),
  getLogs: () => get('/logs'),
  getAnomalies: () => get('/anomalies'),
  getStats: () => get('/dashboard-stats'),
}
