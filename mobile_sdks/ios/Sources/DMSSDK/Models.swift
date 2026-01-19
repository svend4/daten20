import Foundation

// MARK: - Authentication Models

public struct AuthResponse: Codable {
    public let accessToken: String
    public let refreshToken: String?
    public let tokenType: String
    public let expiresIn: Int
    public let user: User

    enum CodingKeys: String, CodingKey {
        case accessToken = "access_token"
        case refreshToken = "refresh_token"
        case tokenType = "token_type"
        case expiresIn = "expires_in"
        case user
    }
}

public struct User: Codable {
    public let id: String
    public let username: String
    public let email: String
    public let firstName: String?
    public let lastName: String?
    public let role: String
    public let createdAt: Date

    enum CodingKeys: String, CodingKey {
        case id, username, email, role
        case firstName = "first_name"
        case lastName = "last_name"
        case createdAt = "created_at"
    }
}

// MARK: - Document Models

public struct Document: Codable {
    public let id: String
    public let title: String
    public let description: String?
    public let fileUrl: String?
    public let mimeType: String?
    public let fileSize: Int?
    public let status: DocumentStatus
    public let tags: [String]?
    public let metadata: [String: String]?
    public let createdBy: String
    public let createdAt: Date
    public let updatedAt: Date

    enum CodingKeys: String, CodingKey {
        case id, title, description, status, tags, metadata
        case fileUrl = "file_url"
        case mimeType = "mime_type"
        case fileSize = "file_size"
        case createdBy = "created_by"
        case createdAt = "created_at"
        case updatedAt = "updated_at"
    }
}

public enum DocumentStatus: String, Codable {
    case draft
    case pending
    case approved
    case rejected
    case archived
}

public struct DocumentCreate: Codable {
    public let title: String
    public let description: String?
    public let tags: [String]?
    public let metadata: [String: String]?

    public init(
        title: String,
        description: String? = nil,
        tags: [String]? = nil,
        metadata: [String: String]? = nil
    ) {
        self.title = title
        self.description = description
        self.tags = tags
        self.metadata = metadata
    }

    func toDictionary() -> [String: Any] {
        var dict: [String: Any] = ["title": title]
        if let description = description { dict["description"] = description }
        if let tags = tags { dict["tags"] = tags }
        if let metadata = metadata { dict["metadata"] = metadata }
        return dict
    }
}

public struct DocumentUpdate: Codable {
    public let title: String?
    public let description: String?
    public let status: DocumentStatus?
    public let tags: [String]?
    public let metadata: [String: String]?

    public init(
        title: String? = nil,
        description: String? = nil,
        status: DocumentStatus? = nil,
        tags: [String]? = nil,
        metadata: [String: String]? = nil
    ) {
        self.title = title
        self.description = description
        self.status = status
        self.tags = tags
        self.metadata = metadata
    }

    func toDictionary() -> [String: Any] {
        var dict: [String: Any] = [:]
        if let title = title { dict["title"] = title }
        if let description = description { dict["description"] = description }
        if let status = status { dict["status"] = status.rawValue }
        if let tags = tags { dict["tags"] = tags }
        if let metadata = metadata { dict["metadata"] = metadata }
        return dict
    }
}

public struct DocumentListResponse: Codable {
    public let documents: [Document]
    public let total: Int
    public let page: Int
    public let pageSize: Int
    public let totalPages: Int

    enum CodingKeys: String, CodingKey {
        case documents, total, page
        case pageSize = "page_size"
        case totalPages = "total_pages"
    }
}

// MARK: - Analytics Models

public struct DashboardResponse: Codable {
    public let metrics: DashboardMetrics
    public let recentDocuments: [Document]
    public let activityChart: ChartData

    enum CodingKeys: String, CodingKey {
        case metrics
        case recentDocuments = "recent_documents"
        case activityChart = "activity_chart"
    }
}

public struct DashboardMetrics: Codable {
    public let totalDocuments: Int
    public let pendingApprovals: Int
    public let recentUploads: Int
    public let storageUsed: Int64

    enum CodingKeys: String, CodingKey {
        case totalDocuments = "total_documents"
        case pendingApprovals = "pending_approvals"
        case recentUploads = "recent_uploads"
        case storageUsed = "storage_used"
    }
}

public struct ChartData: Codable {
    public let labels: [String]
    public let datasets: [Dataset]

    public struct Dataset: Codable {
        public let label: String
        public let data: [Double]
        public let backgroundColor: String?

        enum CodingKeys: String, CodingKey {
            case label, data
            case backgroundColor = "background_color"
        }
    }
}

public struct StatisticsResponse: Codable {
    public let totalDocuments: Int
    public let documentsByStatus: [String: Int]
    public let documentsByType: [String: Int]
    public let uploadTrend: TrendData
    public let topUsers: [UserStatistics]

    enum CodingKeys: String, CodingKey {
        case totalDocuments = "total_documents"
        case documentsByStatus = "documents_by_status"
        case documentsByType = "documents_by_type"
        case uploadTrend = "upload_trend"
        case topUsers = "top_users"
    }
}

public struct TrendData: Codable {
    public let period: String
    public let data: [TrendPoint]

    public struct TrendPoint: Codable {
        public let date: String
        public let count: Int
    }
}

public struct UserStatistics: Codable {
    public let userId: String
    public let username: String
    public let documentCount: Int
    public let lastActivity: Date

    enum CodingKeys: String, CodingKey {
        case userId = "user_id"
        case username
        case documentCount = "document_count"
        case lastActivity = "last_activity"
    }
}

// MARK: - Notification Models

public struct Notification: Codable {
    public let id: String
    public let title: String
    public let message: String
    public let type: NotificationType
    public let isRead: Bool
    public let data: [String: String]?
    public let createdAt: Date

    enum CodingKeys: String, CodingKey {
        case id, title, message, type, data
        case isRead = "is_read"
        case createdAt = "created_at"
    }
}

public enum NotificationType: String, Codable {
    case info
    case success
    case warning
    case error
    case documentUpdate = "document_update"
    case approvalRequest = "approval_request"
}

public struct NotificationListResponse: Codable {
    public let notifications: [Notification]
    public let total: Int
    public let unreadCount: Int
    public let page: Int
    public let pageSize: Int

    enum CodingKeys: String, CodingKey {
        case notifications, total, page
        case unreadCount = "unread_count"
        case pageSize = "page_size"
    }
}

// MARK: - WebSocket Models

public struct WebSocketMessage: Codable {
    public let type: MessageType
    public let data: MessageData
    public let timestamp: Date

    public enum MessageType: String, Codable {
        case documentCreated = "document_created"
        case documentUpdated = "document_updated"
        case documentDeleted = "document_deleted"
        case notification
        case heartbeat
    }

    public struct MessageData: Codable {
        public let documentId: String?
        public let notificationId: String?
        public let message: String?

        enum CodingKeys: String, CodingKey {
            case documentId = "document_id"
            case notificationId = "notification_id"
            case message
        }
    }
}
