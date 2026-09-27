/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Base URL of the backend API. Empty string uses the Vite dev-server proxy. */
  readonly VITE_API_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
