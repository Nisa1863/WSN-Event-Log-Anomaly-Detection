import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Tooltip,
  Legend,
} from 'chart.js'
import { Bar, Line } from 'react-chartjs-2'

ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, Tooltip, Legend)

const opts = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
}

function byNode(logs, field) {
  const map = {}
  logs.forEach((l) => {
    if (!map[l.node_id]) map[l.node_id] = []
    map[l.node_id].push(Number(l[field]) || 0)
  })
  const labels = Object.keys(map).sort()
  const values = labels.map((n) => {
    const arr = map[n]
    return Math.round(arr.reduce((a, b) => a + b, 0) / arr.length)
  })
  return { labels, values }
}

function anomalyByNode(logs) {
  const map = {}
  logs.forEach((l) => {
    if (l.is_anomaly) map[l.node_id] = (map[l.node_id] || 0) + 1
  })
  const labels = Object.keys(map).sort()
  return { labels, values: labels.map((n) => map[n]) }
}

export default function Charts({ logs }) {
  if (!logs.length) {
    return <p className="text-sm text-slate-400 text-center py-8">Grafik için simülasyon başlatın.</p>
  }

  const battery = byNode(logs, 'battery_level')
  const traffic = byNode(logs, 'packet_count')
  const anomaly = anomalyByNode(logs)

  const charts = [
    {
      title: 'Pil Seviyesi (%)',
      el: (
        <Line
          data={{
            labels: battery.labels,
            datasets: [{ data: battery.values, borderColor: '#22c55e', backgroundColor: '#22c55e22', fill: true, tension: 0.3 }],
          }}
          options={opts}
        />
      ),
    },
    {
      title: 'Anomali Sayısı',
      el: (
        <Bar
          data={{
            labels: anomaly.labels.length ? anomaly.labels : ['-'],
            datasets: [{ data: anomaly.values.length ? anomaly.values : [0], backgroundColor: '#ef4444' }],
          }}
          options={opts}
        />
      ),
    },
    {
      title: 'Node Trafiği (paket)',
      el: (
        <Bar
          data={{
            labels: traffic.labels,
            datasets: [{ data: traffic.values, backgroundColor: '#3b82f6' }],
          }}
          options={opts}
        />
      ),
    },
  ]

  return (
    <div className="space-y-4">
      {charts.map((c) => (
        <div key={c.title} className="bg-white border border-slate-200 rounded-lg p-4">
          <h3 className="text-sm font-medium text-slate-700 mb-2">{c.title}</h3>
          <div className="h-40">{c.el}</div>
        </div>
      ))}
    </div>
  )
}
