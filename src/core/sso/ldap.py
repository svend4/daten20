"""
LDAP / Active Directory Authentication

Provides LDAP and Active Directory authentication integration.
"""

from typing import Optional, Dict, Any, List, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import re


class LDAPAuthMethod(str, Enum):
    """LDAP authentication methods"""
    SIMPLE = "simple"
    SASL = "sasl"
    ANONYMOUS = "anonymous"


class LDAPScope(str, Enum):
    """LDAP search scope"""
    BASE = "base"
    ONE_LEVEL = "onelevel"
    SUBTREE = "subtree"


@dataclass
class LDAPConfig:
    """LDAP connection configuration"""
    host: str
    port: int = 389
    use_ssl: bool = False
    use_tls: bool = False
    base_dn: str = ""
    bind_dn: Optional[str] = None
    bind_password: Optional[str] = None
    auth_method: LDAPAuthMethod = LDAPAuthMethod.SIMPLE
    timeout: int = 10
    connection_pool_size: int = 10
    connection_pool_lifetime: int = 3600  # seconds


@dataclass
class ADConfig(LDAPConfig):
    """Active Directory specific configuration"""
    domain: str = ""
    use_paging: bool = True
    page_size: int = 1000
    follow_referrals: bool = True


@dataclass
class UserMapping:
    """User attribute mapping configuration"""
    username_attr: str = "uid"
    email_attr: str = "mail"
    first_name_attr: str = "givenName"
    last_name_attr: str = "sn"
    display_name_attr: str = "displayName"
    group_attr: str = "memberOf"
    object_class: str = "inetOrgPerson"
    user_filter: str = "(objectClass=inetOrgPerson)"


@dataclass
class GroupMapping:
    """Group attribute mapping configuration"""
    name_attr: str = "cn"
    member_attr: str = "member"
    object_class: str = "groupOfNames"
    group_filter: str = "(objectClass=groupOfNames)"


@dataclass
class LDAPUser:
    """LDAP user object"""
    dn: str
    username: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    groups: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True


@dataclass
class LDAPGroup:
    """LDAP group object"""
    dn: str
    name: str
    members: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)


class LDAPConnection:
    """LDAP connection wrapper"""

    def __init__(self, config: LDAPConfig):
        self.config = config
        self._connection = None
        self._bound = False

    def connect(self):
        """Establish LDAP connection"""
        try:
            # In production, use python-ldap or ldap3 library
            # For now, this is a placeholder implementation
            protocol = "ldaps" if self.config.use_ssl else "ldap"
            url = f"{protocol}://{self.config.host}:{self.config.port}"

            # Placeholder for actual LDAP connection
            # self._connection = ldap3.Connection(...)
            self._connection = {"url": url, "connected": True}

        except Exception as e:
            raise ConnectionError(f"Failed to connect to LDAP server: {e}")

    def bind(self):
        """Bind to LDAP server"""
        if not self._connection:
            self.connect()

        try:
            if self.config.bind_dn and self.config.bind_password:
                # Placeholder for actual bind
                # self._connection.bind()
                self._bound = True
            else:
                # Anonymous bind
                self._bound = True

        except Exception as e:
            raise ValueError(f"Failed to bind to LDAP server: {e}")

    def unbind(self):
        """Unbind from LDAP server"""
        if self._connection:
            # Placeholder for actual unbind
            # self._connection.unbind()
            self._bound = False

    def close(self):
        """Close LDAP connection"""
        self.unbind()
        self._connection = None

    def is_connected(self) -> bool:
        """Check if connected to LDAP server"""
        return self._connection is not None and self._bound

    def search(
        self,
        search_base: str,
        search_filter: str,
        attributes: Optional[List[str]] = None,
        scope: LDAPScope = LDAPScope.SUBTREE
    ) -> List[Dict[str, Any]]:
        """
        Search LDAP directory

        Args:
            search_base: Base DN for search
            search_filter: LDAP search filter
            attributes: List of attributes to retrieve
            scope: Search scope

        Returns:
            List of search results
        """
        if not self.is_connected():
            self.bind()

        try:
            # Placeholder for actual search
            # results = self._connection.search(
            #     search_base=search_base,
            #     search_filter=search_filter,
            #     attributes=attributes,
            #     search_scope=scope
            # )
            results = []

            return results

        except Exception as e:
            raise ValueError(f"LDAP search failed: {e}")


