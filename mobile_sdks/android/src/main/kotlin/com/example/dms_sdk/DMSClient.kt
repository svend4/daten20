package com.example.dms_sdk

import kotlinx.coroutines.*
import kotlinx.serialization.*
import kotlinx.serialization.json.*
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.File
import java.io.IOException
import java.util.concurrent.TimeUnit

/**
 * DMS Android SDK - Main client for Document Management System
 * Version: 3.3.0
 */
class DMSClient private constructor() {

    companion object {
        @Volatile
        private var instance: DMSClient? = null

        fun getInstance(): DMSClient {
            return instance ?: synchronized(this) {
                instance ?: DMSClient().also { instance = it }
            }
        }
    }

    // Configuration
    data class Configuration(
        val baseURL: String,
        val apiKey: String? = null,
        val timeout: Long = 30L,
        val enableLogging: Boolean = false
    )

    private lateinit var configuration: Configuration
    private var apiKey: String? = null
    private var accessToken: String? = null

    private val json = Json {
        ignoreUnknownKeys = true
        isLenient = true
        encodeDefaults = true
    }

    private lateinit var client: OkHttpClient

    private fun initializeClient() {
        client = OkHttpClient.Builder()
            .connectTimeout(configuration.timeout, TimeUnit.SECONDS)
            .readTimeout(configuration.timeout, TimeUnit.SECONDS)
            .writeTimeout(configuration.timeout, TimeUnit.SECONDS)
            .apply {
                if (configuration.enableLogging) {
                    addInterceptor(HttpLoggingInterceptor().apply {
                        level = HttpLoggingInterceptor.Level.BODY
                    })
                }
            }
            .build()
    }

    /**
     * Configure the SDK
     */
    fun configure(config: Configuration) {
        this.configuration = config
        this.apiKey = config.apiKey
        initializeClient()

        if (config.enableLogging) {
            println("[DMS SDK] Configured with base URL: ${config.baseURL}")
        }
    }

    /**
     * Set API key for authentication
     */
    fun setAPIKey(key: String) {
        this.apiKey = key
    }

    /**
     * Set OAuth access token
     */
    fun setAccessToken(token: String) {
        this.accessToken = token
    }

    // MARK: - Authentication

