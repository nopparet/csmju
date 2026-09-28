import { useEffect, useState } from 'react'
import { api } from '../api'

const TYPE_TH = { student: 'นักศึกษา', teacher: 'อาจารย์', visitor: 'บุคคลภายนอก' }

export default function Dashboard({ go }) {
  const [d, setD] = useState(null)
  const [err, setErr] = useState(null)

  useEffect(() => { api.stats(7).then(setD).catch(() => setErr('โหลดสถิติไม่สำเร็จ')) }, [])

  if (err) return <><button className="back" onClick={() => go('menu')}>← กลับเมนูหลัก</button><p className="err">{err}</p></>
  if (!d) return <p className="lead">กำลังโหลด…</p>

  const max = Math.max(1, ...d.by_day.map((x) => x.count))

  return (
    <>
      <button className="back" onClick={() => go('menu')}>← กลับเมนูหลัก</button>
      <h1>สถิติผู้ใช้งาน</h1>
      <p className="lead">ย้อนหลัง {d.range_days} วัน</p>

      <div className="stats">
        <div><b>{d.total_visits}</b><small>ผู้ใช้งานรวม</small></div>
        <div><b>{d.chat.total}</b><small>คำถามที่ถามผู้ช่วย</small></div>
        <div><b>{d.chat.coverage}%</b><small>ตอบได้ (coverage)</small></div>
        <div><b>{d.by_type[0] ? TYPE_TH[d.by_type[0].type] : '-'}</b><small>กลุ่มที่ใช้มากที่สุด</small></div>
      </div>

      <h2>ผู้ใช้งานรายวัน</h2>
      <div className="bars">
        {d.by_day.map((x) => (
          <i key={x.date} style={{ height: `${(x.count / max) * 100}%` }}>
            <span>{x.count}</span>
          </i>
        ))}
      </div>

      <h2 style={{ marginTop: 24 }}>คำถามยอดนิยม</h2>
      {d.chat.top_intents.map((t) => (
        <div className="card" key={t.intent}><b>{t.intent}</b><small>{t.count} ครั้ง</small></div>
      ))}

      <h2 style={{ marginTop: 24 }}>คำถามที่ระบบยังตอบไม่ได้</h2>
      <p className="lead" style={{ fontSize: '.9rem' }}>นำไปเพิ่มเป็น intent ใหม่ในตาราง chat_intents</p>
      {d.chat.unanswered_samples.length === 0
        ? <div className="card"><b>ยังไม่มี</b><small>ระบบตอบได้ทุกคำถามในช่วงนี้</small></div>
        : d.chat.unanswered_samples.map((q, i) => <div className="card" key={i}><b>{q}</b></div>)}
    </>
  )
}
