const LABELS = {
  suspicious_activity: 'Şüpheli aktivite',
  energy_drop: 'Enerji düşüşü',
  node_silence: 'Node sessizliği',
  communication_error: 'İletişim hatası',
  packet_loss: 'Paket kaybı',
  node_failure: 'Düğüm arızası',
}

export default function AnomalyPanel({ anomalies }) {
  const seen = new Set()
  const list = []
  anomalies.forEach((a) => {
    if (seen.has(a.node_id)) return
    seen.add(a.node_id)
    list.push(a)
  })

  return (
    <div className="bg-white border border-slate-200 rounded-lg p-4 h-full">
      <h3 className="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-red-500" />
        Anomali Uyarıları ({list.length})
      </h3>

      {list.length === 0 ? (
        <p className="text-sm text-slate-400 py-4">Anomali tespit edilmedi. Ağ normal çalışıyor.</p>
      ) : (
        <ul className="space-y-2 max-h-[420px] overflow-y-auto pr-1">
          {list.map((a) => (
            <li
              key={a.node_id}
              className="p-3 bg-red-50 border border-red-100 rounded-lg"
            >
              <p className="text-sm font-medium text-red-700">
                {a.node_id}
                <span className="text-slate-500 font-normal mx-1">—</span>
                {LABELS[a.status] || a.status}
              </p>
              <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                {a.explanation || `${a.node_id} anormal davranış tespit edildi.`}
              </p>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
