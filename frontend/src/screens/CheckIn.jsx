import { useEffect, useState } from 'react'
import { api } from '../api'

export default function CheckIn({ go }) {
  const [session, setSession] = useState(null)
  const [code, setCode] = useState('')
  const [res, setRes] = useState(null)

  const load = () => api.currentSession().then(setSession).catch(() => setSession({ open: false }))
  useEffect(() => { load() }, [])

  const submit = async () => {
    if (!code.trim()) return
    try {
      const r = await api.checkin(code.trim(), 'manual')
      setRes(r)
      load()
    } catch {
      setRes({ ok: false, result: 'error', message: 'เชื่อมต่อระบบไม่ได้ กรุณาลองใหม่' })
    }
    setCode('')
  }

  const tone = res?.ok ? '' : res?.result === 'duplicate' ? ' warn' : ' bad'

  return (
    <>
      <button className="back" onClick={() => go('menu')}>← กลับเมนูหลัก</button>
      <h1>เช็คชื่อเข้าเรียน</h1>

      {session?.open ? (
        <p className="lead">
          คาบที่เปิดอยู่: <b>{session.title}</b> · {session.time} · {session.room}
          <br />เช็คชื่อแล้ว {session.checked_count} คน
        </p>
      ) : (
        <p className="lead">ขณะนี้ยังไม่มีคาบที่เปิดให้เช็คชื่อ (ระบบเปิดรับ 15 นาทีก่อนเริ่มคาบ)</p>
      )}

      {session?.open && (
        <div className="card">
          <b>สแกน QR ด้วยมือถือ หรือยื่นบัตรนักศึกษาที่เครื่องอ่าน</b>
          <small>
            ข้อมูลใน QR: <code>{session.qr_payload}</code><br />
            สร้างภาพ QR ได้จาก backend ด้วยไลบรารี qrcode (ดู README หัวข้อ “สร้าง QR”)
          </small>
        </div>
      )}

      <div className="row" style={{ marginTop: 14 }}>
        <input type="text" value={code} placeholder="หรือพิมพ์รหัสนักศึกษา เช่น 6712345678"
          onChange={(e) => setCode(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && submit()} />
        <button className="primary" onClick={submit}>เช็คชื่อ</button>
      </div>

      {res && (
        <div className={`result${tone}`}>
          <b>{res.ok ? '✓ เช็คชื่อสำเร็จ' : '✕ เช็คชื่อไม่สำเร็จ'}</b>
          <div>{res.student_name ? `${res.student_name} · ` : ''}{res.message}</div>
          {res.session_title && <small>{res.session_title}</small>}
        </div>
      )}
    </>
  )
}
