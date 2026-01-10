/**
 * DatenClient.kt
 * Daten Android SDK
 *
 * Native Android SDK for Document Management System
 * Version: 3.3.0
 */

package com.daten.sdk

import android.content.Context
import android.content.SharedPreferences
import androidx.biometric.BiometricPrompt
import androidx.core.content.ContextCompat
import androidx.fragment.app.FragmentActivity
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.io.IOException
import java.util.*
import java.util.concurrent.TimeUnit

// MARK: - Configuration

data class DatenConfiguration(
    val baseUrl: String,
    val apiKey: String? = null,
    val enableOfflineMode: Boolean = true,
    val enableBiometrics: Boolean = true,
    val syncIntervalSeconds: Long = 300
)

// MARK: - Models

data class Document(
    val id: String = UUID.randomUUID().toString(),
    var title: String,
    var content: String,
    val createdAt: Date = Date(),
    var updatedAt: Date = Date(),
    val userId: String,
    var version: Int = 1
)

data class AuthCredentials(
    val username: String,
    val password: String
)

data class AuthToken(
    val accessToken: String,
    val refreshToken: String,
    val expiresIn: Int,
    val tokenType: String
)

// MARK: - Sync Status

sealed class SyncStatus {
    object Idle : SyncStatus()
    object Syncing : SyncStatus()
    object Completed : SyncStatus()
    data class Failed(val error: Throwable) : SyncStatus()
}

// MARK: - Errors

sealed class DatenException(message: String) : Exception(message) {
    object NotAuthenticated : DatenException("User is not authenticated")
    data class NetworkError(val cause: Throwable) : DatenException("Network error: ${cause.message}")
    object InvalidResponse : DatenException("Invalid server response")
    object BiometricAuthFailed : DatenException("Biometric authentication failed")
    object OfflineModeDisabled : DatenException("Offline mode is disabled")
    object SyncConflict : DatenException("Sync conflict detected")
}

// MARK: - Main SDK Client

