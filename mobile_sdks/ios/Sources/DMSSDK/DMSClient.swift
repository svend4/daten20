import Foundation
#if canImport(FoundationNetworking)
import FoundationNetworking
#endif

/// DMS iOS SDK - Main client for Document Management System
/// Version: 3.3.0
@available(iOS 13.0, macOS 10.15, *)
public class DMSClient {

    // MARK: - Properties

    /// Singleton instance
    public static let shared = DMSClient()

    /// Base URL for API endpoints
    public var baseURL: URL

    /// API key for authentication
    private var apiKey: String?

    /// OAuth token for authentication
    private var accessToken: String?

    /// URLSession for network requests
    private let session: URLSession

    /// Configuration
    public struct Configuration {
        public let baseURL: String
        public let apiKey: String?
        public let timeout: TimeInterval
        public let enableLogging: Bool

        public init(
            baseURL: String,
            apiKey: String? = nil,
            timeout: TimeInterval = 30.0,
            enableLogging: Bool = false
        ) {
            self.baseURL = baseURL
            self.apiKey = apiKey
            self.timeout = timeout
            self.enableLogging = enableLogging
        }
    }

    private var configuration: Configuration

    // MARK: - Initialization

    private init() {
        self.baseURL = URL(string: "https://api.dms.example.com")!
        self.configuration = Configuration(baseURL: "https://api.dms.example.com")

        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30.0
        config.timeoutIntervalForResource = 60.0
        self.session = URLSession(configuration: config)
    }

    /// Configure the SDK
    public func configure(with configuration: Configuration) {
        self.configuration = configuration
        self.baseURL = URL(string: configuration.baseURL)!
        self.apiKey = configuration.apiKey

        if configuration.enableLogging {
            print("[DMS SDK] Configured with base URL: \(configuration.baseURL)")
        }
    }

    // MARK: - Authentication

    /// Set API key for authentication
    public func setAPIKey(_ key: String) {
        self.apiKey = key
    }

    /// Set OAuth access token
    public func setAccessToken(_ token: String) {
        self.accessToken = token
    }

    /// Login with username and password
    public func login(
        username: String,
        password: String,
        completion: @escaping (Result<AuthResponse, DMSError>) -> Void
    ) {
        let endpoint = "/api/v1/auth/login"
        let body: [String: Any] = [
            "username": username,
            "password": password
        ]

        request(
            method: "POST",
            endpoint: endpoint,
            body: body
        ) { (result: Result<AuthResponse, DMSError>) in
            if case .success(let response) = result {
                self.accessToken = response.accessToken
            }
            completion(result)
        }
    }

    /// Logout current user
    public func logout(completion: @escaping (Result<Void, DMSError>) -> Void) {
        let endpoint = "/api/v1/auth/logout"

        request(method: "POST", endpoint: endpoint) { (result: Result<EmptyResponse, DMSError>) in
            switch result {
            case .success:
                self.accessToken = nil
                completion(.success(()))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }

    // MARK: - Documents

    /// Get list of documents
    public func getDocuments(
        page: Int = 1,
        pageSize: Int = 20,
        completion: @escaping (Result<DocumentListResponse, DMSError>) -> Void
    ) {
        let endpoint = "/api/v1/documents"
        let queryItems = [
            URLQueryItem(name: "page", value: "\(page)"),
            URLQueryItem(name: "page_size", value: "\(pageSize)")
        ]

        request(method: "GET", endpoint: endpoint, queryItems: queryItems, completion: completion)
    }

    /// Get document by ID
    public func getDocument(
        id: String,
        completion: @escaping (Result<Document, DMSError>) -> Void
    ) {
        let endpoint = "/api/v1/documents/\(id)"
        request(method: "GET", endpoint: endpoint, completion: completion)
    }

    /// Create new document
    public func createDocument(
        _ document: DocumentCreate,
        completion: @escaping (Result<Document, DMSError>) -> Void
    ) {
        let endpoint = "/api/v1/documents"
        request(method: "POST", endpoint: endpoint, body: document.toDictionary(), completion: completion)
    }

    /// Update existing document
    public func updateDocument(
        id: String,
        _ document: DocumentUpdate,
        completion: @escaping (Result<Document, DMSError>) -> Void
    ) {
        let endpoint = "/api/v1/documents/\(id)"
        request(method: "PUT", endpoint: endpoint, body: document.toDictionary(), completion: completion)
    }

    /// Delete document
    public func deleteDocument(
        id: String,
        completion: @escaping (Result<Void, DMSError>) -> Void
    ) {
        let endpoint = "/api/v1/documents/\(id)"

        request(method: "DELETE", endpoint: endpoint) { (result: Result<EmptyResponse, DMSError>) in
            switch result {
            case .success:
                completion(.success(()))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }

    /// Upload document file
    public func uploadDocument(
        file: Data,
        filename: String,
        mimeType: String,
        metadata: [String: String]? = nil,
        completion: @escaping (Result<Document, DMSError>) -> Void
    ) {
        let endpoint = "/api/v1/documents/upload"

        var url = baseURL.appendingPathComponent(endpoint)
        let boundary = UUID().uuidString

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")

        addAuthHeaders(to: &request)

        var body = Data()

        // Add file
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"file\"; filename=\"\(filename)\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: \(mimeType)\r\n\r\n".data(using: .utf8)!)
        body.append(file)
        body.append("\r\n".data(using: .utf8)!)

        // Add metadata
        if let metadata = metadata {
            for (key, value) in metadata {
                body.append("--\(boundary)\r\n".data(using: .utf8)!)
                body.append("Content-Disposition: form-data; name=\"\(key)\"\r\n\r\n".data(using: .utf8)!)
                body.append("\(value)\r\n".data(using: .utf8)!)
            }
        }

        body.append("--\(boundary)--\r\n".data(using: .utf8)!)
        request.httpBody = body

        session.dataTask(with: request) { data, response, error in
            self.handleResponse(data: data, response: response, error: error, completion: completion)
        }.resume()
    }

    /// Download document file
    public func downloadDocument(
        id: String,
        completion: @escaping (Result<Data, DMSError>) -> Void
    ) {
        let endpoint = "/api/v1/documents/\(id)/download"
        var url = baseURL.appendingPathComponent(endpoint)

        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        addAuthHeaders(to: &request)

        session.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(.networkError(error.localizedDescription)))
                return
            }

            guard let httpResponse = response as? HTTPURLResponse else {
                completion(.failure(.invalidResponse))
                return
            }

            guard (200...299).contains(httpResponse.statusCode) else {
                completion(.failure(.httpError(statusCode: httpResponse.statusCode)))
                return
            }

            guard let data = data else {
                completion(.failure(.noData))
                return
            }

            completion(.success(data))
        }.resume()
    }

