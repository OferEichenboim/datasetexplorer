import { useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import { DataTable } from './components/DataTable'
import { ErrorPanel } from './components/ErrorPanel'
import { PaginationControls } from './components/PaginationControls'
import { askQuestion, asReadableError, getRows, uploadCsv } from './services/api'
import type { AskResponse, RowsResponse } from './types/api'
import './App.css'

type AppView =
  | 'uploadPrompt'
  | 'uploading'
  | 'rowsReady'
  | 'querying'
  | 'queryResult'
  | 'error'

interface ViewSnapshot {
  view: Exclude<AppView, 'error'>
  rowsData: RowsResponse | null
  queryData: AskResponse | null
  page: number
  pageSize: number
  uploadedFileName: string
  question: string
}

const DEFAULT_PAGE_SIZE = 50
const MIN_PAGE_SIZE = 1
const MAX_PAGE_SIZE = 200

function App() {
  const [view, setView] = useState<AppView>('uploadPrompt')
  const [rowsData, setRowsData] = useState<RowsResponse | null>(null)
  const [queryData, setQueryData] = useState<AskResponse | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadedFileName, setUploadedFileName] = useState('')
  const [question, setQuestion] = useState('')
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(DEFAULT_PAGE_SIZE)
  const [errorMessage, setErrorMessage] = useState('')
  const [snapshot, setSnapshot] = useState<ViewSnapshot | null>(null)

  const hasRowsLoaded = rowsData !== null
  const currentTableTitle =
    view === 'queryResult'
      ? 'Query Result Rows'
      : `Dataset Rows${rowsData ? ` (${rowsData.table})` : ''}`
  const currentRows = useMemo(() => {
    if (view === 'queryResult' && queryData) {
      return queryData.data
    }
    return rowsData?.rows ?? []
  }, [queryData, rowsData, view])

  const saveSnapshot = () => {
    if (view === 'error') {
      return
    }

    setSnapshot({
      view,
      rowsData,
      queryData,
      page,
      pageSize,
      uploadedFileName,
      question,
    })
  }

  const enterError = (message: string) => {
    setErrorMessage(message)
    setView('error')
  }

  const resetApp = () => {
    setView('uploadPrompt')
    setRowsData(null)
    setQueryData(null)
    setSelectedFile(null)
    setUploadedFileName('')
    setQuestion('')
    setPage(1)
    setPageSize(DEFAULT_PAGE_SIZE)
    setErrorMessage('')
    setSnapshot(null)
  }

  const restoreSnapshot = () => {
    if (!snapshot) {
      resetApp()
      return
    }

    setView(snapshot.view)
    setRowsData(snapshot.rowsData)
    setQueryData(snapshot.queryData)
    setPage(snapshot.page)
    setPageSize(snapshot.pageSize)
    setUploadedFileName(snapshot.uploadedFileName)
    setQuestion(snapshot.question)
    setErrorMessage('')
  }

  const loadRowsPage = async (nextPage: number, nextPageSize: number) => {
    const data = await getRows(nextPage, nextPageSize)

    if (!data) {
      throw new Error(
        'No uploaded database was found. Please upload a CSV file and try again.',
      )
    }

    setRowsData(data)
    setPage(nextPage)
    setPageSize(nextPageSize)
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      enterError('Please choose a .csv file before uploading.')
      return
    }

    if (!selectedFile.name.toLowerCase().endsWith('.csv')) {
      enterError('Only .csv files are supported. Please choose a valid CSV file.')
      return
    }

    saveSnapshot()
    setView('uploading')

    try {
      await uploadCsv(selectedFile)
      setUploadedFileName(selectedFile.name)
      setQueryData(null)
      await loadRowsPage(1, pageSize)
      setView('rowsReady')
      setErrorMessage('')
    } catch (error) {
      enterError(asReadableError(error))
    }
  }

  const handlePageChange = async (nextPage: number) => {
    if (!rowsData || nextPage < 1) {
      return
    }

    if (rowsData.total_pages > 0 && nextPage > rowsData.total_pages) {
      return
    }

    saveSnapshot()
    setView('uploading')

    try {
      await loadRowsPage(nextPage, pageSize)
      setView('rowsReady')
      setErrorMessage('')
    } catch (error) {
      enterError(asReadableError(error))
    }
  }

  const handlePageSizeChange = async (nextPageSize: number) => {
    if (!Number.isFinite(nextPageSize)) {
      enterError('Rows per page must be a valid number.')
      return
    }

    if (nextPageSize < MIN_PAGE_SIZE || nextPageSize > MAX_PAGE_SIZE) {
      enterError(`Rows per page must be between ${MIN_PAGE_SIZE} and ${MAX_PAGE_SIZE}.`)
      return
    }

    saveSnapshot()
    setView('uploading')

    try {
      await loadRowsPage(1, nextPageSize)
      setView('rowsReady')
      setErrorMessage('')
    } catch (error) {
      enterError(asReadableError(error))
    }
  }

  const handleAskQuestion = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const cleanQuestion = question.trim()

    if (!cleanQuestion) {
      enterError('Please enter a natural-language query before submitting.')
      return
    }

    saveSnapshot()
    setView('querying')

    try {
      const result = await askQuestion({
        question: cleanQuestion,
        dataset_id: uploadedFileName || undefined,
        execute: true,
      })
      setQueryData(result)
      setView('queryResult')
      setErrorMessage('')
    } catch (error) {
      enterError(asReadableError(error))
    }
  }

  const returnToDatasetRows = () => {
    if (!rowsData) {
      enterError('No rows are available yet. Please upload a CSV file first.')
      return
    }

    setView('rowsReady')
    setErrorMessage('')
  }

  return (
    <main className="app-shell">
      <header className="app-header">
        <p className="kicker">Dataset Explorer</p>
        <h1>CSV Explorer For FastAPI Backend</h1>
        <p className="subtitle">
          Upload a CSV file, browse rows with pagination, and ask natural-language
          questions over the generated SQLite table.
        </p>
      </header>

      {view === 'error' && (
        <ErrorPanel
          message={errorMessage}
          onReturnPrevious={restoreSnapshot}
          onStartOver={resetApp}
        />
      )}

      <section className="panel upload-panel">
        <h2>Step 1: Upload A CSV File</h2>
        <p>Only files ending in .csv are supported.</p>

        <div className="upload-row">
          <input
            type="file"
            accept=".csv,text/csv"
            onChange={(event) => {
              const file = event.target.files?.[0] ?? null
              setSelectedFile(file)
            }}
            disabled={view === 'uploading' || view === 'querying'}
          />
          <button
            type="button"
            onClick={handleUpload}
            disabled={!selectedFile || view === 'uploading' || view === 'querying'}
          >
            {view === 'uploading' ? 'Uploading...' : 'Upload CSV'}
          </button>
        </div>

        {uploadedFileName && <p className="helper">Active dataset: {uploadedFileName}</p>}
      </section>

      {hasRowsLoaded && view !== 'error' && (
        <>
          {view !== 'queryResult' && rowsData && (
            <PaginationControls
              page={page}
              pageSize={pageSize}
              totalPages={rowsData.total_pages}
              totalRows={rowsData.total_rows}
              isBusy={view === 'uploading' || view === 'querying'}
              onPageChange={handlePageChange}
              onPageSizeChange={handlePageSizeChange}
            />
          )}

          <DataTable
            title={currentTableTitle}
            rows={currentRows}
            emptyMessage={
              view === 'queryResult'
                ? 'The query completed successfully but returned no rows.'
                : 'No rows were found for this page.'
            }
          />

          {view === 'queryResult' && queryData && (
            <section className="panel result-panel">
              <div className="result-head">
                <h2>Query Details</h2>
                <button type="button" onClick={returnToDatasetRows}>
                  Back To Dataset Rows
                </button>
              </div>
              <p>
                <strong>Explanation:</strong> {queryData.explanation}
              </p>
              <p>
                <strong>SQL:</strong>
              </p>
              <pre>{queryData.generated_sql}</pre>
            </section>
          )}

          <section className="panel query-panel">
            <h2>Step 2: Ask A Natural-Language Query</h2>
            <form onSubmit={handleAskQuestion}>
              <textarea
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                placeholder="Example: Show the top 10 rows by revenue."
                rows={4}
                disabled={view === 'uploading' || view === 'querying'}
              />
              <div className="query-actions">
                <button type="submit" disabled={view === 'uploading' || view === 'querying'}>
                  {view === 'querying' ? 'Running Query...' : 'Run Query'}
                </button>
                <button type="button" className="secondary" onClick={resetApp}>
                  Start Over
                </button>
              </div>
            </form>
          </section>
        </>
      )}

      {!hasRowsLoaded && view !== 'error' && (
        <section className="panel empty-state">
          <h2>Ready To Explore</h2>
          <p>
            Upload your CSV first. After upload, the first page of rows will appear and
            query input will be enabled below the table.
          </p>
        </section>
      )}

      {view === 'uploading' && (
        <section className="status-note" aria-live="polite">
          Loading rows from backend...
        </section>
      )}

      {view === 'querying' && (
        <section className="status-note" aria-live="polite">
          Asking backend to generate and execute SQL...
        </section>
      )}
    </main>
  )
}

export default App