    /**
     * Login with username and password
     */
    suspend fun login(username: String, password: String): Result<AuthResponse> {
        val body = mapOf(
            "username" to username,
            "password" to password
        )

        return try {
            val response = post<AuthResponse>("/api/v1/auth/login", body)
            response.onSuccess {
                accessToken = it.accessToken
            }
            response
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Logout current user
     */
    suspend fun logout(): Result<Unit> {
        return try {
            post<EmptyResponse>("/api/v1/auth/logout", null)
            accessToken = null
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // MARK: - Documents

    /**
     * Get list of documents
     */
    suspend fun getDocuments(
        page: Int = 1,
        pageSize: Int = 20
    ): Result<DocumentListResponse> {
        val queryParams = mapOf(
            "page" to page.toString(),
            "page_size" to pageSize.toString()
        )
        return get("/api/v1/documents", queryParams)
    }

    /**
     * Get document by ID
     */
    suspend fun getDocument(id: String): Result<Document> {
        return get("/api/v1/documents/$id")
    }

    /**
     * Create new document
     */
    suspend fun createDocument(document: DocumentCreate): Result<Document> {
        return post("/api/v1/documents", document)
    }

    /**
     * Update existing document
     */
    suspend fun updateDocument(id: String, document: DocumentUpdate): Result<Document> {
        return put("/api/v1/documents/$id", document)
    }

    /**
     * Delete document
     */
    suspend fun deleteDocument(id: String): Result<Unit> {
        return try {
            delete<EmptyResponse>("/api/v1/documents/$id")
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Upload document file
     */
    suspend fun uploadDocument(
        file: File,
        metadata: Map<String, String>? = null
    ): Result<Document> {
        return withContext(Dispatchers.IO) {
            try {
                val requestBody = MultipartBody.Builder()
                    .setType(MultipartBody.FORM)
                    .addFormDataPart(
                        "file",
                        file.name,
                        file.asRequestBody("application/octet-stream".toMediaType())
                    )

                metadata?.forEach { (key, value) ->
                    requestBody.addFormDataPart(key, value)
                }

                val request = Request.Builder()
                    .url("${configuration.baseURL}/api/v1/documents/upload")
                    .post(requestBody.build())
                    .apply { addAuthHeaders() }
                    .build()

                val response = client.newCall(request).execute()
                handleResponse<Document>(response)
            } catch (e: Exception) {
                Result.failure(DMSException.NetworkError(e.message ?: "Upload failed"))
            }
        }
    }

    /**
     * Download document file
     */
    suspend fun downloadDocument(id: String): Result<ByteArray> {
        return withContext(Dispatchers.IO) {
            try {
                val request = Request.Builder()
                    .url("${configuration.baseURL}/api/v1/documents/$id/download")
                    .get()
                    .apply { addAuthHeaders() }
                    .build()

                val response = client.newCall(request).execute()

                if (!response.isSuccessful) {
                    Result.failure(DMSException.HttpError(response.code))
                } else {
                    Result.success(response.body?.bytes() ?: ByteArray(0))
                }
            } catch (e: Exception) {
                Result.failure(DMSException.NetworkError(e.message ?: "Download failed"))
            }
        }
    }

    // MARK: - Search

    /**
     * Search documents
     */
    suspend fun searchDocuments(
        query: String,
        filters: Map<String, Any>? = null
    ): Result<DocumentListResponse> {
        val body = mutableMapOf<String, Any>("query" to query)
        filters?.let { body["filters"] = it }

        return post("/api/v1/search", body)
    }

    // MARK: - Analytics

    /**
     * Get dashboard analytics
     */
    suspend fun getDashboard(): Result<DashboardResponse> {
        return get("/api/v1/analytics/dashboard")
    }

    /**
     * Get document statistics
     */
    suspend fun getStatistics(
        startDate: String? = null,
        endDate: String? = null
    ): Result<StatisticsResponse> {
        val queryParams = mutableMapOf<String, String>()
        startDate?.let { queryParams["start_date"] = it }
        endDate?.let { queryParams["end_date"] = it }

        return get("/api/v1/analytics/statistics", queryParams)
    }

    // MARK: - Notifications

    /**
     * Get notifications
     */
    suspend fun getNotifications(
        page: Int = 1,
        pageSize: Int = 20
    ): Result<NotificationListResponse> {
        val queryParams = mapOf(
            "page" to page.toString(),
            "page_size" to pageSize.toString()
        )
        return get("/api/v1/notifications", queryParams)
    }

    /**
     * Mark notification as read
     */
    suspend fun markNotificationAsRead(id: String): Result<Unit> {
        return try {
            post<EmptyResponse>("/api/v1/notifications/$id/read", null)
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // MARK: - WebSocket (Real-time)

    /**
     * Connect to WebSocket for real-time updates
     */
    fun connectWebSocket(
        onMessage: (WebSocketMessage) -> Unit,
        onError: (Throwable) -> Unit,
        onClosed: (Int, String) -> Unit
    ): WebSocket {
        val wsUrl = configuration.baseURL
            .replace("https://", "wss://")
            .replace("http://", "ws://") + "/ws"

        val request = Request.Builder()
            .url(wsUrl)
            .apply { addAuthHeaders() }
            .build()

        return client.newWebSocket(request, object : WebSocketListener() {
            override fun onMessage(webSocket: WebSocket, text: String) {
                try {
                    val message = json.decodeFromString<WebSocketMessage>(text)
                    onMessage(message)
                } catch (e: Exception) {
                    onError(e)
                }
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                onError(t)
            }

            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                onClosed(code, reason)
            }
        })
    }

    // MARK: - Private Helpers

    private suspend inline fun <reified T> get(
        endpoint: String,
        queryParams: Map<String, String>? = null
    ): Result<T> {
        return withContext(Dispatchers.IO) {
            try {
                val urlBuilder = HttpUrl.parse("${configuration.baseURL}$endpoint")!!.newBuilder()
                queryParams?.forEach { (key, value) ->
                    urlBuilder.addQueryParameter(key, value)
                }

                val request = Request.Builder()
                    .url(urlBuilder.build())
                    .get()
                    .apply { addAuthHeaders() }
                    .build()

                val response = client.newCall(request).execute()
                handleResponse<T>(response)
            } catch (e: Exception) {
                Result.failure(DMSException.NetworkError(e.message ?: "Request failed"))
            }
        }
    }

    private suspend inline fun <reified T> post(
        endpoint: String,
        body: Any?
    ): Result<T> {
        return withContext(Dispatchers.IO) {
            try {
                val jsonBody = body?.let {
                    json.encodeToString(it).toRequestBody("application/json".toMediaType())
                } ?: "{}".toRequestBody("application/json".toMediaType())

                val request = Request.Builder()
                    .url("${configuration.baseURL}$endpoint")
                    .post(jsonBody)
                    .apply { addAuthHeaders() }
                    .build()

                val response = client.newCall(request).execute()
                handleResponse<T>(response)
            } catch (e: Exception) {
                Result.failure(DMSException.NetworkError(e.message ?: "Request failed"))
            }
        }
    }

    private suspend inline fun <reified T> put(
        endpoint: String,
        body: Any
    ): Result<T> {
        return withContext(Dispatchers.IO) {
            try {
                val jsonBody = json.encodeToString(body).toRequestBody("application/json".toMediaType())

                val request = Request.Builder()
                    .url("${configuration.baseURL}$endpoint")
                    .put(jsonBody)
                    .apply { addAuthHeaders() }
                    .build()

                val response = client.newCall(request).execute()
                handleResponse<T>(response)
            } catch (e: Exception) {
                Result.failure(DMSException.NetworkError(e.message ?: "Request failed"))
            }
        }
    }

    private suspend inline fun <reified T> delete(endpoint: String): Result<T> {
        return withContext(Dispatchers.IO) {
            try {
                val request = Request.Builder()
                    .url("${configuration.baseURL}$endpoint")
                    .delete()
                    .apply { addAuthHeaders() }
                    .build()

                val response = client.newCall(request).execute()
                handleResponse<T>(response)
            } catch (e: Exception) {
                Result.failure(DMSException.NetworkError(e.message ?: "Request failed"))
            }
        }
    }

    private fun Request.Builder.addAuthHeaders() {
        addHeader("Content-Type", "application/json")
        addHeader("Accept", "application/json")

        apiKey?.let { addHeader("X-API-Key", it) }
        accessToken?.let { addHeader("Authorization", "Bearer $it") }
    }

    private inline fun <reified T> handleResponse(response: Response): Result<T> {
        return try {
            if (!response.isSuccessful) {
                val errorBody = response.body?.string()
                val errorMessage = try {
                    val error = json.decodeFromString<ErrorResponse>(errorBody ?: "{}")
                    error.message
                } catch (e: Exception) {
                    "HTTP ${response.code}"
                }
                Result.failure(DMSException.ApiError(errorMessage))
            } else {
                val body = response.body?.string() ?: "{}"
                val result = json.decodeFromString<T>(body)
                Result.success(result)
            }
        } catch (e: Exception) {
            Result.failure(DMSException.DecodingError(e.message ?: "Decoding failed"))
        }
    }
}

// MARK: - Exceptions

sealed class DMSException(message: String) : Exception(message) {
    class NetworkError(message: String) : DMSException(message)
    class HttpError(val statusCode: Int) : DMSException("HTTP error: $statusCode")
    class ApiError(message: String) : DMSException(message)
    class DecodingError(message: String) : DMSException("Decoding error: $message")
    class InvalidURL : DMSException("Invalid URL")
    class Unauthorized : DMSException("Unauthorized access")
    class NotFound : DMSException("Resource not found")
}

// Empty response for operations that don't return data
@Serializable
private class EmptyResponse

@Serializable
private data class ErrorResponse(
    val message: String,
    val code: String? = null
)
