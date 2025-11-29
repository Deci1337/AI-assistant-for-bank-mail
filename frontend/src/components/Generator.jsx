import { useState, useRef, useEffect } from 'react'
import EmailForm from './EmailForm'
import EmailList from './EmailList'
import AddEmailForm from './AddEmailForm'
import ParametersForm from './ParametersForm'
import Result from './Result'
import Loading from './Loading'
import OperatorSidebar from './OperatorSidebar'
import UserProfile from './UserProfile'
import NotificationPanel from './NotificationPanel'
import { analyzeEmail, analyzeEmailDetailed, generateEmail, createThread, checkRecipientName } from '../services/api'
import { emailTemplates } from '../utils/emailTemplates'
import './Generator.css'

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

function Generator({ onBack, onDashboard, apiStatus }) {
  const [currentRequestData, setCurrentRequestData] = useState(null)
  const [parameters, setParameters] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [loadingText, setLoadingText] = useState('Анализируем письмо...')
  const [showResult, setShowResult] = useState(false)
  const [detailedAnalysis, setDetailedAnalysis] = useState(null)
  const [showProfile, setShowProfile] = useState(false)
  const [showAddEmail, setShowAddEmail] = useState(false)
  const [showNotifications, setShowNotifications] = useState(false)
  const [notifications, setNotifications] = useState([])
  const [generatedResponses, setGeneratedResponses] = useState(new Map()) // Храним сгенерированные ответы
  const [threadId, setThreadId] = useState(null) // ID текущей переписки
  const [hasRecipientName, setHasRecipientName] = useState(false) // Есть ли имя получателя во входящем письме
  const [emailFilter, setEmailFilter] = useState('incoming') // 'incoming' | 'read'
  const notificationIntervalRef = useRef(null)
  const generatingEmailsRef = useRef(new Set())
  const [emails, setEmails] = useState(() => {
    // Загружаем письма из localStorage при инициализации
    try {
      const saved = localStorage.getItem('bizmail_emails')
      if (saved) {
        const parsed = JSON.parse(saved)
        return parsed.map(email => ({ ...email, id: email.id || Date.now() + Math.random(), isRead: email.isRead !== undefined ? email.isRead : false }))
      }
    } catch (e) {
      console.error('Error loading emails from storage:', e)
    }
    return [
      {
        id: Date.now(),
        subject: 'Партнёрское предложение',
        isRead: false,
        body: `Уважаемый Иванов Иван Иванович, 

Просим рассмотреть возможность стратегического партнёрства Банка и ООО, в рамках реализации специального выпуска журнала «Финансовый Дом» №12/2026, посвящённого «Финансовой грамотности для малого и среднего бизнеса».

Журнал «Финансовый Дом» — авторитетное издание с аудиторией более 120 000 читателей — руководителей МСБ, владельцев бизнеса, финансовых директоров и предпринимателей, входящих в клиентскую базу крупных банков. Издание входит в топ-5 финансовых журналов России по уровню доверия и цитируемости (по данным Ассоциации деловой прессы, 2025).

Мы предлагаем:

Разместить эксклюзивную авторскую статью от банка на тему: «Как банк помогает МСБ выйти на международные рынки: инструменты финансирования и поддержки» — с участием экспертов вашего банка;

Организовать интервью с руководителем отдела корпоративного банковского обслуживания (в формате «Ключевой взгляд»);

Включить логотип и ссылку на сайт банка в титульной части выпуска и на сайте журнала;

Провести онлайн-вебинар с участием ваших специалистов — как часть продвижения номера (10 000+ ожидаемых участников);

Создать специальный QR-код, ведущий на страницу банка с условиями поддержки МСБ.

В рамках партнёрства мы также готовы предложить:

Возможность включения в материал информации о ваших продуктах (например, «Кредитный калькулятор МСБ» или «Программа льготного финансирования»), без рекламного характера — только в информационно-аналитическом ключе;

Размещение брендированного чек-листа «5 шагов к устойчивому финансовому росту» — как бесплатный бонус для читателей.

Планируем выпуск номера — март 2026 года.

Прошу рассмотреть возможность участия банка в проекте и направить ответ с указанием интереса.`,
      contact: null
    },
    {
      id: Date.now() + 1,
      subject: 'Запрос на согласование',
      isRead: false,
      body: `Дочерняя организация "Рога и копыта" планирует проведение офлайн-мероприятия для корпоративных клиентов Банка 28 ноября 2025 года в Москве, площадка — конференц-зал бизнес-центра «Горизонт». Цель мероприятия — повышение лояльности и демонстрация интегрированных решений группы компаний. В программе: выступления экспертов, кейсы клиентов, нетворкинг. Направляем на согласование:

Финальная программа мероприятия (в приложении)

Список приглашённых (все — действующие клиенты Банка)

Тезисы докладов (с упоминанием бренда Банка)

Проект коммуникационного письма для рассылки клиентам

Прошу согласовать организацию и проведение мероприятия, а также использование корпоративного бренда Банка в материалах до 23 ноября 2025 года.`,
      contact: null
    }
    ]
  })
  const loadingRef = useRef(null)
  const parametersFormRef = useRef(null)

  const handleAnalyzeAndGenerate = async (formData) => {
    setLoading(true)
    setLoadingText('AI анализирует входящее письмо...')
    setShowResult(false)
    
    setTimeout(() => {
      loadingRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }, 100)

    try {
      // Сохраняем входящее письмо в список
      saveIncomingEmail(formData)

      // ШАГ 0: Создаем или используем существующий thread
      let currentThreadId = threadId
      if (!currentThreadId) {
        setLoadingText('Создаем переписку...')
        const thread = await createThread(formData.source_subject, formData.company_context_id || null)
        currentThreadId = thread.id
        setThreadId(currentThreadId)
      }

      // ШАГ 1: Проверяем наличие имени получателя
      const recipientCheck = await checkRecipientName(
        formData.source_subject,
        formData.source_body
      )
      setHasRecipientName(recipientCheck.has_name)

      // ШАГ 2: Расширенный анализ
      const analysis = await analyzeEmailDetailed(
        formData.source_subject,
        formData.source_body,
        formData.company_context
      )

      setDetailedAnalysis(analysis)
      setParameters(analysis.parameters)
      setCurrentRequestData(formData)

      // ШАГ 2: Генерация с thread_id и всеми данными оператора
      setLoadingText('Генерируем ответное письмо...')
      const emailResult = await generateEmail({
        ...formData,
        thread_id: currentThreadId,
        parameters: analysis.parameters,
        // Добавляем все контактные данные оператора
        sender_first_name: formData.sender_first_name || DEFAULT_PROFILE.sender_first_name,
        sender_last_name: formData.sender_last_name || DEFAULT_PROFILE.sender_last_name,
        sender_middle_name: formData.sender_middle_name || DEFAULT_PROFILE.sender_middle_name,
        sender_position: formData.sender_position || DEFAULT_PROFILE.sender_position,
        sender_phone_work: DEFAULT_PROFILE.phone_work,
        sender_phone_mobile: DEFAULT_PROFILE.phone_mobile,
        sender_email: DEFAULT_PROFILE.email,
        sender_address: DEFAULT_PROFILE.address,
        sender_hotline: DEFAULT_PROFILE.hotline,
        sender_website: DEFAULT_PROFILE.website,
      })

      setResult(emailResult)
      setShowResult(true)
    } catch (error) {
      console.error('Error in handleAnalyzeAndGenerate:', error)
      const errorMessage = error.message || 'Неизвестная ошибка'
      alert('❌ Ошибка: ' + errorMessage)
      setResult({
        subject: 'Ошибка',
        body: errorMessage,
      })
      setShowResult(true)
      setLoading(false)
    } finally {
      setLoading(false)
    }
  }

  const handleRegenerate = async (newParameters) => {
    if (!currentRequestData) return

    setLoading(true)
    setLoadingText('Генерируем ответное письмо...')
    
    setTimeout(() => {
      loadingRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }, 100)

    try {
      // Проверяем наличие имени получателя при перегенерации
      if (!hasRecipientName) {
        const recipientCheck = await checkRecipientName(
          currentRequestData.source_subject,
          currentRequestData.source_body
        )
        setHasRecipientName(recipientCheck.has_name)
      }

      // Создаем thread, если его еще нет
      let currentThreadId = threadId
      if (!currentThreadId) {
        const thread = await createThread(currentRequestData.source_subject, currentRequestData.company_context_id || null)
        currentThreadId = thread.id
        setThreadId(currentThreadId)
      }

      console.log('[DEBUG] Regenerating with thread_id:', currentThreadId)
      console.log('[DEBUG] Parameters:', newParameters)
      console.log('[DEBUG] extra_directives:', newParameters.extra_directives)

      const emailResult = await generateEmail({
        ...currentRequestData,
        thread_id: currentThreadId,
        parameters: newParameters,
        // Добавляем все контактные данные оператора
        sender_first_name: currentRequestData.sender_first_name || DEFAULT_PROFILE.sender_first_name,
        sender_last_name: currentRequestData.sender_last_name || DEFAULT_PROFILE.sender_last_name,
        sender_middle_name: currentRequestData.sender_middle_name || DEFAULT_PROFILE.sender_middle_name,
        sender_position: currentRequestData.sender_position || DEFAULT_PROFILE.sender_position,
        sender_phone_work: DEFAULT_PROFILE.phone_work,
        sender_phone_mobile: DEFAULT_PROFILE.phone_mobile,
        sender_email: DEFAULT_PROFILE.email,
        sender_address: DEFAULT_PROFILE.address,
        sender_hotline: DEFAULT_PROFILE.hotline,
        sender_website: DEFAULT_PROFILE.website,
      })

      setResult(emailResult)
      setParameters(newParameters)
    } catch (error) {
      alert('❌ Ошибка: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  const handleClear = () => {
    setCurrentRequestData(null)
    setParameters(null)
    setResult(null)
    setShowResult(false)
    setDetailedAnalysis(null)
    setThreadId(null) // Сбрасываем thread_id при очистке
  }

  // Функция для перехода к готовому ответу из уведомления
  const handleNavigateToGeneratedResponse = (emailId) => {
    const generatedData = generatedResponses.get(emailId)
    if (!generatedData) {
      alert('Ответ еще не сгенерирован')
      return
    }

    // Показываем подтверждение перед переходом
    const confirmNavigation = window.confirm('Вы действительно хотите перейти к другому письму?')
    if (!confirmNavigation) {
      return
    }

    // Закрываем панель уведомлений
    setShowNotifications(false)

    // Устанавливаем данные для отображения
    setCurrentRequestData({
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
      source_subject: generatedData.email.subject,
      source_body: generatedData.email.body,
      company_context: 'ПСБ банк',
    })
    setDetailedAnalysis(generatedData.analysis)
    setParameters(generatedData.parameters)
    setResult(generatedData.result)
    setShowResult(true)
    
    // Прокручиваем к результату
    setTimeout(() => {
      loadingRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }, 100)
  }

  const handleEmailSelect = (email) => {
    handleAnalyzeAndGenerate({
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
      source_subject: email.subject,
      source_body: email.body,
      company_context: 'ПСБ банк',
    })
  }

  const handleGenerateFromEmail = (email) => {
    handleEmailSelect(email)
  }

  const handleAddEmail = (email) => {
    const newEmail = {
      ...email,
      id: Date.now(),
      isRead: false,
    }
    const updatedEmails = [newEmail, ...emails]
    setEmails(updatedEmails)
    try {
      localStorage.setItem('bizmail_emails', JSON.stringify(updatedEmails))
    } catch (e) {
      console.error('Error saving emails to storage:', e)
    }
  }

  // Сохраняем письма в localStorage при изменении
  useEffect(() => {
    try {
      localStorage.setItem('bizmail_emails', JSON.stringify(emails))
    } catch (e) {
      console.error('Error saving emails to storage:', e)
    }
  }, [emails])

  // Сохраняем входящее письмо в список при генерации
  const saveIncomingEmail = (formData) => {
    const emailExists = emails.some(
      e => e.subject === formData.source_subject && e.body === formData.source_body
    )
    
    if (!emailExists) {
      const newEmail = {
        id: Date.now(),
        subject: formData.source_subject,
        body: formData.source_body,
        isRead: false,
        contact: null,
      }
      const updatedEmails = [newEmail, ...emails]
      setEmails(updatedEmails)
      try {
        localStorage.setItem('bizmail_emails', JSON.stringify(updatedEmails))
      } catch (e) {
        console.error('Error saving emails to storage:', e)
      }
    }
  }

  const handleMarkAsRead = (emailId, isRead) => {
    const updatedEmails = emails.map(email =>
      email.id === emailId ? { ...email, isRead } : email
    )
    setEmails(updatedEmails)
    try {
      localStorage.setItem('bizmail_emails', JSON.stringify(updatedEmails))
    } catch (e) {
      console.error('Error saving emails to storage:', e)
    }
  }

  // Запуск интервала для генерации новых писем
  useEffect(() => {
    if (!showResult) return // Генерируем только когда показан результат

    // Функция для обновления/добавления уведомления по ID письма
    const updateNotification = (emailId, type, title, message, details = null, generatedData = null) => {
      setNotifications((prev) => {
        const existingIndex = prev.findIndex(n => n.emailId === emailId)
        const notification = {
          emailId,
          type,
          title,
          message,
          details,
          timestamp: Date.now(),
        }
        
        if (existingIndex >= 0) {
          // Обновляем существующее уведомление
          const updated = [...prev]
          updated[existingIndex] = notification
          return updated
        } else {
          // Создаем новое уведомление
          return [notification, ...prev]
        }
      })
      
      // Сохраняем сгенерированные данные, если есть
      if (generatedData) {
        setGeneratedResponses((prev) => {
          const newMap = new Map(prev)
          newMap.set(emailId, generatedData)
          return newMap
        })
      }
      
      // Показываем визуальное уведомление в браузере
      if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(title, {
          body: message,
          icon: '/favicon.ico',
        })
      }
    }

    // Функция для генерации случайного письма
    const generateRandomEmail = () => {
      const templates = emailTemplates
      const randomTemplate = templates[Math.floor(Math.random() * templates.length)]
      
      return {
        subject: randomTemplate.subject,
        body: randomTemplate.body,
        contact: null,
      }
    }

    // Функция для автоматической генерации ответа на письмо
    const autoGenerateResponse = async (email, emailId) => {
      // Проверяем, не генерируем ли мы уже ответ на это письмо
      if (generatingEmailsRef.current.has(emailId)) {
        return
      }
      
      generatingEmailsRef.current.add(emailId)
      
      try {
        // Обновляем уведомление - стадия 2: начата генерация
        updateNotification(
          emailId,
          'generation_started',
          'Начата генерация ответа',
          `Генерируется ответ на письмо: "${email.subject}"`,
          {
            subject: email.subject,
            preview: email.body.substring(0, 100) + '...',
          }
        )

        // Анализ письма
        const analysis = await analyzeEmailDetailed(
          email.subject,
          email.body,
          'ПСБ банк'
        )

        // Генерация ответа
        const emailResult = await generateEmail({
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
          source_subject: email.subject,
          source_body: email.body,
          company_context: 'ПСБ банк',
          parameters: analysis.parameters,
        })

        // Обновляем уведомление - стадия 3: ответ сгенерирован
        // Обновляем уведомление - стадия 3: ответ сгенерирован
        updateNotification(
          emailId,
          'generation_completed',
          'Ответ сгенерирован',
          `Ответ на письмо "${email.subject}" успешно создан`,
          {
            subject: email.subject,
            preview: emailResult.body.substring(0, 100) + '...',
          },
          {
            email,
            analysis,
            result: emailResult,
            parameters: analysis.parameters,
          }
        )
      } catch (error) {
        console.error('Ошибка при автоматической генерации ответа:', error)
        // При ошибке не сохраняем данные, чтобы кнопка "Перейти к ответу" не появлялась
        updateNotification(
          emailId,
          'generation_completed',
          'Ошибка генерации',
          `Не удалось сгенерировать ответ на письмо "${email.subject}"`,
          {
            subject: email.subject,
          },
          null // Не сохраняем данные при ошибке
        )
      } finally {
        generatingEmailsRef.current.delete(emailId)
      }
    }

    // Запрашиваем разрешение на уведомления
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission()
    }

    // Функция для создания нового письма и автоматической генерации ответа
    const createNewEmailWithAutoResponse = () => {
      const newEmail = generateRandomEmail()
      const emailId = `${newEmail.subject}-${Date.now()}`
      
      // Добавляем письмо в список с ID
      const emailWithId = { ...newEmail, id: emailId, isRead: false }
      setEmails((prev) => {
        const updated = [emailWithId, ...prev]
        try {
          localStorage.setItem('bizmail_emails', JSON.stringify(updated))
        } catch (e) {
          console.error('Error saving emails to storage:', e)
        }
        return updated
      })
      
      // Создаем уведомление - стадия 1: новое письмо
      updateNotification(
        emailId,
        'new_email',
        'Новое письмо',
        `Получено новое письмо: "${newEmail.subject}"`,
        {
          subject: newEmail.subject,
          preview: newEmail.body.substring(0, 100) + '...',
        }
      )

      // Автоматически начинаем генерацию ответа
      setTimeout(() => {
        autoGenerateResponse(newEmail, emailId)
      }, 2000) // Задержка 2 секунды перед началом генерации
    }

    // Устанавливаем интервал (10-20 секунд)
    const interval = Math.random() * 10000 + 10000 // 10-20 секунд
    notificationIntervalRef.current = setInterval(createNewEmailWithAutoResponse, interval)

    return () => {
      if (notificationIntervalRef.current) {
        clearInterval(notificationIntervalRef.current)
      }
    }
  }, [showResult])

  // Очистка при размонтировании
  useEffect(() => {
    return () => {
      if (notificationIntervalRef.current) {
        clearInterval(notificationIntervalRef.current)
      }
    }
  }, [])

  return (
    <div className="generator-page">
      <div className="generator-header">
        <div className="generator-header-wrapper">
          <div className="generator-header-container">
            <div className="generator-header-content">
              <button className="btn-back" onClick={onBack}>
                ← Назад
              </button>
              <h1>Генератор писем</h1>
              <div style={{ display: 'flex', gap: '12px', marginLeft: 'auto' }}>
                <button 
                  className="btn-add-email" 
                  onClick={() => setShowAddEmail(true)}
                  aria-label="Добавить письмо"
                  title="Добавить письмо"
                >
                  +
                </button>
                <button 
                  className="btn-notifications" 
                  onClick={() => setShowNotifications(true)}
                  aria-label="Уведомления"
                  title="Уведомления"
                >
                  🔔
                  {notifications.length > 0 && (
                    <span className="notification-badge">{notifications.length}</span>
                  )}
                </button>
                {onDashboard && (
                  <button className="btn-analytics" onClick={onDashboard}>
                    📊
                  </button>
                )}
                <button 
                  className="btn-profile" 
                  onClick={() => setShowProfile(true)}
                  aria-label="Профиль пользователя"
                  title="Профиль пользователя"
                >
                  👤
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="generator-main">
        <p className="api-status-small">{apiStatus}</p>
        {!showResult && (
          <div className="email-layout">
            <div className="email-sidebar">
              <button 
                className={`email-filter-btn ${emailFilter === 'incoming' ? 'active' : ''}`}
                onClick={() => setEmailFilter('incoming')}
              >
                Входящие
                <span className="email-count">
                  {emails.filter(e => !e.isRead).length}
                </span>
              </button>
              <button 
                className={`email-filter-btn ${emailFilter === 'read' ? 'active' : ''}`}
                onClick={() => setEmailFilter('read')}
              >
                Прочитанные
                <span className="email-count">
                  {emails.filter(e => e.isRead).length}
                </span>
              </button>
            </div>
            <div className="email-content">
              <EmailList 
                emails={emailFilter === 'incoming' 
                  ? emails.filter(e => !e.isRead)
                  : emails.filter(e => e.isRead)}
                title={emailFilter === 'incoming' ? 'Входящие письма' : 'Прочитанные письма'}
                onSelectEmail={handleEmailSelect}
                onGenerateFromEmail={handleGenerateFromEmail}
                onMarkAsRead={handleMarkAsRead}
              />
            </div>
          </div>
        )}

        {showResult && parameters && result && (
          <>
            <div className="operator-section">
              <OperatorSidebar 
                emailData={currentRequestData}
                parameters={parameters}
                detailedAnalysis={detailedAnalysis}
                isVisible={true}
              />
            </div>

            <div className="result-layout">
              <div className="result-wrapper">
                <Result 
                  result={result} 
                  onRedirect={handleClear}
                  onRegenerateWithCurrentParams={() => {
                    if (parametersFormRef.current) {
                      parametersFormRef.current.handleRegenerate()
                    }
                  }}
                  isLoading={loading}
                />
              </div>

              <div className="parameters-sidebar">
                <ParametersForm
                  ref={parametersFormRef}
                  initialParameters={parameters}
                  onRegenerate={handleRegenerate}
                  onClear={handleClear}
                  hasSenderName={hasRecipientName}
                  isLoading={loading}
                />
              </div>
            </div>
          </>
        )}

        <div ref={loadingRef}>
          <Loading active={loading} text={loadingText} />
        </div>
      </div>
      <UserProfile isOpen={showProfile} onClose={() => setShowProfile(false)} />
      <AddEmailForm 
        isOpen={showAddEmail} 
        onClose={() => setShowAddEmail(false)}
        onAdd={handleAddEmail}
      />
      <NotificationPanel 
        isOpen={showNotifications}
        onClose={() => setShowNotifications(false)}
        notifications={notifications}
        generatedResponses={generatedResponses}
        onNavigateToResponse={handleNavigateToGeneratedResponse}
      />
    </div>
  )
}

export default Generator;
