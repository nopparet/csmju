import { useEffect, useRef, useState } from 'react'
import { api } from '../api'

const STARTERS = ['ตารางวันนี้', 'ห้อง CS-601 ว่างไหม', 'อ.กิตติกร อยู่ห้องไหน', 'กิจกรรมของสาขา', 'เว็บไซต์สาขา', 'สมัครเรียน']

export default function Chat({ go, userType }) {
  const [log, setLog] = useState([
    { who: 'bot', text: 'สวัสดีครับ ถามเรื่องตารางเรียน-สอน ห้องเรียน ห้องอาจารย์ หรือกิจกรรมของสาขาวิทยาการคอมพิวเตอร์ มหาวิทยาลัยแม่โจ้ได้เลย', meta: 'intent: greeting' },
  ])
  const [text, setText] = useState('')
  const [busy, setBusy] = useState(false)
  const endRef = useRef(null)

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [log])

  const send = async (q) => {
    const question = (q ?? text).trim()
    if (!question || busy) return
    setText('')
    setLog((l) => [...l, { who: 'me', text: question }])
    setBusy(true)
    try {
      const r = await api.ask(question, userType)
      setLog((l) => [...l, { who: 'bot', text: r.answer, meta: `intent: ${r.intent} · score ${r.score}`, quick: r.quick_replies }])
    } catch {
      setLog((l) => [...l, { who: 'bot', text: 'ตอนนี้เชื่อมต่อระบบไม่ได้ กรุณาลองใหม่อีกครั้ง' }])
    } finally {
      setBusy(false)
    }
  }

  const last = log[log.length - 1]
  const chips = last?.quick?.length ? last.quick : STARTERS

  return (
    <>
      <button className="back" onClick={() => go('menu')}>← กลับเมนูหลัก</button>
      <h1>ผู้ช่วยตอบคำถาม</h1>
      <p className="lead">พิมพ์คำถามเกี่ยวกับตารางเรียน-สอน ห้อง หรือกิจกรรมของสาขา</p>

      <div className="chips">
        {chips.map((c) => <button key={c} className="chip" onClick={() => send(c)}>{c}</button>)}
      </div>

      <div className="chat">
        {log.map((m, i) => (
          <div key={i} className={`msg ${m.who}`}>
            {m.text}
            {m.meta && <span className="meta">{m.meta}</span>}
          </div>
        ))}
        <div ref={endRef} />
      </div>

      <div className="row">
        <input type="text" value={text} placeholder="พิมพ์คำถามที่นี่…"
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && send()} />
        <button className="primary" onClick={() => send()} disabled={busy}>
          {busy ? 'กำลังค้น…' : 'ส่ง'}
        </button>
      </div>
    </>
  )
}