class DatenClient(
    private val context: Context,
    private val configuration: DatenConfiguration
) {

    // MARK: - Public State Flows

    private val _isAuthenticated = MutableStateFlow(false)
    val isAuthenticated: StateFlow<Boolean> = _isAuthenticated.asStateFlow()

    private val _currentUser = MutableStateFlow<String?>(null)
    val currentUser: StateFlow<String?> = _currentUser.asStateFlow()

    private val _syncStatus = MutableStateFlow<SyncStatus>(SyncStatus.Idle)
    val syncStatus: StateFlow<SyncStatus> = _syncStatus.asStateFlow()

    private val _documents = MutableStateFlow<List<Document>>(emptyList())
    val documents: StateFlow<List<Document>> = _documents.asStateFlow()

    // MARK: - Private Properties

    private var authToken: AuthToken? = null
    private val httpClient: OkHttpClient
    private val prefs: SharedPreferences
    private var syncJob: Job? = null
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())

    // MARK: - Services

    private val authService: AuthenticationService by lazy { AuthenticationService(this) }
    private val documentService: DocumentService by lazy { DocumentService(this) }
    private val syncManager: SyncManager by lazy { SyncManager(this) }
    private val biometricService: BiometricAuthService by lazy { BiometricAuthService(context) }

    init {
        httpClient = OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .build()

        prefs = context.getSharedPreferences("daten_sdk", Context.MODE_PRIVATE)

        loadAuthToken()

        if (configuration.enableOfflineMode) {
            setupAutoSync()
        }
    }

    // MARK: - Authentication

    suspend fun signIn(credentials: AuthCredentials): Result<Unit> = withContext(Dispatchers.IO) {
        try {
            val token = authService.signIn(credentials)
            authToken = token
            _isAuthenticated.value = true
            _currentUser.value = credentials.username
            saveAuthToken(token)

            if (configuration.enableOfflineMode) {
                syncManager.performSync()
            }

            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    fun signOut() {
        authToken = null
        _isAuthenticated.value = false
        _currentUser.value = null
        _documents.value = emptyList()
        clearAuthToken()
        stopAutoSync()
    }

    suspend fun refreshToken(): Result<Unit> = withContext(Dispatchers.IO) {
        try {
            val currentToken = authToken ?: throw DatenException.NotAuthenticated

            val newToken = authService.refreshToken(currentToken.refreshToken)
            authToken = newToken
            saveAuthToken(newToken)

            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // MARK: - Biometric Authentication

    suspend fun authenticateWithBiometrics(
        activity: FragmentActivity,
        title: String = "Authenticate",
        subtitle: String = "Unlock Daten"
    ): Result<Boolean> {
        if (!configuration.enableBiometrics) {
            return Result.success(false)
        }

        return biometricService.authenticate(activity, title, subtitle)
    }

    // MARK: - Document Operations

    suspend fun fetchDocuments(): Result<List<Document>> = withContext(Dispatchers.IO) {
        try {
            if (!_isAuthenticated.value) {
                throw DatenException.NotAuthenticated
            }

            val docs = documentService.fetchDocuments()
            _documents.value = docs
            Result.success(docs)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun createDocument(document: Document): Result<Document> = withContext(Dispatchers.IO) {
        try {
            if (!_isAuthenticated.value) {
                throw DatenException.NotAuthenticated
            }

            val created = documentService.createDocument(document)

            if (configuration.enableOfflineMode) {
                syncManager.queueOperation(SyncOperation.Create(created))
            }

            _documents.value = _documents.value + created
            Result.success(created)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun updateDocument(document: Document): Result<Document> = withContext(Dispatchers.IO) {
        try {
            if (!_isAuthenticated.value) {
                throw DatenException.NotAuthenticated
            }

            val updated = documentService.updateDocument(document)

            if (configuration.enableOfflineMode) {
                syncManager.queueOperation(SyncOperation.Update(updated))
            }

            _documents.value = _documents.value.map {
                if (it.id == document.id) updated else it
            }

            Result.success(updated)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun deleteDocument(id: String): Result<Unit> = withContext(Dispatchers.IO) {
        try {
            if (!_isAuthenticated.value) {
                throw DatenException.NotAuthenticated
            }

            documentService.deleteDocument(id)

            if (configuration.enableOfflineMode) {
                syncManager.queueOperation(SyncOperation.Delete(id))
            }

            _documents.value = _documents.value.filter { it.id != id }
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // MARK: - Sync Operations

    suspend fun syncNow(): Result<Unit> = withContext(Dispatchers.IO) {
        try {
            if (!configuration.enableOfflineMode) {
                throw DatenException.OfflineModeDisabled
            }

            _syncStatus.value = SyncStatus.Syncing

            syncManager.performSync()

            _syncStatus.value = SyncStatus.Completed
            Result.success(Unit)
        } catch (e: Exception) {
            _syncStatus.value = SyncStatus.Failed(e)
            Result.failure(e)
        }
    }

    // MARK: - Private Helpers

    private fun setupAutoSync() {
        syncJob = scope.launch {
            while (isActive) {
                delay(configuration.syncIntervalSeconds * 1000)
                if (_isAuthenticated.value) {
                    try {
                        syncNow()
                    } catch (e: Exception) {
                        // Log error but continue syncing
                    }
                }
            }
        }
    }

    private fun stopAutoSync() {
        syncJob?.cancel()
        syncJob = null
    }

    private fun saveAuthToken(token: AuthToken) {
        prefs.edit()
            .putString("access_token", token.accessToken)
            .putString("refresh_token", token.refreshToken)
            .putInt("expires_in", token.expiresIn)
            .putString("token_type", token.tokenType)
            .apply()
    }

    private fun loadAuthToken() {
        val accessToken = prefs.getString("access_token", null)
        val refreshToken = prefs.getString("refresh_token", null)
        val expiresIn = prefs.getInt("expires_in", 0)
        val tokenType = prefs.getString("token_type", "Bearer")

        if (accessToken != null && refreshToken != null) {
            authToken = AuthToken(accessToken, refreshToken, expiresIn, tokenType!!)
            _isAuthenticated.value = true
        }
    }

    private fun clearAuthToken() {
        prefs.edit().clear().apply()
    }

    // MARK: - Internal API

    internal suspend fun <T> makeRequest(
        endpoint: String,
        method: String = "GET",
        body: String? = null,
        parser: (String) -> T
    ): T = withContext(Dispatchers.IO) {
        val url = "${configuration.baseUrl}$endpoint"

        val requestBuilder = Request.Builder().url(url)

        when (method) {
            "GET" -> requestBuilder.get()
            "POST" -> requestBuilder.post(
                body?.toRequestBody("application/json".toMediaType())
                    ?: "".toRequestBody()
            )
            "PUT" -> requestBuilder.put(
                body?.toRequestBody("application/json".toMediaType())
                    ?: "".toRequestBody()
            )
            "DELETE" -> requestBuilder.delete()
        }

        requestBuilder.addHeader("Content-Type", "application/json")

        authToken?.let {
            requestBuilder.addHeader("Authorization", "Bearer ${it.accessToken}")
        } ?: configuration.apiKey?.let {
            requestBuilder.addHeader("X-API-Key", it)
        }

        val request = requestBuilder.build()

        val response = httpClient.newCall(request).execute()

        if (!response.isSuccessful) {
            throw DatenException.NetworkError(IOException("HTTP ${response.code}"))
        }

        val responseBody = response.body?.string() ?: throw DatenException.InvalidResponse

        parser(responseBody)
    }

    fun close() {
        stopAutoSync()
        scope.cancel()
        httpClient.dispatcher.executorService.shutdown()
        httpClient.connectionPool.evictAll()
    }
}

// MARK: - Authentication Service

internal class AuthenticationService(private val client: DatenClient) {

    suspend fun signIn(credentials: AuthCredentials): AuthToken {
        val json = JSONObject().apply {
            put("username", credentials.username)
            put("password", credentials.password)
        }

        return client.makeRequest("/auth/login", "POST", json.toString()) { response ->
            val jsonResponse = JSONObject(response)
            AuthToken(
                accessToken = jsonResponse.getString("access_token"),
                refreshToken = jsonResponse.getString("refresh_token"),
                expiresIn = jsonResponse.getInt("expires_in"),
                tokenType = jsonResponse.getString("token_type")
            )
        }
    }

    suspend fun refreshToken(refreshToken: String): AuthToken {
        val json = JSONObject().apply {
            put("refresh_token", refreshToken)
        }

        return client.makeRequest("/auth/refresh", "POST", json.toString()) { response ->
            val jsonResponse = JSONObject(response)
            AuthToken(
                accessToken = jsonResponse.getString("access_token"),
                refreshToken = jsonResponse.getString("refresh_token"),
                expiresIn = jsonResponse.getInt("expires_in"),
                tokenType = jsonResponse.getString("token_type")
            )
        }
    }
}

// MARK: - Document Service

internal class DocumentService(private val client: DatenClient) {

    suspend fun fetchDocuments(): List<Document> {
        return client.makeRequest("/documents") { response ->
            val jsonArray = org.json.JSONArray(response)
            (0 until jsonArray.length()).map { i ->
                val obj = jsonArray.getJSONObject(i)
                Document(
                    id = obj.getString("id"),
                    title = obj.getString("title"),
                    content = obj.getString("content"),
                    createdAt = Date(obj.getLong("created_at")),
                    updatedAt = Date(obj.getLong("updated_at")),
                    userId = obj.getString("user_id"),
                    version = obj.getInt("version")
                )
            }
        }
    }

    suspend fun createDocument(document: Document): Document {
        val json = documentToJson(document)

        return client.makeRequest("/documents", "POST", json.toString()) { response ->
            jsonToDocument(JSONObject(response))
        }
    }

    suspend fun updateDocument(document: Document): Document {
        val json = documentToJson(document)

        return client.makeRequest("/documents/${document.id}", "PUT", json.toString()) { response ->
            jsonToDocument(JSONObject(response))
        }
    }

    suspend fun deleteDocument(id: String) {
        client.makeRequest<Unit>("/documents/$id", "DELETE") { }
    }

    private fun documentToJson(document: Document): JSONObject {
        return JSONObject().apply {
            put("id", document.id)
            put("title", document.title)
            put("content", document.content)
            put("created_at", document.createdAt.time)
            put("updated_at", document.updatedAt.time)
            put("user_id", document.userId)
            put("version", document.version)
        }
    }

    private fun jsonToDocument(json: JSONObject): Document {
        return Document(
            id = json.getString("id"),
            title = json.getString("title"),
            content = json.getString("content"),
            createdAt = Date(json.getLong("created_at")),
            updatedAt = Date(json.getLong("updated_at")),
            userId = json.getString("user_id"),
            version = json.getInt("version")
        )
    }
}

// MARK: - Sync Manager

internal sealed class SyncOperation {
    data class Create(val document: Document) : SyncOperation()
    data class Update(val document: Document) : SyncOperation()
    data class Delete(val id: String) : SyncOperation()
}

internal class SyncManager(private val client: DatenClient) {
    private val pendingOperations = mutableListOf<SyncOperation>()

    fun queueOperation(operation: SyncOperation) {
        synchronized(pendingOperations) {
            pendingOperations.add(operation)
        }
    }

    suspend fun performSync() {
        val operations = synchronized(pendingOperations) {
            pendingOperations.toList()
        }

        for (operation in operations) {
            when (operation) {
                is SyncOperation.Create -> client.documentService.createDocument(operation.document)
                is SyncOperation.Update -> client.documentService.updateDocument(operation.document)
                is SyncOperation.Delete -> client.documentService.deleteDocument(operation.id)
            }
        }

        synchronized(pendingOperations) {
            pendingOperations.clear()
        }
    }
}

// MARK: - Biometric Service

internal class BiometricAuthService(private val context: Context) {

    fun canAuthenticateWithBiometrics(): Boolean {
        val biometricManager = androidx.biometric.BiometricManager.from(context)
        return biometricManager.canAuthenticate(androidx.biometric.BiometricManager.Authenticators.BIOMETRIC_STRONG) ==
                androidx.biometric.BiometricManager.BIOMETRIC_SUCCESS
    }

    suspend fun authenticate(
        activity: FragmentActivity,
        title: String,
        subtitle: String
    ): Result<Boolean> = suspendCancellableCoroutine { continuation ->

        if (!canAuthenticateWithBiometrics()) {
            continuation.resume(Result.failure(DatenException.BiometricAuthFailed)) {}
            return@suspendCancellableCoroutine
        }

        val executor = ContextCompat.getMainExecutor(context)

        val biometricPrompt = BiometricPrompt(
            activity,
            executor,
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                    continuation.resume(Result.success(true)) {}
                }

                override fun onAuthenticationFailed() {
                    continuation.resume(Result.failure(DatenException.BiometricAuthFailed)) {}
                }

                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    continuation.resume(Result.failure(DatenException.BiometricAuthFailed)) {}
                }
            }
        )

        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle(title)
            .setSubtitle(subtitle)
            .setNegativeButtonText("Cancel")
            .build()

        biometricPrompt.authenticate(promptInfo)
    }
}
