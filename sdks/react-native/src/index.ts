/**
 * Daten React Native SDK
 *
 * Cross-platform SDK for React Native applications
 * Version: 3.3.0
 */

import { useState, useEffect, useCallback, useContext, createContext } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import axios, { AxiosInstance } from 'axios';

// MARK: - Configuration

export interface DatenConfiguration {
  baseUrl: string;
  apiKey?: string;
  enableOfflineMode?: boolean;
  syncIntervalSeconds?: number;
}

// MARK: - Models

export interface Document {
  id: string;
  title: string;
  content: string;
  createdAt: Date;
  updatedAt: Date;
  userId: string;
  version: number;
}

export interface AuthCredentials {
  username: string;
  password: string;
}

export interface AuthToken {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
  tokenType: string;
}

// MARK: - Sync Status

export type SyncStatus =
  | { type: 'idle' }
  | { type: 'syncing' }
  | { type: 'completed' }
  | { type: 'failed'; error: Error };

// MARK: - Errors

export class DatenError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'DatenError';
  }
}

export class NotAuthenticatedError extends DatenError {
  constructor() {
    super('User is not authenticated');
    this.name = 'NotAuthenticatedError';
  }
}

export class OfflineModeDisabledError extends DatenError {
  constructor() {
    super('Offline mode is disabled');
    this.name = 'OfflineModeDisabledError';
  }
}

// MARK: - Sync Operations

type SyncOperation =
  | { type: 'create'; document: Document }
  | { type: 'update'; document: Document }
  | { type: 'delete'; id: string };

// MARK: - Main SDK Client

export class DatenClient {
  private config: Required<DatenConfiguration>;
  private httpClient: AxiosInstance;
  private authToken: AuthToken | null = null;
  private syncInterval: NodeJS.Timer | null = null;
  private pendingOperations: SyncOperation[] = [];

