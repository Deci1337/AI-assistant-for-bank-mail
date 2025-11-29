import React, { useState, useEffect } from 'react'
import DepartmentSelector from './DepartmentSelector'
import './Result.css'
import psbLogo from '../PSB_logo_original_png.png'

function Result({ result, onRedirect, onRegenerateWithCurrentParams, isLoading }) {
  const [subject, setSubject] = useState(result?.subject || '')
  const [body, setBody] = useState(result?.body || '')
  const [showDepartmentSelector, setShowDepartmentSelector] = useState(false)

  // Обновляем состояние при изменении result
  useEffect(() => {
    if (result) {
      setSubject(result.subject || '')
      setBody(result.body || '')
    }
  }, [result])

  // Функция для рендеринга HTML с логотипом
  const renderBodyWithLogo = () => {
    if (!body) return ''
    if (!body.includes('[LOGO]')) {
      return body.replace(/\n/g, '<br>')
    }
    return body.split('[LOGO]').map((part, index, array) => {
      if (index === array.length - 1) {
        return part.replace(/\n/g, '<br>')
      }
      const logoHtml = `<div style="margin-top: 20px; display: inline-block;"><img src="${psbLogo}" alt="ПСБ" style="height: 88px; width: auto;" /></div>`
      return part.replace(/\n/g, '<br>') + logoHtml
    }).join('')
  }

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text)
    alert('Скопировано в буфер обмена!')
  }

  const handleCopyAll = () => {
    const fullText = `Тема: ${subject}\n\n${body}`
    navigator.clipboard.writeText(fullText)
    alert('Письмо скопировано в буфер обмена!')
  }


  const handleSendEmail = () => {
    const subjectEncoded = encodeURIComponent(subject)
    const bodyEncoded = encodeURIComponent(body)
    window.location.href = `mailto:?subject=${subjectEncoded}&body=${bodyEncoded}`
  }

  const handleRedirect = (department, email) => {
    setShowDepartmentSelector(false)
    alert(`✓ Письмо успешно перенаправлено в ${department}\nEmail: ${email}`)
    if (onRedirect) {
      onRedirect()
    }
  }

  if (!result) {
    return null
  }

  return (
    <div className="result-container">
      <div className="result-header">
        <h3>Результат</h3>
        <div className="result-actions">
          <button className="btn-icon" onClick={handleCopyAll}>
            Копировать всё
          </button>
          <button className="btn-icon" onClick={handleSendEmail}>
            Отправить ответ
          </button>
          <button className="btn-icon" onClick={() => setShowDepartmentSelector(true)}>
            Перенаправить в другой отдел
          </button>
        </div>
      </div>

      <div className="form-group">
        <label>Тема письма</label>
        <div
          className="result-field"
          contentEditable
          suppressContentEditableWarning
          onBlur={(e) => setSubject(e.target.textContent)}
        >
          {subject}
        </div>
        <button className="btn-icon" onClick={() => handleCopy(subject)}>
          Копировать тему
        </button>
      </div>

      <div className="form-group">
        <label>Текст письма</label>
        <div className="result-field-wrapper">
          <div
            className="result-field email-body"
            contentEditable
            suppressContentEditableWarning
            style={{ minHeight: '300px' }}
            onBlur={(e) => {
              // При сохранении получаем текст и восстанавливаем маркер [LOGO] если его нет
              let text = e.target.innerText || e.target.textContent
              // Если в исходном body был маркер [LOGO], но в сохраненном тексте его нет, добавляем его
              if (body.includes('[LOGO]') && !text.includes('[LOGO]')) {
                // Проверяем, есть ли изображение в HTML
                const html = e.target.innerHTML
                if (html.includes('<img')) {
                  // Если изображение есть, добавляем маркер в конец
                  text = text.trim() + '\n[LOGO]'
                }
              }
              setBody(text)
            }}
            dangerouslySetInnerHTML={{
              __html: renderBodyWithLogo()
            }}
          />
        </div>
        <div className="result-buttons-wrapper">
          <button className="btn-icon" onClick={() => handleCopy(body)}>
            Копировать текст
          </button>
          {onRegenerateWithCurrentParams && (
            <button 
              className="btn-icon btn-regenerate-inline" 
              onClick={onRegenerateWithCurrentParams}
              disabled={isLoading}
            >
              {isLoading ? '⏳ Генерируем...' : '🔄 Сгенерировать с новыми параметрами'}
            </button>
          )}
        </div>
      </div>
      <DepartmentSelector
        isOpen={showDepartmentSelector}
        onClose={() => setShowDepartmentSelector(false)}
        onSelect={handleRedirect}
      />
    </div>
  )
}

export default Result

