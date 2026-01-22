"""
Tests for LDAP / Active Directory authentication module

Tests LDAP and Active Directory authentication integration.
"""

import sys
from unittest.mock import Mock, MagicMock, patch

# No external dependencies needed - module uses standard library
from src.core.sso.ldap import (
    LDAPAuthMethod,
    LDAPScope,
    LDAPConfig,
    ADConfig,
    UserMapping,
    GroupMapping,
    LDAPUser,
    LDAPGroup,
    LDAPConnection,
    LDAPAuthenticator,
    ActiveDirectoryAuthenticator,
    get_ldap_authenticator,
    configure_ldap_authenticator,
)


class TestLDAPAuthMethod:
    """Test LDAPAuthMethod enum"""

    def test_simple_auth_method(self):
        """Test SIMPLE auth method"""
        assert LDAPAuthMethod.SIMPLE == "simple"
        assert LDAPAuthMethod.SIMPLE.value == "simple"

    def test_sasl_auth_method(self):
        """Test SASL auth method"""
        assert LDAPAuthMethod.SASL == "sasl"
        assert LDAPAuthMethod.SASL.value == "sasl"

    def test_anonymous_auth_method(self):
        """Test ANONYMOUS auth method"""
        assert LDAPAuthMethod.ANONYMOUS == "anonymous"
        assert LDAPAuthMethod.ANONYMOUS.value == "anonymous"


class TestLDAPScope:
    """Test LDAPScope enum"""

    def test_base_scope(self):
        """Test BASE scope"""
        assert LDAPScope.BASE == "base"
        assert LDAPScope.BASE.value == "base"

    def test_one_level_scope(self):
        """Test ONE_LEVEL scope"""
        assert LDAPScope.ONE_LEVEL == "onelevel"
        assert LDAPScope.ONE_LEVEL.value == "onelevel"

    def test_subtree_scope(self):
        """Test SUBTREE scope"""
        assert LDAPScope.SUBTREE == "subtree"
        assert LDAPScope.SUBTREE.value == "subtree"


class TestLDAPConfig:
    """Test LDAPConfig dataclass"""

    def test_config_creation_minimal(self):
        """Test creating config with minimal fields"""
        config = LDAPConfig(host="ldap.example.com")
        assert config.host == "ldap.example.com"
        assert config.port == 389
        assert config.use_ssl is False
        assert config.use_tls is False

    def test_config_default_values(self):
        """Test default values"""
        config = LDAPConfig(host="ldap.example.com")
        assert config.base_dn == ""
        assert config.bind_dn is None
        assert config.bind_password is None
        assert config.auth_method == LDAPAuthMethod.SIMPLE
        assert config.timeout == 10
        assert config.connection_pool_size == 10
        assert config.connection_pool_lifetime == 3600

    def test_config_with_ssl(self):
        """Test config with SSL enabled"""
        config = LDAPConfig(host="ldap.example.com", port=636, use_ssl=True)
        assert config.port == 636
        assert config.use_ssl is True

    def test_config_with_credentials(self):
        """Test config with bind credentials"""
        config = LDAPConfig(
            host="ldap.example.com",
            bind_dn="cn=admin,dc=example,dc=com",
            bind_password="secret",
        )
        assert config.bind_dn == "cn=admin,dc=example,dc=com"
        assert config.bind_password == "secret"

    def test_config_with_base_dn(self):
        """Test config with base DN"""
        config = LDAPConfig(host="ldap.example.com", base_dn="dc=example,dc=com")
        assert config.base_dn == "dc=example,dc=com"


class TestADConfig:
    """Test ADConfig dataclass"""

    def test_ad_config_creation(self):
        """Test creating AD config"""
        config = ADConfig(host="ad.example.com", domain="example.com")
        assert config.host == "ad.example.com"
        assert config.domain == "example.com"

    def test_ad_config_default_values(self):
        """Test AD specific default values"""
        config = ADConfig(host="ad.example.com")
        assert config.domain == ""
        assert config.use_paging is True
        assert config.page_size == 1000
        assert config.follow_referrals is True

    def test_ad_config_inherits_ldap_config(self):
        """Test AD config inherits from LDAP config"""
        config = ADConfig(host="ad.example.com", port=636, use_ssl=True)
        assert config.port == 636
        assert config.use_ssl is True


