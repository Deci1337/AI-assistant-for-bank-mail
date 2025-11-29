import './Homepage.css'

function Homepage({ onStart, onDashboard, apiStatus }) {
  return (
    <>
      <section className="hero">
        <div className="container">
          <h1>SHIFT HAPPENS</h1>
          <h2>AI-ассистент для корпоративной переписки</h2>
          <p>Генерируйте профессиональные деловые письма за секунды</p>
          <div className="hero-buttons">
            <button className="hero-btn" onClick={onStart}>
              Создать письмо
            </button>
            <button className="hero-btn secondary" onClick={onDashboard}>
              Аналитика
            </button>
          </div>
          <p id="apiStatus" className={`api-status ${apiStatus.includes('✓') ? 'success' : apiStatus.includes('✗') ? 'error' : ''}`}>
            {apiStatus}
          </p>
        </div>
      </section>
      <section className="benefits">
        <div className="container">
          <h2>Преимущества</h2>
          <div className="benefits-grid">
            <div className="benefit-card">
              <div className="benefit-icon">⚡</div>
              <h3>Быстрая генерация</h3>
              <p>Создавайте письма за секунды, экономьте часы работы</p>
            </div>
            <div className="benefit-card">
              <div className="benefit-icon">✓</div>
              <h3>Корпоративный стиль</h3>
              <p>Соответствие стандартам вашей компании</p>
            </div>
            <div className="benefit-card">
              <div className="benefit-icon">🔒</div>
              <h3>Безопасность данных</h3>
              <p>Защита конфиденциальной информации</p>
            </div>
            <div className="benefit-card">
              <div className="benefit-icon">✎</div>
              <h3>Множество стилей</h3>
              <p>Шаблоны для любых деловых ситуаций</p>
            </div>
          </div>
        </div>
      </section>
      <section className="how-it-works">
        <div className="container">
          <h2>Как это работает</h2>
          <div className="steps">
            <div className="step">
              <div className="step-number">1</div>
              <h3>Введите данные</h3>
              <p>Укажите свои данные и входящее письмо</p>
            </div>
            <div className="step">
              <div className="step-number">2</div>
              <h3>AI анализирует</h3>
              <p>Автоматически определяет параметры</p>
            </div>
            <div className="step">
              <div className="step-number">3</div>
              <h3>Настройте и получите</h3>
              <p>Измените параметры и перегенерируйте</p>
            </div>
          </div>
        </div>
      </section>
      <footer className="footer">
        <div className="container">
          <p>© 2025 SHIFT HAPPENS. AI-ассистент для корпоративной переписки.</p>
        </div>
      </footer>
    </>
  )
}

export default Homepage

