import { useState } from 'react'
import './EmailForm.css'

const DEFAULT_PROFILE = {
  sender_last_name: 'Победоносцев',
  sender_first_name: 'Константин',
  sender_middle_name: 'Константинович',
  sender_position: 'Начальник отдела медиа продвижения управления маркетинговых коммуникаций департамента маркетинга',
  phone_work: '+7 (495) 777-10-20, доб. 7000',
  phone_mobile: '+7 (903) 676-00-00',
  email: 'k.p.pobedonoscev@psbank.ru',
  address: 'ул. Смирновская, д. 10, стр. 22, г. Москва, Россия, 109052',
  hotline: '8 800 333 78 90',
  website: 'psbank.ru'
}

function EmailForm({ onSubmit }) {
  const [formData, setFormData] = useState({
    source_subject: '',
    source_body: '',
  })

  const handleSubmit = (e) => {
    e.preventDefault()

    const subject = formData.source_subject.trim()
    const body = formData.source_body.trim()

    if (!subject || !body) {
      alert('Заполните тему и текст входящего письма')
      return
    }

    onSubmit({
      sender_first_name: DEFAULT_PROFILE.sender_first_name,
      sender_last_name: DEFAULT_PROFILE.sender_last_name,
      sender_middle_name: DEFAULT_PROFILE.sender_middle_name,
      sender_position: DEFAULT_PROFILE.sender_position,
      sender_phone_work: DEFAULT_PROFILE.phone_work,
      sender_phone_mobile: DEFAULT_PROFILE.phone_mobile,
      sender_email: DEFAULT_PROFILE.email,
      sender_address: DEFAULT_PROFILE.address,
      sender_hotline: DEFAULT_PROFILE.hotline,
      sender_website: DEFAULT_PROFILE.website,
      source_subject: subject,
      source_body: body,
      company_context: 'ПСБ банк',
    })
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  return (
    <form onSubmit={handleSubmit} className="email-form">
      <div className="column-header">Входящее письмо</div>
      <div className="form-group">
        <label htmlFor="source_subject">Тема письма *</label>
        <input
          type="text"
          id="source_subject"
          name="source_subject"
          value={formData.source_subject}
          onChange={handleChange}
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor="source_body">Текст письма *</label>
        <textarea
          id="source_body"
          name="source_body"
          value={formData.source_body}
          onChange={handleChange}
          required
        />
      </div>

      <button type="submit" className="btn-analyze">
        🤖 Анализировать и сгенерировать ответ
      </button>
    </form>
  )
}

export default EmailForm

