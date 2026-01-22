/**
 * DMS React Native SDK - Main client for Document Management System
 * Version: 3.3.0
 */

import {
  AuthResponse,
  User,
  Document,
  DocumentCreate,
  DocumentUpdate,
  DocumentListResponse,
  DashboardResponse,
  StatisticsResponse,
  NotificationListResponse,
  WebSocketMessage,
  DMSError,
  Configuration,
} from './types';

export class DMSClient {
  private static instance: DMSClient;
  private baseURL: string = 'https://api.dms.example.com';
  private apiKey?: string;
  private accessToken?: string;
  private config: Configuration;
  private ws?: WebSocket;

  private constructor() {
    this.config = {
      baseURL: 'https://api.dms.example.com',
      timeout: 30000,
      enableLogging: false,
    };
  }

  /**
   * Get singleton instance
   */
  public static getInstance(): DMSClient {
    if (!DMSClient.instance) {
      DMSClient.instance = new DMSClient();
    }
    return DMSClient.instance;
  }

  /**
   * Configure the SDK
   */
  public configure(config: Configuration): void {
    this.config = { ...this.config, ...config };
    this.baseURL = config.baseURL;
    this.apiKey = config.apiKey;

    if (config.enableLogging) {
      console.log(`[DMS SDK] Configured with base URL: ${config.baseURL}`);
    }
  }

  /**
   * Set API key for authentication
   */
  public setAPIKey(key: string): void {
    this.apiKey = key;
  }

  /**
   * Set OAuth access token
   */
  public setAccessToken(token: string): void {
    this.accessToken = token;
  }

  // MARK: - Authentication

  /**
   * Login with username and password
   */
  public async login(username: string, password: string): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>('POST', '/api/v1/auth/login', {
      username,
      password,
    });

