/**
 * Collaborative Editor Client
 *
 * Real-time collaborative text editing with WebSocket support.
 */

class CollaborativeEditor {
    constructor(documentId, userId, username) {
        this.documentId = documentId;
        this.userId = userId;
        this.username = username;

        this.socket = null;
        this.editor = null;
        this.revision = 0;
        this.content = '';
        this.activeUsers = new Map();
        this.cursors = new Map();

        this.pendingOperation = null;
        this.isApplyingRemoteEdit = false;

        this.init();
    }

    init() {
        // Get DOM elements
        this.editor = document.getElementById('editor');
        this.documentNameEl = document.getElementById('document-name');
        this.connectionStatusEl = document.getElementById('connection-status');
        this.revisionNumberEl = document.getElementById('revision-number');
        this.userCountEl = document.getElementById('user-count');
        this.activeUsersEl = document.getElementById('active-users');
        this.activityLogEl = document.getElementById('activity-log');
        this.wordCountEl = document.getElementById('word-count');
        this.charCountEl = document.getElementById('char-count');

        // Initialize Socket.IO
        this.initSocket();

        // Setup event listeners
        this.setupEventListeners();
    }

    initSocket() {
        // Connect to Socket.IO server
        this.socket = io();

        // Connection events
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.updateConnectionStatus('connecting');
            this.joinDocument();
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
            this.updateConnectionStatus('disconnected');
        });

        // Collaboration events
        this.socket.on('collab:document_state', (data) => {
            this.handleDocumentState(data);
        });

        this.socket.on('collab:user_joined', (data) => {
            this.handleUserJoined(data);
        });

        this.socket.on('collab:user_left', (data) => {
            this.handleUserLeft(data);
        });

        this.socket.on('collab:remote_edit', (data) => {
            this.handleRemoteEdit(data);
        });

        this.socket.on('collab:cursor_update', (data) => {
            this.handleCursorUpdate(data);
        });

        this.socket.on('collab:ack', (data) => {
            this.handleAck(data);
        });

        this.socket.on('collab:snapshot_created', (data) => {
            this.handleSnapshotCreated(data);
        });

        this.socket.on('collab:statistics', (data) => {
            this.updateStatistics(data);
        });

        this.socket.on('collab:error', (data) => {
            console.error('Collaboration error:', data.message);
            this.addActivityLog(`Error: ${data.message}`, 'danger');
        });
    }

    setupEventListeners() {
        // Editor input
        this.editor.addEventListener('input', (e) => {
            this.handleLocalEdit(e);
        });

        // Cursor movement
        this.editor.addEventListener('selectionchange', () => {
            this.handleCursorMove();
        });

        this.editor.addEventListener('click', () => {
            this.handleCursorMove();
        });

        this.editor.addEventListener('keyup', () => {
            this.handleCursorMove();
        });

        // Toolbar buttons
        document.getElementById('btn-save').addEventListener('click', () => {
            this.createSnapshot();
        });

        // Update word/char count
        this.editor.addEventListener('input', () => {
            this.updateWordCount();
        });
    }

    joinDocument() {
        this.socket.emit('collab:join_document', {
            document_id: this.documentId,
            user_id: this.userId,
            username: this.username
        });
    }

    handleDocumentState(data) {
        console.log('Received document state:', data);

        // Update document info
        this.documentNameEl.textContent = data.document.name;
        this.content = data.document.content;
        this.revision = data.document.revision;

        // Set editor content
        this.editor.value = this.content;

        // Update revision number
        this.revisionNumberEl.textContent = this.revision;

        // Update active users
        this.activeUsers.clear();
        data.active_users.forEach(user => {
            this.activeUsers.set(user.user_id, user);
        });
        this.renderActiveUsers();

        // Update connection status
        this.updateConnectionStatus('connected');

        // Update stats
        this.loadStatistics();

        // Update word count
        this.updateWordCount();

        this.addActivityLog(`Joined document: ${data.document.name}`, 'success');
    }

    handleUserJoined(data) {
        console.log('User joined:', data);

        this.activeUsers.set(data.user_id, {
            user_id: data.user_id,
            username: data.username,
            cursor: { position: 0, color: this.getUserColor(data.user_id) }
        });

        this.renderActiveUsers();
        this.addActivityLog(`${data.username} joined`, 'info');
    }

    handleUserLeft(data) {
        console.log('User left:', data);

        this.activeUsers.delete(data.user_id);
        this.cursors.delete(data.user_id);

        this.renderActiveUsers();
        this.renderCursors();
        this.addActivityLog(`${data.username} left`, 'secondary');
    }

    handleLocalEdit(event) {
        if (this.isApplyingRemoteEdit) {
            return;
        }

        const newContent = this.editor.value;
        const cursorPos = this.editor.selectionStart;

        // Calculate operation
        const operation = this.calculateOperation(this.content, newContent, cursorPos);

        if (operation) {
            // Update local content
            this.content = newContent;

            // Send operation to server
            this.socket.emit('collab:edit', {
                operation: {
                    type: operation.type,
                    position: operation.position,
                    content: operation.content,
                    length: operation.length
                },
                client_revision: this.revision
            });
        }
    }

    handleRemoteEdit(data) {
        console.log('Remote edit:', data);

        this.isApplyingRemoteEdit = true;

        const operation = data.operation;
        const cursorPos = this.editor.selectionStart;

        // Apply operation to content
        this.content = this.applyOperation(this.content, operation);

        // Update editor
        this.editor.value = this.content;

        // Adjust cursor position
        let newCursorPos = cursorPos;
        if (operation.type === 'insert' && operation.position <= cursorPos) {
            newCursorPos += operation.content.length;
        } else if (operation.type === 'delete' && operation.position < cursorPos) {
            newCursorPos -= Math.min(operation.length, cursorPos - operation.position);
        }

        this.editor.setSelectionRange(newCursorPos, newCursorPos);

        // Update revision
        this.revision = data.revision;
        this.revisionNumberEl.textContent = this.revision;

        this.isApplyingRemoteEdit = false;

        // Update word count
        this.updateWordCount();

        // Get username
        const user = this.activeUsers.get(data.user_id);
        const username = user ? user.username : `User ${data.user_id}`;

        this.addActivityLog(
            `${username} edited (${operation.type} at ${operation.position})`,
            'primary'
        );
    }

    handleAck(data) {
        console.log('Operation acknowledged, revision:', data.revision);
        this.revision = data.revision;
        this.revisionNumberEl.textContent = this.revision;
    }

    handleCursorMove() {
        const position = this.editor.selectionStart;
        const selectionEnd = this.editor.selectionEnd;

        this.socket.emit('collab:cursor', {
            position: position,
            selection_start: position !== selectionEnd ? position : null,
            selection_end: position !== selectionEnd ? selectionEnd : null
        });
    }

    handleCursorUpdate(data) {
        this.cursors.set(data.user_id, {
            position: data.position,
            selection_start: data.selection_start,
            selection_end: data.selection_end,
            user: this.activeUsers.get(data.user_id)
        });

        this.renderCursors();
    }

    handleSnapshotCreated(data) {
        console.log('Snapshot created:', data.snapshot_id);
        this.addActivityLog(`Snapshot saved`, 'success');
        this.loadStatistics();
    }

    calculateOperation(oldContent, newContent, cursorPos) {
        // Simple diff algorithm

        if (oldContent === newContent) {
            return null;
        }

        // Find the first difference
        let i = 0;
        while (i < Math.min(oldContent.length, newContent.length) && oldContent[i] === newContent[i]) {
            i++;
        }

        // Find the last difference
        let oldEnd = oldContent.length;
        let newEnd = newContent.length;
        while (oldEnd > i && newEnd > i && oldContent[oldEnd - 1] === newContent[newEnd - 1]) {
            oldEnd--;
            newEnd--;
        }

        const deletedText = oldContent.substring(i, oldEnd);
        const insertedText = newContent.substring(i, newEnd);

        if (deletedText && !insertedText) {
            // Delete operation
            return {
                type: 'delete',
                position: i,
                length: deletedText.length
            };
        } else if (!deletedText && insertedText) {
            // Insert operation
            return {
                type: 'insert',
                position: i,
                content: insertedText
            };
        } else if (deletedText && insertedText) {
            // Replace operation (delete + insert)
            // For simplicity, we'll treat this as an insert
            return {
                type: 'insert',
                position: i,
                content: insertedText
            };
        }

        return null;
    }

    applyOperation(content, operation) {
        if (operation.type === 'insert') {
            return content.substring(0, operation.position) +
                   operation.content +
                   content.substring(operation.position);
        } else if (operation.type === 'delete') {
            return content.substring(0, operation.position) +
                   content.substring(operation.position + operation.length);
        }
        return content;
    }

    renderActiveUsers() {
        this.activeUsersEl.innerHTML = '';
        this.userCountEl.textContent = this.activeUsers.size;

        this.activeUsers.forEach((user, userId) => {
            const color = user.cursor?.color || this.getUserColor(userId);

            const badge = document.createElement('div');
            badge.className = 'user-badge';
            badge.style.backgroundColor = color;
            badge.innerHTML = `
                <i class="fas fa-user me-2"></i>
                ${user.username}
                ${userId === this.userId ? ' (You)' : ''}
            `;

            this.activeUsersEl.appendChild(badge);
        });
    }

    renderCursors() {
        // Remove old cursors
        document.querySelectorAll('.cursor, .selection').forEach(el => el.remove());

        // Render cursors for other users
        this.cursors.forEach((cursor, userId) => {
            if (userId === this.userId) {
                return; // Don't render own cursor
            }

            const user = cursor.user;
            if (!user) return;

            const color = user.cursor?.color || this.getUserColor(userId);

            // This is a simplified cursor rendering
            // In production, you'd calculate exact pixel positions

            // For now, just show in the UI that users are active
        });
    }

    updateConnectionStatus(status) {
        const statusMap = {
            'connected': {
                class: 'status-connected',
                text: 'Connected'
            },
            'connecting': {
                class: 'status-connecting',
                text: 'Connecting...'
            },
            'disconnected': {
                class: 'status-disconnected',
                text: 'Disconnected'
            }
        };

        const statusInfo = statusMap[status] || statusMap.disconnected;

        this.connectionStatusEl.innerHTML = `
            <span class="status-indicator ${statusInfo.class}"></span>
            ${statusInfo.text}
        `;
    }

    updateWordCount() {
        const text = this.editor.value;
        const words = text.trim() ? text.trim().split(/\s+/).length : 0;
        const chars = text.length;

        this.wordCountEl.textContent = words;
        this.charCountEl.textContent = chars;
    }

    createSnapshot() {
        this.socket.emit('collab:create_snapshot', {});
    }

    loadStatistics() {
        this.socket.emit('collab:get_statistics', {});
    }

    updateStatistics(stats) {
        document.getElementById('stat-operations').textContent = stats.operations_count || 0;
        document.getElementById('stat-snapshots').textContent = stats.snapshots_count || 0;
    }

    addActivityLog(message, type = 'info') {
        const now = new Date().toLocaleTimeString();

        const item = document.createElement('div');
        item.className = `activity-item text-${type}`;
        item.innerHTML = `
            <span class="activity-time">${now}</span>
            <div>${message}</div>
        `;

        this.activityLogEl.prepend(item);

        // Keep only last 20 items
        while (this.activityLogEl.children.length > 20) {
            this.activityLogEl.lastChild.remove();
        }
    }

    getUserColor(userId) {
        const colors = [
            '#0d6efd', // blue
            '#198754', // green
            '#dc3545', // red
            '#ffc107', // yellow
            '#6f42c1', // purple
            '#fd7e14', // orange
            '#20c997', // teal
            '#d63384'  // pink
        ];

        return colors[userId % colors.length];
    }
}

// Initialize editor when page loads
document.addEventListener('DOMContentLoaded', () => {
    // Get document ID from URL or data attribute
    const urlParams = new URLSearchParams(window.location.search);
    const documentId = urlParams.get('doc') || 'default-doc';

    // In production, get these from session/auth
    const userId = parseInt(urlParams.get('user') || '1');
    const username = urlParams.get('username') || `User${userId}`;

    // Create editor instance
    window.collabEditor = new CollaborativeEditor(documentId, userId, username);

    console.log('Collaborative editor initialized');
});
