"""
Примеры средних (medium) тестов

Medium тесты могут:
- Выполняться до 5 минут
- Использовать локальные ресурсы (тестовая БД, файлы)
- Использовать моки для внешних API
- Тестировать взаимодействие между компонентами
"""

import pytest
import tempfile
import os
from pathlib import Path

# Пометить весь модуль как medium тесты
pytestmark = [pytest.mark.medium, pytest.mark.integration]


class TestDatabaseOperations:
    """Примеры medium тестов с базой данных"""

    def test_user_crud_operations(self, test_db, db_session):
        """Test complete CRUD operations for User model"""
        from src.models.user import User

        # Create
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()

        # Read
        retrieved_user = db_session.query(User).filter_by(
            username="testuser"
        ).first()
        assert retrieved_user is not None
        assert retrieved_user.email == "test@example.com"

        # Update
        retrieved_user.email = "newemail@example.com"
        db_session.commit()

        updated_user = db_session.query(User).get(retrieved_user.id)
        assert updated_user.email == "newemail@example.com"

        # Delete
        db_session.delete(updated_user)
        db_session.commit()

        deleted_user = db_session.query(User).get(retrieved_user.id)
        assert deleted_user is None

    def test_document_relationships(self, test_db, db_session):
        """Test relationships between Document and User models"""
        from src.models.user import User
        from src.models.document import Document

        # Create user
        user = User(
            username="owner",
            email="owner@example.com",
            password_hash="hash"
        )
        db_session.add(user)
        db_session.commit()

        # Create documents for user
        doc1 = Document(
            title="Document 1",
            content="Content 1",
            owner_id=user.id
        )
        doc2 = Document(
            title="Document 2",
            content="Content 2",
            owner_id=user.id
        )

        db_session.add_all([doc1, doc2])
        db_session.commit()

        # Test relationship
        retrieved_user = db_session.query(User).get(user.id)
        assert len(retrieved_user.documents) == 2
        assert retrieved_user.documents[0].title in ["Document 1", "Document 2"]

    def test_transaction_rollback(self, test_db, db_session):
        """Test database transaction rollback"""
        from src.models.user import User

        # Start transaction
        user = User(
            username="rollback_test",
            email="rollback@example.com",
            password_hash="hash"
        )
        db_session.add(user)
        db_session.flush()

        # Verify user exists in current transaction
        assert db_session.query(User).filter_by(
            username="rollback_test"
        ).first() is not None

        # Rollback
        db_session.rollback()

        # Verify user doesn't exist after rollback
        assert db_session.query(User).filter_by(
            username="rollback_test"
        ).first() is None


class TestFileOperations:
    """Примеры medium тестов с файловой системой"""

    def test_document_upload_to_filesystem(self, tmp_path):
        """Test uploading document to filesystem"""
        from src.services.storage import FileStorage

        storage = FileStorage(base_path=str(tmp_path))

        # Create test file content
        test_content = b"Test document content"
        filename = "test_document.txt"

        # Upload
        file_path = storage.save_file(filename, test_content)

        # Verify file exists
        assert os.path.exists(file_path)

        # Verify content
        with open(file_path, 'rb') as f:
            saved_content = f.read()
        assert saved_content == test_content

    def test_document_retrieval_from_filesystem(self, tmp_path):
        """Test retrieving document from filesystem"""
        from src.services.storage import FileStorage

        storage = FileStorage(base_path=str(tmp_path))

        # Setup: save file
        test_content = b"Retrieve me!"
        filename = "retrieve_test.txt"
        storage.save_file(filename, test_content)

        # Test: retrieve file
        retrieved_content = storage.get_file(filename)
        assert retrieved_content == test_content

    def test_document_deletion_from_filesystem(self, tmp_path):
        """Test deleting document from filesystem"""
        from src.services.storage import FileStorage

        storage = FileStorage(base_path=str(tmp_path))

        # Setup: save file
        filename = "delete_test.txt"
        file_path = storage.save_file(filename, b"Delete me!")

        # Verify file exists
        assert os.path.exists(file_path)

        # Test: delete file
        storage.delete_file(filename)

        # Verify file doesn't exist
        assert not os.path.exists(file_path)

    def test_large_file_handling(self, tmp_path):
        """Test handling of large files"""
        from src.services.storage import FileStorage

        storage = FileStorage(base_path=str(tmp_path))

        # Create 10MB file
        large_content = b"x" * (10 * 1024 * 1024)
        filename = "large_file.bin"

        # Upload large file
        file_path = storage.save_file(filename, large_content)

        # Verify file size
        assert os.path.getsize(file_path) == 10 * 1024 * 1024

        # Retrieve in chunks
        retrieved_size = 0
        for chunk in storage.get_file_chunks(filename, chunk_size=1024*1024):
            retrieved_size += len(chunk)

        assert retrieved_size == 10 * 1024 * 1024


