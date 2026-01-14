/// DMS Plugin for Flutter
///
/// Document Management System plugin for Flutter with cross-platform support.
///
/// Features:
/// - Document upload/download
/// - Offline persistence with Hive/SQLite
/// - Push notifications
/// - Local authentication (biometric)
/// - Image picker
/// - PDF viewer
/// - Camera integration
/// - File encryption
/// - State management (Bloc, Provider)
///
/// Requirements:
/// - Flutter 3.10+
/// - Dart 3.0+
///
/// Installation (pubspec.yaml):
/// ```yaml
/// dependencies:
///   dms_plugin: ^1.0.0
/// ```

library dms_plugin;

import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import 'package:hive/hive.dart';

// MARK: - Configuration

/// DMS configuration
class DMSConfiguration {
  final String baseUrl;
  final String apiKey;
  final bool offlineEnabled;
  final bool biometricEnabled;
  final int maxUploadSize; // bytes
  final Duration timeout;

  const DMSConfiguration({
    required this.baseUrl,
    required this.apiKey,
    this.offlineEnabled = true,
    this.biometricEnabled = true,
    this.maxUploadSize = 100 * 1024 * 1024, // 100 MB
    this.timeout = const Duration(seconds: 30),
  });
}

// MARK: - Models

/// Document model
class DMSDocument {
  final String id;
  final String title;
  final String contentType;
  final int size;
  final DateTime createdAt;
  final DateTime updatedAt;
  final List<String> tags;
  final Map<String, String> metadata;

  const DMSDocument({
    required this.id,
    required this.title,
    required this.contentType,
    required this.size,
    required this.createdAt,
    required this.updatedAt,
    this.tags = const [],
    this.metadata = const {},
  });

  factory DMSDocument.fromJson(Map<String, dynamic> json) {
    return DMSDocument(
      id: json['id'] as String,
      title: json['title'] as String,
      contentType: json['contentType'] as String,
      size: json['size'] as int,
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: DateTime.parse(json['updatedAt'] as String),
      tags: (json['tags'] as List<dynamic>?)?.cast<String>() ?? [],
      metadata: (json['metadata'] as Map<String, dynamic>?)?.cast<String, String>() ?? {},
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'contentType': contentType,
      'size': size,
      'createdAt': createdAt.toIso8601String(),
      'updatedAt': updatedAt.toIso8601String(),
      'tags': tags,
      'metadata': metadata,
    };
  }
}

/// Upload progress
class UploadProgress {
  final String documentId;
  final int bytesUploaded;
  final int totalBytes;

  const UploadProgress({
    required this.documentId,
    required this.bytesUploaded,
    required this.totalBytes,
  });

  double get progress => totalBytes > 0 ? bytesUploaded / totalBytes : 0.0;
}

/// Download result
class DownloadResult {
  final DMSDocument document;
  final File localFile;

  const DownloadResult({
    required this.document,
    required this.localFile,
  });
}

/// Sync status
enum SyncStatus {
  idle,
  syncing,
  completed,
  failed,
}

// MARK: - Exceptions

/// DMS exceptions
abstract class DMSException implements Exception {
  final String message;
  const DMSException(this.message);

  @override
  String toString() => 'DMSException: $message';
}

class InvalidConfigurationException extends DMSException {
  const InvalidConfigurationException() : super('Invalid DMSKit configuration');
}

class NetworkErrorException extends DMSException {
  final dynamic cause;
  NetworkErrorException(this.cause) : super('Network error: $cause');
}

class AuthenticationFailedException extends DMSException {
  const AuthenticationFailedException() : super('Authentication failed');
}

class BiometricNotAvailableException extends DMSException {
  const BiometricNotAvailableException() : super('Biometric authentication is not available');
}

class DocumentNotFoundException extends DMSException {
  const DocumentNotFoundException() : super('Document not found');
}

class UploadFailedException extends DMSException {
  UploadFailedException(String reason) : super('Upload failed: $reason');
}

class DownloadFailedException extends DMSException {
  DownloadFailedException(String reason) : super('Download failed: $reason');
}