    // MARK: - Search

    /// Search documents
    public func searchDocuments(
        query: String,
        filters: [String: Any]? = nil,
        completion: @escaping (Result<DocumentListResponse, DMSError>) -> Void
    ) {
        let endpoint = "/api/v1/search"
        var body: [String: Any] = ["query": query]

        if let filters = filters {
            body["filters"] = filters
        }

        request(method: "POST", endpoint: endpoint, body: body, completion: completion)
    }

    // MARK: - Analytics

    /// Get dashboard analytics
    public func getDashboard(
        completion: @escaping (Result<DashboardResponse, DMSError>) -> Void
    ) {
        let endpoint = "/api/v1/analytics/dashboard"
        request(method: "GET", endpoint: endpoint, completion: completion)
    }

    /// Get document statistics
    public func getStatistics(
        startDate: Date? = nil,
        endDate: Date? = nil,
        completion: @escaping (Result<StatisticsResponse, DMSError>) -> Void
    ) {
        let endpoint = "/api/v1/analytics/statistics"
        var queryItems: [URLQueryItem] = []

        let formatter = ISO8601DateFormatter()
        if let startDate = startDate {
            queryItems.append(URLQueryItem(name: "start_date", value: formatter.string(from: startDate)))
        }
        if let endDate = endDate {
            queryItems.append(URLQueryItem(name: "end_date", value: formatter.string(from: endDate)))
        }

        request(method: "GET", endpoint: endpoint, queryItems: queryItems, completion: completion)
    }

    // MARK: - Notifications

    /// Get notifications
    public func getNotifications(
        page: Int = 1,
        pageSize: Int = 20,
        completion: @escaping (Result<NotificationListResponse, DMSError>) -> Void
    ) {
        let endpoint = "/api/v1/notifications"
        let queryItems = [
            URLQueryItem(name: "page", value: "\(page)"),
            URLQueryItem(name: "page_size", value: "\(pageSize)")
        ]

        request(method: "GET", endpoint: endpoint, queryItems: queryItems, completion: completion)
    }

