import { useEffect, useState } from 'react'
import { api } from '../api'

export default function Welcome({ onStart }) {
  const [news, setNews] = useState([])
  useEffect(() => { api.activities().then(setNews).catch(() => setNews([])) }, [])

  return (
    <div className="welcome" onClick={onStart}>
      <img className="welcome-logo" src="/csmju-logo.png" alt="CSMJU" />
      <h1>ยินดีต้อนรับสู่<br />สาขาวิทยาการคอมพิวเตอร์</h1>
      <p className="lead">คณะวิทยาศาสตร์ มหาวิทยาลัยแม่โจ้<br />อาคาร 60 ปี ชั้น 6</p>
      {news.length > 0 && (
        <p className="lead" style={{ fontSize: '.92rem', color: '#6B7280' }}>
          📌 {news.slice(0, 2).map((a) =>
            `${a.title} (${new Date(a.start_at).toLocaleDateString('th-TH')})`
          ).join(' · ')}
        </p>
      )}
      <div className="tap-hint">👆 แตะหน้าจอเพื่อเริ่มใช้งาน</div>
    </div>
  )
}
