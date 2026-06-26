import type {
  ApiError,
  AskRequest,
  AskResponse,
  RowRecord,
  RowsResponse,
  UploadResponse,
} from '../types/api'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.trim() || 'http://127.0.0.1:8000'

const DEFAULT_ERROR_MESSAGE =
  'Something went wrong while talking to the server. Please try again.'

async function parseError(response: Response): Promise<ApiError> {
  let message = DEFAULT_ERROR_MESSAGE

  try {
    const payload = (await response.json()) as { detail?: string }
    if (payload?.detail && typeof payload.detail === 'string') {
      message = payload.detail
    }
  } catch {
    message = response.statusText || DEFAULT_ERROR_MESSAGE
  }

  return {
    message,
    status: response.status,
  }
}

async function parseJsonOrThrow<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw await parseError(response)
  }

  return (await response.json()) as T
}

export async function uploadCsv(file: File): Promise<UploadResponse> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE_URL}/upload-file`, {
    method: 'POST',
    body: formData,
  })

  return parseJsonOrThrow<UploadResponse>(response)
}

export async function getRows(
  page: number,
  pageSize: number,
): Promise<RowsResponse | null> {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  })

  const response = await fetch(`${API_BASE_URL}/rows?${params.toString()}`)

  return parseJsonOrThrow<RowsResponse | null>(response)
}

export async function askQuestion(payload: AskRequest): Promise<AskResponse> {
  const response = await fetch(`${API_BASE_URL}/ask`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  return parseJsonOrThrow<AskResponse>(response)
}

export function asReadableError(error: unknown): string {
  if (typeof error === 'object' && error && 'message' in error) {
    const message = (error as ApiError).message
    if (message && typeof message === 'string') {
      return message
    }
  }

  if (error instanceof Error) {
    return error.message
  }

  return DEFAULT_ERROR_MESSAGE
}

export function extractColumns(rows: RowRecord[]): string[] {
  if (!rows.length) {
    return []
  }

  return Object.keys(rows[0])
}
