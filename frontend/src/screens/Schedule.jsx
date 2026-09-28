import { useEffect, useState } from 'react'
import { api } from '../api'

const DAYS = [['mon', 'จันทร์'], ['tue', 'อังคาร'], ['wed', 'พุธ'],
              ['thu', 'พฤหัสบดี'], ['fri', 'ศุกร์']]

export default function Schedule({ go }) {
  const [day, setDay] = useState(DAYS[Math.min(new Date().getDay() - 1, 4)]?.[0] || 'mon')
  const [rows, setRows] = useState([])
  const [err, setErr] = useState(null)

  useEffect(() => {
    api.schedule({ day })
      .then((d) => { setRows(d.items); setErr(null) })
      .catch(() => setErr('โหลดตารางไม่สำเร็จ ลองใหม่อีกครั้ง'))
  }, [day])

  return (
    <>
      <button className="back" onClick={() => go('menu')}>← กลับเมนูหลัก</button>
      <h1>ตารางเรียน-สอน</h1>
      <p className="lead">แถวที่เน้นสีคือคาบที่กำลังเรียนอยู่ตอนนี้</p>

      <div className="chips">
        {DAYS.map(([k, th]) => (
          <button key={k} className="chip" aria-pressed={day === k} onClick={() => setDay(k)}>
            {th}
          </button>
        ))}
      </div>

      {err && <p className="err">{err}</p>}
      {!err && rows.length === 0 && <div className="card"><b>วันนี้ไม่มีคาบเรียน</b><small>ลองเลือกวันอื่น</small></div>}

      {rows.length > 0 && (
        <table>
          <thead>
            <tr><th>เวลา</th><th>วิชา</th><th>ผู้สอน</th><th>ห้อง</th><th>ชั้นปี</th></tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.schedule_id} className={r.is_now ? 'now' : ''}>
                <td>{r.start_time}–{r.end_time}</td>
                <td>{r.course_code} {r.course_name}</td>
                <td>{r.teacher}</td>
                <td>{r.room}</td>
                <td>{r.year_level ? `ปี ${r.year_level}` : '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </>
  )
}
