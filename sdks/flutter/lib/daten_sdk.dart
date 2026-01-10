///
/// daten_sdk.dart
/// Daten Flutter SDK
///
/// Cross-platform SDK for Flutter applications
/// Version: 3.3.0
///

library daten_sdk;

import 'dart:async';
import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

// MARK: - Configuration

class DatenConfiguration {
  final String baseUrl;
  final String? apiKey;
  final bool enableOfflineMode;
  final int syncIntervalSeconds;

  const DatenConfiguration({
    required this.baseUrl,
    this.apiKey,
    this.enableOfflineMode = true,
    this.syncIntervalSeconds = 300,
  });
}

// MARK: - Models

class Document {
  final String id;
  String title;
  String content;
  final DateTime createdAt;
  DateTime updatedAt;
  final String userId;
  int version;

  Document({
    required this.id,
    required this.title,
    required this.content,
    required this.createdAt,
    required this.updatedAt,
    required this.userId,
    this.version = 1,
  });

  factory Document.fromJson(Map<String, dynamic> json) {
    return Document(
      id: json['id'] as String,
      title: json['title'] as String,
      content: json['content'] as String,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
      userId: json['user_id'] as String,
      version: json['version'] as int? ?? 1,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'content': content,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'user_id': userId,
      'version': version,
    };
  }
}

class AuthCredentials {
  final String username;
  final String password;

  const AuthCredentials({
    required this.username,
    required this.password,
  });
}

class AuthToken {
  final String accessToken;
  final String refreshToken;
  final int expiresIn;
  final String tokenType;

  const AuthToken({
    required this.accessToken,
    required this.refreshToken,
    required this.expiresIn,
    required this.tokenType,
  });

  factory AuthToken.fromJson(Map<String, dynamic> json) {
    return AuthToken(
      accessToken: json['access_token'] as String,
      refreshToken: json['refresh_token'] as String,
      expiresIn: json['expires_in'] as int,
      tokenType: json['token_type'] as String,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'access_token': accessToken,
      'refresh_token': refreshToken,
      'expires_in': expiresIn,
      'token_type': tokenType,
    };
  }
}

// MARK: - Sync Status

abstract class SyncStatus {
  const SyncStatus();
}

class SyncStatusIdle extends SyncStatus {
  const SyncStatusIdle();
}

class SyncStatusSyncing extends SyncStatus {
  const SyncStatusSyncing();
}

class SyncStatusCompleted extends SyncStatus {
  const SyncStatusCompleted();
}

class SyncStatusFailed extends SyncStatus {
  final Object error;
  const SyncStatusFailed(this.error);
}

// MARK: - Errors

class DatenException implements Exception {
  final String message;
  const DatenException(this.message);

  @override
  String toString() => 'DatenException: $message';
}

class NotAuthenticatedException extends DatenException {
  const NotAuthenticatedException() : super('User is not authenticated');
}

class OfflineModeDisabledException extends DatenException {
  const OfflineModeDisabledException() : super('Offline mode is disabled');
}

// MARK: - Sync Operations

abstract class SyncOperation {}

class CreateOperation extends SyncOperation {
  final Document document;
  CreateOperation(this.document);
}

class UpdateOperation extends SyncOperation {
  final Document document;
  UpdateOperation(this.document);
}

class DeleteOperation extends SyncOperation {
  final String id;
  DeleteOperation(this.id);
}

// MARK: - Main SDK Client

class DatenClient with ChangeNotifier {
  final DatenConfiguration configuration;
  final Dio _dio;
  AuthToken? _authToken;
  Timer? _syncTimer;
  final List<SyncOperation> _pendingOperations = [];

  bool _isAuthenticated = false;
  String? _currentUser;
  SyncStatus _syncStatus = const SyncStatusIdle();
  List<Document> _documents = [];

  DatenClient(this.configuration) : _dio = Dio(
    BaseOptions(
      baseUrl: configuration.baseUrl,
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
      headers: {'Content-Type': 'application/json'},
    ),
  ) {
    _setupInterceptors();
    _loadAuthToken();
  }

  // MARK: - Getters

  bool get isAuthenticated => _isAuthenticated;
  String? get currentUser => _currentUser;
  SyncStatus get syncStatus => _syncStatus;
  List<Document> get documents => List.unmodifiable(_documents);

  // MARK: - Authentication