class TestUserMapping:
    """Test UserMapping dataclass"""

    def test_user_mapping_defaults(self):
        """Test default user mapping"""
        mapping = UserMapping()
        assert mapping.username_attr == "uid"
        assert mapping.email_attr == "mail"
        assert mapping.first_name_attr == "givenName"
        assert mapping.last_name_attr == "sn"
        assert mapping.display_name_attr == "displayName"
        assert mapping.group_attr == "memberOf"
        assert mapping.object_class == "inetOrgPerson"
        assert mapping.user_filter == "(objectClass=inetOrgPerson)"

    def test_user_mapping_custom(self):
        """Test custom user mapping"""
        mapping = UserMapping(
            username_attr="sAMAccountName",
            user_filter="(&(objectClass=user)(objectCategory=person))",
        )
        assert mapping.username_attr == "sAMAccountName"
        assert mapping.user_filter == "(&(objectClass=user)(objectCategory=person))"


class TestGroupMapping:
    """Test GroupMapping dataclass"""

    def test_group_mapping_defaults(self):
        """Test default group mapping"""
        mapping = GroupMapping()
        assert mapping.name_attr == "cn"
        assert mapping.member_attr == "member"
        assert mapping.object_class == "groupOfNames"
        assert mapping.group_filter == "(objectClass=groupOfNames)"

    def test_group_mapping_custom(self):
        """Test custom group mapping"""
        mapping = GroupMapping(object_class="group", group_filter="(objectClass=group)")
        assert mapping.object_class == "group"
        assert mapping.group_filter == "(objectClass=group)"


class TestLDAPUser:
    """Test LDAPUser dataclass"""

    def test_user_creation_minimal(self):
        """Test creating user with minimal fields"""
        user = LDAPUser(dn="uid=jdoe,ou=users,dc=example,dc=com", username="jdoe")
        assert user.dn == "uid=jdoe,ou=users,dc=example,dc=com"
        assert user.username == "jdoe"
        assert user.email is None
        assert user.groups == []
        assert user.is_active is True

    def test_user_creation_full(self):
        """Test creating user with all fields"""
        user = LDAPUser(
            dn="uid=jdoe,ou=users,dc=example,dc=com",
            username="jdoe",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
            display_name="John Doe",
            groups=["cn=admin,ou=groups,dc=example,dc=com"],
            attributes={"uid": "jdoe", "mail": "jdoe@example.com"},
            is_active=True,
        )
        assert user.username == "jdoe"
        assert user.email == "jdoe@example.com"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.display_name == "John Doe"
        assert len(user.groups) == 1
        assert "uid" in user.attributes


class TestLDAPGroup:
    """Test LDAPGroup dataclass"""

    def test_group_creation_minimal(self):
        """Test creating group with minimal fields"""
        group = LDAPGroup(dn="cn=admin,ou=groups,dc=example,dc=com", name="admin")
        assert group.dn == "cn=admin,ou=groups,dc=example,dc=com"
        assert group.name == "admin"
        assert group.members == []

    def test_group_creation_with_members(self):
        """Test creating group with members"""
        group = LDAPGroup(
            dn="cn=admin,ou=groups,dc=example,dc=com",
            name="admin",
            members=["uid=jdoe,ou=users,dc=example,dc=com"],
            attributes={"cn": "admin"},
        )
        assert len(group.members) == 1
        assert "cn" in group.attributes


