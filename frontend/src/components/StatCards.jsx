const statusStyle = {
  Normal: 'bg-green-100 text-green-700',
  Dikkat: 'bg-amber-100 text-amber-700',
  Riskli: 'bg-red-100 text-red-700',
  'Veri Yok': 'bg-slate-100 text-slate-500',
}

export default function StatCards({ stats }) {
  const cards = [
    { label: 'Toplam Node', value: stats?.total_nodes ?? 10 },
    { label: 'Aktif Node', value: stats?.active_nodes ?? 0 },
    { label: 'Toplam Log', value: stats?.total_logs ?? 0 },
    { label: 'Tespit Edilen Anomali', value: stats?.anomaly_count ?? 0, highlight: true },
    { label: 'Anomali Node Sayısı', value: stats?.anomaly_nodes ?? 0, highlight: true },
    { label: 'Ortalama Pil', value: stats?.avg_battery ?? 0, unit: '%' },
    { label: 'Ortalama Hata Oranı', value: stats?.avg_error_rate ?? 0 },
  ]

  const status = stats?.system_status ?? 'Veri Yok'

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
      {cards.map((c) => (
        <div key={c.label} className="bg-white border border-slate-200 rounded-lg p-4">
          <p className="text-xs text-slate-500 mb-1">{c.label}</p>
          <p className={`text-xl font-semibold ${c.highlight ? 'text-red-600' : 'text-slate-800'}`}>
            {c.value}{c.unit && <span className="text-sm font-normal text-slate-500 ml-0.5">{c.unit}</span>}
          </p>
        </div>
      ))}
      <div className="bg-white border border-slate-200 rounded-lg p-4">
        <p className="text-xs text-slate-500 mb-1">Sistem Durumu</p>
        <span className={`inline-block px-2.5 py-1 rounded-full text-sm font-medium ${statusStyle[status]}`}>
          {status}
        </span>
        {stats?.riskiest_node && stats.riskiest_node !== 'Yok' && (
          <p className="text-xs text-slate-400 mt-2">En riskli: {stats.riskiest_node}</p>
        )}
      </div>
    </div>
  )
}
