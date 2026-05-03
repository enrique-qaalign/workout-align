import React, { useState } from 'react';
import { Line } from 'react-chartjs-2';

// A simple React component demonstrating authentication, meal loading and trend visualisation.
// This skeleton can be extended to cover all features of the platform.

function App() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [token, setToken] = useState(null);
  const [meals, setMeals] = useState([]);
  const [chartData, setChartData] = useState(null);

  const apiUrl = 'http://localhost:8000';

  const login = async () => {
    const params = new URLSearchParams();
    params.append('username', email);
    params.append('password', password);
    const res = await fetch(`${apiUrl}/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: params.toString(),
    });
    if (res.ok) {
      const data = await res.json();
      setToken(data.access_token);
    } else {
      alert('Login failed');
    }
  };

  const loadMeals = async () => {
    const res = await fetch(`${apiUrl}/meals/`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    const data = await res.json();
    setMeals(data);
  };

  const loadTrends = async (userId, metric) => {
    const res = await fetch(`${apiUrl}/trends/${userId}?metric_type=${metric}`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    const data = await res.json();
    // Build data for Chart.js
    setChartData({
      labels: ['30 day', '7 day'],
      datasets: [
        {
          label: metric,
          data: [data.average_30_day, data.average_7_day],
          borderColor: 'rgba(75,192,192,1)',
          fill: false,
        },
      ],
    });
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Health Dashboard</h1>
      <div style={{ marginBottom: '20px' }}>
        <h2>Login</h2>
        <input type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} />
        <br />
        <input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} />
        <br />
        <button onClick={login}>Login</button>
      </div>
      {token && (
        <>
          <div style={{ marginBottom: '20px' }}>
            <h2>Meals</h2>
            <button onClick={loadMeals}>Load Meals</button>
            <ul>
              {meals.map(meal => (
                <li key={meal.id}><strong>{meal.name}</strong>: {meal.description}</li>
              ))}
            </ul>
          </div>
          <div>
            <h2>Trend</h2>
            <button onClick={() => loadTrends(1, 'HRV')}>Load Trends for User 1 (HRV)</button>
            {chartData && <Line data={chartData} />}
          </div>
        </>
      )}
    </div>
  );
}

export default App;