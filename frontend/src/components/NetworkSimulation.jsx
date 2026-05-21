import { useEffect, useMemo, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const POS = {
  Node_1: { x: 14, y: 22 }, Node_2: { x: 32, y: 14 }, Node_3: { x: 52, y: 18 },
  Node_4: { x: 72, y: 12 }, Node_5: { x: 86, y: 28 }, Node_6: { x: 18, y: 48 },
  Node_7: { x: 40, y: 52 }, Node_8: { x: 62, y: 44 }, Node_9: { x: 78, y: 58 },
  Node_10: { x: 48, y: 76 },
}

const LINKS = [
  ['Node_1', 'Node_2'], ['Node_1', 'Node_6'], ['Node_2', 'Node_3'], ['Node_2', 'Node_7'],
  ['Node_3', 'Node_4'], ['Node_4', 'Node_5'], ['Node_6', 'Node_7'], ['Node_7', 'Node_8'],
  ['Node_8', 'Node_9'], ['Node_7', 'Node_10'], ['Node_3', 'Node_8'],
]

// yeşil = normal, turuncu = şüpheli, kırmızı = hata
function nodeColor(status) {
  if (['communication_error', 'packet_loss', 'node_failure'].includes(status)) return '#ef4444'
  if (['suspicious_activity', 'energy_drop', 'node_silence'].includes(status)) return '#f97316'
  return '#22c55e'
}

function isAnomaly(state) {
  if (!state) return false
  return state.is_anomaly === true || state.is_anomaly === 1 ||
    ['suspicious_activity', 'energy_drop', 'node_silence', 'communication_error', 'packet_loss', 'node_failure'].includes(state.status)
}

function latestByNode(logs) {
  const m = {}
  logs.forEach((l) => {
    if (!m[l.node_id] || l.timestamp > m[l.node_id].timestamp) m[l.node_id] = l
  })
  return m
}

function Packet({ from, to, color, speed, onDone }) {
  const a = POS[from], b = POS[to]
  if (!a || !b) return null
  return (
    <motion.circle
      r="0.7" fill={color}
      initial={{ cx: a.x, cy: a.y, opacity: 0 }}
      animate={{ cx: [a.x, b.x], cy: [a.y, b.y], opacity: [0, 1, 0] }}
      transition={{ duration: speed, ease: 'linear' }}
      onAnimationComplete={onDone}
    />
  )
}

function Node({ id, state, running }) {
  const status = state?.status || 'normal'
  const color = nodeColor(status)
  const anomaly = isAnomaly(state)
  const pos = POS[id]

  return (
    <div
      className="absolute -translate-x-1/2 -translate-y-1/2 z-10"
      style={{ left: `${pos.x}%`, top: `${pos.y}%` }}
    >
      <div
        className="absolute rounded-full border border-dashed -translate-x-1/2 -translate-y-1/2 pointer-events-none"
        style={{ width: 64, height: 64, left: '50%', top: '50%', borderColor: color, opacity: 0.4 }}
      />

      {anomaly && (
        <motion.div
          className="absolute rounded-full border-2 -translate-x-1/2 -translate-y-1/2"
          style={{ width: 76, height: 76, left: '50%', top: '50%', borderColor: color }}
          animate={{ scale: [1, 1.2, 1], opacity: [0.6, 0.2, 0.6] }}
          transition={{ repeat: Infinity, duration: 1.5 }}
        />
      )}

      <motion.div
        className="w-9 h-9 rounded-full flex items-center justify-center text-white text-xs font-bold shadow"
        style={{ backgroundColor: color }}
        animate={anomaly ? { scale: [1, 1.1, 1] } : {}}
        transition={{ repeat: anomaly ? Infinity : 0, duration: 1 }}
      >
        {id.replace('Node_', '')}
      </motion.div>

      {/* Normal: sadece ad + pil */}
      <div className="absolute top-11 left-1/2 -translate-x-1/2 text-center text-[10px] whitespace-nowrap">
        <p className="font-medium text-slate-700">{id}</p>
        <p className="text-slate-500">%{state?.battery_level ?? '-'}</p>
      </div>

      {/* Anomali: detay kutusu */}
      {anomaly && state?.explanation && (
        <div className="absolute top-[4.5rem] left-1/2 -translate-x-1/2 w-28 bg-white border border-orange-200 rounded p-1.5 text-[9px] text-slate-600 shadow-sm z-20">
          {state.explanation}
        </div>
      )}
    </div>
  )
}

export default function NetworkSimulation({ logs, active, loading }) {
  const [packets, setPackets] = useState([])
  const states = useMemo(() => latestByNode(logs), [logs])
  const running = active || loading

  useEffect(() => {
    if (!running) { setPackets([]); return }
    const t = setInterval(() => {
      const links = LINKS.filter(([a, b]) =>
        states[a]?.status !== 'node_silence' && states[b]?.status !== 'node_silence'
      )
      if (!links.length) return
      const [from, to] = links[Math.floor(Math.random() * links.length)]
      const st = states[from]?.status || 'normal'
      const color = nodeColor(st) === '#22c55e' ? '#3b82f6' : nodeColor(st)
      const id = Date.now()
      setPackets((p) => [...p.slice(-15), { id, from, to, color, speed: st === 'suspicious_activity' ? 0.8 : 1.5 }])
    }, 500)
    return () => clearInterval(t)
  }, [running, states])

  return (
    <div
      className="relative rounded-xl border border-slate-200 bg-slate-50 overflow-hidden"
      style={{
        height: 460,
        backgroundImage: 'linear-gradient(#e2e8f0 1px, transparent 1px), linear-gradient(90deg, #e2e8f0 1px, transparent 1px)',
        backgroundSize: '20px 20px',
      }}
    >
      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
        {LINKS.map(([a, b]) => {
          const anomalyLink = isAnomaly(states[a]) || isAnomaly(states[b])
          return (
            <line
              key={`${a}-${b}`}
              x1={POS[a].x}
              y1={POS[a].y}
              x2={POS[b].x}
              y2={POS[b].y}
              stroke={anomalyLink ? '#fca5a5' : '#cbd5e1'}
              strokeWidth={anomalyLink ? 0.6 : 0.5}
              strokeLinecap="round"
              vectorEffect="non-scaling-stroke"
              opacity={anomalyLink ? 0.35 : 0.25}
            />
          )
        })}
        <AnimatePresence>
          {running && packets.map((p) => (
            <Packet key={p.id} {...p} onDone={() => setPackets((x) => x.filter((i) => i.id !== p.id))} />
          ))}
        </AnimatePresence>
      </svg>

      {Object.keys(POS).map((id) => (
        <Node key={id} id={id} state={states[id]} running={running} />
      ))}

      {!running && (
        <div className="absolute inset-0 flex items-center justify-center bg-white/50">
          <p className="text-slate-500 text-sm">Simülasyonu başlatın</p>
        </div>
      )}

      <div className="absolute bottom-2 left-2 flex gap-3 text-[10px] text-slate-500">
        <span><span className="inline-block w-2 h-2 rounded-full bg-green-500 mr-1" />Normal</span>
        <span><span className="inline-block w-2 h-2 rounded-full bg-orange-500 mr-1" />Şüpheli</span>
        <span><span className="inline-block w-2 h-2 rounded-full bg-red-500 mr-1" />Hata</span>
      </div>
    </div>
  )
}
