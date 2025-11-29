import React, { useState } from 'react'
import './DepartmentSelector.css'

const DEPARTMENT_EMAILS = {
  "Отдел кредитования": "credit@psb.ru",
  "Отдел депозитов и вкладов": "deposits@psb.ru",
  "Отдел карточных продуктов": "cards@psb.ru",
  "Отдел корпоративного обслуживания": "corporate@psb.ru",
  "Отдел розничного обслуживания": "retail@psb.ru",
  "Отдел инвестиционных продуктов": "investments@psb.ru",
  "Отдел ипотечного кредитования": "mortgage@psb.ru",
  "Отдел валютных операций": "forex@psb.ru",
  "Отдел безопасности": "security@psb.ru",
  "Отдел по работе с проблемной задолженностью": "collections@psb.ru",
  "Отдел партнерств и развития бизнеса": "partnerships@psb.ru",
  "Отдел IT и цифровых решений": "it@psb.ru",
  "Отдел претензий и жалоб": "complaints@psb.ru",
  "Отдел юридических вопросов": "legal@psb.ru",
  "Отдел риск-менеджмента": "risk@psb.ru",
  "Отдел комплаенса": "compliance@psb.ru",
  "Отдел казначейства": "treasury@psb.ru",
  "Отдел операционного обслуживания": "operations@psb.ru",
}

const DEPARTMENTS = Object.keys(DEPARTMENT_EMAILS)

function DepartmentSelector({ isOpen, onClose, onSelect }) {
  const [email, setEmail] = useState('')
  const [selectedDepartment, setSelectedDepartment] = useState(null)

  if (!isOpen) return null

  const handleSelectDepartment = (department) => {
    setSelectedDepartment(department)
    setEmail(DEPARTMENT_EMAILS[department])
  }

  const handleEmailChange = (e) => {
    setEmail(e.target.value)
    setSelectedDepartment(null)
  }

  const handleSubmit = () => {
    if (!email.trim()) {
      alert('Пожалуйста, укажите email адрес')
      return
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email.trim())) {
      alert('Пожалуйста, введите корректный email адрес')
      return
    }

    const departmentName = selectedDepartment || email
    onSelect(departmentName, email.trim())
  }

  return (
    <>
      <div className="department-overlay" onClick={onClose}></div>
      <div className="department-modal">
        <div className="department-header">
          <h3>Перенаправить в отдел</h3>
          <button className="department-close-btn" onClick={onClose} aria-label="Закрыть">
            ×
          </button>
        </div>
        <div className="department-content">
          <div className="department-email-section">
            <label className="department-email-label">Email адрес:</label>
            <input
              type="email"
              className="department-email-input"
              placeholder="Введите email или выберите из списка"
              value={email}
              onChange={handleEmailChange}
            />
          </div>
          
          <div className="department-divider">
            <span>Или выберите из списка:</span>
          </div>

          <div className="department-list">
            {DEPARTMENTS.map((department) => (
              <button
                key={department}
                className={`department-item ${selectedDepartment === department ? 'selected' : ''}`}
                onClick={() => handleSelectDepartment(department)}
              >
                <div className="department-item-name">{department}</div>
                <div className="department-item-email">{DEPARTMENT_EMAILS[department]}</div>
              </button>
            ))}
          </div>

          <div className="department-actions">
            <button className="department-submit-btn" onClick={handleSubmit}>
              Перенаправить
            </button>
            <button className="department-cancel-btn" onClick={onClose}>
              Отмена
            </button>
          </div>
        </div>
      </div>
    </>
  )
}

export default DepartmentSelector

