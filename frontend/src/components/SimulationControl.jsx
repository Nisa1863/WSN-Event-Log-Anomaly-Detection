export default function SimulationControl({ loading, message, onStart }) {
  return (
    <div className="flex flex-wrap items-center gap-4">
      <button
        onClick={onStart}
        disabled={loading}
        className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-lg text-sm font-medium disabled:opacity-50"
      >
        {loading ? 'Çalışıyor...' : 'Simülasyonu Başlat'}
      </button>
      {message && (
        <p className="text-sm text-slate-600">{message}</p>
      )}
    </div>
  )
}
