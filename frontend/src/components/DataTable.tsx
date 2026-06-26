import type { RowRecord } from '../types/api'

interface DataTableProps {
  title: string
  rows: RowRecord[]
  emptyMessage: string
}

export function DataTable({ title, rows, emptyMessage }: DataTableProps) {
  const columns = rows.length ? Object.keys(rows[0]) : []

  return (
    <section className="panel table-panel" aria-live="polite">
      <div className="panel-head">
        <h2>{title}</h2>
        <span className="badge">{rows.length} shown</span>
      </div>

      {rows.length === 0 ? (
        <div className="empty-table">{emptyMessage}</div>
      ) : (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                {columns.map((column) => (
                  <th key={column}>{column}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, rowIndex) => (
                <tr key={rowIndex}>
                  {columns.map((column) => (
                    <td key={`${rowIndex}-${column}`}>{String(row[column] ?? '')}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