  constructor(configuration: DatenConfiguration) {
    this.config = {
      baseUrl: configuration.baseUrl,
      apiKey: configuration.apiKey,
      enableOfflineMode: configuration.enableOfflineMode ?? true,
      syncIntervalSeconds: configuration.syncIntervalSeconds ?? 300,
    };

    this.httpClient = axios.create({
      baseURL: this.config.baseUrl,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add interceptor for auth token
    this.httpClient.interceptors.request.use((config) => {
      if (this.authToken) {
        config.headers.Authorization = `Bearer ${this.authToken.accessToken}`;
      } else if (this.config.apiKey) {
        config.headers['X-API-Key'] = this.config.apiKey;
      }
      return config;
    });

    this.loadAuthToken();
  }

  // MARK: - Authentication

  async signIn(credentials: AuthCredentials): Promise<void> {
    const response = await this.httpClient.post<AuthToken>('/auth/login', {
      username: credentials.username,
      password: credentials.password,
    });

    this.authToken = response.data;
    await this.saveAuthToken(response.data);

    if (this.config.enableOfflineMode) {
      this.startAutoSync();
      await this.performSync();
    }
  }

  async signOut(): Promise<void> {
    this.authToken = null;
    await this.clearAuthToken();
    this.stopAutoSync();
    this.pendingOperations = [];
  }

  async refreshToken(): Promise<void> {
    if (!this.authToken) {
      throw new NotAuthenticatedError();
    }

    const response = await this.httpClient.post<AuthToken>('/auth/refresh', {
      refresh_token: this.authToken.refreshToken,
    });

    this.authToken = response.data;
    await this.saveAuthToken(response.data);
  }

  isAuthenticated(): boolean {
    return this.authToken !== null;
  }

  // MARK: - Document Operations

  async fetchDocuments(): Promise<Document[]> {
    if (!this.isAuthenticated()) {
      throw new NotAuthenticatedError();
    }

    const response = await this.httpClient.get<Document[]>('/documents');
    return response.data.map(this.parseDocument);
  }

  async createDocument(document: Omit<Document, 'id' | 'createdAt' | 'updatedAt' | 'version'>): Promise<Document> {
    if (!this.isAuthenticated()) {
      throw new NotAuthenticatedError();
    }

    const response = await this.httpClient.post<Document>('/documents', document);
    const created = this.parseDocument(response.data);

    if (this.config.enableOfflineMode) {
      this.queueOperation({ type: 'create', document: created });
    }

    return created;
  }

  async updateDocument(document: Document): Promise<Document> {
    if (!this.isAuthenticated()) {
      throw new NotAuthenticatedError();
    }

    const response = await this.httpClient.put<Document>(`/documents/${document.id}`, document);
    const updated = this.parseDocument(response.data);

    if (this.config.enableOfflineMode) {
      this.queueOperation({ type: 'update', document: updated });
    }

    return updated;
  }

  async deleteDocument(id: string): Promise<void> {
    if (!this.isAuthenticated()) {
      throw new NotAuthenticatedError();
    }

    await this.httpClient.delete(`/documents/${id}`);

    if (this.config.enableOfflineMode) {
      this.queueOperation({ type: 'delete', id });
    }
  }

  // MARK: - Sync Operations

  async syncNow(): Promise<void> {
    if (!this.config.enableOfflineMode) {
      throw new OfflineModeDisabledError();
    }

    await this.performSync();
  }

  private async performSync(): Promise<void> {
    const operations = [...this.pendingOperations];
    this.pendingOperations = [];

    for (const operation of operations) {
      try {
        switch (operation.type) {
          case 'create':
            await this.httpClient.post('/documents', operation.document);
            break;
          case 'update':
            await this.httpClient.put(`/documents/${operation.document.id}`, operation.document);
            break;
          case 'delete':
            await this.httpClient.delete(`/documents/${operation.id}`);
            break;
        }
      } catch (error) {
        // Re-queue failed operations
        this.pendingOperations.push(operation);
      }
    }
  }

  private queueOperation(operation: SyncOperation): void {
    this.pendingOperations.push(operation);
  }

  private startAutoSync(): void {
    if (this.syncInterval) return;

    this.syncInterval = setInterval(async () => {
      if (this.isAuthenticated()) {
        try {
          await this.performSync();
        } catch (error) {
          console.error('Auto-sync failed:', error);
        }
      }
    }, this.config.syncIntervalSeconds * 1000);
  }

  private stopAutoSync(): void {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
      this.syncInterval = null;
    }
  }

  // MARK: - Storage Helpers

  private async saveAuthToken(token: AuthToken): Promise<void> {
    await AsyncStorage.setItem('daten_auth_token', JSON.stringify(token));
  }

  private async loadAuthToken(): Promise<void> {
    const stored = await AsyncStorage.getItem('daten_auth_token');
    if (stored) {
      this.authToken = JSON.parse(stored);
    }
  }

  private async clearAuthToken(): Promise<void> {
    await AsyncStorage.removeItem('daten_auth_token');
  }

  private parseDocument(doc: any): Document {
    return {
      ...doc,
      createdAt: new Date(doc.createdAt),
      updatedAt: new Date(doc.updatedAt),
    };
  }

  // MARK: - Cleanup

  destroy(): void {
    this.stopAutoSync();
  }
}

// MARK: - React Context

interface DatenContextValue {
  client: DatenClient;
  isAuthenticated: boolean;
  syncStatus: SyncStatus;
}

const DatenContext = createContext<DatenContextValue | null>(null);

export interface DatenProviderProps {
  configuration: DatenConfiguration;
  children: React.ReactNode;
}

export function DatenProvider({ configuration, children }: DatenProviderProps): JSX.Element {
  const [client] = useState(() => new DatenClient(configuration));
  const [isAuthenticated, setIsAuthenticated] = useState(client.isAuthenticated());
  const [syncStatus, setSyncStatus] = useState<SyncStatus>({ type: 'idle' });

  useEffect(() => {
    return () => {
      client.destroy();
    };
  }, [client]);

  const value: DatenContextValue = {
    client,
    isAuthenticated,
    syncStatus,
  };

  return <DatenContext.Provider value={value}>{children}</DatenContext.Provider>;
}

export function useDatenClient(): DatenClient {
  const context = useContext(DatenContext);
  if (!context) {
    throw new Error('useDatenClient must be used within DatenProvider');
  }
  return context.client;
}

// MARK: - React Hooks

export function useAuth() {
  const client = useDatenClient();
  const [isAuthenticated, setIsAuthenticated] = useState(client.isAuthenticated());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const signIn = useCallback(
    async (credentials: AuthCredentials) => {
      try {
        setLoading(true);
        setError(null);
        await client.signIn(credentials);
        setIsAuthenticated(true);
      } catch (err) {
        setError(err as Error);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [client]
  );

  const signOut = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      await client.signOut();
      setIsAuthenticated(false);
    } catch (err) {
      setError(err as Error);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [client]);

  return {
    isAuthenticated,
    loading,
    error,
    signIn,
    signOut,
  };
}

export function useDocuments() {
  const client = useDatenClient();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchDocuments = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const docs = await client.fetchDocuments();
      setDocuments(docs);
      return docs;
    } catch (err) {
      setError(err as Error);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [client]);

  const createDocument = useCallback(
    async (document: Omit<Document, 'id' | 'createdAt' | 'updatedAt' | 'version'>) => {
      try {
        setLoading(true);
        setError(null);
        const created = await client.createDocument(document);
        setDocuments((prev) => [...prev, created]);
        return created;
      } catch (err) {
        setError(err as Error);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [client]
  );

  const updateDocument = useCallback(
    async (document: Document) => {
      try {
        setLoading(true);
        setError(null);
        const updated = await client.updateDocument(document);
        setDocuments((prev) => prev.map((doc) => (doc.id === updated.id ? updated : doc)));
        return updated;
      } catch (err) {
        setError(err as Error);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [client]
  );

  const deleteDocument = useCallback(
    async (id: string) => {
      try {
        setLoading(true);
        setError(null);
        await client.deleteDocument(id);
        setDocuments((prev) => prev.filter((doc) => doc.id !== id));
      } catch (err) {
        setError(err as Error);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [client]
  );

  useEffect(() => {
    if (client.isAuthenticated()) {
      fetchDocuments();
    }
  }, [client, fetchDocuments]);

  return {
    documents,
    loading,
    error,
    fetchDocuments,
    createDocument,
    updateDocument,
    deleteDocument,
  };
}

export function useSync() {
  const client = useDatenClient();
  const [syncStatus, setSyncStatus] = useState<SyncStatus>({ type: 'idle' });

  const syncNow = useCallback(async () => {
    try {
      setSyncStatus({ type: 'syncing' });
      await client.syncNow();
      setSyncStatus({ type: 'completed' });
    } catch (error) {
      setSyncStatus({ type: 'failed', error: error as Error });
      throw error;
    }
  }, [client]);

  return {
    syncStatus,
    syncNow,
  };
}

// MARK: - Exports

export default DatenClient;