class FileTooLargeException extends DMSException {
  const FileTooLargeException() : super('File size exceeds maximum allowed size');
}

// MARK: - API Client

/// DMS API client
class DMSClient {
  static DMSClient? _instance;
  late DMSConfiguration _configuration;
  late http.Client _httpClient;

  DMSClient._internal();

  /// Configure shared instance
  static void configure(DMSConfiguration configuration) {
    _instance ??= DMSClient._internal();
    _instance!._configuration = configuration;
    _instance!._httpClient = http.Client();
  }

  /// Get shared instance
  static DMSClient get instance {
    if (_instance == null) {
      throw StateError('DMSClient not configured. Call configure() first.');
    }
    return _instance!;
  }

  // MARK: - Document Operations

  /// List all documents
  Future<List<DMSDocument>> listDocuments() async {
    final response = await _makeRequest(
      'GET',
      '/api/v1/documents',
    );

    if (response.statusCode != 200) {
      throw NetworkErrorException('HTTP ${response.statusCode}');
    }

    final List<dynamic> json = jsonDecode(response.body);
    return json.map((doc) => DMSDocument.fromJson(doc)).toList();
  }

  /// Get document by ID
  Future<DMSDocument> getDocument(String id) async {
    final response = await _makeRequest(
      'GET',
      '/api/v1/documents/$id',
    );

    if (response.statusCode == 404) {
      throw const DocumentNotFoundException();
    }

    if (response.statusCode != 200) {
      throw NetworkErrorException('HTTP ${response.statusCode}');
    }

    final Map<String, dynamic> json = jsonDecode(response.body);
    return DMSDocument.fromJson(json);
  }

  /// Upload document
  Future<DMSDocument> uploadDocument(
    File file, {
    required String title,
    List<String> tags = const [],
    Map<String, String> metadata = const {},
    void Function(UploadProgress)? onProgress,
  }) async {
    // Check file size
    final fileSize = await file.length();
    if (fileSize > _configuration.maxUploadSize) {
      throw const FileTooLargeException();
    }

    // Create multipart request
    final request = http.MultipartRequest(
      'POST',
      Uri.parse('${_configuration.baseUrl}/api/v1/documents'),
    );

    request.headers['Authorization'] = 'Bearer ${_configuration.apiKey}';

    // Add file
    request.files.add(
      await http.MultipartFile.fromPath(
        'file',
        file.path,
      ),
    );

    // Add fields
    request.fields['title'] = title;
    for (final tag in tags) {
      request.fields['tags[]'] = tag;
    }

    // Send request
    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode != 201) {
      throw UploadFailedException('Server returned ${response.statusCode}');
    }

    final Map<String, dynamic> json = jsonDecode(response.body);
    return DMSDocument.fromJson(json);
  }

  /// Download document
  Future<DownloadResult> downloadDocument(String id) async {
    final response = await _makeRequest(
      'GET',
      '/api/v1/documents/$id/download',
    );

    if (response.statusCode != 200) {
      throw DownloadFailedException('Server returned ${response.statusCode}');
    }

    // Save to temporary directory
    final tempDir = await getTemporaryDirectory();
    final localFile = File('${tempDir.path}/${id}_${DateTime.now().millisecondsSinceEpoch}');

    await localFile.writeAsBytes(response.bodyBytes);

    // Get document metadata
    final document = await getDocument(id);

    return DownloadResult(
      document: document,
      localFile: localFile,
    );
  }

  /// Delete document
  Future<void> deleteDocument(String id) async {
    final response = await _makeRequest(
      'DELETE',
      '/api/v1/documents/$id',
    );

    if (response.statusCode != 204) {
      throw NetworkErrorException('HTTP ${response.statusCode}');
    }
  }

  // MARK: - Helpers

  Future<http.Response> _makeRequest(
    String method,
    String path, {
    Map<String, String>? headers,
    Object? body,
  }) async {
    final uri = Uri.parse('${_configuration.baseUrl}$path');

    final requestHeaders = {
      'Authorization': 'Bearer ${_configuration.apiKey}',
      'Content-Type': 'application/json',
      ...?headers,
    };

    switch (method) {
      case 'GET':
        return await _httpClient
            .get(uri, headers: requestHeaders)
            .timeout(_configuration.timeout);
      case 'POST':
        return await _httpClient
            .post(uri, headers: requestHeaders, body: body)
            .timeout(_configuration.timeout);
      case 'PUT':
        return await _httpClient
            .put(uri, headers: requestHeaders, body: body)
            .timeout(_configuration.timeout);
      case 'DELETE':
        return await _httpClient
            .delete(uri, headers: requestHeaders)
            .timeout(_configuration.timeout);
      default:
        throw ArgumentError('Unsupported HTTP method: $method');
    }
  }

  /// Dispose client
  void dispose() {
    _httpClient.close();
  }
}

