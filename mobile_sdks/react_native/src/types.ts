/**
 * Type definitions for DMS React Native SDK
 */

// MARK: - Configuration

export interface Configuration {
  baseURL: string;
  apiKey?: string;
  timeout?: number;
  enableLogging?: boolean;
}

// MARK: - Authentication Types

export interface AuthResponse {
  accessToken: string;
  refreshToken?: string;
  tokenType: string;
  expiresIn: number;
  user: User;
}

export interface User {
  id: string;
  username: string;
  email: string;
  firstName?: string;
  lastName?: string;
  role: string;
  createdAt: string;
}

// MARK: - Document Types

export interface Document {
  id: string;
  title: string;
  description?: string;
  fileUrl?: string;
  mimeType?: string;
  fileSize?: number;
  status: DocumentStatus;
  tags?: string[];
  metadata?: Record<string, string>;
  createdBy: string;
  createdAt: string;
  updatedAt: string;
}

export enum DocumentStatus {
  DRAFT = 'draft',
  PENDING = 'pending',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  ARCHIVED = 'archived',
}

export interface DocumentCreate {
  title: string;
  description?: string;
  tags?: string[];
  metadata?: Record<string, string>;
}

export interface DocumentUpdate {
  title?: string;
  description?: string;
  status?: DocumentStatus;
  tags?: string[];
  metadata?: Record<string, string>;
}

export interface DocumentListResponse {
  documents: Document[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

// MARK: - Analytics Types

export interface DashboardResponse {
  metrics: DashboardMetrics;
  recentDocuments: Document[];
  activityChart: ChartData;
}

export interface DashboardMetrics {
  totalDocuments: number;
  pendingApprovals: number;
  recentUploads: number;
  storageUsed: number;
}

export interface ChartData {
  labels: string[];
  datasets: Dataset[];
}

export interface Dataset {
  label: string;
  data: number[];
  backgroundColor?: string;
}

export interface StatisticsResponse {
  totalDocuments: number;
  documentsByStatus: Record<string, number>;
  documentsByType: Record<string, number>;
  uploadTrend: TrendData;
  topUsers: UserStatistics[];
}

export interface TrendData {
  period: string;
  data: TrendPoint[];
}

export interface TrendPoint {
  date: string;
  count: number;
}

export interface UserStatistics {
  userId: string;
  username: string;
  documentCount: number;
  lastActivity: string;
}

// MARK: - Notification Types

export interface Notification {
  id: string;
  title: string;
  message: string;
  type: NotificationType;
  isRead: boolean;
  data?: Record<string, string>;
  createdAt: string;
}

export enum NotificationType {
  INFO = 'info',
  SUCCESS = 'success',
  WARNING = 'warning',
  ERROR = 'error',
  DOCUMENT_UPDATE = 'document_update',
  APPROVAL_REQUEST = 'approval_request',
}

export interface NotificationListResponse {
  notifications: Notification[];
  total: number;
  unreadCount: number;
  page: number;
  pageSize: number;
}

// MARK: - WebSocket Types

export interface WebSocketMessage {
  type: WebSocketMessageType;
  data: WebSocketMessageData;
  timestamp: string;
}

export enum WebSocketMessageType {
  DOCUMENT_CREATED = 'document_created',
  DOCUMENT_UPDATED = 'document_updated',
  DOCUMENT_DELETED = 'document_deleted',
  NOTIFICATION = 'notification',
  HEARTBEAT = 'heartbeat',
}

export interface WebSocketMessageData {
  documentId?: string;
  notificationId?: string;
  message?: string;
}

// MARK: - Error Types

export class DMSError extends Error {
  public readonly statusCode?: number;
  public readonly errorCode: string;

  constructor(message: string, statusCode?: number, errorCode: string = 'unknown_error') {
    super(message);
    this.name = 'DMSError';
    this.statusCode = statusCode;
    this.errorCode = errorCode;
    Object.setPrototypeOf(this, DMSError.prototype);
  }
}

// MARK: - React Native Specific Types

export interface DocumentPickerResult {
  uri: string;
  name: string;
  type: string;
  size: number;
}

export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}
