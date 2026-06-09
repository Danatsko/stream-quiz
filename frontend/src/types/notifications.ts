export interface AppNotification {
  id: string
  message: string
  type: 'error' | 'success' | 'info'
}