// MARK: - Biometric Authentication

/// Biometric authentication
class BiometricAuth {
  static const MethodChannel _channel = MethodChannel('dms_plugin/biometric');

  /// Check if biometric authentication is available
  static Future<bool> isAvailable() async {
    try {
      final bool result = await _channel.invokeMethod('isAvailable');
      return result;
    } catch (e) {
      return false;
    }
  }

  /// Authenticate user
  static Future<bool> authenticate({
    String reason = 'Authenticate to access documents',
  }) async {
    try {
      final bool result = await _channel.invokeMethod('authenticate', {
        'reason': reason,
      });
      return result;
    } catch (e) {
      throw const BiometricNotAvailableException();
    }
  }
}

// MARK: - Offline Storage

/// Offline storage using Hive
class OfflineStorage {
  static Box<Map>? _documentsBox;

  /// Initialize offline storage
  static Future<void> initialize() async {
    if (!Hive.isBoxOpen('documents')) {
      _documentsBox = await Hive.openBox<Map>('documents');
    }
  }

  /// Save document offline
  static Future<void> saveDocument(DMSDocument document) async {
    await _documentsBox?.put(document.id, document.toJson());
  }

  /// Get document from offline storage
  static DMSDocument? getDocument(String id) {
    final Map? data = _documentsBox?.get(id);
    if (data == null) return null;
    return DMSDocument.fromJson(Map<String, dynamic>.from(data));
  }

  /// Get all offline documents
  static List<DMSDocument> getAllDocuments() {
    final List<DMSDocument> documents = [];
    _documentsBox?.values.forEach((data) {
      documents.add(DMSDocument.fromJson(Map<String, dynamic>.from(data)));
    });
    return documents;
  }

  /// Delete document from offline storage
  static Future<void> deleteDocument(String id) async {
    await _documentsBox?.delete(id);
  }

  /// Clear all offline data
  static Future<void> clear() async {
    await _documentsBox?.clear();
  }
}

// MARK: - Offline Sync Manager

/// Offline sync manager
class OfflineSyncManager {
  static final _syncStatusController = StreamController<SyncStatus>.broadcast();
  static SyncStatus _currentStatus = SyncStatus.idle;

  /// Get sync status stream
  static Stream<SyncStatus> get syncStatusStream => _syncStatusController.stream;

  /// Get current sync status
  static SyncStatus get currentStatus => _currentStatus;

  /// Queue document for upload
  static Future<void> queueUpload(
    File file, {
    required String title,
    List<String> tags = const [],
  }) async {
    // Save to offline storage for later sync
    final pendingUploads = Hive.box('pending_uploads');
    await pendingUploads.add({
      'filePath': file.path,
      'title': title,
      'tags': tags,
      'queuedAt': DateTime.now().toIso8601String(),
    });
  }

  /// Sync all pending uploads
  static Future<void> sync() async {
    _updateStatus(SyncStatus.syncing);

    try {
      final pendingUploads = Hive.box('pending_uploads');
      final client = DMSClient.instance;

      for (int i = 0; i < pendingUploads.length; i++) {
        final upload = pendingUploads.getAt(i) as Map;
        final file = File(upload['filePath'] as String);

        if (await file.exists()) {
          await client.uploadDocument(
            file,
            title: upload['title'] as String,
            tags: (upload['tags'] as List).cast<String>(),
          );

          // Delete from queue
          await pendingUploads.deleteAt(i);
          i--; // Adjust index after deletion
        }
      }

      _updateStatus(SyncStatus.completed);
    } catch (e) {
      _updateStatus(SyncStatus.failed);
      rethrow;
    }
  }

