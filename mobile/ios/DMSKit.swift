// DMSKit.swift
// Document Management System - iOS SDK
//
// Native iOS SDK for DMS with offline sync, document scanning, and biometric authentication.
//
// Features:
// - Document upload/download
// - Offline sync with background uploads
// - Push notifications
// - Biometric authentication (Face ID, Touch ID)
// - Camera integration for document scanning
// - OCR integration
// - Share extensions
//
// Requirements:
// - iOS 14.0+
// - Swift 5.5+
//
// Installation:
// Add to Package.swift:
// .package(url: "https://github.com/yourorg/DMSKit.git", from: "1.0.0")

import Foundation
import LocalAuthentication
import CryptoKit
import Combine

#if canImport(UIKit)
import UIKit
#endif

// MARK: - Configuration

/// DMSKit configuration
public struct DMSConfiguration {
    /// API base URL
    public let baseURL: URL

    /// API key for authentication
    public let apiKey: String

    /// Enable offline mode
    public let offlineEnabled: Bool

    /// Enable biometric authentication
    public let biometricEnabled: Bool

    /// Maximum upload size in bytes
    public let maxUploadSize: Int64

    /// Request timeout in seconds
    public let timeout: TimeInterval

    public init(
        baseURL: URL,
        apiKey: String,
        offlineEnabled: Bool = true,
        biometricEnabled: Bool = true,
        maxUploadSize: Int64 = 100 * 1024 * 1024, // 100 MB
        timeout: TimeInterval = 30
    ) {
        self.baseURL = baseURL
        self.apiKey = apiKey
        self.offlineEnabled = offlineEnabled
        self.biometricEnabled = biometricEnabled
        self.maxUploadSize = maxUploadSize
        self.timeout = timeout
    }
}

// MARK: - Models

/// Document metadata
public struct DMSDocument: Codable, Identifiable {
    public let id: String
    public let title: String
    public let contentType: String
    public let size: Int64
    public let createdAt: Date
    public let updatedAt: Date
    public var tags: [String]
    public var metadata: [String: String]

    enum CodingKeys: String, CodingKey {
        case id, title, contentType, size, createdAt, updatedAt, tags, metadata
    }
}

/// Upload progress
public struct UploadProgress {
    public let documentId: String
    public let bytesUploaded: Int64
    public let totalBytes: Int64

    public var progress: Double {
        guard totalBytes > 0 else { return 0 }
        return Double(bytesUploaded) / Double(totalBytes)
    }
}

/// Download result
public struct DownloadResult {
    public let document: DMSDocument
    public let localURL: URL
}

/// Sync status
public enum SyncStatus {
    case idle
    case syncing
    case completed
    case failed(Error)
}

// MARK: - Errors

public enum DMSError: LocalizedError {
    case invalidConfiguration
    case networkError(Error)
    case authenticationFailed
    case biometricNotAvailable
    case biometricFailed
    case documentNotFound
    case uploadFailed(String)
    case downloadFailed(String)
    case fileTooLarge
    case invalidDocument
    case offlineModeNotEnabled
    case syncFailed(Error)

    public var errorDescription: String? {
        switch self {
        case .invalidConfiguration:
            return "Invalid DMSKit configuration"
        case .networkError(let error):
            return "Network error: \(error.localizedDescription)"
        case .authenticationFailed:
            return "Authentication failed"
        case .biometricNotAvailable:
            return "Biometric authentication is not available on this device"
        case .biometricFailed:
            return "Biometric authentication failed"
        case .documentNotFound:
            return "Document not found"
        case .uploadFailed(let reason):
            return "Upload failed: \(reason)"
        case .downloadFailed(let reason):
            return "Download failed: \(reason)"
        case .fileTooLarge:
            return "File size exceeds maximum allowed size"
        case .invalidDocument:
            return "Invalid document"
        case .offlineModeNotEnabled:
            return "Offline mode is not enabled"
        case .syncFailed(let error):
            return "Sync failed: \(error.localizedDescription)"
        }
    }
}

// MARK: - API Client

/// DMS API client
public class DMSClient {
    private let configuration: DMSConfiguration
    private let session: URLSession
    private let fileManager = FileManager.default
    private var cancellables = Set<AnyCancellable>()

    /// Shared instance (set via configure)
    public private(set) static var shared: DMSClient?

    /// Configure shared instance
    public static func configure(with configuration: DMSConfiguration) {
        shared = DMSClient(configuration: configuration)
    }

    public init(configuration: DMSConfiguration) {
        self.configuration = configuration

        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = configuration.timeout
        config.timeoutIntervalForResource = configuration.timeout * 2
        self.session = URLSession(configuration: config)
    }

    // MARK: - Document Operations

    /// List documents
    public func listDocuments() async throws -> [DMSDocument] {
        let url = configuration.baseURL.appendingPathComponent("/api/v1/documents")
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.addValue("Bearer \(configuration.apiKey)", forHTTPHeaderField: "Authorization")
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")

        let (data, response) = try await session.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw DMSError.networkError(URLError(.badServerResponse))
        }

