const BASE = import.meta.env.VITE_API_BASE || ''

async function req(path, options = {}) {
  const res = await fetch(BASE + path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json()
}

export const api = {
  rooms: (q = '') => req(`/api/rooms${q ? `?q=${encodeURIComponent(q)}` : ''}`),
  teachers: () => req('/api/rooms/teachers'),
  schedule: (params = {}) => {
    const qs = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== undefined && v !== '')
    ).toString()
    return req(`/api/schedule${qs ? `?${qs}` : ''}`)
  },
  activities: () => req('/api/schedule/activities'),
  ask: (question, userType) =>
    req('/api/chat', { method: 'POST', body: JSON.stringify({ question, user_type: userType }) }),
  currentSession: () => req('/api/attendance/current'),
  checkin: (code, method = 'qr') =>
    req('/api/attendance', { method: 'POST', body: JSON.stringify({ code, ref_type: 'class', method }) }),
  stats: (days = 7) => req(`/api/stats?days=${days}`),
  logVisit: (userType, module) =>
    req('/api/logs/visit', { method: 'POST', body: JSON.stringify({ user_type: userType, module }) })
      .catch(() => {}),
}
