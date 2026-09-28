import { useEffect, useState } from 'react'
import { api } from './api'
import Welcome from './screens/Welcome'
import UserType from './screens/UserType'
import Menu from './screens/Menu'
import Navigate from './screens/Navigate'
import Schedule from './screens/Schedule'
import Chat from './screens/Chat'
import CheckIn from './screens/CheckIn'
import Dashboard from './screens/Dashboard'

const IDLE_MS = 90_000   // ไม่มีคนแตะ 90 วินาที กลับหน้าจอพัก

const LABEL = { student: 'นักศึกษา', teacher: 'อาจารย์', visitor: 'บุคคลภายนอก' }

export default function App() {
  const [screen, setScreen] = useState('welcome')
  const [userType, setUserType] = useState(null)
  const [clock, setClock] = useState(new Date())

  useEffect(() => {
    const t = setInterval(() => setClock(new Date()), 1000)
    return () => clearInterval(t)
  }, [])

  // กลับหน้าจอพักเมื่อไม่มีการใช้งาน
  useEffect(() => {
    let timer
    const reset = () => {
      clearTimeout(timer)
      timer = setTimeout(() => { setScreen('welcome'); setUserType(null) }, IDLE_MS)
    }
    const events = ['pointerdown', 'keydown']
    events.forEach((e) => window.addEventListener(e, reset))
    reset()
    return () => { clearTimeout(timer); events.forEach((e) => window.removeEventListener(e, reset)) }
  }, [])

  const go = (next, module) => {
    if (userType && module) api.logVisit(userType, module)
    setScreen(next)
  }

  const pick = (type) => {
    setUserType(type)
    api.logVisit(type, 'menu')
    setScreen('menu')
  }

  const common = { go, userType }

  return (
    <div className="app">
      {screen !== 'welcome' && (
        <div className="topbar">
          <div className="topbar-logo">
            <img src="/csmju-logo.png" alt="CSMJU Logo" />
            <div className="topbar-name">
              สาขาวิชาวิทยาการคอมพิวเตอร์
              <small>คณะวิทยาศาสตร์ มหาวิทยาลัยแม่โจ้ · อาคาร 60 ปี ชั้น 6</small>
            </div>
          </div>
          <div className="topbar-right">
            <div className="topbar-clock">
              {clock.toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' })}
            </div>
            {userType && <div className="topbar-user">{LABEL[userType]}</div>}
          </div>
        </div>
      )}
      <div className="content">
        {screen === 'welcome' && <Welcome onStart={() => setScreen('type')} />}
        {screen === 'type' && <UserType onPick={pick} />}
        {screen === 'menu' && <Menu {...common} />}
        {screen === 'navigate' && <Navigate {...common} />}
        {screen === 'schedule' && <Schedule {...common} />}
        {screen === 'chat' && <Chat {...common} />}
        {screen === 'checkin' && <CheckIn {...common} />}
        {screen === 'dashboard' && <Dashboard {...common} />}
      </div>
    </div>
  )
}
