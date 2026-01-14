/**
 * @dms/react-native-sdk
 *
 * Cross-platform React Native module for Document Management System
 *
 * Features:
 * - Document upload/download
 * - Offline-first architecture with Redux/MobX integration
 * - Push notifications (FCM, APNs)
 * - Biometric authentication
 * - Camera & gallery access
 * - File picker
 * - Document preview
 * - TypeScript support
 * - React hooks
 *
 * Requirements:
 * - React Native 0.70+
 * - TypeScript 4.9+
 *
 * Installation:
 * npm install @dms/react-native-sdk
 * # or
 * yarn add @dms/react-native-sdk
 */

import { NativeModules, NativeEventEmitter, Platform } from 'react-native';
import { useState, useEffect, useCallback, useRef } from 'react';

// MARK: - Types

export interface DMSConfiguration {
  baseUrl: string;
  apiKey: string;
  offlineEnabled?: boolean;
  biometricEnabled?: boolean;
  maxUploadSize?: number; // bytes
  timeout?: number; // milliseconds
}

export interface DMSDocument {
  id: string;
  title: string;
  contentType: string;
  size: number;
  createdAt: Date;
  updatedAt: Date;
  tags?: string[];
  metadata?: Record<string, string>;
}

export interface UploadProgress {
  documentId: string;
  bytesUploaded: number;
  totalBytes: number;
  progress: number; // 0-1
}

export interface DownloadResult {
  document: DMSDocument;
  localPath: string;
}

export enum SyncStatus {
  Idle = 'idle',
  Syncing = 'syncing',
  Completed = 'completed',
  Failed = 'failed'
}

export interface UploadOptions {
  title: string;
  tags?: string[];
  metadata?: Record<string, string>;
  onProgress?: (progress: UploadProgress) => void;
}

export interface BiometricType {
  available: boolean;
  type: 'fingerprint' | 'face' | 'iris' | 'none';
}

// MARK: - Native Module

const { DMSNativeModule } = NativeModules;

if (!DMSNativeModule) {
  throw new Error(
    'DMSNativeModule is not available. Make sure the native module is properly linked.'
  );
}

const eventEmitter = new NativeEventEmitter(DMSNativeModule);

// MARK: - API Client

export class DMSClient {
  private static instance: DMSClient | null = null;
  private configuration: DMSConfiguration | null = null;
  private uploadListeners: Map<string, (progress: UploadProgress) => void> = new Map();

  private constructor() {
    // Set up upload progress listener
    eventEmitter.addListener('onUploadProgress', (progress: UploadProgress) => {
      const listener = this.uploadListeners.get(progress.documentId);
      if (listener) {
        listener(progress);
      }
    });
  }

  /**
   * Configure the SDK
   */
  static configure(configuration: DMSConfiguration): void {
    if (!DMSClient.instance) {
      DMSClient.instance = new DMSClient();
    }
    DMSClient.instance.configuration = configuration;
    DMSNativeModule.configure(configuration);
  }

  /**
   * Get shared instance
   */
  static getInstance(): DMSClient {
    if (!DMSClient.instance) {
      throw new Error('DMSClient not configured. Call configure() first.');
    }
    return DMSClient.instance;
  }

  /**
   * List all documents
   */
  async listDocuments(): Promise<DMSDocument[]> {
    const documents = await DMSNativeModule.listDocuments();
    return documents.map(this.parseDocument);
  }

  /**
   * Get document by ID
   */
  async getDocument(id: string): Promise<DMSDocument> {
    const document = await DMSNativeModule.getDocument(id);
    return this.parseDocument(document);
  }

  /**
   * Upload document
   */
  async uploadDocument(
    localPath: string,
    options: UploadOptions
  ): Promise<DMSDocument> {
    const documentId = Math.random().toString(36).substring(7);

    if (options.onProgress) {
      this.uploadListeners.set(documentId, options.onProgress);
    }

    try {
      const document = await DMSNativeModule.uploadDocument(
        localPath,
        options.title,
        options.tags || [],
        options.metadata || {}
      );

      return this.parseDocument(document);
    } finally {
      this.uploadListeners.delete(documentId);
    }
  }

  /**
   * Download document
   */
  async downloadDocument(id: string): Promise<DownloadResult> {
    const result = await DMSNativeModule.downloadDocument(id);
    return {
      document: this.parseDocument(result.document),
      localPath: result.localPath
    };
  }

  /**
   * Delete document
   */
  async deleteDocument(id: string): Promise<void> {
    await DMSNativeModule.deleteDocument(id);
  }

  /**
   * Parse document from native
   */
  private parseDocument(doc: any): DMSDocument {
    return {
      ...doc,
      createdAt: new Date(doc.createdAt),
      updatedAt: new Date(doc.updatedAt)
    };
  }
}

// MARK: - Biometric Authentication

