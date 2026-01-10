///
/// DatenClient.swift
/// Daten iOS SDK
///
/// Native iOS SDK for Document Management System
/// Version: 3.3.0
///

import Foundation
import Combine
import LocalAuthentication

// MARK: - SDK Configuration

public struct DatenConfiguration {
    public let baseURL: URL
    public let apiKey: String?
    public let enableOfflineMode: Bool
    public let enableBiometrics: Bool
    public let syncInterval: TimeInterval

    public init(
        baseURL: URL,
        apiKey: String? = nil,
        enableOfflineMode: Bool = true,
        enableBiometrics: Bool = true,
        syncInterval: TimeInterval = 300
    ) {
        self.baseURL = baseURL
        self.apiKey = apiKey
        self.enableOfflineMode = enableOfflineMode
        self.enableBiometrics = enableBiometrics
        self.syncInterval = syncInterval
    }
}

// MARK: - Document Model

public struct Document: Codable, Identifiable {
    public let id: String
    public var title: String
    public var content: String
    public var createdAt: Date
    public var updatedAt: Date
    public var userId: String
    public var version: Int

    public init(
        id: String = UUID().uuidString,
        title: String,
        content: String,
        createdAt: Date = Date(),
        updatedAt: Date = Date(),
        userId: String,
        version: Int = 1
    ) {
        self.id = id
        self.title = title
        self.content = content
        self.createdAt = createdAt
        self.updatedAt = updatedAt
        self.userId = userId
        self.version = version
    }
}

// MARK: - Authentication

public struct AuthCredentials {
    public let username: String
    public let password: String

    public init(username: String, password: String) {
        self.username = username
        self.password = password
    }
}

public struct AuthToken: Codable {
    public let accessToken: String
    public let refreshToken: String
    public let expiresIn: Int
    public let tokenType: String
}

// MARK: - Sync Status

public enum SyncStatus {
    case idle
    case syncing
    case completed
    case failed(Error)
}

// MARK: - SDK Errors

public enum DatenError: LocalizedError {
    case notAuthenticated
    case networkError(Error)
    case invalidResponse
    case biometricAuthFailed
    case offlineModeDisabled
    case syncConflict

    public var errorDescription: String? {
        switch self {
        case .notAuthenticated:
            return "User is not authenticated"
        case .networkError(let error):
            return "Network error: \(error.localizedDescription)"
        case .invalidResponse:
            return "Invalid server response"
        case .biometricAuthFailed:
            return "Biometric authentication failed"
        case .offlineModeDisabled:
            return "Offline mode is disabled"
        case .syncConflict:
            return "Sync conflict detected"
        }
    }
}

// MARK: - Main SDK Client

@MainActor
public class DatenClient: ObservableObject {

    // MARK: - Published Properties

    @Published public private(set) var isAuthenticated = false
    @Published public private(set) var currentUser: String?
    @Published public private(set) var syncStatus: SyncStatus = .idle
    @Published public private(set) var documents: [Document] = []

    // MARK: - Private Properties

    private let configuration: DatenConfiguration
    private var authToken: AuthToken?
    private var cancellables = Set<AnyCancellable>()
    private let urlSession: URLSession
    private var syncTimer: Timer?

    // MARK: - Services

    private lazy var authService = AuthenticationService(client: self)
    private lazy var documentService = DocumentService(client: self)
    private lazy var syncManager = SyncManager(client: self)
    private lazy var biometricService = BiometricAuthService()

    // MARK: - Initialization

    public init(configuration: DatenConfiguration) {
        self.configuration = configuration

        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.timeoutIntervalForResource = 300
        self.urlSession = URLSession(configuration: config)

        loadAuthToken()

        if configuration.enableOfflineMode {
            setupAutoSync()
        }
    }

    // MARK: - Authentication

    public func signIn(credentials: AuthCredentials) async throws {
        let token = try await authService.signIn(credentials: credentials)
        self.authToken = token
        self.isAuthenticated = true
        self.currentUser = credentials.username
        saveAuthToken(token)

        // Start syncing
        if configuration.enableOfflineMode {
            try await syncManager.performSync()
        }
    }

    public func signOut() {
        authToken = nil
        isAuthenticated = false
        currentUser = nil
        documents = []
        clearAuthToken()
        stopAutoSync()
    }

    public func refreshToken() async throws {
        guard let currentToken = authToken else {
            throw DatenError.notAuthenticated
        }

        let newToken = try await authService.refreshToken(refreshToken: currentToken.refreshToken)
        self.authToken = newToken
        saveAuthToken(newToken)
    }

    // MARK: - Biometric Authentication

    public func authenticateWithBiometrics() async throws -> Bool {
        guard configuration.enableBiometrics else {
            return false
        }

        return try await biometricService.authenticate(reason: "Unlock Daten")
    }

    // MARK: - Document Operations

    public func fetchDocuments() async throws -> [Document] {
        guard isAuthenticated else {
            throw DatenError.notAuthenticated
        }

        let docs = try await documentService.fetchDocuments()
        self.documents = docs
        return docs
    }

    public func createDocument(_ document: Document) async throws -> Document {
        guard isAuthenticated else {
            throw DatenError.notAuthenticated
        }

        let created = try await documentService.createDocument(document)

        if configuration.enableOfflineMode {
            await syncManager.queueOperation(.create(created))
        }

        self.documents.append(created)
        return created
    }

    public func updateDocument(_ document: Document) async throws -> Document {
        guard isAuthenticated else {
            throw DatenError.notAuthenticated
        }

        let updated = try await documentService.updateDocument(document)

        if configuration.enableOfflineMode {
            await syncManager.queueOperation(.update(updated))
        }

        if let index = documents.firstIndex(where: { $0.id == document.id }) {
            documents[index] = updated
        }

        return updated
    }