  Future<void> signIn(AuthCredentials credentials) async {
    try {
      final response = await _dio.post('/auth/login', data: {
        'username': credentials.username,
        'password': credentials.password,
      });

      _authToken = AuthToken.fromJson(response.data as Map<String, dynamic>);
      _isAuthenticated = true;
      _currentUser = credentials.username;

      await _saveAuthToken(_authToken!);

      if (configuration.enableOfflineMode) {
        _startAutoSync();
        await performSync();
      }

      notifyListeners();
    } catch (e) {
      rethrow;
    }
  }

  Future<void> signOut() async {
    _authToken = null;
    _isAuthenticated = false;
    _currentUser = null;
    _documents = [];
    _pendingOperations.clear();

    await _clearAuthToken();
    _stopAutoSync();

    notifyListeners();
  }

  Future<void> refreshToken() async {
    if (_authToken == null) {
      throw const NotAuthenticatedException();
    }

    final response = await _dio.post('/auth/refresh', data: {
      'refresh_token': _authToken!.refreshToken,
    });

    _authToken = AuthToken.fromJson(response.data as Map<String, dynamic>);
    await _saveAuthToken(_authToken!);

    notifyListeners();
  }

  // MARK: - Document Operations

  Future<List<Document>> fetchDocuments() async {
    if (!_isAuthenticated) {
      throw const NotAuthenticatedException();
    }

    final response = await _dio.get('/documents');
    final List<dynamic> data = response.data as List<dynamic>;

    _documents = data
        .map((json) => Document.fromJson(json as Map<String, dynamic>))
        .toList();

    notifyListeners();
    return _documents;
  }

  Future<Document> createDocument(Document document) async {
    if (!_isAuthenticated) {
      throw const NotAuthenticatedException();
    }

    final response = await _dio.post('/documents', data: document.toJson());
    final created = Document.fromJson(response.data as Map<String, dynamic>);

    if (configuration.enableOfflineMode) {
      _queueOperation(CreateOperation(created));
    }

    _documents.add(created);
    notifyListeners();

    return created;
  }

  Future<Document> updateDocument(Document document) async {
    if (!_isAuthenticated) {
      throw const NotAuthenticatedException();
    }

    final response = await _dio.put(
      '/documents/${document.id}',
      data: document.toJson(),
    );
    final updated = Document.fromJson(response.data as Map<String, dynamic>);

    if (configuration.enableOfflineMode) {
      _queueOperation(UpdateOperation(updated));
    }

    final index = _documents.indexWhere((doc) => doc.id == updated.id);
    if (index != -1) {
      _documents[index] = updated;
    }
    notifyListeners();

    return updated;
  }

  Future<void> deleteDocument(String id) async {
    if (!_isAuthenticated) {
      throw const NotAuthenticatedException();
    }

    await _dio.delete('/documents/$id');

    if (configuration.enableOfflineMode) {
      _queueOperation(DeleteOperation(id));
    }

    _documents.removeWhere((doc) => doc.id == id);
    notifyListeners();
  }

  // MARK: - Sync Operations

  Future<void> syncNow() async {
    if (!configuration.enableOfflineMode) {
      throw const OfflineModeDisabledException();
    }

    _syncStatus = const SyncStatusSyncing();
    notifyListeners();

    try {
      await performSync();
      _syncStatus = const SyncStatusCompleted();
    } catch (e) {
      _syncStatus = SyncStatusFailed(e);
      rethrow;
    } finally {
      notifyListeners();
    }
  }

  Future<void> performSync() async {
    final operations = List<SyncOperation>.from(_pendingOperations);
    _pendingOperations.clear();

    for (final operation in operations) {
      try {
        if (operation is CreateOperation) {
          await _dio.post('/documents', data: operation.document.toJson());
        } else if (operation is UpdateOperation) {
          await _dio.put(
            '/documents/${operation.document.id}',
            data: operation.document.toJson(),
          );
        } else if (operation is DeleteOperation) {
          await _dio.delete('/documents/${operation.id}');
        }
      } catch (e) {
        // Re-queue failed operations
        _pendingOperations.add(operation);
      }
    }
  }

  void _queueOperation(SyncOperation operation) {
    _pendingOperations.add(operation);
  }

  void _startAutoSync() {
    if (_syncTimer != null) return;

    _syncTimer = Timer.periodic(
      Duration(seconds: configuration.syncIntervalSeconds),
      (_) async {
        if (_isAuthenticated) {
          try {
            await performSync();
          } catch (e) {
            debugPrint('Auto-sync failed: $e');
          }
        }
      },
    );
  }

  void _stopAutoSync() {
    _syncTimer?.cancel();
    _syncTimer = null;
  }

  // MARK: - Interceptors