export class BiometricAuth {
  /**
   * Check if biometric authentication is available
   */
  static async isAvailable(): Promise<BiometricType> {
    const result = await DMSNativeModule.biometricIsAvailable();
    return result;
  }

  /**
   * Authenticate user
   */
  static async authenticate(
    reason: string = 'Authenticate to access documents'
  ): Promise<boolean> {
    const result = await DMSNativeModule.biometricAuthenticate(reason);
    return result;
  }
}

// MARK: - Offline Sync

export class OfflineSyncManager {
  /**
   * Queue document for upload when online
   */
  static async queueUpload(
    localPath: string,
    title: string,
    tags: string[] = []
  ): Promise<void> {
    await DMSNativeModule.queueUpload(localPath, title, tags);
  }

  /**
   * Sync all pending uploads
   */
  static async sync(): Promise<void> {
    await DMSNativeModule.sync();
  }

  /**
   * Get sync status
   */
  static async getSyncStatus(): Promise<SyncStatus> {
    const status = await DMSNativeModule.getSyncStatus();
    return status as SyncStatus;
  }
}

// MARK: - File Picker

export interface PickFileOptions {
  multiple?: boolean;
  type?: string[]; // MIME types
}

export interface PickedFile {
  uri: string;
  name: string;
  size: number;
  type: string;
}

export class FilePicker {
  /**
   * Pick file from device
   */
  static async pickFile(options: PickFileOptions = {}): Promise<PickedFile | PickedFile[]> {
    const result = await DMSNativeModule.pickFile(
      options.multiple || false,
      options.type || ['*/*']
    );
    return result;
  }

  /**
   * Pick image from camera
   */
  static async pickFromCamera(): Promise<PickedFile> {
    const result = await DMSNativeModule.pickFromCamera();
    return result;
  }

  /**
   * Pick image from gallery
   */
  static async pickFromGallery(multiple: boolean = false): Promise<PickedFile | PickedFile[]> {
    const result = await DMSNativeModule.pickFromGallery(multiple);
    return result;
  }
}

// MARK: - Push Notifications

export interface PushNotification {
  title: string;
  body: string;
  data?: Record<string, any>;
}

export class PushNotifications {
  /**
   * Request notification permission
   */
  static async requestPermission(): Promise<boolean> {
    const result = await DMSNativeModule.requestNotificationPermission();
    return result;
  }

  /**
   * Get device token
   */
  static async getDeviceToken(): Promise<string> {
    const token = await DMSNativeModule.getDeviceToken();
    return token;
  }

  /**
   * Handle notification received
   */
  static onNotificationReceived(callback: (notification: PushNotification) => void): () => void {
    const subscription = eventEmitter.addListener('onNotificationReceived', callback);
    return () => subscription.remove();
  }
}

// MARK: - React Hooks

/**
 * Hook for document list
 */
