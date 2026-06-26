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
  const canGoBack = page > 1 && !isBusy
  const canGoForward = totalPages > 0 && page < totalPages && !isBusy

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
            value={pageSize}
            onChange={(event) => onPageSizeChange(Number(event.target.value))}
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