class TestLDAPConnection:
    """Test LDAPConnection class"""

    def test_connection_initialization(self):
        """Test connection initialization"""
        config = LDAPConfig(host="ldap.example.com")
        conn = LDAPConnection(config)
        assert conn.config == config
        assert conn._connection is None
        assert conn._bound is False

    def test_connect_ldap(self):
        """Test connecting to LDAP server"""
        config = LDAPConfig(host="ldap.example.com")
        conn = LDAPConnection(config)
        conn.connect()
        assert conn._connection is not None
        assert conn._connection["url"] == "ldap://ldap.example.com:389"
        assert conn._connection["connected"] is True

    def test_connect_ldaps(self):
        """Test connecting to LDAPS server"""
        config = LDAPConfig(host="ldap.example.com", port=636, use_ssl=True)
        conn = LDAPConnection(config)
        conn.connect()
        assert conn._connection["url"] == "ldaps://ldap.example.com:636"

    def test_bind_with_credentials(self):
        """Test binding with credentials"""
        config = LDAPConfig(
            host="ldap.example.com",
            bind_dn="cn=admin,dc=example,dc=com",
            bind_password="secret",
        )
        conn = LDAPConnection(config)
        conn.bind()
        assert conn._bound is True
        assert conn._connection is not None

    def test_bind_anonymous(self):
        """Test anonymous bind"""
        config = LDAPConfig(host="ldap.example.com")
        conn = LDAPConnection(config)
        conn.bind()
        assert conn._bound is True

    def test_unbind(self):
        """Test unbinding"""
        config = LDAPConfig(host="ldap.example.com")
        conn = LDAPConnection(config)
        conn.bind()
        conn.unbind()
        assert conn._bound is False

    def test_close(self):
        """Test closing connection"""
        config = LDAPConfig(host="ldap.example.com")
        conn = LDAPConnection(config)
        conn.bind()
        conn.close()
        assert conn._bound is False
        assert conn._connection is None

    def test_is_connected(self):
        """Test checking connection status"""
        config = LDAPConfig(host="ldap.example.com")
        conn = LDAPConnection(config)
        assert conn.is_connected() is False
        conn.bind()
        assert conn.is_connected() is True

    def test_search_basic(self):
        """Test basic search"""
        config = LDAPConfig(host="ldap.example.com", base_dn="dc=example,dc=com")
        conn = LDAPConnection(config)
        results = conn.search(
            search_base="dc=example,dc=com",
            search_filter="(uid=jdoe)",
        )
        assert isinstance(results, list)

    def test_search_with_attributes(self):
        """Test search with specific attributes"""
        config = LDAPConfig(host="ldap.example.com")
        conn = LDAPConnection(config)
        results = conn.search(
            search_base="dc=example,dc=com",
            search_filter="(uid=jdoe)",
            attributes=["uid", "mail", "cn"],
        )
        assert isinstance(results, list)

    def test_search_with_scope(self):
        """Test search with different scope"""
        config = LDAPConfig(host="ldap.example.com")
        conn = LDAPConnection(config)
        results = conn.search(
            search_base="dc=example,dc=com",
            search_filter="(uid=jdoe)",
            scope=LDAPScope.ONE_LEVEL,
        )
        assert isinstance(results, list)