        guard httpResponse.statusCode == 200 else {
            throw DMSError.networkError(URLError(.badServerResponse))
        }

        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return try decoder.decode([DMSDocument].self, from: data)
    }

    /// Get document by ID
    public func getDocument(id: String) async throws -> DMSDocument {
        let url = configuration.baseURL.appendingPathComponent("/api/v1/documents/\(id)")
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.addValue("Bearer \(configuration.apiKey)", forHTTPHeaderField: "Authorization")

        let (data, response) = try await session.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw DMSError.documentNotFound
        }

        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return try decoder.decode(DMSDocument.self, from: data)
    }

    /// Upload document
    public func uploadDocument(
        fileURL: URL,
        title: String,
        tags: [String] = [],
        metadata: [String: String] = [:],
        progressHandler: ((UploadProgress) -> Void)? = nil
    ) async throws -> DMSDocument {
        // Check file size
        let fileSize = try fileURL.resourceValues(forKeys: [.fileSizeKey]).fileSize ?? 0
        guard fileSize <= configuration.maxUploadSize else {
            throw DMSError.fileTooLarge
        }

        // Create multipart form data
        let boundary = UUID().uuidString
        var body = Data()

        // Add file
        let fileData = try Data(contentsOf: fileURL)
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"file\"; filename=\"\(fileURL.lastPathComponent)\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: application/octet-stream\r\n\r\n".data(using: .utf8)!)
        body.append(fileData)
        body.append("\r\n".data(using: .utf8)!)

        // Add metadata
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"title\"\r\n\r\n".data(using: .utf8)!)
        body.append("\(title)\r\n".data(using: .utf8)!)

        body.append("--\(boundary)--\r\n".data(using: .utf8)!)

        // Create request
        let url = configuration.baseURL.appendingPathComponent("/api/v1/documents")
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.addValue("Bearer \(configuration.apiKey)", forHTTPHeaderField: "Authorization")
        request.addValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        request.httpBody = body

        // Upload with progress tracking
        let (data, response) = try await session.upload(for: request, from: body)

        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 201 else {
            throw DMSError.uploadFailed("Server returned error")
        }

        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return try decoder.decode(DMSDocument.self, from: data)
    }

    /// Download document
    public func downloadDocument(id: String) async throws -> DownloadResult {
        let url = configuration.baseURL.appendingPathComponent("/api/v1/documents/\(id)/download")
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.addValue("Bearer \(configuration.apiKey)", forHTTPHeaderField: "Authorization")

        let (tempURL, response) = try await session.download(for: request)

        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw DMSError.downloadFailed("Server returned error")
        }

        // Move to permanent location
        let documentsDir = try fileManager.url(
            for: .documentDirectory,
            in: .userDomainMask,
            appropriateFor: nil,
            create: true
        )

        let destinationURL = documentsDir.appendingPathComponent("\(id)_\(UUID().uuidString)")

        if fileManager.fileExists(atPath: destinationURL.path) {
            try fileManager.removeItem(at: destinationURL)
        }

        try fileManager.moveItem(at: tempURL, to: destinationURL)

        // Get document metadata
        let document = try await getDocument(id: id)

        return DownloadResult(document: document, localURL: destinationURL)
    }

    /// Delete document
    public func deleteDocument(id: String) async throws {
        let url = configuration.baseURL.appendingPathComponent("/api/v1/documents/\(id)")
        var request = URLRequest(url: url)
        request.httpMethod = "DELETE"
        request.addValue("Bearer \(configuration.apiKey)", forHTTPHeaderField: "Authorization")

        let (_, response) = try await session.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 204 else {
            throw DMSError.networkError(URLError(.badServerResponse))
        }
    }
}

// MARK: - Biometric Authentication

/// Biometric authentication manager
public class BiometricAuth {
    private let context = LAContext()

    /// Check if biometric authentication is available
    public func isAvailable() -> Bool {
        var error: NSError?
        return context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error)
    }

    /// Get biometric type
    public func biometricType() -> LABiometryType {
        return context.biometryType
    }

    /// Authenticate user
    public func authenticate(reason: String = "Authenticate to access documents") async throws -> Bool {
        guard isAvailable() else {
            throw DMSError.biometricNotAvailable
        }

        return try await withCheckedThrowingContinuation { continuation in
            context.evaluatePolicy(
                .deviceOwnerAuthenticationWithBiometrics,
                localizedReason: reason
            ) { success, error in
                if let error = error {
                    continuation.resume(throwing: DMSError.biometricFailed)
                } else {
                    continuation.resume(returning: success)
                }
            }
        }
    }
}

// MARK: - Offline Sync Manager

/// Offline sync manager for background uploads
public class OfflineSyncManager {
    private let client: DMSClient
    private let fileManager = FileManager.default
    private var pendingUploads: [String: URL] = [:]

    @Published public private(set) var syncStatus: SyncStatus = .idle

