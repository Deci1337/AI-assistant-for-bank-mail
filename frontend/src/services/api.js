export const getApiBase = async () => {
  // Сначала пробуем относительный путь (через Vite proxy в dev-режиме)
  try {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 1000)
    const res = await fetch('/health', {
      signal: controller.signal,
      method: 'GET',
    })
    clearTimeout(timeoutId)
    if (res.ok) {
      return '' // Пустая строка = относительный путь
    }
  } catch {
    // Proxy не работает, пробуем найти бэкенд напрямую
  }

  // Проверяем мета-тег
  const meta = document.querySelector('meta[name="bizmail-api-base"]')
  if (meta?.content) {
    const base = meta.content.replace(/\/$/, '')
    if (await checkBackendAvailable(base)) {
      return base
    }
  }
  
  // Пробуем найти бэкенд на портах 8000-8009
  const ports = [8001, 8000, 8002, 8003, 8004, 8005, 8006, 8007, 8008, 8009]
  for (const port of ports) {
    const base = `http://localhost:${port}`
    if (await checkBackendAvailable(base)) {
      return base
    }
  }
  
  // Fallback на стандартный порт
  return 'http://localhost:8001'
}

const checkBackendAvailable = async (baseUrl) => {
  try {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 1000)
    const url = baseUrl ? `${baseUrl}/health` : '/health'
    const res = await fetch(url, {
      signal: controller.signal,
      method: 'GET',
    })
    clearTimeout(timeoutId)
    return res.ok
  } catch {
    return false
  }
}

export const analyzeEmail = async (subject, body, companyContext) => {
  const apiBase = await getApiBase()
  const url = apiBase ? `${apiBase}/api/emails/analyze` : '/api/emails/analyze'
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      source_subject: subject,
      source_body: body,
      company_context: companyContext,
    }),
  })

  if (!response.ok) {
    throw new Error(`Ошибка анализа: HTTP ${response.status}`)
  }

  return response.json()
}

export const analyzeEmailDetailed = async (subject, body, companyContext) => {
  const apiBase = await getApiBase()
  const url = apiBase ? `${apiBase}/api/emails/analyze-detailed` : '/api/emails/analyze-detailed'
  
  let errorDetails = null
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        source_subject: subject || '',
        source_body: body || '',
        company_context: companyContext || 'ПСБ банк',
      }),
    })

    if (!response.ok) {
      try {
        const errorPayload = await response.json()
        if (errorPayload.detail) {
          errorDetails = typeof errorPayload.detail === 'string' 
            ? errorPayload.detail 
            : JSON.stringify(errorPayload.detail)
        } else if (errorPayload.message) {
          errorDetails = errorPayload.message
        }
      } catch {
        errorDetails = `HTTP ${response.status}: ${response.statusText}`
      }
      
      const errorMsg = errorDetails 
        ? `Ошибка расширенного анализа: ${errorDetails}` 
        : `Ошибка расширенного анализа: HTTP ${response.status}`
      throw new Error(errorMsg)
    }

    return response.json()
  } catch (error) {
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error('Не удалось подключиться к серверу. Проверьте, что бэкенд запущен.')
    }
    throw error
  }
}

export const createThread = async (subject, companyContextId = null) => {
  const apiBase = await getApiBase()
  const url = apiBase ? `${apiBase}/api/threads` : '/api/threads'
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        subject,
        company_context_id: companyContextId,
      }),
    })

    if (!response.ok) {
      let err = `HTTP ${response.status}`
      try {
        const payload = await response.json()
        if (payload.detail) {
          err = typeof payload.detail === 'string' ? payload.detail : JSON.stringify(payload.detail)
        } else if (payload.message) {
          err = payload.message
        }
      } catch {}
      
      if (response.status === 404) {
        throw new Error(`Endpoint not found: ${url}. Проверьте, что бэкенд запущен и доступен.`)
      }
      throw new Error(err)
    }

    return response.json()
  } catch (error) {
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error('Не удалось подключиться к серверу. Проверьте, что бэкенд запущен.')
    }
    throw error
  }
}