class TestLDAPAuthenticator:
    """Test LDAPAuthenticator class"""

    def setup_method(self):
        """Setup test fixtures"""
        self.config = LDAPConfig(
            host="ldap.example.com",
            base_dn="dc=example,dc=com",
            bind_dn="cn=admin,dc=example,dc=com",
            bind_password="secret",
        )
        self.authenticator = LDAPAuthenticator(self.config)

    def test_authenticator_initialization(self):
        """Test authenticator initialization"""
        assert self.authenticator.config == self.config
        assert isinstance(self.authenticator.user_mapping, UserMapping)
        assert isinstance(self.authenticator.group_mapping, GroupMapping)
        assert self.authenticator._connection_pool == []

    def test_authenticator_with_custom_mappings(self):
        """Test authenticator with custom mappings"""
        user_mapping = UserMapping(username_attr="sAMAccountName")
        group_mapping = GroupMapping(object_class="group")
        auth = LDAPAuthenticator(self.config, user_mapping, group_mapping)
        assert auth.user_mapping.username_attr == "sAMAccountName"
        assert auth.group_mapping.object_class == "group"

    def test_get_connection_creates_new(self):
        """Test getting connection creates new one"""
        conn = self.authenticator.get_connection()
        assert isinstance(conn, LDAPConnection)
        assert conn.config == self.config

    def test_return_connection_to_pool(self):
        """Test returning connection to pool"""
        conn = self.authenticator.get_connection()
        self.authenticator.return_connection(conn)
        assert len(self.authenticator._connection_pool) == 1

    def test_return_connection_pool_full(self):
        """Test returning connection when pool is full"""
        # Fill pool
        for _ in range(self.config.connection_pool_size):
            conn = LDAPConnection(self.config)
            self.authenticator._connection_pool.append(conn)

        # Try to return one more
        extra_conn = LDAPConnection(self.config)
        extra_conn.connect()
        self.authenticator.return_connection(extra_conn)

        # Pool should still be at max size
        assert len(self.authenticator._connection_pool) == self.config.connection_pool_size

    def test_get_connection_from_pool(self):
        """Test getting connection from pool"""
        conn1 = LDAPConnection(self.config)
        self.authenticator._connection_pool.append(conn1)

        conn2 = self.authenticator.get_connection()
        assert conn2 == conn1
        assert len(self.authenticator._connection_pool) == 0

    def test_authenticate_success(self):
        """Test successful authentication"""
        # Mock _find_user_dn to return a DN
        self.authenticator._find_user_dn = Mock(return_value="uid=jdoe,ou=users,dc=example,dc=com")

        # Authentication will succeed because bind() always succeeds in placeholder
        result = self.authenticator.authenticate("jdoe", "password123")
        assert result is True

    def test_authenticate_user_not_found(self):
        """Test authentication when user not found"""
        # Mock _find_user_dn to return None
        self.authenticator._find_user_dn = Mock(return_value=None)

        result = self.authenticator.authenticate("jdoe", "password123")
        assert result is False

    def test_find_user_dn(self):
        """Test finding user DN"""
        # Mock connection search
        mock_conn = Mock()
        mock_conn.search.return_value = [{"dn": "uid=jdoe,ou=users,dc=example,dc=com"}]

        self.authenticator.get_connection = Mock(return_value=mock_conn)
        self.authenticator.return_connection = Mock()

        dn = self.authenticator._find_user_dn("jdoe")
        assert dn == "uid=jdoe,ou=users,dc=example,dc=com"
        mock_conn.bind.assert_called_once()
        mock_conn.search.assert_called_once()

    def test_find_user_dn_not_found(self):
        """Test finding user DN when not found"""
        mock_conn = Mock()
        mock_conn.search.return_value = []

        self.authenticator.get_connection = Mock(return_value=mock_conn)
        self.authenticator.return_connection = Mock()

        dn = self.authenticator._find_user_dn("jdoe")
        assert dn is None

    def test_get_user_success(self):
        """Test getting user information"""
        mock_conn = Mock()
        mock_conn.search.return_value = [
            {
                "dn": "uid=jdoe,ou=users,dc=example,dc=com",
                "uid": "jdoe",
                "mail": "jdoe@example.com",
                "givenName": "John",
                "sn": "Doe",
                "displayName": "John Doe",
                "memberOf": ["cn=admin,ou=groups,dc=example,dc=com"],
            }
        ]

        self.authenticator.get_connection = Mock(return_value=mock_conn)
        self.authenticator.return_connection = Mock()

        user = self.authenticator.get_user("jdoe")
        assert user is not None
        assert user.username == "jdoe"
        assert user.email == "jdoe@example.com"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.display_name == "John Doe"
        assert len(user.groups) == 1

    def test_get_user_not_found(self):
        """Test getting user when not found"""
        mock_conn = Mock()
        mock_conn.search.return_value = []

        self.authenticator.get_connection = Mock(return_value=mock_conn)
        self.authenticator.return_connection = Mock()

        user = self.authenticator.get_user("jdoe")
        assert user is None

    def test_search_users_basic(self):
        """Test searching for users"""
        mock_conn = Mock()
        mock_conn.search.return_value = [
            {
                "dn": "uid=jdoe,ou=users,dc=example,dc=com",
                "uid": "jdoe",
                "mail": "jdoe@example.com",
            },
            {
                "dn": "uid=asmith,ou=users,dc=example,dc=com",
                "uid": "asmith",
                "mail": "asmith@example.com",
            },
        ]

        self.authenticator.get_connection = Mock(return_value=mock_conn)
        self.authenticator.return_connection = Mock()

        users = self.authenticator.search_users()
        assert len(users) == 2
        assert users[0].username == "jdoe"
        assert users[1].username == "asmith"

    def test_search_users_with_filter(self):
        """Test searching users with custom filter"""
        mock_conn = Mock()
        mock_conn.search.return_value = []

        self.authenticator.get_connection = Mock(return_value=mock_conn)
        self.authenticator.return_connection = Mock()

        self.authenticator.search_users(search_filter="(mail=*@example.com)")

        # Verify combined filter was used
        call_args = mock_conn.search.call_args
        assert "(mail=*@example.com)" in call_args[1]["search_filter"]

    def test_search_users_max_results(self):
        """Test searching users with max results limit"""
        # Create 150 mock users
        mock_results = [
            {"dn": f"uid=user{i},ou=users,dc=example,dc=com", "uid": f"user{i}"} for i in range(150)
        ]

        mock_conn = Mock()
        mock_conn.search.return_value = mock_results

        self.authenticator.get_connection = Mock(return_value=mock_conn)
        self.authenticator.return_connection = Mock()

        users = self.authenticator.search_users(max_results=50)
        assert len(users) == 50

    def test_get_group_success(self):
        """Test getting group information"""
        mock_conn = Mock()
        mock_conn.search.return_value = [
            {
                "dn": "cn=admin,ou=groups,dc=example,dc=com",
                "cn": "admin",
                "member": ["uid=jdoe,ou=users,dc=example,dc=com"],
            }
        ]

        self.authenticator.get_connection = Mock(return_value=mock_conn)
        self.authenticator.return_connection = Mock()

        group = self.authenticator.get_group("admin")
        assert group is not None
        assert group.name == "admin"
        assert len(group.members) == 1

    def test_get_group_not_found(self):
        """Test getting group when not found"""
        mock_conn = Mock()
        mock_conn.search.return_value = []

        self.authenticator.get_connection = Mock(return_value=mock_conn)
        self.authenticator.return_connection = Mock()

        group = self.authenticator.get_group("admin")
        assert group is None

    def test_get_user_groups(self):
        """Test getting user's groups"""
        # Mock get_user to return user with groups
        mock_user = LDAPUser(
            dn="uid=jdoe,ou=users,dc=example,dc=com",
            username="jdoe",
            groups=[
                "CN=Admin,OU=Groups,DC=example,DC=com",
                "CN=Users,OU=Groups,DC=example,DC=com",
            ],
        )
        self.authenticator.get_user = Mock(return_value=mock_user)

        groups = self.authenticator.get_user_groups("jdoe")
        assert len(groups) == 2
        assert "Admin" in groups
        assert "Users" in groups

    def test_get_user_groups_user_not_found(self):
        """Test getting groups for non-existent user"""
        self.authenticator.get_user = Mock(return_value=None)

        groups = self.authenticator.get_user_groups("jdoe")
        assert groups == []

    def test_is_user_in_group(self):
        """Test checking if user is in group"""
        self.authenticator.get_user_groups = Mock(return_value=["Admin", "Users"])

        assert self.authenticator.is_user_in_group("jdoe", "Admin") is True
        assert self.authenticator.is_user_in_group("jdoe", "Guests") is False


