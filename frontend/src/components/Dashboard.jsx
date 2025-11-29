import { useState, useEffect } from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Line, Doughnut } from 'react-chartjs-2'
import {
  getAnalyticsOverview,
  getThreadsByContext,
  getThreadsGrowth,
  getTopThreads,
  getDirectivesUsage,
} from '../services/api'
import './Dashboard.css'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
)

function Dashboard({ onBack, apiStatus }) {
  const [loading, setLoading] = useState(true)
  const [overview, setOverview] = useState(null)
  const [threadsByContext, setThreadsByContext] = useState(null)
  const [threadsGrowth, setThreadsGrowth] = useState(null)
  const [topThreads, setTopThreads] = useState(null)
  const [directivesUsage, setDirectivesUsage] = useState(null)
  const [periodDays, setPeriodDays] = useState(7)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadData()
  }, [periodDays])

  const loadData = async () => {
    setLoading(true)
    setError(null)
    try {
      const [overviewData, contextData, growthData, topData, directivesData] = await Promise.all([
        getAnalyticsOverview(periodDays),
        getThreadsByContext(30),
        getThreadsGrowth(30),
        getTopThreads(10, 30),
        getDirectivesUsage(30),
      ])
      setOverview(overviewData)
      setThreadsByContext(contextData)
      setThreadsGrowth(growthData)
      setTopThreads(topData)
      setDirectivesUsage(directivesData)
    } catch (err) {
      setError(err.message)
      console.error('Error loading analytics:', err)
    } finally {
      setLoading(false)
    }
  }

  const threadsGrowthChartData = threadsGrowth && threadsGrowth.data && threadsGrowth.data.length > 0 ? {
    labels: threadsGrowth.data.map(d => new Date(d.date).toLocaleDateString('ru-RU')),
    datasets: [
      {
        label: 'Новых переписок',
        data: threadsGrowth.data.map(d => d.daily || 0),
        backgroundColor: 'rgba(139, 92, 246, 0.1)',
        borderColor: 'rgba(139, 92, 246, 1)',
        borderWidth: 3,
        tension: 0.4,
        fill: true,
        pointRadius: 5,
        pointHoverRadius: 7,
        pointBackgroundColor: 'rgba(139, 92, 246, 1)',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
      },
      {
        label: 'Всего переписок',
        data: threadsGrowth.data.map(d => d.cumulative || 0),
        backgroundColor: 'rgba(251, 146, 60, 0.1)',
        borderColor: 'rgba(251, 146, 60, 1)',
        borderWidth: 3,
        tension: 0.4,
        fill: true,
        pointRadius: 5,
        pointHoverRadius: 7,
        pointBackgroundColor: 'rgba(251, 146, 60, 1)',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
      },
    ],
  } : null

  const directivesChartData = directivesUsage && directivesUsage.total_threads ? {
    labels: ['С использованием дополнительных указаний', 'Без использования дополнительных указаний'],
    datasets: [
      {
        data: [
          directivesUsage.threads_with_directives || 0,
          (directivesUsage.total_threads || 0) - (directivesUsage.threads_with_directives || 0)
        ],
        backgroundColor: [
          'rgba(16, 185, 129, 0.7)',
          'rgba(59, 130, 246, 0.7)',
        ],
        borderColor: [
          'rgba(16, 185, 129, 1)',
          'rgba(59, 130, 246, 1)',
        ],
        borderWidth: 3,
        hoverOffset: 8,
      },
    ],
  } : null

  if (loading) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-header">
          <button className="btn-back" onClick={onBack}>← Назад</button>
          <h1>Аналитика и дашборды</h1>
        </div>
        <div className="dashboard-loading">
          <p>Загрузка данных...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-header">
          <button className="btn-back" onClick={onBack}>← Назад</button>
          <h1>Аналитика и дашборды</h1>
        </div>
        <div className="dashboard-error">
          <p>Ошибка загрузки данных: {error}</p>
          <button onClick={loadData}>Повторить</button>
        </div>
      </div>
    )
  }

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <div className="dashboard-header-content">
          <button className="btn-back" onClick={onBack}>← Назад</button>
          <h1 className="dashboard-title-center">Аналитика и дашборды</h1>
          <div className="dashboard-controls">
            <label>
              Период:
              <select value={periodDays} onChange={(e) => setPeriodDays(Number(e.target.value))}>
                <option value={7}>7 дней</option>
                <option value={14}>14 дней</option>
                <option value={30}>30 дней</option>
                <option value={90}>90 дней</option>
              </select>
            </label>
            <button onClick={loadData}>Обновить</button>
          </div>
        </div>
        <p className="api-status-small">{apiStatus}</p>
      </div>

      <div className="dashboard-content">
        {overview && (
          <div className="dashboard-overview">
            <div className="stat-card">
              <div className="stat-value">{overview.total_threads}</div>
              <div className="stat-label">Переписок</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{overview.total_messages}</div>
              <div className="stat-label">Сообщений</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{overview.incoming_messages}</div>
              <div className="stat-label">Входящих</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{overview.outgoing_messages}</div>
              <div className="stat-label">Исходящих</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{overview.threads_with_directives}</div>
              <div className="stat-label">С указаниями</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{overview.avg_response_time_seconds}с</div>
              <div className="stat-label">Среднее время ответа</div>
            </div>
          </div>
        )}

        <div className="dashboard-charts">
          {directivesChartData && (
            <div className="chart-card">
              <h3>Использование дополнительных указаний</h3>
              <Doughnut data={directivesChartData} options={{
                responsive: true,
                maintainAspectRatio: false,
                aspectRatio: 1.5,
                plugins: {
                  legend: { 
                    position: 'right',
                    labels: {
                      usePointStyle: true,
                      padding: 12,
                      font: {
                        size: 13,
                        weight: '500'
                      }
                    }
                  },
                  title: { display: false },
                  tooltip: {
                    backgroundColor: 'rgba(30, 41, 59, 0.95)',
                    padding: 12,
                    titleFont: { size: 14, weight: '600' },
                    bodyFont: { size: 13 },
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    cornerRadius: 8,
                  }
                },
              }} />
            </div>
          )}

          {threadsGrowthChartData && (
            <div className="chart-card">
              <h3>Рост переписок</h3>
              <Line data={threadsGrowthChartData} options={{
                responsive: true,
                maintainAspectRatio: false,
                aspectRatio: 2,
                plugins: {
                  legend: { 
                    position: 'top',
                    labels: {
                      usePointStyle: true,
                      padding: 15,
                      font: {
                        size: 13,
                        weight: '600'
                      }
                    }
                  },
                  title: { display: false },
                  tooltip: {
                    backgroundColor: 'rgba(30, 41, 59, 0.95)',
                    padding: 12,
                    titleFont: { size: 14, weight: '600' },
                    bodyFont: { size: 13 },
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    cornerRadius: 8,
                  }
                },
                scales: {
                  y: { 
                    beginAtZero: true,
                    grid: {
                      color: 'rgba(0, 0, 0, 0.05)',
                    },
                    ticks: {
                      font: { size: 12 }
                    }
                  },
                  x: {
                    grid: {
                      display: false
                    },
                    ticks: {
                      font: { size: 12 }
                    }
                  }
                },
              }} />
            </div>
          )}
        </div>

        {topThreads && topThreads.data.length > 0 && (
          <div className="chart-card chart-card-full-width">
            <h3>Топ переписок по количеству сообщений</h3>
            <div className="top-threads-list">
              {topThreads.data.map((thread, index) => (
                <div key={thread.id} className="thread-item">
                  <div className="thread-rank">#{index + 1}</div>
                  <div className="thread-info">
                    <div className="thread-subject">{thread.subject}</div>
                    <div className="thread-meta">
                      <span>{thread.message_count} сообщений</span>
                      <span>{new Date(thread.created_at).toLocaleDateString('ru-RU')}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Dashboard

