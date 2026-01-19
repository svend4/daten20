package com.example.dms_sdk

import kotlinx.serialization.*

// MARK: - Authentication Models

@Serializable
data class AuthResponse(
    @SerialName("access_token") val accessToken: String,
    @SerialName("refresh_token") val refreshToken: String? = null,
    @SerialName("token_type") val tokenType: String,
    @SerialName("expires_in") val expiresIn: Int,
    val user: User
)

@Serializable
data class User(
    val id: String,
    val username: String,
    val email: String,
    @SerialName("first_name") val firstName: String? = null,
    @SerialName("last_name") val lastName: String? = null,
    val role: String,
    @SerialName("created_at") val createdAt: String
)

// MARK: - Document Models

@Serializable
data class Document(
    val id: String,
    val title: String,
    val description: String? = null,
    @SerialName("file_url") val fileUrl: String? = null,
    @SerialName("mime_type") val mimeType: String? = null,
    @SerialName("file_size") val fileSize: Long? = null,
    val status: DocumentStatus,
    val tags: List<String>? = null,
    val metadata: Map<String, String>? = null,
    @SerialName("created_by") val createdBy: String,
    @SerialName("created_at") val createdAt: String,
    @SerialName("updated_at") val updatedAt: String
)

@Serializable
enum class DocumentStatus {
    @SerialName("draft") DRAFT,
    @SerialName("pending") PENDING,
    @SerialName("approved") APPROVED,
    @SerialName("rejected") REJECTED,
    @SerialName("archived") ARCHIVED
}

@Serializable
data class DocumentCreate(
    val title: String,
    val description: String? = null,
    val tags: List<String>? = null,
    val metadata: Map<String, String>? = null
)

@Serializable
data class DocumentUpdate(
    val title: String? = null,
    val description: String? = null,
    val status: DocumentStatus? = null,
    val tags: List<String>? = null,
    val metadata: Map<String, String>? = null
)

@Serializable
data class DocumentListResponse(
    val documents: List<Document>,
    val total: Int,
    val page: Int,
    @SerialName("page_size") val pageSize: Int,
    @SerialName("total_pages") val totalPages: Int
)

// MARK: - Analytics Models

@Serializable
data class DashboardResponse(
    val metrics: DashboardMetrics,
    @SerialName("recent_documents") val recentDocuments: List<Document>,
    @SerialName("activity_chart") val activityChart: ChartData
)

@Serializable
data class DashboardMetrics(
    @SerialName("total_documents") val totalDocuments: Int,
    @SerialName("pending_approvals") val pendingApprovals: Int,
    @SerialName("recent_uploads") val recentUploads: Int,
    @SerialName("storage_used") val storageUsed: Long
)

@Serializable
data class ChartData(
    val labels: List<String>,
    val datasets: List<Dataset>
) {
    @Serializable
    data class Dataset(
        val label: String,
        val data: List<Double>,
        @SerialName("background_color") val backgroundColor: String? = null
    )
}

@Serializable
data class StatisticsResponse(
    @SerialName("total_documents") val totalDocuments: Int,
    @SerialName("documents_by_status") val documentsByStatus: Map<String, Int>,
    @SerialName("documents_by_type") val documentsByType: Map<String, Int>,
    @SerialName("upload_trend") val uploadTrend: TrendData,
    @SerialName("top_users") val topUsers: List<UserStatistics>
)

@Serializable
data class TrendData(
    val period: String,
    val data: List<TrendPoint>
) {
    @Serializable
    data class TrendPoint(
        val date: String,
        val count: Int
    )
}

@Serializable
data class UserStatistics(
    @SerialName("user_id") val userId: String,
    val username: String,
    @SerialName("document_count") val documentCount: Int,
    @SerialName("last_activity") val lastActivity: String
)

// MARK: - Notification Models

@Serializable
data class Notification(
    val id: String,
    val title: String,
    val message: String,
    val type: NotificationType,
    @SerialName("is_read") val isRead: Boolean,
    val data: Map<String, String>? = null,
    @SerialName("created_at") val createdAt: String
)

@Serializable
enum class NotificationType {
    @SerialName("info") INFO,
    @SerialName("success") SUCCESS,
    @SerialName("warning") WARNING,
    @SerialName("error") ERROR,
    @SerialName("document_update") DOCUMENT_UPDATE,
    @SerialName("approval_request") APPROVAL_REQUEST
}

@Serializable
data class NotificationListResponse(
    val notifications: List<Notification>,
    val total: Int,
    @SerialName("unread_count") val unreadCount: Int,
    val page: Int,
    @SerialName("page_size") val pageSize: Int
)

// MARK: - WebSocket Models

@Serializable
data class WebSocketMessage(
    val type: MessageType,
    val data: MessageData,
    val timestamp: String
) {
    @Serializable
    enum class MessageType {
        @SerialName("document_created") DOCUMENT_CREATED,
        @SerialName("document_updated") DOCUMENT_UPDATED,
        @SerialName("document_deleted") DOCUMENT_DELETED,
        @SerialName("notification") NOTIFICATION,
        @SerialName("heartbeat") HEARTBEAT
    }

    @Serializable
    data class MessageData(
        @SerialName("document_id") val documentId: String? = null,
        @SerialName("notification_id") val notificationId: String? = null,
        val message: String? = null
    )
}
