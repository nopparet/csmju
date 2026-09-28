const MENUS = {
  student: [
    ['schedule', '📅', 'ตารางเรียน', 'ดูตามวันและชั้นปี'],
    ['navigate', '🗺️', 'หาห้องเรียน / ห้องอาจารย์', 'แผนผังอาคาร'],
    ['chat', '💬', 'ถามผู้ช่วย', 'พิมพ์คำถามได้เลย'],
    ['checkin', '📲', 'เช็คชื่อเข้าเรียน', 'QR หรือบัตรนักศึกษา'],
  ],
  teacher: [
    ['schedule', '📅', 'ตารางสอน', 'คาบของวันนี้'],
    ['navigate', '🗺️', 'ห้องว่าง / ผังอาคาร', 'ดูสถานะห้องตอนนี้'],
    ['chat', '💬', 'ถามผู้ช่วย', 'ค้นข้อมูลสาขา'],
    ['dashboard', '📊', 'สถิติผู้ใช้งาน', 'ย้อนหลัง 7 วัน'],
  ],
  visitor: [
    ['navigate', '🗺️', 'นำทางไปยังห้อง', 'สำนักงานและห้องอาจารย์'],
    ['chat', '💬', 'สอบถามข้อมูล', 'ติดต่อสาขา'],
    ['schedule', '📅', 'ตารางการใช้ห้อง', 'ดูว่าห้องว่างไหม'],
  ],
}

export default function Menu({ go, userType }) {
  return (
    <>
      <button className="back" onClick={() => go('type')}>← เปลี่ยนประเภทผู้ใช้</button>
      <h1>ต้องการทำอะไร</h1>
      <p className="lead">แตะเมนูเพื่อเริ่ม</p>
      <div className="grid">
        {(MENUS[userType] || MENUS.visitor).map(([s, ic, t, sub]) => (
          <button key={s} className="tile" onClick={() => go(s, s)}>
            <span className="ic">{ic}</span>
            <b>{t}</b>
            <small>{sub}</small>
          </button>
        ))}
      </div>
    </>
  )
}
