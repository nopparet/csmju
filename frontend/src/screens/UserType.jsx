const TYPES = [
  { key: 'student', ic: '🎓', title: 'นักศึกษา',     sub: 'ตารางเรียน เช็คชื่อ ถามผู้ช่วย' },
  { key: 'teacher', ic: '👩‍🏫', title: 'อาจารย์',     sub: 'ตารางสอน ห้องว่าง สถิติ' },
  { key: 'visitor', ic: '🧳', title: 'บุคคลภายนอก', sub: 'นำทาง ติดต่อสำนักงาน' },
]

export default function UserType({ onPick }) {
  return (
    <>
      <h1>คุณคือใคร?</h1>
      <p className="lead">เลือกเพื่อให้ระบบแสดงข้อมูลที่ตรงกับคุณ</p>
      <div className="type-grid">
        {TYPES.map((t) => (
          <button key={t.key} className="type-card" onClick={() => onPick(t.key)}>
            <span className="ic" style={{ fontSize: '3.5rem' }}>{t.ic}</span>
            <b>{t.title}</b>
            <small>{t.sub}</small>
          </button>
        ))}
      </div>
    </>
  )
}