export const generateEmail = async (requestData) => {
  const apiBase = await getApiBase()
  const url = apiBase ? `${apiBase}/api/emails/generate` : '/api/emails/generate'
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestData),
    })

    if (!response.ok) {
      let err = `HTTP ${response.status}`
      try {
        const payload = await response.json()
        if (payload.detail) {
          err = typeof payload.detail === 'string' ? payload.detail : JSON.stringify(payload.detail)
        } else if (payload.message) {
          err = payload.message
        }
      } catch {}
      
      if (response.status === 404) {
        throw new Error(`Endpoint not found: ${url}. Проверьте, что бэкенд запущен и доступен.`)
      }
      throw new Error(err)
    }

    return response.json()
  } catch (error) {
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error('Не удалось подключиться к серверу. Проверьте, что бэкенд запущен.')
    }
    throw error
  }
}

export const getAnalyticsOverview = async (days = 7) => {
  const apiBase = await getApiBase()
  const url = apiBase ? `${apiBase}/api/analytics/overview` : '/api/analytics/overview'
  const response = await fetch(`${url}?days=${days}`)
  if (!response.ok) throw new Error(`HTTP ${response.status}`)
  return response.json()
}

export const getMessagesByDay = async (days = 7) => {
  const apiBase = await getApiBase()
  const url = apiBase ? `${apiBase}/api/analytics/messages-by-day` : '/api/analytics/messages-by-day'
  const response = await fetch(`${url}?days=${days}`)
  if (!response.ok) throw new Error(`HTTP ${response.status}`)
  return response.json()
}

export const getThreadsByContext = async (days = 30) => {
  const apiBase = await getApiBase()
  const url = apiBase ? `${apiBase}/api/analytics/threads-by-context` : '/api/analytics/threads-by-context'
  const response = await fetch(`${url}?days=${days}`)
  if (!response.ok) throw new Error(`HTTP ${response.status}`)
  return response.json()
}

export const getThreadsGrowth = async (days = 30) => {
  const apiBase = await getApiBase()
  const url = apiBase ? `${apiBase}/api/analytics/threads-growth` : '/api/analytics/threads-growth'
  const response = await fetch(`${url}?days=${days}`)
  if (!response.ok) throw new Error(`HTTP ${response.status}`)
  return response.json()
}

export const getTopThreads = async (limit = 10, days = 30) => {
  const apiBase = await getApiBase()
  const url = apiBase ? `${apiBase}/api/analytics/top-threads` : '/api/analytics/top-threads'
  const response = await fetch(`${url}?limit=${limit}&days=${days}`)
  if (!response.ok) throw new Error(`HTTP ${response.status}`)
  return response.json()
}

export const getDirectivesUsage = async (days = 30) => {
  const apiBase = await getApiBase()
  const url = apiBase ? `${apiBase}/api/analytics/directives-usage` : '/api/analytics/directives-usage'
  const response = await fetch(`${url}?days=${days}`)
  if (!response.ok) throw new Error(`HTTP ${response.status}`)
  return response.json()
}

export const checkRecipientName = async (subject, body) => {
  const apiBase = await getApiBase()
  const url = apiBase ? `${apiBase}/api/recipient/check` : '/api/recipient/check'
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        source_subject: subject,
        source_body: body,
      }),
    })

    if (!response.ok) {
      let err = `HTTP ${response.status}`
      try {
        const payload = await response.json()
        if (payload.detail) {
          err = typeof payload.detail === 'string' ? payload.detail : JSON.stringify(payload.detail)
        } else if (payload.message) {
          err = payload.message
        }
      } catch {}
      
      if (response.status === 404) {
        throw new Error(`Endpoint not found: ${url}. Проверьте, что бэкенд запущен и доступен.`)
      }
      throw new Error(`Ошибка проверки получателя: ${err}`)
    }

    return response.json()
  } catch (error) {
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error('Не удалось подключиться к серверу. Проверьте, что бэкенд запущен.')
    }
    throw error
  }
}

