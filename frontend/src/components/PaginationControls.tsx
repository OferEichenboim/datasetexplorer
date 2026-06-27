import { useEffect, useState } from 'react'

interface PaginationControlsProps {
  page: number
  pageSize: number
  totalPages: number
  totalRows: number
  isBusy: boolean
  onPageChange: (nextPage: number) => void
  onPageSizeChange: (nextPageSize: number) => void
}

const MIN_PAGE_SIZE = 1
const MAX_PAGE_SIZE = 200

export function PaginationControls({
  page,
  pageSize,
  totalPages,
  totalRows,
  isBusy,
  onPageChange,
  onPageSizeChange,
}: PaginationControlsProps) {
  const [draftPageSize, setDraftPageSize] = useState(String(pageSize))

  useEffect(() => {
    setDraftPageSize(String(pageSize))
  }, [pageSize])

  const canGoBack = page > 1 && !isBusy
  const canGoForward = totalPages > 0 && page < totalPages && !isBusy

  const commitPageSize = () => {
    const rawValue = draftPageSize.trim()

    if (!rawValue) {
      setDraftPageSize(String(pageSize))
      return
    }

    const parsedValue = Number(rawValue)
    const isWholeNumber = Number.isInteger(parsedValue)
    const isInRange = parsedValue >= MIN_PAGE_SIZE && parsedValue <= MAX_PAGE_SIZE

    if (!isWholeNumber || !isInRange) {
      setDraftPageSize(String(pageSize))
      return
    }

    if (parsedValue !== pageSize) {
      onPageSizeChange(parsedValue)
    }
  }

  return (
    <section className="panel controls-panel">
      <div className="controls-grid">
        <div className="control-block">
          <label htmlFor="page-size-input">Rows Per Page</label>
          <input
            id="page-size-input"
            type="number"
            min={MIN_PAGE_SIZE}
            max={MAX_PAGE_SIZE}
            step={1}
            inputMode="numeric"
            value={draftPageSize}
            onChange={(event) => setDraftPageSize(event.target.value)}
            onBlur={commitPageSize}
            onKeyDown={(event) => {
              if (event.key === 'Enter') {
                event.preventDefault()
                commitPageSize()
                event.currentTarget.blur()
                return
              }

              if (event.key === 'Escape') {
                setDraftPageSize(String(pageSize))
                event.currentTarget.blur()
              }
            }}
            disabled={isBusy}
          />
        </div>

        <div className="control-block">
          <span>Page Navigation</span>
          <div className="pager-buttons">
            <button type="button" onClick={() => onPageChange(page - 1)} disabled={!canGoBack}>
              Previous
            </button>
            <span>
              Page {page} / {Math.max(totalPages, 1)}
            </span>
            <button
              type="button"
              onClick={() => onPageChange(page + 1)}
              disabled={!canGoForward}
            >
              Next
            </button>
          </div>
        </div>

        <div className="control-block summary-block">
          <span>Total Rows</span>
          <strong>{totalRows}</strong>
        </div>
      </div>
    </section>
  )
}