    this.accessToken = response.accessToken;
    return response;
  }

  /**
   * Logout current user
   */
  public async logout(): Promise<void> {
    await this.request('POST', '/api/v1/auth/logout');
    this.accessToken = undefined;
  }

  // MARK: - Documents

  /**
   * Get list of documents
   */
  public async getDocuments(page: number = 1, pageSize: number = 20): Promise<DocumentListResponse> {
    return this.request<DocumentListResponse>('GET', '/api/v1/documents', undefined, {
      page: page.toString(),
      page_size: pageSize.toString(),
    });
  }

  /**
   * Get document by ID
   */
  public async getDocument(id: string): Promise<Document> {
    return this.request<Document>('GET', `/api/v1/documents/${id}`);
  }

  /**
   * Create new document
   */
  public async createDocument(document: DocumentCreate): Promise<Document> {
    return this.request<Document>('POST', '/api/v1/documents', document);
  }

  /**
   * Update existing document
   */
  public async updateDocument(id: string, document: DocumentUpdate): Promise<Document> {
    return this.request<Document>('PUT', `/api/v1/documents/${id}`, document);
  }

  /**
   * Delete document
   */
  public async deleteDocument(id: string): Promise<void> {
    await this.request('DELETE', `/api/v1/documents/${id}`);
  }

  /**
   * Upload document file
   */
  public async uploadDocument(
    file: File | Blob,
    filename: string,
    metadata?: Record<string, string>
  ): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file, filename);

    if (metadata) {
      Object.entries(metadata).forEach(([key, value]) => {
        formData.append(key, value);
      });
    }

    const url = `${this.baseURL}/api/v1/documents/upload`;
    const headers: HeadersInit = {};

    this.addAuthHeaders(headers);

    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (!response.ok) {
      throw await this.handleErrorResponse(response);
    }

    return response.json();
  }

  /**
   * Download document file
   */
  public async downloadDocument(id: string): Promise<Blob> {
    const url = `${this.baseURL}/api/v1/documents/${id}/download`;
    const headers: HeadersInit = {};

    this.addAuthHeaders(headers);

    const response = await fetch(url, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      throw await this.handleErrorResponse(response);
    }

    return response.blob();
  }

  // MARK: - Search

  /**
   * Search documents
   */
  public async searchDocuments(
    query: string,
    filters?: Record<string, any>
  ): Promise<DocumentListResponse> {
    return this.request<DocumentListResponse>('POST', '/api/v1/search', {
      query,
      filters,
    });
  }

  // MARK: - Analytics

  /**
   * Get dashboard analytics
   */
  public async getDashboard(): Promise<DashboardResponse> {
    return this.request<DashboardResponse>('GET', '/api/v1/analytics/dashboard');
  }

  /**
   * Get document statistics
   */
  public async getStatistics(startDate?: string, endDate?: string): Promise<StatisticsResponse> {
    const queryParams: Record<string, string> = {};
    if (startDate) queryParams.start_date = startDate;
    if (endDate) queryParams.end_date = endDate;

    return this.request<StatisticsResponse>('GET', '/api/v1/analytics/statistics', undefined, queryParams);
  }

  // MARK: - Notifications

  /**
   * Get notifications
   */
  public async getNotifications(page: number = 1, pageSize: number = 20): Promise<NotificationListResponse> {
    return this.request<NotificationListResponse>('GET', '/api/v1/notifications', undefined, {
      page: page.toString(),
      page_size: pageSize.toString(),
    });
  }

  /**
   * Mark notification as read
   */
  public async markNotificationAsRead(id: string): Promise<void> {
    await this.request('POST', `/api/v1/notifications/${id}/read`);
  }

  // MARK: - WebSocket (Real-time)

  /**
   * Connect to WebSocket for real-time updates
   */
  public connectWebSocket(
    onMessage: (message: WebSocketMessage) => void,
    onError: (error: Event) => void,
    onClose: (event: CloseEvent) => void
  ): WebSocket {
    const wsUrl = this.baseURL
      .replace('https://', 'wss://')
      .replace('http://', 'ws://') + '/ws';

    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      if (this.config.enableLogging) {
        console.log('[DMS SDK] WebSocket connected');
      }
    };

    this.ws.onmessage = (event: MessageEvent) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        onMessage(message);
      } catch (error) {
        console.error('[DMS SDK] Failed to parse WebSocket message:', error);
      }
    };

    this.ws.onerror = (error: Event) => {
      if (this.config.enableLogging) {
        console.error('[DMS SDK] WebSocket error:', error);
      }
      onError(error);
    };

    this.ws.onclose = (event: CloseEvent) => {
      if (this.config.enableLogging) {
        console.log('[DMS SDK] WebSocket closed');
      }
      onClose(event);
    };

    return this.ws;
  }

  /**
   * Disconnect WebSocket
   */
  public disconnectWebSocket(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = undefined;
    }
  }

  // MARK: - Private Helpers

  private async request<T>(
    method: string,
    endpoint: string,
    body?: any,
    queryParams?: Record<string, string>
  ): Promise<T> {
    let url = `${this.baseURL}${endpoint}`;

    if (queryParams) {
      const params = new URLSearchParams(queryParams);
      url += `?${params.toString()}`;
    }

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    this.addAuthHeaders(headers);

    if (this.config.enableLogging) {
      console.log(`[DMS SDK] ${method} ${url}`);
    }

    const response = await fetch(url, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });

    if (!response.ok) {
      throw await this.handleErrorResponse(response);
    }

    // For DELETE requests, return empty response
    if (method === 'DELETE') {
      return {} as T;
    }

    return response.json();
  }

  private addAuthHeaders(headers: HeadersInit): void {
    if (this.apiKey) {
      headers['X-API-Key'] = this.apiKey;
    }

    if (this.accessToken) {
      headers['Authorization'] = `Bearer ${this.accessToken}`;
    }
  }

  private async handleErrorResponse(response: Response): Promise<DMSError> {
    let message = `HTTP ${response.status}`;

    try {
      const errorData = await response.json();
      message = errorData.message || message;
    } catch (e) {
      // Failed to parse error response
    }

    return new DMSError(
      message,
      response.status,
      response.status === 401 ? 'unauthorized' :
      response.status === 404 ? 'not_found' :
      response.status >= 500 ? 'server_error' :
      'api_error'
    );
  }
}

export default DMSClient;
