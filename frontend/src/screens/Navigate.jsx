import { useEffect, useState } from 'react'
import { api } from '../api'

// ขนาดห้องตามผังจริง
const ROOM_W = 135
const ROOM_H = 140

// ขนาดห้องพิเศษ (เล็กกว่า — ห้องเก็บของ, ห้องประชุม)
const SMALL_H = 65

// rooms ที่ควรแสดงขนาดเล็ก
const SMALL_ROOMS = ['STORE', 'MEET']

export default function Navigate({ go }) {
  const [rooms, setRooms] = useState([])
  const [sel, setSel] = useState(null)
  const [err, setErr] = useState(null)

  useEffect(() => {
    api.rooms().then(setRooms).catch(() => setErr('เชื่อมต่อฐานข้อมูลไม่ได้ กรุณาแจ้งผู้ดูแลระบบ'))
  }, [])

  const byCode = Object.fromEntries(rooms.map(r => [r.code, r]))

  const roomColor = (r) => {
    if (!r) return '#2a2a3a'
    if (r.code === sel?.code) return '#1a6b5a'
    if (r.type === 'lab') return '#1e3a5f'
    if (r.type === 'lecture') return '#3b2a5f'
    if (r.type === 'meeting') return '#3a3a1e'
    if (r.type === 'service') return '#2e2e2e'
    return '#2a2a3a'
  }

  const RoomBox = ({ code, x, y, w = ROOM_W, h = ROOM_H, labelOverride }) => {
    const r = byCode[code]
    if (!r && !labelOverride) return null
    const label = labelOverride || r?.code || code
    const sub = r?.name?.replace(/ห้องปฏิบัติการคอมพิวเตอร์/, 'Lab').replace(/ห้องบรรยายคอมพิวเตอร์/, 'Lect') || ''
    return (
      <g onClick={() => r && setSel(r)} style={{ cursor: r ? 'pointer' : 'default' }}>
        <rect x={x} y={y} width={w} height={h} rx="6"
          fill={roomColor(r)} stroke={sel?.code === code ? '#4ecca3' : '#444'} strokeWidth="2" />
        <text x={x + w / 2} y={y + h / 2 - 8} textAnchor="middle"
          fill="#fff" fontSize="15" fontWeight="bold">{label}</text>
        {sub && (
          <text x={x + w / 2} y={y + h / 2 + 12} textAnchor="middle"
            fill="#aaa" fontSize="10">{sub}</text>
        )}
      </g>
    )
  }

  return (
    <>
      <button className="back" onClick={() => go('menu')}>← กลับเมนูหลัก</button>
      <h1>นำทางภายในอาคาร</h1>
      <p className="lead">แตะห้องบนแผนผังเพื่อดูตำแหน่งและสถานะการใช้งาน</p>
      {err && <p className="err">{err}</p>}

      {/* SVG แผนผัง — ตามผังที่วาด */}
      <svg className="map" viewBox="0 0 760 340" role="img" aria-label="แผนผังชั้น 6 อาคาร 60 ปี">

        {/* ========== ห้องพักอาจารย์ (ซ้ายสุด) ========== */}
        <rect x="2" y="10" width="55" height="290" rx="4" fill="#1a3a2a" stroke="#4ecca3" strokeWidth="1.5" />
        <text x="30" y="85" textAnchor="middle" fill="#4ecca3" fontSize="9" transform="rotate(-90,30,85)">
          ห้องพักอาจารย์
        </text>

        {/* ========== บล็อกซ้าย: LAB-1, LAB-4, LAB-2, LAB-3 ========== */}
        <rect x="62" y="10" width="280" height="290" rx="6" fill="none" stroke="#555" strokeWidth="1.5" />

        <RoomBox code="LAB-1" x={64}  y={12}  w={136} h={143} />
        <RoomBox code="LAB-4" x={204} y={12}  w={136} h={143} />
        <RoomBox code="LAB-2" x={64}  y={157} w={136} h={141} />
        <RoomBox code="LAB-3" x={204} y={157} w={136} h={141} />

        {/* ========== บล็อกกลาง: NET, STORE, LAB-5 ========== */}
        <rect x="348" y="10" width="138" height="290" rx="6" fill="none" stroke="#555" strokeWidth="1.5" />

        <RoomBox code="NET"   x={350} y={12}  w={134} h={100} />
        <RoomBox code="STORE" x={350} y={115} w={134} h={65}  />
        <RoomBox code="LAB-5" x={350} y={183} w={134} h={115} />

        {/* ========== ช่องว่าง (ทางเดิน) ========== */}
        <text x="492" y="165" textAnchor="middle" fill="#555" fontSize="11">· · ·</text>

        {/* ========== บล็อกขวา: LECT-8, MEET, LECT-6 ========== */}
        <rect x="492" y="10" width="260" height="290" rx="6" fill="none" stroke="#555" strokeWidth="1.5" />

        <RoomBox code="LECT-8" x={494} y={12}  w={256} h={100} />
        <RoomBox code="MEET"   x={494} y={115} w={256} h={65}  />
        <RoomBox code="LECT-6" x={494} y={183} w={256} h={115} />

        {/* ========== ลิฟต์ (ด้านล่างกลาง) ========== */}
        <rect x="220" y="310" width="70" height="28" rx="4" fill="#333" stroke="#666" strokeWidth="1.5" />
        <text x="255" y="329" textAnchor="middle" fill="#aaa" fontSize="11">🛗 ลิฟต์</text>

      </svg>

      <div className="card" style={{ marginTop: 14 }}>
        {sel ? (
          <>
            <b>{sel.code} · {sel.name}</b>
            <small>
              ชั้น {sel.floor} · {sel.status}
              {sel.owner ? ` · ${sel.owner}` : ''}
              <br />{sel.hint}
            </small>
          </>
        ) : (
          <>
            <b>เลือกห้องเพื่อดูข้อมูล</b>
            <small>ระบบจะบอกชั้น เจ้าของห้อง เส้นทาง และสถานะการใช้งานตอนนี้</small>
          </>
        )}
      </div>
    </>
  )
}