class TestActiveDirectoryAuthenticator:
    """Test ActiveDirectoryAuthenticator class"""

    def setup_method(self):
        """Setup test fixtures"""
        self.config = ADConfig(
            host="ad.example.com",
            base_dn="dc=example,dc=com",
            domain="example.com",
        )
        self.authenticator = ActiveDirectoryAuthenticator(self.config)

    def test_ad_authenticator_initialization(self):
        """Test AD authenticator initialization with default mappings"""
        assert isinstance(self.authenticator, ActiveDirectoryAuthenticator)
        assert self.authenticator.user_mapping.username_attr == "sAMAccountName"
        assert self.authenticator.user_mapping.user_filter == "(&(objectClass=user)(objectCategory=person))"
        assert self.authenticator.group_mapping.object_class == "group"

    def test_ad_authenticator_custom_mappings(self):
        """Test AD authenticator with custom mappings"""
        user_mapping = UserMapping(username_attr="userPrincipalName")
        group_mapping = GroupMapping(name_attr="name")

        auth = ActiveDirectoryAuthenticator(self.config, user_mapping, group_mapping)
        assert auth.user_mapping.username_attr == "userPrincipalName"
        assert auth.group_mapping.name_attr == "name"

    def test_authenticate_with_domain(self):
        """Test authentication with domain appended"""
        # Mock parent authenticate
        with patch.object(LDAPAuthenticator, "authenticate", return_value=True) as mock_auth:
            result = self.authenticator.authenticate("jdoe", "password123")

            assert result is True
            # Verify domain was appended
            mock_auth.assert_called_once_with("jdoe@example.com", "password123")

    def test_authenticate_username_already_has_domain(self):
        """Test authentication when username already has domain"""
        with patch.object(LDAPAuthenticator, "authenticate", return_value=True) as mock_auth:
            result = self.authenticator.authenticate("jdoe@otherdomain.com", "password123")

            assert result is True
            # Should not append domain if already present
            mock_auth.assert_called_once_with("jdoe@otherdomain.com", "password123")

    def test_authenticate_no_domain_configured(self):
        """Test authentication when no domain configured"""
        config = ADConfig(host="ad.example.com", domain="")
        auth = ActiveDirectoryAuthenticator(config)

        with patch.object(LDAPAuthenticator, "authenticate", return_value=True) as mock_auth:
            auth.authenticate("jdoe", "password123")

            # Should not append domain if not configured
            mock_auth.assert_called_once_with("jdoe", "password123")

    def test_check_password_policy(self):
        """Test checking password policy"""
        mock_user = LDAPUser(
            dn="cn=jdoe,ou=users,dc=example,dc=com",
            username="jdoe",
            attributes={
                "pwdLastSet": 132456789000000000,
                "userAccountControl": 512,  # Normal account
                "lockoutTime": 0,
            },
        )

        self.authenticator.get_user = Mock(return_value=mock_user)

        policy = self.authenticator.check_password_policy("jdoe")
        assert policy["password_expired"] is False
        assert policy["password_never_expires"] is False
        assert policy["account_disabled"] is False
        assert policy["account_locked"] is False

    def test_check_password_policy_expired(self):
        """Test password policy for expired password"""
        mock_user = LDAPUser(
            dn="cn=jdoe,ou=users,dc=example,dc=com",
            username="jdoe",
            attributes={
                "pwdLastSet": 0,  # Password expired
                "userAccountControl": 512,
            },
        )

        self.authenticator.get_user = Mock(return_value=mock_user)

        policy = self.authenticator.check_password_policy("jdoe")
        assert policy["password_expired"] is True
        assert policy["must_change_password"] is True

    def test_check_password_policy_never_expires(self):
        """Test password policy for password that never expires"""
        mock_user = LDAPUser(
            dn="cn=jdoe,ou=users,dc=example,dc=com",
            username="jdoe",
            attributes={
                "pwdLastSet": 132456789000000000,
                "userAccountControl": 0x10000 | 512,  # DONT_EXPIRE_PASSWORD flag
            },
        )

        self.authenticator.get_user = Mock(return_value=mock_user)

        policy = self.authenticator.check_password_policy("jdoe")
        assert policy["password_never_expires"] is True

    def test_check_password_policy_account_disabled(self):
        """Test password policy for disabled account"""
        mock_user = LDAPUser(
            dn="cn=jdoe,ou=users,dc=example,dc=com",
            username="jdoe",
            attributes={
                "pwdLastSet": 132456789000000000,
                "userAccountControl": 0x2,  # ACCOUNTDISABLE flag
            },
        )

        self.authenticator.get_user = Mock(return_value=mock_user)

        policy = self.authenticator.check_password_policy("jdoe")
        assert policy["account_disabled"] is True

    def test_check_password_policy_account_locked(self):
        """Test password policy for locked account"""
        mock_user = LDAPUser(
            dn="cn=jdoe,ou=users,dc=example,dc=com",
            username="jdoe",
            attributes={
                "pwdLastSet": 132456789000000000,
                "userAccountControl": 512,
                "lockoutTime": 132456789000000000,  # Non-zero = locked
            },
        )

        self.authenticator.get_user = Mock(return_value=mock_user)

        policy = self.authenticator.check_password_policy("jdoe")
        assert policy["account_locked"] is True

    def test_check_password_policy_user_not_found(self):
        """Test password policy when user not found"""
        self.authenticator.get_user = Mock(return_value=None)

        policy = self.authenticator.check_password_policy("jdoe")
        assert policy == {}


