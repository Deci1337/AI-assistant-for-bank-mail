import { useState, useEffect } from 'react'
import Homepage from './components/Homepage'
import Generator from './components/Generator'
import Dashboard from './components/Dashboard'
import { getApiBase } from './services/api'
import './styles/App.css'

function App() {
  const [currentPage, setCurrentPage] = useState('homepage')
  const [apiStatus, setApiStatus] = useState('Проверяем соединение...')

  useEffect(() => {
    verifyBackend()
  }, [])

  const verifyBackend = async () => {
    setApiStatus('Проверяем соединение с API...')
    try {
      const apiBase = await getApiBase()
      const url = apiBase ? `${apiBase}/health` : '/health'
      const res = await fetch(url)
      if (!res.ok) throw new Error(`Health check failed with ${res.status}`)
      const displayUrl = apiBase || 'через proxy'
      setApiStatus(`✓ Бэкенд подключен (${displayUrl})`)
    } catch (e) {
      setApiStatus(`✗ Нет связи с сервером. Проверьте порты 8000-8009`)
    }
  }

  return (
    <div className="app">
      {currentPage === 'homepage' && (
        <Homepage 
          onStart={() => setCurrentPage('generator')} 
          onDashboard={() => setCurrentPage('dashboard')}
          apiStatus={apiStatus} 
        />
      )}
      {currentPage === 'generator' && (
        <Generator 
          onBack={() => setCurrentPage('homepage')} 
          onDashboard={() => setCurrentPage('dashboard')}
          apiStatus={apiStatus} 
        />
      )}
      {currentPage === 'dashboard' && (
        <Dashboard onBack={() => setCurrentPage('homepage')} apiStatus={apiStatus} />
      )}
    </div>
  )
}

export default App