    public func deleteDocument(id: String) async throws {
        guard isAuthenticated else {
            throw DatenError.notAuthenticated
        }

        try await documentService.deleteDocument(id: id)

        if configuration.enableOfflineMode {
            await syncManager.queueOperation(.delete(id))
        }

        documents.removeAll(where: { $0.id == id })
    }

    // MARK: - Sync Operations

    public func syncNow() async throws {
        guard configuration.enableOfflineMode else {
            throw DatenError.offlineModeDisabled
        }

        syncStatus = .syncing

        do {
            try await syncManager.performSync()
            syncStatus = .completed
        } catch {
            syncStatus = .failed(error)
            throw error
        }
    }

    // MARK: - Private Helpers

    private func setupAutoSync() {
        syncTimer = Timer.scheduledTimer(
            withTimeInterval: configuration.syncInterval,
            repeats: true
        ) { [weak self] _ in
            Task { @MainActor [weak self] in
                try? await self?.syncNow()
            }
        }
    }

    private func stopAutoSync() {
        syncTimer?.invalidate()
        syncTimer = nil
    }

    private func saveAuthToken(_ token: AuthToken) {
        // Save to Keychain in production
        if let data = try? JSONEncoder().encode(token) {
            UserDefaults.standard.set(data, forKey: "auth_token")
        }
    }

    private func loadAuthToken() {
        if let data = UserDefaults.standard.data(forKey: "auth_token"),
           let token = try? JSONDecoder().decode(AuthToken.self, from: data) {
            self.authToken = token
            self.isAuthenticated = true
        }
    }

    private func clearAuthToken() {
        UserDefaults.standard.removeObject(forKey: "auth_token")
    }

    // MARK: - Internal API

    func makeRequest<T: Decodable>(
        _ endpoint: String,
        method: String = "GET",
        body: Data? = nil
    ) async throws -> T {
        guard let url = URL(string: endpoint, relativeTo: configuration.baseURL) else {
            throw DatenError.invalidResponse
        }

        var request = URLRequest(url: url)
        request.httpMethod = method
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")

        if let token = authToken {
            request.addValue("Bearer \(token.accessToken)", forHTTPHeaderField: "Authorization")
        } else if let apiKey = configuration.apiKey {
            request.addValue(apiKey, forHTTPHeaderField: "X-API-Key")
        }

        if let body = body {
            request.httpBody = body
        }

        let (data, response) = try await urlSession.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw DatenError.invalidResponse
        }

        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return try decoder.decode(T.self, from: data)
    }
}

// MARK: - Authentication Service

class AuthenticationService {
    private weak var client: DatenClient?

    init(client: DatenClient) {
        self.client = client
    }

    func signIn(credentials: AuthCredentials) async throws -> AuthToken {
        let body = [
            "username": credentials.username,
            "password": credentials.password
        ]

        let data = try JSONEncoder().encode(body)
        return try await client!.makeRequest("/auth/login", method: "POST", body: data)
    }

    func refreshToken(refreshToken: String) async throws -> AuthToken {
        let body = ["refresh_token": refreshToken]
        let data = try JSONEncoder().encode(body)
        return try await client!.makeRequest("/auth/refresh", method: "POST", body: data)
    }
}

// MARK: - Document Service

class DocumentService {
    private weak var client: DatenClient?

    init(client: DatenClient) {
        self.client = client
    }

    func fetchDocuments() async throws -> [Document] {
        return try await client!.makeRequest("/documents")
    }

    func createDocument(_ document: Document) async throws -> Document {
        let data = try JSONEncoder().encode(document)
        return try await client!.makeRequest("/documents", method: "POST", body: data)
    }

    func updateDocument(_ document: Document) async throws -> Document {
        let data = try JSONEncoder().encode(document)
        return try await client!.makeRequest("/documents/\(document.id)", method: "PUT", body: data)
    }

    func deleteDocument(id: String) async throws {
        let _: [String: String] = try await client!.makeRequest("/documents/\(id)", method: "DELETE")
    }
}

// MARK: - Sync Manager

enum SyncOperation {
    case create(Document)
    case update(Document)
    case delete(String)
}

@MainActor
class SyncManager {
    private weak var client: DatenClient?
    private var pendingOperations: [SyncOperation] = []

    init(client: DatenClient) {
        self.client = client
    }

    func queueOperation(_ operation: SyncOperation) {
        pendingOperations.append(operation)
    }

    func performSync() async throws {
        guard let client = client else { return }

        for operation in pendingOperations {
            switch operation {
            case .create(let document):
                _ = try await client.documentService.createDocument(document)
            case .update(let document):
                _ = try await client.documentService.updateDocument(document)
            case .delete(let id):
                try await client.documentService.deleteDocument(id: id)
            }
        }

        pendingOperations.removeAll()
    }
}

// MARK: - Biometric Service

class BiometricAuthService {
    private let context = LAContext()

    func canAuthenticateWithBiometrics() -> Bool {
        var error: NSError?
        return context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error)
    }

    func authenticate(reason: String) async throws -> Bool {
        guard canAuthenticateWithBiometrics() else {
            throw DatenError.biometricAuthFailed
        }

        return try await context.evaluatePolicy(
            .deviceOwnerAuthenticationWithBiometrics,
            localizedReason: reason
        )
    }
}

// MARK: - SwiftUI Preview Support

#if DEBUG
extension DatenClient {
    static var preview: DatenClient {
        let config = DatenConfiguration(
            baseURL: URL(string: "https://api.example.com")!,
            enableOfflineMode: false
        )
        return DatenClient(configuration: config)
    }
}
#endif
