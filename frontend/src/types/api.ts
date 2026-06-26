export type RowRecord = Record<string, unknown>

export interface UploadResponse {
  status: string
  path: string
  message: string
  sqlite?: {
    db_path?: string
    table_name?: string
    row_count?: number
  }
}

export interface RowsResponse {
  table: string
  page: number
  page_size: number
  total_rows: number
  total_pages: number
  rows: RowRecord[]
}

export interface AskRequest {
  question: string
  dataset_id?: string
  execute?: boolean
}

export interface AskResponse {
  status: string
  question: string
  generated_sql: string
  explanation: string
  data: RowRecord[]
}

export interface ApiError {
  message: string
  status?: number
}
