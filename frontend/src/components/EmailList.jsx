import { useState } from 'react'
import EmailDetails from './EmailDetails'
import './EmailList.css'

function EmailList({ emails, onSelectEmail, onGenerateFromEmail, onMarkAsRead, title }) {
  const [selectedEmail, setSelectedEmail] = useState(null)

  const handleEmailClick = (email) => {
    setSelectedEmail(email)
    // Помечаем как прочитанное при открытии
    if (!email.isRead && onMarkAsRead) {
      onMarkAsRead(email.id, true)
    }
  }

  const handleGenerateClick = (e, email) => {
    e.stopPropagation()
    onGenerateFromEmail(email)
  }

  const handleStartResponse = (email) => {
    setSelectedEmail(null)
    onSelectEmail(email)
  }

  return (
    <>
      <div className="email-list-container">
        <div className="email-list-header">
          <h3>{title || 'Входящие письма'}</h3>
        </div>
        <div className="email-list">
          {emails.length === 0 ? (
            <div className="email-list-empty">
              <p>Нет писем в этой категории</p>
            </div>
          ) : (
            emails.map((email, index) => (
              <div
                key={email.id || index}
                className={`email-item ${email.isRead ? 'email-item-read' : 'email-item-unread'}`}
                onClick={() => handleEmailClick(email)}
              >
                <div className="email-item-content">
                  <div className={`email-item-subject ${email.isRead ? '' : 'unread'}`}>
                    {email.subject}
                  </div>
                  <div className="email-item-preview">
                    {email.body.substring(0, 100)}
                    {email.body.length > 100 ? '...' : ''}
                  </div>
                  {email.contact && (
                    <div className="email-item-contact">{email.contact}</div>
                  )}
                </div>
                <button
                  className="email-item-generate-btn"
                  onClick={(e) => handleGenerateClick(e, email)}
                  title="Сгенерировать ответ"
                >
                  📨
                </button>
              </div>
            ))
          )}
        </div>
      </div>
      {selectedEmail && (
        <EmailDetails
          email={selectedEmail}
          onClose={() => setSelectedEmail(null)}
          onStartResponse={() => handleStartResponse(selectedEmail)}
        />
      )}
    </>
  )
}

export default EmailList