class LDAPAuthenticator:
    """LDAP authentication service"""

    def __init__(
        self,
        config: LDAPConfig,
        user_mapping: Optional[UserMapping] = None,
        group_mapping: Optional[GroupMapping] = None
    ):
        self.config = config
        self.user_mapping = user_mapping or UserMapping()
        self.group_mapping = group_mapping or GroupMapping()
        self._connection_pool: List[LDAPConnection] = []

    def get_connection(self) -> LDAPConnection:
        """Get connection from pool or create new one"""
        # Simple implementation - in production use proper connection pooling
        if self._connection_pool:
            return self._connection_pool.pop()

        conn = LDAPConnection(self.config)
        return conn

    def return_connection(self, conn: LDAPConnection):
        """Return connection to pool"""
        if len(self._connection_pool) < self.config.connection_pool_size:
            self._connection_pool.append(conn)
        else:
            conn.close()

    def authenticate(self, username: str, password: str) -> bool:
        """
        Authenticate user against LDAP

        Args:
            username: Username
            password: Password

        Returns:
            True if authentication successful
        """
        try:
            # Find user DN
            user_dn = self._find_user_dn(username)
            if not user_dn:
                return False

            # Try to bind with user credentials
            conn = LDAPConnection(self.config)

            # Create temporary config with user credentials
            temp_config = LDAPConfig(
                host=self.config.host,
                port=self.config.port,
                use_ssl=self.config.use_ssl,
                use_tls=self.config.use_tls,
                bind_dn=user_dn,
                bind_password=password
            )

            temp_conn = LDAPConnection(temp_config)
            try:
                temp_conn.bind()
                return temp_conn.is_connected()
            finally:
                temp_conn.close()

        except Exception:
            return False

    def _find_user_dn(self, username: str) -> Optional[str]:
        """Find user DN by username"""
        conn = self.get_connection()
        try:
            conn.bind()

            # Build search filter
            search_filter = f"(&{self.user_mapping.user_filter}({self.user_mapping.username_attr}={username}))"

            results = conn.search(
                search_base=self.config.base_dn,
                search_filter=search_filter,
                attributes=["dn"],
                scope=LDAPScope.SUBTREE
            )

            if results:
                return results[0].get("dn")

            return None

        finally:
            self.return_connection(conn)

    def get_user(self, username: str) -> Optional[LDAPUser]:
        """
        Get user information from LDAP

        Args:
            username: Username

        Returns:
            LDAP user object or None if not found
        """
        conn = self.get_connection()
        try:
            conn.bind()

            # Build search filter
            search_filter = f"(&{self.user_mapping.user_filter}({self.user_mapping.username_attr}={username}))"

            # Attributes to retrieve
            attributes = [
                self.user_mapping.username_attr,
                self.user_mapping.email_attr,
                self.user_mapping.first_name_attr,
                self.user_mapping.last_name_attr,
                self.user_mapping.display_name_attr,
                self.user_mapping.group_attr,
            ]

            results = conn.search(
                search_base=self.config.base_dn,
                search_filter=search_filter,
                attributes=attributes,
                scope=LDAPScope.SUBTREE
            )

            if not results:
                return None

            entry = results[0]

            return LDAPUser(
                dn=entry.get("dn", ""),
                username=entry.get(self.user_mapping.username_attr, username),
                email=entry.get(self.user_mapping.email_attr),
                first_name=entry.get(self.user_mapping.first_name_attr),
                last_name=entry.get(self.user_mapping.last_name_attr),
                display_name=entry.get(self.user_mapping.display_name_attr),
                groups=entry.get(self.user_mapping.group_attr, []),
                attributes=entry
            )

        finally:
            self.return_connection(conn)

    def search_users(
        self,
        search_filter: Optional[str] = None,
        max_results: int = 100
    ) -> List[LDAPUser]:
        """
        Search for users in LDAP

        Args:
            search_filter: Additional search filter (combined with user filter)
            max_results: Maximum number of results

        Returns:
            List of LDAP users
        """
        conn = self.get_connection()
        try:
            conn.bind()

            # Build combined filter
            if search_filter:
                combined_filter = f"(&{self.user_mapping.user_filter}{search_filter})"
            else:
                combined_filter = self.user_mapping.user_filter

            attributes = [
                self.user_mapping.username_attr,
                self.user_mapping.email_attr,
                self.user_mapping.first_name_attr,
                self.user_mapping.last_name_attr,
                self.user_mapping.display_name_attr,
                self.user_mapping.group_attr,
            ]

            results = conn.search(
                search_base=self.config.base_dn,
                search_filter=combined_filter,
                attributes=attributes,
                scope=LDAPScope.SUBTREE
            )

            users = []
            for entry in results[:max_results]:
                user = LDAPUser(
                    dn=entry.get("dn", ""),
                    username=entry.get(self.user_mapping.username_attr, ""),
                    email=entry.get(self.user_mapping.email_attr),
                    first_name=entry.get(self.user_mapping.first_name_attr),
                    last_name=entry.get(self.user_mapping.last_name_attr),
                    display_name=entry.get(self.user_mapping.display_name_attr),
                    groups=entry.get(self.user_mapping.group_attr, []),
                    attributes=entry
                )
                users.append(user)

            return users

        finally:
            self.return_connection(conn)

    def get_group(self, group_name: str) -> Optional[LDAPGroup]:
        """
        Get group information from LDAP

        Args:
            group_name: Group name

        Returns:
            LDAP group object or None if not found
        """
        conn = self.get_connection()
        try:
            conn.bind()

            # Build search filter
            search_filter = f"(&{self.group_mapping.group_filter}({self.group_mapping.name_attr}={group_name}))"

            attributes = [
                self.group_mapping.name_attr,
                self.group_mapping.member_attr,
            ]

            results = conn.search(
                search_base=self.config.base_dn,
                search_filter=search_filter,
                attributes=attributes,
                scope=LDAPScope.SUBTREE
            )

            if not results:
                return None

            entry = results[0]

            return LDAPGroup(
                dn=entry.get("dn", ""),
                name=entry.get(self.group_mapping.name_attr, group_name),
                members=entry.get(self.group_mapping.member_attr, []),
                attributes=entry
            )

        finally:
            self.return_connection(conn)

    def get_user_groups(self, username: str) -> List[str]:
        """
        Get list of groups for a user

        Args:
            username: Username

        Returns:
            List of group names
        """
        user = self.get_user(username)
        if not user:
            return []

        # Extract group names from DNs
        group_names = []
        for group_dn in user.groups:
            # Parse CN from DN (e.g., "CN=Admin,OU=Groups,DC=example,DC=com" -> "Admin")
            match = re.search(r'CN=([^,]+)', group_dn)
            if match:
                group_names.append(match.group(1))

        return group_names

    def is_user_in_group(self, username: str, group_name: str) -> bool:
        """
        Check if user is member of group

        Args:
            username: Username
            group_name: Group name

        Returns:
            True if user is in group
        """
        user_groups = self.get_user_groups(username)
        return group_name in user_groups


