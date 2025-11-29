import './Loading.css'

function Loading({ active, text }) {
  if (!active) return null

  return (
    <div className="loading active">
      <div className="spinner"></div>
      <p>{text}</p>
    </div>
  )
}

export default Loading

