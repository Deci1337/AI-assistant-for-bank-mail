import './UserProfile.css'

function UserProfile({ isOpen, onClose }) {
  if (!isOpen) return null

  const profile = {
    lastName: 'Победоносцев',
    firstName: 'Константин',
    middleName: 'Константинович',
    fullName: 'Победоносцев Константин Константинович',
    position: 'Начальник отдела медиа продвижения управления маркетинговых коммуникаций департамента маркетинга',
    phoneWork: '+7 (495) 777-10-20, доб. 7000',
    phoneMobile: '+7 (903) 676-00-00',
    email: 'k.p.pobedonoscev@psbank.ru',
    address: 'ул. Смирновская, д. 10, стр. 22, г. Москва, Россия, 109052',
    hotline: '8 800 333 78 90',
    website: 'psbank.ru'
  }

  return (
    <>
      <div className="profile-overlay" onClick={onClose}></div>
      <div className="profile-modal">
        <div className="profile-header">
          <h3>Профиль пользователя</h3>
          <button className="profile-close-btn" onClick={onClose} aria-label="Закрыть">
            ×
          </button>
        </div>
        <div className="profile-content">
          <div className="profile-section">
            <div className="profile-section-title">Личная информация</div>
            <div className="profile-info">
              <div className="profile-field">
                <div className="profile-label">Фамилия</div>
                <div className="profile-value">{profile.lastName}</div>
              </div>
              <div className="profile-field">
                <div className="profile-label">Имя</div>
                <div className="profile-value">{profile.firstName}</div>
              </div>
              <div className="profile-field">
                <div className="profile-label">Отчество</div>
                <div className="profile-value">{profile.middleName}</div>
              </div>
            </div>
          </div>

          <div className="profile-section">
            <div className="profile-section-title">Должность</div>
            <div className="profile-info">
              <div className="profile-field">
                <div className="profile-label">Должность</div>
                <div className="profile-value">{profile.position}</div>
              </div>
            </div>
          </div>

          <div className="profile-section">
            <div className="profile-section-title">Контактная информация</div>
            <div className="profile-info">
              <div className="profile-field">
                <div className="profile-label">Рабочий телефон</div>
                <div className="profile-value">
                  <a href={`tel:${profile.phoneWork.replace(/\s/g, '')}`}>{profile.phoneWork}</a>
                </div>
              </div>
              <div className="profile-field">
                <div className="profile-label">Мобильный телефон</div>
                <div className="profile-value">
                  <a href={`tel:${profile.phoneMobile.replace(/\s/g, '')}`}>{profile.phoneMobile}</a>
                </div>
              </div>
              <div className="profile-field">
                <div className="profile-label">Email</div>
                <div className="profile-value">
                  <a href={`mailto:${profile.email}`}>{profile.email}</a>
                </div>
              </div>
              <div className="profile-field">
                <div className="profile-label">Адрес</div>
                <div className="profile-value">{profile.address}</div>
              </div>
            </div>
          </div>

          <div className="profile-section">
            <div className="profile-section-title">Корпоративная информация</div>
            <div className="profile-info">
              <div className="profile-field">
                <div className="profile-label">Горячая линия</div>
                <div className="profile-value">
                  <a href={`tel:${profile.hotline.replace(/\s/g, '')}`}>{profile.hotline}</a>
                </div>
              </div>
              <div className="profile-field">
                <div className="profile-label">Сайт</div>
                <div className="profile-value">
                  <a href={`https://${profile.website}`} target="_blank" rel="noopener noreferrer">{profile.website}</a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

export default UserProfile
