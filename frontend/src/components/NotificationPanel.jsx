import './NotificationPanel.css'

function NotificationPanel({ isOpen, onClose, notifications, generatedResponses, onNavigateToResponse }) {
  if (!isOpen) return null

  const formatTime = (timestamp) => {
    const now = new Date()
    const time = new Date(timestamp)
    const diff = now - time
    const seconds = Math.floor(diff / 1000)
    const minutes = Math.floor(seconds / 60)
    
    if (seconds < 60) return 'только что'
    if (minutes < 60) return `${minutes} мин назад`
    const hours = Math.floor(minutes / 60)
    if (hours < 24) return `${hours} ч назад`
    return time.toLocaleDateString('ru-RU')
  }

  return (
    <>
      <div className="notification-overlay" onClick={onClose}></div>
      <div className="notification-panel">
        <div className="notification-panel-header">
          <h3>Уведомления</h3>
          <button className="notification-close-btn" onClick={onClose} aria-label="Закрыть">
            ×
          </button>
        </div>
        <div className="notification-list">
          {notifications.length === 0 ? (
            <div className="notification-empty">Нет уведомлений</div>
          ) : (
            notifications.map((notification, index) => {
              // Проверяем, что ответ успешно сгенерирован (есть данные и это не ошибка)
              const hasGeneratedResponse = notification.type === 'generation_completed' && 
                generatedResponses && generatedResponses.has(notification.emailId) &&
                notification.title !== 'Ошибка генерации'
              
              return (
                <div key={notification.emailId || index} className={`notification-item notification-${notification.type}`}>
                  <div className="notification-icon">
                    {notification.type === 'new_email' && '📧'}
                    {notification.type === 'generation_started' && '🤖'}
                    {notification.type === 'generation_completed' && '✅'}
                  </div>
                  <div className="notification-content">
                    <div className="notification-title">{notification.title}</div>
                    <div className="notification-message">{notification.message}</div>
                    <div className="notification-time">{formatTime(notification.timestamp)}</div>
                    {notification.details && (
                      <div className="notification-details">
                        <div className="notification-detail-item">
                          <strong>Тема:</strong> {notification.details.subject}
                        </div>
                        {notification.details.preview && (
                          <div className="notification-detail-item">
                            <strong>Текст:</strong> {notification.details.preview}
                          </div>
                        )}
                      </div>
                    )}
                    {hasGeneratedResponse && (
                      <div className="notification-actions">
                        <button
                          className="btn-notification-navigate"
                          onClick={() => {
                            onNavigateToResponse(notification.emailId)
                          }}
                        >
                          Перейти к ответу
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              )
            })
          )}
        </div>
      </div>
    </>
  )
}

export default NotificationPanel