export function useDocuments() {
  const [documents, setDocuments] = useState<DMSDocument[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const client = DMSClient.getInstance();
      const docs = await client.listDocuments();
      setDocuments(docs);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { documents, loading, error, refresh };
}

/**
 * Hook for document upload
 */
export function useDocumentUpload() {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<Error | null>(null);

  const upload = useCallback(async (
    localPath: string,
    options: UploadOptions
  ): Promise<DMSDocument | null> => {
    setUploading(true);
    setProgress(0);
    setError(null);

    try {
      const client = DMSClient.getInstance();
      const document = await client.uploadDocument(localPath, {
        ...options,
        onProgress: (prog) => {
          setProgress(prog.progress);
          options.onProgress?.(prog);
        }
      });
      return document;
    } catch (err) {
      setError(err as Error);
      return null;
    } finally {
      setUploading(false);
    }
  }, []);

  return { upload, uploading, progress, error };
}

/**
 * Hook for offline sync status
 */
export function useSyncStatus() {
  const [status, setStatus] = useState<SyncStatus>(SyncStatus.Idle);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const updateStatus = async () => {
      const syncStatus = await OfflineSyncManager.getSyncStatus();
      setStatus(syncStatus);
    };

    updateStatus();

    // Poll every 5 seconds
    intervalRef.current = setInterval(updateStatus, 5000);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  const sync = useCallback(async () => {
    await OfflineSyncManager.sync();
  }, []);

  return { status, sync };
}

/**
 * Hook for biometric authentication
 */
export function useBiometric() {
  const [available, setAvailable] = useState(false);
  const [type, setType] = useState<BiometricType['type']>('none');

  useEffect(() => {
    BiometricAuth.isAvailable().then((result) => {
      setAvailable(result.available);
      setType(result.type);
    });
  }, []);

  const authenticate = useCallback(async (reason?: string): Promise<boolean> => {
    if (!available) {
      return false;
    }
    return await BiometricAuth.authenticate(reason);
  }, [available]);

  return { available, type, authenticate };
}

// MARK: - Redux Integration

export interface DMSState {
  documents: DMSDocument[];
  loading: boolean;
  error: string | null;
  syncStatus: SyncStatus;
}

export const initialState: DMSState = {
  documents: [],
  loading: false,
  error: null,
  syncStatus: SyncStatus.Idle
};

// Action types
export const DMS_ACTIONS = {
  FETCH_DOCUMENTS_START: 'DMS/FETCH_DOCUMENTS_START',
  FETCH_DOCUMENTS_SUCCESS: 'DMS/FETCH_DOCUMENTS_SUCCESS',
  FETCH_DOCUMENTS_FAILURE: 'DMS/FETCH_DOCUMENTS_FAILURE',
  UPLOAD_DOCUMENT_SUCCESS: 'DMS/UPLOAD_DOCUMENT_SUCCESS',
  DELETE_DOCUMENT_SUCCESS: 'DMS/DELETE_DOCUMENT_SUCCESS',
  SET_SYNC_STATUS: 'DMS/SET_SYNC_STATUS'
};

// Reducer
export function dmsReducer(state = initialState, action: any): DMSState {
  switch (action.type) {
    case DMS_ACTIONS.FETCH_DOCUMENTS_START:
      return { ...state, loading: true, error: null };

    case DMS_ACTIONS.FETCH_DOCUMENTS_SUCCESS:
      return { ...state, loading: false, documents: action.payload };

    case DMS_ACTIONS.FETCH_DOCUMENTS_FAILURE:
      return { ...state, loading: false, error: action.payload };

    case DMS_ACTIONS.UPLOAD_DOCUMENT_SUCCESS:
      return {
        ...state,
        documents: [...state.documents, action.payload]
      };

    case DMS_ACTIONS.DELETE_DOCUMENT_SUCCESS:
      return {
        ...state,
        documents: state.documents.filter((doc) => doc.id !== action.payload)
      };

    case DMS_ACTIONS.SET_SYNC_STATUS:
      return { ...state, syncStatus: action.payload };

    default:
      return state;
  }
}

// Action creators
export const dmsActions = {
  fetchDocuments: () => async (dispatch: any) => {
    dispatch({ type: DMS_ACTIONS.FETCH_DOCUMENTS_START });
    try {
      const client = DMSClient.getInstance();
      const documents = await client.listDocuments();
      dispatch({
        type: DMS_ACTIONS.FETCH_DOCUMENTS_SUCCESS,
        payload: documents
      });
    } catch (error) {
      dispatch({
        type: DMS_ACTIONS.FETCH_DOCUMENTS_FAILURE,
        payload: (error as Error).message
      });
    }
  },

  uploadDocument: (localPath: string, options: UploadOptions) => async (dispatch: any) => {
    const client = DMSClient.getInstance();
    const document = await client.uploadDocument(localPath, options);
    dispatch({
      type: DMS_ACTIONS.UPLOAD_DOCUMENT_SUCCESS,
      payload: document
    });
  },

  deleteDocument: (id: string) => async (dispatch: any) => {
    const client = DMSClient.getInstance();
    await client.deleteDocument(id);
    dispatch({
      type: DMS_ACTIONS.DELETE_DOCUMENT_SUCCESS,
      payload: id
    });
  }
};

// MARK: - Example Usage

/*
// Configure SDK
import { DMSClient } from '@dms/react-native-sdk';

DMSClient.configure({
  baseUrl: 'https://api.example.com',
  apiKey: 'your-api-key',
  offlineEnabled: true,
  biometricEnabled: true
});

// Using hooks
import { useDocuments, useDocumentUpload, useBiometric } from '@dms/react-native-sdk';

function DocumentList() {
  const { documents, loading, error, refresh } = useDocuments();
  const { upload, uploading, progress } = useDocumentUpload();
  const { available, authenticate } = useBiometric();

  const handleUpload = async () => {
    // Authenticate first
    if (available) {
      const authenticated = await authenticate();
      if (!authenticated) return;
    }

    // Pick file
    const file = await FilePicker.pickFile();

    // Upload
    const document = await upload(file.uri, {
      title: file.name,
      tags: ['important'],
      onProgress: (prog) => {
        console.log(`Upload progress: ${prog.progress * 100}%`);
      }
    });
  };

  if (loading) return <ActivityIndicator />;
  if (error) return <Text>Error: {error.message}</Text>;

  return (
    <FlatList
      data={documents}
      renderItem={({ item }) => <DocumentItem document={item} />}
      onRefresh={refresh}
      refreshing={loading}
    />
  );
}

// Redux usage
import { createStore, applyMiddleware } from 'redux';
import thunk from 'redux-thunk';
import { dmsReducer, dmsActions } from '@dms/react-native-sdk';

const store = createStore(dmsReducer, applyMiddleware(thunk));

// Dispatch actions
store.dispatch(dmsActions.fetchDocuments());
*/

export default DMSClient;