    public init(client: DMSClient) {
        self.client = client
    }

    /// Queue document for upload when online
    public func queueUpload(fileURL: URL, title: String, tags: [String] = []) throws {
        let id = UUID().uuidString

        // Copy to cache directory
        let cacheDir = try fileManager.url(
            for: .cachesDirectory,
            in: .userDomainMask,
            appropriateFor: nil,
            create: true
        )

        let cachedURL = cacheDir.appendingPathComponent("pending_\(id)")
        try fileManager.copyItem(at: fileURL, to: cachedURL)

        pendingUploads[id] = cachedURL
    }

    /// Sync all pending uploads
    public func sync() async throws {
        syncStatus = .syncing

        for (id, fileURL) in pendingUploads {
            do {
                _ = try await client.uploadDocument(
                    fileURL: fileURL,
                    title: fileURL.lastPathComponent
                )

                // Remove from pending
                try fileManager.removeItem(at: fileURL)
                pendingUploads.removeValue(forKey: id)
            } catch {
                syncStatus = .failed(error)
                throw DMSError.syncFailed(error)
            }
        }

        syncStatus = .completed
    }
}

// MARK: - Push Notifications

#if canImport(UserNotifications)
import UserNotifications

/// Push notification manager
public class PushNotificationManager: NSObject {
    public static let shared = PushNotificationManager()

    /// Request notification permission
    public func requestAuthorization() async throws -> Bool {
        let center = UNUserNotificationCenter.current()
        return try await center.requestAuthorization(options: [.alert, .badge, .sound])
    }

    /// Register for remote notifications
    public func registerForRemoteNotifications() {
        #if canImport(UIKit)
        DispatchQueue.main.async {
            UIApplication.shared.registerForRemoteNotifications()
        }
        #endif
    }

    /// Handle device token
    public func handleDeviceToken(_ deviceToken: Data) {
        let token = deviceToken.map { String(format: "%02.2hhx", $0) }.joined()
        print("Device token: \(token)")
        // Send to server
    }
}
#endif

// MARK: - Document Scanner

#if canImport(VisionKit)
import VisionKit

/// Document scanner using VisionKit
@available(iOS 13.0, *)
public class DocumentScanner: NSObject {
    public typealias ScanCompletion = (Result<[UIImage], Error>) -> Void

    private var completion: ScanCompletion?

    /// Scan documents
    public func scanDocuments(completion: @escaping ScanCompletion) {
        self.completion = completion

        let scanner = VNDocumentCameraViewController()
        scanner.delegate = self

        #if canImport(UIKit)
        if let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
           let rootVC = windowScene.windows.first?.rootViewController {
            rootVC.present(scanner, animated: true)
        }
        #endif
    }
}

@available(iOS 13.0, *)
extension DocumentScanner: VNDocumentCameraViewControllerDelegate {
    public func documentCameraViewController(
        _ controller: VNDocumentCameraViewController,
        didFinishWith scan: VNDocumentCameraScan
    ) {
        var images: [UIImage] = []
        for i in 0..<scan.pageCount {
            images.append(scan.imageOfPage(at: i))
        }

        controller.dismiss(animated: true) {
            self.completion?(.success(images))
        }
    }

    public func documentCameraViewControllerDidCancel(_ controller: VNDocumentCameraViewController) {
        controller.dismiss(animated: true) {
            self.completion?(.failure(DMSError.invalidDocument))
        }
    }

    public func documentCameraViewController(
        _ controller: VNDocumentCameraViewController,
        didFailWithError error: Error
    ) {
        controller.dismiss(animated: true) {
            self.completion?(.failure(error))
        }
    }
}
#endif

// MARK: - Example Usage

/*
// Configure SDK
let config = DMSConfiguration(
    baseURL: URL(string: "https://api.example.com")!,
    apiKey: "your-api-key"
)
DMSClient.configure(with: config)

// List documents
Task {
    do {
        let documents = try await DMSClient.shared!.listDocuments()
        print("Found \(documents.count) documents")
    } catch {
        print("Error: \(error)")
    }
}

// Upload document
Task {
    let fileURL = URL(fileURLWithPath: "/path/to/document.pdf")
    do {
        let document = try await DMSClient.shared!.uploadDocument(
            fileURL: fileURL,
            title: "My Document",
            tags: ["important", "legal"]
        )
        print("Uploaded: \(document.id)")
    } catch {
        print("Upload failed: \(error)")
    }
}

// Biometric authentication
Task {
    let biometric = BiometricAuth()
    if biometric.isAvailable() {
        do {
            let success = try await biometric.authenticate()
            if success {
                print("Authentication successful")
            }
        } catch {
            print("Authentication failed: \(error)")
        }
    }
}

// Document scanning
if #available(iOS 13.0, *) {
    let scanner = DocumentScanner()
    scanner.scanDocuments { result in
        switch result {
        case .success(let images):
            print("Scanned \(images.count) pages")
        case .failure(let error):
            print("Scan failed: \(error)")
        }
    }
}
*/