    /// Mark notification as read
    public func markNotificationAsRead(
        id: String,
        completion: @escaping (Result<Void, DMSError>) -> Void
    ) {
        let endpoint = "/api/v1/notifications/\(id)/read"

        request(method: "POST", endpoint: endpoint) { (result: Result<EmptyResponse, DMSError>) in
            switch result {
            case .success:
                completion(.success(()))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }

    // MARK: - WebSocket (Real-time)

    /// Connect to WebSocket for real-time updates
    public func connectWebSocket(
        onMessage: @escaping (WebSocketMessage) -> Void,
        onError: @escaping (Error) -> Void
    ) -> URLSessionWebSocketTask {
        let wsURL = baseURL
            .absoluteString
            .replacingOccurrences(of: "https://", with: "wss://")
            .replacingOccurrences(of: "http://", with: "ws://")

        guard let url = URL(string: wsURL + "/ws") else {
            fatalError("Invalid WebSocket URL")
        }

        var request = URLRequest(url: url)
        addAuthHeaders(to: &request)

        let task = session.webSocketTask(with: request)
        task.resume()

        func receiveMessage() {
            task.receive { result in
                switch result {
                case .success(let message):
                    switch message {
                    case .string(let text):
                        if let data = text.data(using: .utf8),
                           let wsMessage = try? JSONDecoder().decode(WebSocketMessage.self, from: data) {
                            onMessage(wsMessage)
                        }
                    case .data(let data):
                        if let wsMessage = try? JSONDecoder().decode(WebSocketMessage.self, from: data) {
                            onMessage(wsMessage)
                        }
                    @unknown default:
                        break
                    }
                    receiveMessage()
                case .failure(let error):
                    onError(error)
                }
            }
        }

        receiveMessage()
        return task
    }

    // MARK: - Private Helpers

    private func request<T: Decodable>(
        method: String,
        endpoint: String,
        queryItems: [URLQueryItem]? = nil,
        body: [String: Any]? = nil,
        completion: @escaping (Result<T, DMSError>) -> Void
    ) {
        var urlComponents = URLComponents(url: baseURL.appendingPathComponent(endpoint), resolvingAgainstBaseURL: false)!

        if let queryItems = queryItems {
            urlComponents.queryItems = queryItems
        }

        guard let url = urlComponents.url else {
            completion(.failure(.invalidURL))
            return
        }

        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("application/json", forHTTPHeaderField: "Accept")

        addAuthHeaders(to: &request)

        if let body = body {
            request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        }

        if configuration.enableLogging {
            print("[DMS SDK] \(method) \(url.absoluteString)")
        }

        session.dataTask(with: request) { data, response, error in
            self.handleResponse(data: data, response: response, error: error, completion: completion)
        }.resume()
    }

    private func addAuthHeaders(to request: inout URLRequest) {
        if let apiKey = apiKey {
            request.setValue(apiKey, forHTTPHeaderField: "X-API-Key")
        }

        if let accessToken = accessToken {
            request.setValue("Bearer \(accessToken)", forHTTPHeaderField: "Authorization")
        }
    }

    private func handleResponse<T: Decodable>(
        data: Data?,
        response: URLResponse?,
        error: Error?,
        completion: @escaping (Result<T, DMSError>) -> Void
    ) {
        if let error = error {
            completion(.failure(.networkError(error.localizedDescription)))
            return
        }

        guard let httpResponse = response as? HTTPURLResponse else {
            completion(.failure(.invalidResponse))
            return
        }

        guard (200...299).contains(httpResponse.statusCode) else {
            if let data = data,
               let errorResponse = try? JSONDecoder().decode(ErrorResponse.self, from: data) {
                completion(.failure(.apiError(message: errorResponse.message)))
            } else {
                completion(.failure(.httpError(statusCode: httpResponse.statusCode)))
            }
            return
        }

        guard let data = data else {
            completion(.failure(.noData))
            return
        }

        do {
            let decoder = JSONDecoder()
            decoder.dateDecodingStrategy = .iso8601
            let result = try decoder.decode(T.self, from: data)
            completion(.success(result))
        } catch {
            if configuration.enableLogging {
                print("[DMS SDK] Decoding error: \(error)")
            }
            completion(.failure(.decodingError(error.localizedDescription)))
        }
    }
}

// MARK: - Error Types

public enum DMSError: Error, LocalizedError {
    case invalidURL
    case invalidResponse
    case networkError(String)
    case httpError(statusCode: Int)
    case apiError(message: String)
    case noData
    case decodingError(String)
    case unauthorized
    case notFound
    case serverError

    public var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid URL"
        case .invalidResponse:
            return "Invalid response from server"
        case .networkError(let message):
            return "Network error: \(message)"
        case .httpError(let statusCode):
            return "HTTP error: \(statusCode)"
        case .apiError(let message):
            return "API error: \(message)"
        case .noData:
            return "No data received"
        case .decodingError(let message):
            return "Decoding error: \(message)"
        case .unauthorized:
            return "Unauthorized access"
        case .notFound:
            return "Resource not found"
        case .serverError:
            return "Server error"
        }
    }
}

// MARK: - Empty Response

private struct EmptyResponse: Decodable {}

// MARK: - Error Response

private struct ErrorResponse: Decodable {
    let message: String
    let code: String?
}