class ActiveDirectoryAuthenticator(LDAPAuthenticator):
    """Active Directory specific authenticator"""

    def __init__(
        self,
        config: ADConfig,
        user_mapping: Optional[UserMapping] = None,
        group_mapping: Optional[GroupMapping] = None
    ):
        # AD specific defaults
        if user_mapping is None:
            user_mapping = UserMapping(
                username_attr="sAMAccountName",
                email_attr="mail",
                first_name_attr="givenName",
                last_name_attr="sn",
                display_name_attr="displayName",
                group_attr="memberOf",
                object_class="user",
                user_filter="(&(objectClass=user)(objectCategory=person))"
            )

        if group_mapping is None:
            group_mapping = GroupMapping(
                name_attr="cn",
                member_attr="member",
                object_class="group",
                group_filter="(objectClass=group)"
            )

        super().__init__(config, user_mapping, group_mapping)
        self.ad_config = config

    def authenticate(self, username: str, password: str) -> bool:
        """
        Authenticate against Active Directory

        Supports both username and username@domain formats
        """
        # If domain is configured and username doesn't contain @, add domain
        if self.ad_config.domain and '@' not in username:
            username_with_domain = f"{username}@{self.ad_config.domain}"
        else:
            username_with_domain = username

        return super().authenticate(username_with_domain, password)

    def check_password_policy(self, username: str) -> Dict[str, Any]:
        """
        Check password policy status for user

        Returns:
            Dictionary with password policy information
        """
        user = self.get_user(username)
        if not user:
            return {}

        # AD specific attributes
        attrs = user.attributes

        return {
            "password_expired": attrs.get("pwdLastSet", 0) == 0,
            "password_never_expires": bool(attrs.get("userAccountControl", 0) & 0x10000),
            "account_disabled": bool(attrs.get("userAccountControl", 0) & 0x2),
            "account_locked": bool(attrs.get("lockoutTime", 0) > 0),
            "must_change_password": attrs.get("pwdLastSet", 0) == 0,
        }


# Global LDAP authenticator instance
_ldap_authenticator: Optional[LDAPAuthenticator] = None


def get_ldap_authenticator() -> LDAPAuthenticator:
    """Get global LDAP authenticator instance"""
    global _ldap_authenticator
    if _ldap_authenticator is None:
        raise ValueError("LDAP authenticator not configured. Call configure_ldap_authenticator first.")
    return _ldap_authenticator


def configure_ldap_authenticator(
    config: LDAPConfig,
    user_mapping: Optional[UserMapping] = None,
    group_mapping: Optional[GroupMapping] = None,
    use_ad: bool = False
):
    """
    Configure global LDAP authenticator

    Args:
        config: LDAP configuration
        user_mapping: User attribute mapping
        group_mapping: Group attribute mapping
        use_ad: Use Active Directory specific features
    """
    global _ldap_authenticator

    if use_ad and isinstance(config, ADConfig):
        _ldap_authenticator = ActiveDirectoryAuthenticator(
            config,
            user_mapping,
            group_mapping
        )
    else:
        _ldap_authenticator = LDAPAuthenticator(
            config,
            user_mapping,
            group_mapping
        )