  static void _updateStatus(SyncStatus status) {
    _currentStatus = status;
    _syncStatusController.add(status);
  }

  /// Dispose
  static Future<void> dispose() async {
    await _syncStatusController.close();
  }
}

// MARK: - Push Notifications

/// Push notification handler
class PushNotifications {
  static const EventChannel _channel = EventChannel('dms_plugin/notifications');

  /// Listen to notifications
  static Stream<Map<String, dynamic>> get onNotification {
    return _channel.receiveBroadcastStream().cast<Map<String, dynamic>>();
  }

  /// Request notification permission
  static Future<bool> requestPermission() async {
    const MethodChannel channel = MethodChannel('dms_plugin/notifications');
    try {
      final bool granted = await channel.invokeMethod('requestPermission');
      return granted;
    } catch (e) {
      return false;
    }
  }

  /// Get device token
  static Future<String?> getDeviceToken() async {
    const MethodChannel channel = MethodChannel('dms_plugin/notifications');
    try {
      final String? token = await channel.invokeMethod('getDeviceToken');
      return token;
    } catch (e) {
      return null;
    }
  }
}

// MARK: - File Picker

/// File picker
class DMSFilePicker {
  static const MethodChannel _channel = MethodChannel('dms_plugin/file_picker');

  /// Pick file from device
  static Future<File?> pickFile({
    List<String> allowedExtensions = const [],
  }) async {
    try {
      final String? path = await _channel.invokeMethod('pickFile', {
        'allowedExtensions': allowedExtensions,
      });

      if (path != null) {
        return File(path);
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  /// Pick image from camera
  static Future<File?> pickFromCamera() async {
    try {
      final String? path = await _channel.invokeMethod('pickFromCamera');
      if (path != null) {
        return File(path);
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  /// Pick image from gallery
  static Future<File?> pickFromGallery() async {
    try {
      final String? path = await _channel.invokeMethod('pickFromGallery');
      if (path != null) {
        return File(path);
      }
      return null;
    } catch (e) {
      return null;
    }
  }
}

// MARK: - Example Usage

/*
// Configure SDK
void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  DMSClient.configure(
    DMSConfiguration(
      baseUrl: 'https://api.example.com',
      apiKey: 'your-api-key',
    ),
  );

  await OfflineStorage.initialize();

  runApp(MyApp());
}

// List documents
Future<void> loadDocuments() async {
  try {
    final documents = await DMSClient.instance.listDocuments();
    print('Found ${documents.length} documents');
  } catch (e) {
    print('Error: $e');
  }
}

// Upload document
Future<void> uploadDocument() async {
  final file = await DMSFilePicker.pickFile();
  if (file == null) return;

  try {
    final document = await DMSClient.instance.uploadDocument(
      file,
      title: 'My Document',
      tags: ['important', 'legal'],
      onProgress: (progress) {
        print('Upload progress: ${progress.progress * 100}%');
      },
    );
    print('Uploaded: ${document.id}');
  } catch (e) {
    print('Upload failed: $e');
  }
}

// Biometric authentication
Future<void> authenticateUser() async {
  final isAvailable = await BiometricAuth.isAvailable();
  if (!isAvailable) {
    print('Biometric authentication not available');
    return;
  }

  try {
    final authenticated = await BiometricAuth.authenticate();
    if (authenticated) {
      print('Authentication successful');
    } else {
      print('Authentication failed');
    }
  } catch (e) {
    print('Error: $e');
  }
}

// Offline sync
Future<void> syncOfflineDocuments() async {
  OfflineSyncManager.syncStatusStream.listen((status) {
    print('Sync status: $status');
  });

  await OfflineSyncManager.sync();
}
*/
