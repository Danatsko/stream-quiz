const WS_PATH: string = window.APP_CONFIG.WS_PATH

export class WebSocketService {
  private ws: WebSocket | null = null
  private url: string
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectInterval = 2000
  private messageQueue: object[] = []
  public onOpen: (() => void) | null = null
  public onMessage: ((data: any) => void) | null = null
  public onDisconnect: ((event: CloseEvent) => void) | null = null
  public onReconnectAttempt: ((attempt: number) => void) | null = null
  public onError: ((message: string) => void) | null = null

  constructor(sessionUuid: string, role: 'take' | 'host' = 'take') {
    let baseUrl = WS_PATH

    if (baseUrl.startsWith('/')) {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      baseUrl = `${protocol}//${window.location.host}${baseUrl}`
    }

    this.url = `${baseUrl}/sessions/${sessionUuid}/${role}`
  }

  public connect(): void {
    if (
      this.ws &&
      (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)
    ) {
      return
    }

    this.ws = new WebSocket(this.url)

    this.ws.onopen = (): void => {
      setTimeout((): void => {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
          this.reconnectAttempts = 0
        }
      }, 1000)

      this.flushQueue()

      if (this.onOpen) {
        this.onOpen()
      }
    }

    this.ws.onmessage = (event: MessageEvent): void => {
      try {
        const data = JSON.parse(event.data)

        if (this.onMessage) {
          this.onMessage(data)
        }
      } catch (error) {}
    }

    this.ws.onclose = (event: CloseEvent): void => {
      if (this.onDisconnect) {
        this.onDisconnect(event)
      }
      if (event.code !== 1000 && event.code !== 1008 && event.code !== 1001) {
        this.attemptReconnect()
      }
    }

    this.ws.onerror = (): void => {
      this.ws?.close()
    }
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++

      if (this.onReconnectAttempt) {
        this.onReconnectAttempt(this.reconnectAttempts)
      }

      setTimeout((): void => {
        this.connect()
      }, this.reconnectInterval)
    } else {
      if (this.onError) {
        this.onError('Failed to connect to the server after multiple attempts')
      }
    }
  }

  public send(payload: object): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(payload))
    } else {
      this.messageQueue.push(payload)
    }
  }

  private flushQueue(): void {
    while (this.messageQueue.length > 0) {
      const payload = this.messageQueue.shift()

      if (payload) {
        this.send(payload)
      }
    }
  }

  public disconnect(): void {
    if (this.ws) {
      this.ws.close(1000, 'Client disconnected intentionally')

      this.ws = null
    }
  }
}
