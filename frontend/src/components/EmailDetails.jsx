import './EmailDetails.css'

function EmailDetails({ email, onClose, onStartResponse }) {
  return (
    <>
      <div className="email-details-overlay" onClick={onClose}></div>
      <div className="email-details-modal">
        <div className="email-details-header">
          <h3>Детали письма</h3>
          <button className="email-details-close-btn" onClick={onClose} aria-label="Закрыть">
            ×
          </button>
        </div>
        <div className="email-details-content">
          <div className="email-details-field">
            <div className="email-details-label">Тема</div>
            <div className="email-details-value">{email.subject}</div>
          </div>
          <div className="email-details-field">
            <div className="email-details-label">Текст письма</div>
            <div className="email-details-value email-details-body">{email.body}</div>
          </div>
          {email.contact && (
            <div className="email-details-field">
              <div className="email-details-label">Контактная информация</div>
              <div className="email-details-value">{email.contact}</div>
            </div>
          )}
        </div>
        <div className="email-details-actions">
          <button className="btn-email-details-primary" onClick={onStartResponse}>
            Приступить к ответу
          </button>
        </div>
      </div>
    </>
  )
}

export default EmailDetails