  void _setupInterceptors() {
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          if (_authToken != null) {
            options.headers['Authorization'] = 'Bearer ${_authToken!.accessToken}';
          } else if (configuration.apiKey != null) {
            options.headers['X-API-Key'] = configuration.apiKey;
          }
          handler.next(options);
        },
        onError: (error, handler) async {
          if (error.response?.statusCode == 401 && _authToken != null) {
            try {
              await refreshToken();
              // Retry request
              final response = await _dio.fetch(error.requestOptions);
              handler.resolve(response);
              return;
            } catch (e) {
              // Refresh failed, continue with error
            }
          }
          handler.next(error);
        },
      ),
    );
  }

  // MARK: - Storage

  Future<void> _saveAuthToken(AuthToken token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('daten_auth_token', jsonEncode(token.toJson()));
  }

  Future<void> _loadAuthToken() async {
    final prefs = await SharedPreferences.getInstance();
    final stored = prefs.getString('daten_auth_token');

    if (stored != null) {
      _authToken = AuthToken.fromJson(
        jsonDecode(stored) as Map<String, dynamic>,
      );
      _isAuthenticated = true;
      notifyListeners();
    }
  }

  Future<void> _clearAuthToken() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('daten_auth_token');
  }

  // MARK: - Cleanup

  @override
  void dispose() {
    _stopAutoSync();
    _dio.close();
    super.dispose();
  }
}

// MARK: - Providers

class DocumentProvider with ChangeNotifier {
  final DatenClient client;

  DocumentProvider(this.client) {
    client.addListener(_onClientChange);
  }

  List<Document> get documents => client.documents;
  bool get loading => _loading;
  Object? get error => _error;

  bool _loading = false;
  Object? _error;

  void _onClientChange() {
    notifyListeners();
  }

  Future<void> fetchDocuments() async {
    _setLoading(true);
    try {
      await client.fetchDocuments();
      _error = null;
    } catch (e) {
      _error = e;
      rethrow;
    } finally {
      _setLoading(false);
    }
  }

  Future<Document> createDocument(Document document) async {
    _setLoading(true);
    try {
      final created = await client.createDocument(document);
      _error = null;
      return created;
    } catch (e) {
      _error = e;
      rethrow;
    } finally {
      _setLoading(false);
    }
  }

  Future<Document> updateDocument(Document document) async {
    _setLoading(true);
    try {
      final updated = await client.updateDocument(document);
      _error = null;
      return updated;
    } catch (e) {
      _error = e;
      rethrow;
    } finally {
      _setLoading(false);
    }
  }

  Future<void> deleteDocument(String id) async {
    _setLoading(true);
    try {
      await client.deleteDocument(id);
      _error = null;
    } catch (e) {
      _error = e;
      rethrow;
    } finally {
      _setLoading(false);
    }
  }

  void _setLoading(bool value) {
    _loading = value;
    notifyListeners();
  }

  @override
  void dispose() {
    client.removeListener(_onClientChange);
    super.dispose();
  }
}

class AuthProvider with ChangeNotifier {
  final DatenClient client;

  AuthProvider(this.client) {
    client.addListener(_onClientChange);
  }

  bool get isAuthenticated => client.isAuthenticated;
  String? get currentUser => client.currentUser;
  bool get loading => _loading;
  Object? get error => _error;

  bool _loading = false;
  Object? _error;

  void _onClientChange() {
    notifyListeners();
  }

  Future<void> signIn(AuthCredentials credentials) async {
    _setLoading(true);
    try {
      await client.signIn(credentials);
      _error = null;
    } catch (e) {
      _error = e;
      rethrow;
    } finally {
      _setLoading(false);
    }
  }

  Future<void> signOut() async {
    _setLoading(true);
    try {
      await client.signOut();
      _error = null;
    } catch (e) {
      _error = e;
      rethrow;
    } finally {
      _setLoading(false);
    }
  }

  void _setLoading(bool value) {
    _loading = value;
    notifyListeners();
  }

  @override
  void dispose() {
    client.removeListener(_onClientChange);
    super.dispose();
  }
}

class SyncProvider with ChangeNotifier {
  final DatenClient client;

  SyncProvider(this.client) {
    client.addListener(_onClientChange);
  }

  SyncStatus get syncStatus => client.syncStatus;

  void _onClientChange() {
    notifyListeners();
  }

  Future<void> syncNow() async {
    await client.syncNow();
  }

  @override
  void dispose() {
    client.removeListener(_onClientChange);
    super.dispose();
  }
}
