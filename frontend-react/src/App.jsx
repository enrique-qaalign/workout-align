import React, { useEffect, useState } from 'react'
import ReadinessCard from './components/ReadinessCard.jsx'
import TelemetryForm from './components/TelemetryForm.jsx'
import { getReadiness } from './api/client'

export default function App() {
  const [data, setData] = useState(null)
  const [token, setToken] = useState('')
  const userId = 1

  async function load() {
    if (!token) return
    const res = await getReadiness(userId, token)
    setData(res)
  }

  useEffect(() => {
    load()
  }, [token])

  return (
    <div style={{ padding: 20, background: '#0b0e14', minHeight: '100vh', color: 'white' }}>
      <h1>Workout Align</h1>

      <input
        placeholder="Paste token"
        value={token}
        onChange={(e) => setToken(e.target.value)}
        style={{ width: 300 }}
      />

      <TelemetryForm userId={userId} token={token} onSuccess={load} />

      <ReadinessCard data={data} />
    </div>
  )
}