class TestGlobalFunctions:
    """Test global functions"""

    def setup_method(self):
        """Reset global state"""
        import src.core.sso.ldap as ldap_module

        ldap_module._ldap_authenticator = None

    def teardown_method(self):
        """Clean up global state"""
        import src.core.sso.ldap as ldap_module

        ldap_module._ldap_authenticator = None

    def test_get_ldap_authenticator_not_configured(self):
        """Test getting authenticator when not configured"""
        try:
            get_ldap_authenticator()
            assert False, "Should raise ValueError"
        except ValueError as e:
            assert "not configured" in str(e)

    def test_configure_ldap_authenticator(self):
        """Test configuring LDAP authenticator"""
        config = LDAPConfig(host="ldap.example.com")
        configure_ldap_authenticator(config)

        auth = get_ldap_authenticator()
        assert isinstance(auth, LDAPAuthenticator)
        assert auth.config == config

    def test_configure_ldap_authenticator_singleton(self):
        """Test authenticator is singleton"""
        config = LDAPConfig(host="ldap.example.com")
        configure_ldap_authenticator(config)

        auth1 = get_ldap_authenticator()
        auth2 = get_ldap_authenticator()
        assert auth1 is auth2

    def test_configure_ldap_authenticator_with_mappings(self):
        """Test configuring with custom mappings"""
        config = LDAPConfig(host="ldap.example.com")
        user_mapping = UserMapping(username_attr="sAMAccountName")
        group_mapping = GroupMapping(object_class="group")

        configure_ldap_authenticator(config, user_mapping, group_mapping)

        auth = get_ldap_authenticator()
        assert auth.user_mapping.username_attr == "sAMAccountName"
        assert auth.group_mapping.object_class == "group"

    def test_configure_ad_authenticator(self):
        """Test configuring Active Directory authenticator"""
        config = ADConfig(host="ad.example.com", domain="example.com")
        configure_ldap_authenticator(config, use_ad=True)

        auth = get_ldap_authenticator()
        assert isinstance(auth, ActiveDirectoryAuthenticator)

    def test_configure_ldap_replaces_instance(self):
        """Test configuring replaces existing instance"""
        config1 = LDAPConfig(host="ldap1.example.com")
        configure_ldap_authenticator(config1)
        auth1 = get_ldap_authenticator()

        config2 = LDAPConfig(host="ldap2.example.com")
        configure_ldap_authenticator(config2)
        auth2 = get_ldap_authenticator()

        assert auth1 is not auth2
        assert auth2.config.host == "ldap2.example.com"
