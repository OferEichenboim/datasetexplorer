interface ErrorPanelProps {
  message: string
  onReturnPrevious: () => void
  onStartOver: () => void
}

export function ErrorPanel({
  message,
  onReturnPrevious,
  onStartOver,
}: ErrorPanelProps) {
  return (
    <section className="panel error-panel" role="alert">
      <h2>Something Went Wrong</h2>
      <p>{message}</p>
      <div className="error-actions">
        <button type="button" onClick={onReturnPrevious}>
          Return To Previous Step
        </button>
        <button type="button" className="secondary" onClick={onStartOver}>
          Start From Beginning
        </button>
      </div>
    </section>
  )
}
