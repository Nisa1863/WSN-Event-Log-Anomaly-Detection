import SimulationControl from './SimulationControl'
import StatCards from './StatCards'
import NetworkSimulation from './NetworkSimulation'
import AnomalyPanel from './AnomalyPanel'
import Charts from './Charts'

export default function Dashboard({ logs, anomalies, stats, loading, message, active, onStart }) {
  return (
    <div className="min-h-screen bg-slate-100">
      <header className="bg-white border-b border-slate-200 px-6 py-4">
        <h1 className="text-lg font-semibold text-slate-800">
          WSN Anomali İzleme Sistemi
        </h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Kablosuz algılayıcı ağ node davranışlarını analiz ederek anomalileri tespit eden görsel izleme sistemi
        </p>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-6 space-y-5">
        <div className="bg-white border border-slate-200 rounded-lg px-4 py-3">
          <SimulationControl loading={loading} message={message} onStart={onStart} />
        </div>

        <StatCards stats={stats} />

        {/* Ana odak: canlı ağ */}
        <section className="bg-white border border-slate-200 rounded-lg p-4">
          <h2 className="text-sm font-medium text-slate-700 mb-3">Canlı WSN Ağı</h2>
          <NetworkSimulation logs={logs} active={active} loading={loading} />
        </section>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          <AnomalyPanel anomalies={anomalies} />
          <div>
            <h2 className="text-sm font-medium text-slate-700 mb-3">Özet Grafikler</h2>
            <Charts logs={logs} />
          </div>
        </div>
      </main>

    </div>
  )
}
