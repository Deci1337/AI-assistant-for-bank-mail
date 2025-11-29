import './OperatorSidebar.css'

function OperatorSidebar({ emailData, parameters, detailedAnalysis, isVisible }) {
  if (!emailData && !parameters) {
    return null
  }

  const getCategoryLabel = (category) => {
    const labels = {
      information_request: 'Запрос информации/документов',
      complaint: 'Официальная жалоба или претензия',
      regulatory_request: 'Регуляторный запрос',
      partnership_proposal: 'Партнёрское предложение',
      approval_request: 'Запрос на согласование',
      notification: 'Уведомление или информирование',
      other: 'Прочее'
    }
    return labels[category] || category
  }

  const getPurposeLabel = (purpose) => {
    const labels = {
      response: 'Ответ на запрос',
      proposal: 'Коммерческое предложение',
      notification: 'Уведомление',
      refusal: 'Отказ'
    }
    return labels[purpose] || purpose
  }

  const getUrgencyLabel = (urgency) => {
    const labels = {
      low: 'Низкая',
      normal: 'Обычная',
      high: 'Высокая'
    }
    return labels[urgency] || urgency
  }

  const getUrgencyColor = (urgency) => {
    const colors = {
      low: '#10b981',
      normal: '#f59e0b',
      high: '#ef4444'
    }
    return colors[urgency] || '#64748b'
  }

  const getAudienceLabel = (audience) => {
    const labels = {
      colleague: 'Коллега (внутренняя переписка)',
      manager: 'Руководитель',
      client: 'Клиент (пользователь услуг банка)',
      partner: 'Партнер (бизнес-сотрудничество)',
      regulator: 'Регулятор'
    }
    return labels[audience] || audience
  }

  const getToneLabel = (tone) => {
    const labels = {
      formal: 'Формальный',
      neutral: 'Нейтральный',
      friendly: 'Дружелюбный'
    }
    return labels[tone] || tone
  }

  const getSLA = (days) => {
    if (days === 0) return 'Ответ не требуется'
    if (days === 1) return '1 рабочий день'
    return `${days} рабочих дней`
  }

  if (!isVisible) {
    return null
  }

  return (
    <div className="operator-sidebar-wrapper">
      <div className="operator-sidebar">
        <div className="sidebar-header">
          <h3>Информация для оператора</h3>
        </div>

      <div className="sidebar-grid">
        {detailedAnalysis && (
          <>
            <div className="info-block">
              <div className="info-label">Категория письма</div>
              <div className="info-value category">{getCategoryLabel(detailedAnalysis.category)}</div>
            </div>

            <div className="info-block">
              <div className="info-label">Маршрутизация</div>
              <div className="info-value department">{detailedAnalysis.department}</div>
            </div>

            {detailedAnalysis.extracted_deadline_days !== null && detailedAnalysis.extracted_deadline_days !== undefined ? (
              <div className="info-block">
                <div className="info-label">Дедлайн из письма</div>
                <div className="info-value sla">
                  {getSLA(detailedAnalysis.extracted_deadline_days)}
                </div>
              </div>
            ) : (
              <div className="info-block">
                <div className="info-label">Дедлайн из письма</div>
                <div className="info-value" style={{ color: 'var(--text-light)', fontStyle: 'italic' }}>
                  не указан
                </div>
              </div>
            )}

            <div className="info-block">
              <div className="info-label">SLA (стандартный срок)</div>
              <div className="info-value sla">
                {getSLA(detailedAnalysis.estimated_sla_days)}
              </div>
            </div>

            {detailedAnalysis.extracted_info?.contact_info && (
              <div className="info-block">
                <div className="info-label">Контактные данные</div>
                <div className="info-value small-text">{detailedAnalysis.extracted_info.contact_info}</div>
              </div>
            )}

            {detailedAnalysis.extracted_info?.regulatory_references && detailedAnalysis.extracted_info.regulatory_references.length > 0 && (
              <div className="info-block">
                <div className="info-label">Нормативные акты</div>
                <div className="info-value small-text">
                  {detailedAnalysis.extracted_info.regulatory_references.map((ref, idx) => (
                    <div key={idx}>• {ref}</div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}

        {parameters && (
          <>
            <div className="info-block">
              <div className="info-label">Тип запроса</div>
              <div className={`info-value purpose purpose-${parameters.purpose}`}>{getPurposeLabel(parameters.purpose)}</div>
            </div>

            <div className="info-block">
              <div className="info-label">Срочность</div>
              <div 
                className={`info-value urgency urgency-${parameters.urgency}`}
                style={{ color: getUrgencyColor(parameters.urgency) }}
              >
                {getUrgencyLabel(parameters.urgency)}
              </div>
            </div>

            <div className="info-block">
              <div className="info-label">Аудитория</div>
              <div className={`info-value audience audience-${parameters.audience}`}>{getAudienceLabel(parameters.audience)}</div>
            </div>

            <div className="info-block">
              <div className="info-label">Тон письма</div>
              <div className={`info-value tone tone-${parameters.tone}`}>{getToneLabel(parameters.tone)}</div>
            </div>

            <div className="info-block">
              <div className="info-label">Длина ответа</div>
              <div className={`info-value length length-${parameters.length}`}>
                {parameters.length === 'short' && 'Короткое (3-4 предложения)'}
                {parameters.length === 'medium' && 'Среднее (5-8 предложений)'}
                {parameters.length === 'long' && 'Длинное (8-12 предложений)'}
              </div>
            </div>
          </>
        )}

        {emailData && (
          <>
            <div className="info-block">
              <div className="info-label">Тема входящего</div>
              <div className="info-value small-text">{emailData.source_subject}</div>
            </div>

            <div className="info-block">
              <div className="info-label">Длина текста</div>
              <div className="info-value">
                {emailData.source_body.length} символов
              </div>
            </div>
          </>
        )}

        <div className="info-block">
          <div className="info-label">Статус</div>
          <div className="info-value status-active">В обработке</div>
        </div>
      </div>

      <div className="sidebar-full-width">
        {detailedAnalysis?.extracted_info?.request_essence && (
          <div className="info-block info-block-full">
            <div className="info-label">Суть запроса</div>
            <div className="info-value small-text">{detailedAnalysis.extracted_info.request_essence}</div>
          </div>
        )}

        {detailedAnalysis?.extracted_info?.requirements && detailedAnalysis.extracted_info.requirements.length > 0 && (
          <div className="info-block info-block-full">
            <div className="info-label">Требования отправителя</div>
            <div className="info-value small-text">
              {detailedAnalysis.extracted_info.requirements.map((req, idx) => (
                <div key={idx}>• {req}</div>
              ))}
            </div>
          </div>
        )}

        {detailedAnalysis?.extracted_info?.legal_risks && detailedAnalysis.extracted_info.legal_risks.length > 0 && (
          <div className="info-block info-block-full risk-block">
            <div className="info-label">Юридические риски</div>
            <div className="info-value risk-text">
              {detailedAnalysis.extracted_info.legal_risks.map((risk, idx) => (
                <div key={idx}>⚠️ {risk}</div>
              ))}
            </div>
          </div>
        )}
      </div>
      </div>
    </div>
  )
}

export default OperatorSidebar

