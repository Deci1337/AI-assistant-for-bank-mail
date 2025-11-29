import { useState, useEffect, useImperativeHandle, forwardRef } from 'react'
import './ParametersForm.css'

const ParametersForm = forwardRef(function ParametersForm({ initialParameters, onRegenerate, onClear, hasSenderName = false, isLoading = false }, ref) {
  const [parameters, setParameters] = useState(initialParameters)
  const [directives, setDirectives] = useState([])

  useEffect(() => {
    setParameters(initialParameters)
    // Если полное имя недоступно, но было выбрано, сбрасываем на "vy"
    if (!hasSenderName && initialParameters.address_style === 'full_name') {
      setParameters({
        ...initialParameters,
        address_style: 'vy'
      })
    }
  }, [initialParameters, hasSenderName])

  const handleChange = (field, value) => {
    // Prevent selecting "full_name" if recipient name is not available
    if (field === 'address_style' && value === 'full_name' && !hasSenderName) {
      return // Ignore the change
    }
    setParameters({
      ...parameters,
      [field]: value,
    })
  }

  const handleDirectiveChange = (index, value) => {
    const newDirectives = [...directives]
    newDirectives[index] = value
    setDirectives(newDirectives)
  }

  const addDirective = () => {
    setDirectives([...directives, ''])
  }

  const removeDirective = (index) => {
    setDirectives(directives.filter((_, i) => i !== index))
  }

  const handleRegenerate = () => {
    const params = {
      ...parameters,
      extra_directives: directives.filter((d) => d.trim()).length
        ? directives.filter((d) => d.trim())
        : null,
    }
    onRegenerate(params)
  }

  useImperativeHandle(ref, () => ({
    handleRegenerate
  }))

  return (
    <div className="parameters-form">
      <div className="column-header">Параметры генерации</div>

      <div className="param-section">
        <div className="param-label">Тон письма</div>
        <div className="radio-group">
          <label>
            <input
              type="radio"
              name="tone"
              value="formal"
              checked={parameters.tone === 'formal'}
              onChange={(e) => handleChange('tone', e.target.value)}
            />
            Формальный
          </label>
          <label>
            <input
              type="radio"
              name="tone"
              value="neutral"
              checked={parameters.tone === 'neutral'}
              onChange={(e) => handleChange('tone', e.target.value)}
            />
            Нейтральный
          </label>
          <label>
            <input
              type="radio"
              name="tone"
              value="friendly"
              checked={parameters.tone === 'friendly'}
              onChange={(e) => handleChange('tone', e.target.value)}
            />
            Дружелюбный
          </label>
        </div>
      </div>

      <div className="param-section">
        <div className="param-label">Длина ответа</div>
        <div className="radio-group">
          <label>
            <input
              type="radio"
              name="length"
              value="short"
              checked={parameters.length === 'short'}
              onChange={(e) => handleChange('length', e.target.value)}
            />
            Короткое (3-4 предложения)
          </label>
          <label>
            <input
              type="radio"
              name="length"
              value="medium"
              checked={parameters.length === 'medium'}
              onChange={(e) => handleChange('length', e.target.value)}
            />
            Среднее (5-8 предложений)
          </label>
          <label>
            <input
              type="radio"
              name="length"
              value="long"
              checked={parameters.length === 'long'}
              onChange={(e) => handleChange('length', e.target.value)}
            />
            Длинное (8-12 предложений)
          </label>
        </div>
      </div>

      <div className="param-section">
        <div className="param-label">Цель письма</div>
        <select
          id="purpose"
          value={parameters.purpose}
          onChange={(e) => handleChange('purpose', e.target.value)}
        >
          <option value="response">Ответ</option>
          <option value="proposal">Предложение</option>
          <option value="notification">Уведомление</option>
          <option value="refusal">Отказ</option>
        </select>
      </div>

      <div className="param-section">
        <div className="param-label">Аудитория</div>
        <select
          id="audience"
          value={parameters.audience}
          onChange={(e) => handleChange('audience', e.target.value)}
        >
          <option value="colleague">Коллега (внутренняя переписка)</option>
          <option value="manager">Руководитель (вышестоящее руководство)</option>
          <option value="client">Клиент (пользователь услуг банка: физлицо или юрлицо)</option>
          <option value="partner">Партнер (бизнес-партнер, совместные проекты, B2B)</option>
          <option value="regulator">Регулятор (Банк России, надзорные органы)</option>
        </select>
      </div>

      <div className="param-section">
        <div className="param-label">Стиль обращения</div>
        <div className="radio-group">
          <label>
            <input
              type="radio"
              name="address_style"
              value="vy"
              checked={parameters.address_style === 'vy'}
              onChange={(e) => handleChange('address_style', e.target.value)}
            />
            "Вы"
          </label>
          <label style={{ opacity: hasSenderName ? 1 : 0.5, cursor: hasSenderName ? 'pointer' : 'not-allowed' }}>
            <input
              type="radio"
              name="address_style"
              value="full_name"
              checked={parameters.address_style === 'full_name'}
              onChange={(e) => handleChange('address_style', e.target.value)}
              disabled={!hasSenderName}
            />
            Полное имя
            {!hasSenderName && <span style={{ fontSize: '0.75rem', color: 'var(--text-light)', marginLeft: '8px' }}>(не указано в исходном письме)</span>}
          </label>
        </div>
      </div>

      <div className="param-section">
        <div className="param-label">Срочность</div>
        <select
          id="urgency"
          value={parameters.urgency}
          onChange={(e) => handleChange('urgency', e.target.value)}
        >
          <option value="low">Низкая</option>
          <option value="normal">Обычная</option>
          <option value="high">Высокая</option>
        </select>
      </div>

      <div className="param-section">
        <div className="checkbox-group">
          <label>
            <input
              type="checkbox"
              checked={parameters.include_formal_greetings}
              onChange={(e) =>
                handleChange('include_formal_greetings', e.target.checked)
              }
            />
            Формальные приветствия
          </label>
          <label>
            <input
              type="checkbox"
              checked={parameters.include_greeting_and_signoff}
              onChange={(e) =>
                handleChange('include_greeting_and_signoff', e.target.checked)
              }
            />
            Приветствие и заключение
          </label>
          <label>
            <input
              type="checkbox"
              checked={parameters.include_corporate_phrases}
              onChange={(e) =>
                handleChange('include_corporate_phrases', e.target.checked)
              }
            />
            Корпоративные фразы
          </label>
        </div>
      </div>

      <div className="param-section">
        <div className="param-label">Дополнительные указания</div>
        {directives.map((directive, index) => (
          <div key={index} className="directive-item">
            <input
              type="text"
              placeholder="Введите дополнительное указание"
              className="directive-input"
              value={directive}
              onChange={(e) => handleDirectiveChange(index, e.target.value)}
            />
            <button
              type="button"
              className="btn-remove"
              onClick={() => removeDirective(index)}
            >
              ✕
            </button>
          </div>
        ))}
        <button type="button" className="btn-add" onClick={addDirective}>
          + Добавить указание
        </button>
      </div>

      <button type="button" className="btn-clear" onClick={onClear}>
        Очистить и начать заново
      </button>
    </div>
  )
})

export default ParametersForm

