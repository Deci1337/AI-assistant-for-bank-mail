import { useState } from 'react'
import './AddEmailForm.css'

function AddEmailForm({ isOpen, onClose, onAdd }) {
  const [formData, setFormData] = useState({
    subject: '',
    body: '',
    contact: ''
  })

  if (!isOpen) return null

  const handleSubmit = (e) => {
    e.preventDefault()

    const subject = formData.subject.trim()
    const body = formData.body.trim()

    if (!subject || !body) {
      alert('Заполните тему и текст письма')
      return
    }

    onAdd({
      subject,
      body,
      contact: formData.contact.trim() || null
    })

    setFormData({ subject: '', body: '', contact: '' })
    onClose()
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  return (
    <>
      <div className="add-email-overlay" onClick={onClose}></div>
      <div className="add-email-modal">
        <div className="add-email-header">
          <h3>Добавить новое письмо</h3>
          <button className="add-email-close-btn" onClick={onClose} aria-label="Закрыть">
            ×
          </button>
        </div>
        <form onSubmit={handleSubmit} className="add-email-form">
          <div className="add-email-field">
            <label htmlFor="add_subject">Тема письма *</label>
            <input
              type="text"
              id="add_subject"
              name="subject"
              value={formData.subject}
              onChange={handleChange}
              required
              placeholder="Введите тему письма"
            />
          </div>
          <div className="add-email-field">
            <label htmlFor="add_body">Текст письма *</label>
            <textarea
              id="add_body"
              name="body"
              value={formData.body}
              onChange={handleChange}
              required
              placeholder="Введите текст письма"
              rows="8"
            />
          </div>
          <div className="add-email-field">
            <label htmlFor="add_contact">Контактная информация</label>
            <input
              type="text"
              id="add_contact"
              name="contact"
              value={formData.contact}
              onChange={handleChange}
              placeholder="Email, телефон и т.д. (необязательно)"
            />
          </div>
          <div className="add-email-actions">
            <button type="button" className="btn-cancel" onClick={onClose}>
              Отмена
            </button>
            <button type="submit" className="btn-submit">
              Добавить письмо
            </button>
          </div>
        </form>
      </div>
    </>
  )
}

export default AddEmailForm