class TestAPIEndpoints:
    """Примеры medium тестов для API endpoints"""

    def test_user_registration_endpoint(self, client, test_db):
        """Test user registration API endpoint"""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'StrongP@ss123'
        })

        assert response.status_code == 201
        data = response.get_json()
        assert 'user_id' in data
        assert data['username'] == 'newuser'

        # Verify user in database
        from src.models.user import User
        user = User.query.filter_by(username='newuser').first()
        assert user is not None

    def test_user_login_endpoint(self, client, test_db, test_user):
        """Test user login API endpoint"""
        response = client.post('/api/auth/login', json={
            'username': test_user.username,
            'password': 'password123'  # From fixture
        })

        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert 'refresh_token' in data

    def test_document_list_endpoint(self, client, auth_headers, test_documents):
        """Test listing documents endpoint"""
        response = client.get('/api/documents/', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert 'documents' in data
        assert len(data['documents']) > 0

    def test_document_create_endpoint(self, client, auth_headers, test_db):
        """Test document creation endpoint"""
        response = client.post('/api/documents/', headers=auth_headers, json={
            'title': 'New Document',
            'content': 'Document content',
            'tags': ['test', 'api']
        })

        assert response.status_code == 201
        data = response.get_json()
        assert data['title'] == 'New Document'
        assert 'document_id' in data

    def test_document_update_endpoint(self, client, auth_headers, test_document):
        """Test document update endpoint"""
        doc_id = test_document.id

        response = client.put(f'/api/documents/{doc_id}',
                            headers=auth_headers,
                            json={'title': 'Updated Title'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['title'] == 'Updated Title'

    def test_document_delete_endpoint(self, client, auth_headers, test_document):
        """Test document deletion endpoint"""
        doc_id = test_document.id

        response = client.delete(f'/api/documents/{doc_id}',
                               headers=auth_headers)

        assert response.status_code == 204

        # Verify document is deleted
        get_response = client.get(f'/api/documents/{doc_id}',
                                 headers=auth_headers)
        assert get_response.status_code == 404


class TestServiceIntegration:
    """Примеры medium тестов для интеграции сервисов"""

    def test_document_processing_service(self, test_db, tmp_path):
        """Test document processing service integration"""
        from src.services.document_processor import DocumentProcessor
        from src.services.storage import FileStorage

        # Setup
        storage = FileStorage(base_path=str(tmp_path))
        processor = DocumentProcessor(storage=storage)

        # Create test document
        test_content = b"Test document for processing"
        file_path = storage.save_file("test.txt", test_content)

        # Process document
        result = processor.process_document(file_path)

        assert result['status'] == 'success'
        assert result['word_count'] > 0
        assert result['char_count'] > 0

    def test_search_service_integration(self, test_db, test_documents):
        """Test search service with database"""
        from src.services.search import SearchService

        search = SearchService()

        # Search for documents
        results = search.search("test query")

        assert len(results) > 0
        assert all(hasattr(r, 'title') for r in results)

    def test_authentication_service_integration(self, test_db):
        """Test authentication service integration"""
        from src.services.auth import AuthService

        auth = AuthService()

        # Register user
        user = auth.register_user(
            username="authtest",
            email="authtest@example.com",
            password="StrongP@ss123"
        )

        assert user is not None
        assert user.id is not None

        # Login
        token = auth.login(username="authtest", password="StrongP@ss123")
        assert token is not None

        # Verify token
        verified_user = auth.verify_token(token)
        assert verified_user.id == user.id


class TestCacheIntegration:
    """Примеры medium тестов с кешированием"""

    def test_cache_set_and_get(self, redis_client):
        """Test cache set and get operations"""
        from src.services.cache import CacheService

        cache = CacheService(redis_client)

        # Set value
        cache.set("test_key", "test_value", ttl=60)

        # Get value
        value = cache.get("test_key")
        assert value == "test_value"

    def test_cache_expiration(self, redis_client):
        """Test cache expiration"""
        import time
        from src.services.cache import CacheService

        cache = CacheService(redis_client)

        # Set value with short TTL
        cache.set("expire_key", "expire_value", ttl=1)

        # Verify value exists
        assert cache.get("expire_key") == "expire_value"

        # Wait for expiration
        time.sleep(2)

        # Verify value expired
        assert cache.get("expire_key") is None

    def test_cache_invalidation(self, redis_client):
        """Test cache invalidation"""
        from src.services.cache import CacheService

        cache = CacheService(redis_client)

        # Set multiple values
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        # Invalidate specific key
        cache.delete("key1")

        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"


class TestEmailService:
    """Примеры medium тестов для email сервиса"""

    @pytest.mark.parametrize("email_type", [
        "welcome",
        "password_reset",
        "verification",
    ])
    def test_email_template_rendering(self, email_type):
        """Test email template rendering"""
        from src.services.email import EmailService

        email = EmailService()

        context = {
            'username': 'testuser',
            'verification_link': 'https://example.com/verify/123'
        }

        rendered = email.render_template(email_type, context)

        assert rendered is not None
        assert 'testuser' in rendered
        assert len(rendered) > 0

    def test_email_queue(self, test_db):
        """Test email queueing system"""
        from src.services.email import EmailService

        email = EmailService()

        # Queue email
        message_id = email.queue_email(
            to="test@example.com",
            subject="Test Email",
            body="Test Body"
        )

        assert message_id is not None

        # Verify email in queue
        from src.models.email_queue import EmailQueue
        queued = EmailQueue.query.get(message_id)
        assert queued is not None
        assert queued.to_address == "test@example.com"


# Пример medium теста с множественными фикстурами
def test_complete_user_workflow(client, test_db, tmp_path, redis_client):
    """Test complete user workflow with multiple services"""
    from src.services.cache import CacheService

    cache = CacheService(redis_client)

    # 1. Register user
    response = client.post('/api/auth/register', json={
        'username': 'workflow_user',
        'email': 'workflow@example.com',
        'password': 'StrongP@ss123'
    })
    assert response.status_code == 201

    # 2. Login
    login_response = client.post('/api/auth/login', json={
        'username': 'workflow_user',
        'password': 'StrongP@ss123'
    })
    assert login_response.status_code == 200
    token = login_response.get_json()['access_token']

    # 3. Create document
    headers = {'Authorization': f'Bearer {token}'}
    doc_response = client.post('/api/documents/', headers=headers, json={
        'title': 'Workflow Document',
        'content': 'Test content'
    })
    assert doc_response.status_code == 201

    # 4. Verify cache updated
    # (assuming documents are cached)
    cached_docs = cache.get(f"user_documents:workflow_user")
    # Cache implementation specific assertions...

    # 5. Logout (if implemented)
    logout_response = client.post('/api/auth/logout', headers=headers)
    # Verify logout behavior...
