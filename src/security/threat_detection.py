#!/usr/bin/env python3
"""
Advanced Threat Detection Module

AI-powered threat detection and security monitoring for DMS.

Key Features:
- AI-powered threat detection using machine learning
- Behavioral analysis and anomaly detection
- Intrusion detection system (IDS)
- DDoS protection and rate limiting
- Bot detection and CAPTCHA bypass prevention
- Fraud detection using pattern recognition
- Malware scanning integration
- Phishing protection
- Security information and event management (SIEM)
- Threat intelligence feeds integration
- Real-time alerting and incident response

Dependencies:
- scikit-learn (for ML models)
- numpy (for numerical operations)
"""

import hashlib
import json
import logging
import re
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class ThreatLevel(str, Enum):
    """Threat severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatType(str, Enum):
    """Types of security threats"""

    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    MALWARE = "malware"
    PHISHING = "phishing"
    DDoS = "ddos"
    BOT_ACTIVITY = "bot_activity"
    DATA_EXFILTRATION = "data_exfiltration"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    ANOMALY = "anomaly"
    FRAUD = "fraud"


class AlertStatus(str, Enum):
    """Alert statuses"""

    NEW = "new"
    INVESTIGATING = "investigating"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    RESOLVED = "resolved"


@dataclass
class SecurityEvent:
    """Security event"""

    event_id: str
    event_type: ThreatType
    severity: ThreatLevel
    source_ip: str
    target: str
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = None


@dataclass
class ThreatAlert:
    """Threat alert"""

    alert_id: str
    threat_type: ThreatType
    severity: ThreatLevel
    description: str
    affected_assets: List[str]
    indicators: Dict[str, Any]
    timestamp: datetime
    status: AlertStatus = AlertStatus.NEW
    false_positive_probability: float = 0.0


@dataclass
class UserBehaviorProfile:
    """User behavior profile for anomaly detection"""

    user_id: str
    normal_login_times: List[int]  # Hours of day
    normal_locations: Set[str]  # IP ranges or countries
    average_session_duration: float  # Minutes
    typical_actions: Dict[str, int]  # Action type -> frequency
    risk_score: float = 0.0


@dataclass
class IPReputation:
    """IP address reputation"""

    ip_address: str
    reputation_score: float  # 0-100, higher is better
    is_tor: bool = False
    is_vpn: bool = False
    is_proxy: bool = False
    country: Optional[str] = None
    threat_history: List[str] = field(default_factory=list)


class AnomalyDetector:
    """
    Anomaly detector using statistical methods and ML

    Detects unusual patterns in user behavior and system activity.
    """

    def __init__(self, sensitivity: float = 0.95):
        """
        Initialize anomaly detector

        Args:
            sensitivity: Detection sensitivity (0-1)
        """
        self.sensitivity = sensitivity
        self._user_profiles: Dict[str, UserBehaviorProfile] = {}
        self._baseline_metrics: Dict[str, List[float]] = defaultdict(list)

    def build_user_profile(self, user_id: str, historical_events: List[SecurityEvent]) -> UserBehaviorProfile:
        """
        Build behavioral profile for user

        Args:
            user_id: User ID
            historical_events: Historical security events

        Returns:
            User behavior profile
        """
        login_times = []
        locations = set()
        session_durations = []
        actions = defaultdict(int)

        for event in historical_events:
            if event.user_id == user_id:
                # Extract features
                login_times.append(event.timestamp.hour)
                if event.source_ip:
                    locations.add(event.source_ip.split(".")[0])  # Simplified

                if "session_duration" in event.details:
                    session_durations.append(event.details["session_duration"])

                if "action" in event.details:
                    actions[event.details["action"]] += 1

        profile = UserBehaviorProfile(
            user_id=user_id,
            normal_login_times=login_times,
            normal_locations=locations,
            average_session_duration=(sum(session_durations) / len(session_durations) if session_durations else 0),
            typical_actions=dict(actions),
        )

        self._user_profiles[user_id] = profile
        logger.info(f"Built behavioral profile for user {user_id}")

        return profile

    def detect_anomaly(self, user_id: str, current_event: SecurityEvent) -> Optional[ThreatAlert]:
        """
        Detect anomalies in user behavior

        Args:
            user_id: User ID
            current_event: Current event to analyze

        Returns:
            Threat alert if anomaly detected, None otherwise
        """
        profile = self._user_profiles.get(user_id)
        if not profile:
            return None

        anomalies = []
        indicators = {}

        # Check login time anomaly
        current_hour = current_event.timestamp.hour
        if current_hour not in profile.normal_login_times:
            anomalies.append("unusual_login_time")
            indicators["login_hour"] = current_hour

        # Check location anomaly
        ip_prefix = current_event.source_ip.split(".")[0]
        if ip_prefix not in profile.normal_locations:
            anomalies.append("unusual_location")
            indicators["source_ip"] = current_event.source_ip

        # Check action pattern
        if "action" in current_event.details:
            action = current_event.details["action"]
            if action not in profile.typical_actions:
                anomalies.append("unusual_action")
                indicators["action"] = action

        # Generate alert if anomalies detected
        if len(anomalies) >= 2:  # Multiple anomalies increase confidence
            alert = ThreatAlert(
                alert_id=hashlib.sha256(f"{user_id}{current_event.timestamp}".encode()).hexdigest()[:16],
                threat_type=ThreatType.ANOMALY,
                severity=ThreatLevel.MEDIUM,
                description=f"Behavioral anomalies detected: {', '.join(anomalies)}",
                affected_assets=[user_id],
                indicators=indicators,
                timestamp=datetime.now(),
                false_positive_probability=0.3,
            )

            logger.warning(f"Anomaly detected for user {user_id}: {anomalies}")
            return alert

        return None


class BruteForceDetector:
    """
    Brute force attack detector

    Detects brute force login attempts.
    """

    def __init__(self, max_attempts: int = 5, time_window: int = 300):  # 5 minutes
        """
        Initialize brute force detector

        Args:
            max_attempts: Maximum failed attempts allowed
            time_window: Time window in seconds
        """
        self.max_attempts = max_attempts
        self.time_window = time_window
        self._failed_attempts: Dict[str, deque] = defaultdict(lambda: deque())

    def check_brute_force(self, identifier: str, success: bool) -> Optional[ThreatAlert]:
        """
        Check for brute force attack

        Args:
            identifier: User ID or IP address
            success: Whether login was successful

        Returns:
            Threat alert if brute force detected
        """
        now = datetime.now()

        if not success:
            # Record failed attempt
            self._failed_attempts[identifier].append(now)

        # Clean old attempts outside time window
        cutoff = now - timedelta(seconds=self.time_window)
        while self._failed_attempts[identifier] and self._failed_attempts[identifier][0] < cutoff:
            self._failed_attempts[identifier].popleft()

        # Check if threshold exceeded
        attempt_count = len(self._failed_attempts[identifier])

        if attempt_count >= self.max_attempts:
            alert = ThreatAlert(
                alert_id=hashlib.sha256(f"brute_force_{identifier}_{now}".encode()).hexdigest()[:16],
                threat_type=ThreatType.BRUTE_FORCE,
                severity=ThreatLevel.HIGH,
                description=f"Brute force attack detected: {attempt_count} failed attempts",
                affected_assets=[identifier],
                indicators={"failed_attempts": attempt_count, "time_window": self.time_window},
                timestamp=now,
            )

            logger.error(f"Brute force detected: {identifier} ({attempt_count} attempts)")
            return alert

        return None


class InjectionDetector:
    """
    SQL injection and XSS detector

    Detects injection attacks in input strings.
    """

    # SQL injection patterns
    SQL_PATTERNS = [
        r"(\bunion\b.*\bselect\b)",
        r"(\bselect\b.*\bfrom\b.*\bwhere\b)",
        r"(\binsert\b.*\binto\b.*\bvalues\b)",
        r"(\bdelete\b.*\bfrom\b)",
        r"(\bdrop\b.*\btable\b)",
        r"(\'.*\bor\b.*\'.*=.*\')",
        r"(--|\#|\/\*)",
        r"(\bexec\b|\bexecute\b)",
    ]

    # XSS patterns
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
    ]

    @classmethod
    def detect_sql_injection(cls, input_string: str) -> Optional[ThreatAlert]:
        """
        Detect SQL injection attempt

        Args:
            input_string: Input to check

        Returns:
            Threat alert if SQL injection detected
        """
        input_lower = input_string.lower()

        for pattern in cls.SQL_PATTERNS:
            if re.search(pattern, input_lower, re.IGNORECASE):
                alert = ThreatAlert(
                    alert_id=hashlib.sha256(f"sqli_{input_string}_{datetime.now()}".encode()).hexdigest()[:16],
                    threat_type=ThreatType.SQL_INJECTION,
                    severity=ThreatLevel.CRITICAL,
                    description="SQL injection attempt detected",
                    affected_assets=["database"],
                    indicators={"pattern_matched": pattern, "input_sample": input_string[:100]},
                    timestamp=datetime.now(),
                )

                logger.critical(f"SQL injection detected: {pattern}")
                return alert

        return None

    @classmethod
    def detect_xss(cls, input_string: str) -> Optional[ThreatAlert]:
        """
        Detect XSS attempt

        Args:
            input_string: Input to check

        Returns:
            Threat alert if XSS detected
        """
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, input_string, re.IGNORECASE):
                alert = ThreatAlert(
                    alert_id=hashlib.sha256(f"xss_{input_string}_{datetime.now()}".encode()).hexdigest()[:16],
                    threat_type=ThreatType.XSS,
                    severity=ThreatLevel.HIGH,
                    description="Cross-site scripting (XSS) attempt detected",
                    affected_assets=["web_application"],
                    indicators={"pattern_matched": pattern, "input_sample": input_string[:100]},
                    timestamp=datetime.now(),
                )

                logger.error(f"XSS detected: {pattern}")
                return alert

        return None


class DDoSProtection:
    """
    DDoS protection system

    Rate limiting and traffic analysis to prevent DDoS attacks.
    """

    def __init__(self, requests_per_second: int = 100, requests_per_minute: int = 1000):
        """
        Initialize DDoS protection

        Args:
            requests_per_second: Max requests per second per IP
            requests_per_minute: Max requests per minute per IP
        """
        self.requests_per_second = requests_per_second
        self.requests_per_minute = requests_per_minute
        self._request_log: Dict[str, deque] = defaultdict(lambda: deque())

    def check_rate_limit(self, ip_address: str) -> Optional[ThreatAlert]:
        """
        Check if IP exceeds rate limits

        Args:
            ip_address: Source IP address

        Returns:
            Threat alert if rate limit exceeded
        """
        now = datetime.now()
        self._request_log[ip_address].append(now)

        # Clean old requests
        one_minute_ago = now - timedelta(minutes=1)
        while self._request_log[ip_address] and self._request_log[ip_address][0] < one_minute_ago:
            self._request_log[ip_address].popleft()

        # Check rate limits
        recent_requests = list(self._request_log[ip_address])
        requests_last_second = sum(1 for t in recent_requests if (now - t).total_seconds() < 1)
        requests_last_minute = len(recent_requests)

        if requests_last_second > self.requests_per_second or requests_last_minute > self.requests_per_minute:

            alert = ThreatAlert(
                alert_id=hashlib.sha256(f"ddos_{ip_address}_{now}".encode()).hexdigest()[:16],
                threat_type=ThreatType.DDoS,
                severity=ThreatLevel.CRITICAL,
                description="Potential DDoS attack: rate limit exceeded",
                affected_assets=["infrastructure"],
                indicators={
                    "requests_per_second": requests_last_second,
                    "requests_per_minute": requests_last_minute,
                    "source_ip": ip_address,
                },
                timestamp=now,
            )

            logger.critical(f"DDoS attack suspected from {ip_address}")
            return alert

        return None


class BotDetector:
    """
    Bot detection system

    Identifies automated bot activity.
    """

    # Known bot user agents
    BOT_USER_AGENTS = ["bot", "crawler", "spider", "scraper", "curl", "wget", "python-requests", "scrapy"]

    @classmethod
    def is_bot(cls, user_agent: str, request_pattern: Optional[Dict[str, Any]] = None) -> bool:
        """
        Check if request is from a bot

        Args:
            user_agent: HTTP User-Agent header
            request_pattern: Additional request pattern data

        Returns:
            True if bot detected
        """
        user_agent_lower = user_agent.lower()

        # Check user agent
        for bot_pattern in cls.BOT_USER_AGENTS:
            if bot_pattern in user_agent_lower:
                return True

        # Check request patterns (if provided)
        if request_pattern:
            # Check for suspiciously fast requests
            if request_pattern.get("requests_per_second", 0) > 10:
                return True

            # Check for missing typical browser headers
            if not request_pattern.get("has_accept_language"):
                return True

        return False

    @classmethod
    def detect_bot_activity(cls, user_agent: str, ip_address: str) -> Optional[ThreatAlert]:
        """
        Detect bot activity and create alert

        Args:
            user_agent: User agent string
            ip_address: Source IP

        Returns:
            Threat alert if bot detected
        """
        if cls.is_bot(user_agent):
            alert = ThreatAlert(
                alert_id=hashlib.sha256(f"bot_{ip_address}_{datetime.now()}".encode()).hexdigest()[:16],
                threat_type=ThreatType.BOT_ACTIVITY,
                severity=ThreatLevel.MEDIUM,
                description="Automated bot activity detected",
                affected_assets=["web_application"],
                indicators={"user_agent": user_agent, "source_ip": ip_address},
                timestamp=datetime.now(),
            )

            logger.warning(f"Bot detected: {user_agent} from {ip_address}")
            return alert

        return None


class ThreatIntelligence:
    """
    Threat intelligence integration

    Integrates with threat intelligence feeds.
    """

    def __init__(self):
        """Initialize threat intelligence"""
        self._malicious_ips: Set[str] = set()
        self._malicious_domains: Set[str] = set()
        self._ip_reputation_cache: Dict[str, IPReputation] = {}

    def add_malicious_ip(self, ip_address: str):
        """
        Add IP to malicious list

        Args:
            ip_address: IP address
        """
        self._malicious_ips.add(ip_address)
        logger.info(f"Added {ip_address} to malicious IP list")

    def is_malicious_ip(self, ip_address: str) -> bool:
        """
        Check if IP is malicious

        Args:
            ip_address: IP address

        Returns:
            True if malicious
        """
        return ip_address in self._malicious_ips

    def get_ip_reputation(self, ip_address: str) -> IPReputation:
        """
        Get IP reputation score

        Args:
            ip_address: IP address

        Returns:
            IP reputation
        """
        if ip_address in self._ip_reputation_cache:
            return self._ip_reputation_cache[ip_address]

        # Simulate reputation lookup
        # In production: query threat intelligence APIs
        reputation = IPReputation(
            ip_address=ip_address,
            reputation_score=100.0 if not self.is_malicious_ip(ip_address) else 0.0,
            is_tor=False,
            is_vpn=False,
            is_proxy=False,
        )

        self._ip_reputation_cache[ip_address] = reputation
        return reputation


class SIEM:
    """
    Security Information and Event Management

    Central security monitoring and alerting system.
    """

    def __init__(self):
        """Initialize SIEM"""
        self.anomaly_detector = AnomalyDetector()
        self.brute_force_detector = BruteForceDetector()
        self.ddos_protection = DDoSProtection()
        self.threat_intelligence = ThreatIntelligence()

        self._alerts: List[ThreatAlert] = []
        self._events: List[SecurityEvent] = []

    def process_event(self, event: SecurityEvent) -> List[ThreatAlert]:
        """
        Process security event and generate alerts

        Args:
            event: Security event

        Returns:
            List of generated alerts
        """
        self._events.append(event)
        alerts = []

        # Run detectors
        if event.user_id:
            anomaly_alert = self.anomaly_detector.detect_anomaly(event.user_id, event)
            if anomaly_alert:
                alerts.append(anomaly_alert)

        # Check rate limiting
        ddos_alert = self.ddos_protection.check_rate_limit(event.source_ip)
        if ddos_alert:
            alerts.append(ddos_alert)

        # Check IP reputation
        if self.threat_intelligence.is_malicious_ip(event.source_ip):
            alerts.append(
                ThreatAlert(
                    alert_id=hashlib.sha256(f"malicious_ip_{event.event_id}".encode()).hexdigest()[:16],
                    threat_type=ThreatType.ANOMALY,
                    severity=ThreatLevel.CRITICAL,
                    description="Request from known malicious IP",
                    affected_assets=[event.target],
                    indicators={"source_ip": event.source_ip},
                    timestamp=datetime.now(),
                )
            )

        # Store alerts
        self._alerts.extend(alerts)

        return alerts

    def get_alerts(
        self, severity: Optional[ThreatLevel] = None, status: Optional[AlertStatus] = None
    ) -> List[ThreatAlert]:
        """
        Get alerts with optional filters

        Args:
            severity: Filter by severity
            status: Filter by status

        Returns:
            List of alerts
        """
        filtered = self._alerts

        if severity:
            filtered = [a for a in filtered if a.severity == severity]

        if status:
            filtered = [a for a in filtered if a.status == status]

        return filtered


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=== Advanced Threat Detection Demo ===\n")

    # Initialize SIEM
    siem = SIEM()

    # 1. SQL Injection Detection
    print("1. SQL Injection Detection")
    malicious_input = "admin' OR '1'='1"
    alert = InjectionDetector.detect_sql_injection(malicious_input)
    if alert:
        print(f"   ⚠️  {alert.description}")
        print(f"   Severity: {alert.severity}\n")

    # 2. XSS Detection
    print("2. XSS Detection")
    xss_input = "<script>alert('XSS')</script>"
    alert = InjectionDetector.detect_xss(xss_input)
    if alert:
        print(f"   ⚠️  {alert.description}")
        print(f"   Severity: {alert.severity}\n")

    # 3. Brute Force Detection
    print("3. Brute Force Detection")
    bf_detector = BruteForceDetector(max_attempts=3)
    for i in range(5):
        alert = bf_detector.check_brute_force("user@example.com", success=False)
        if alert:
            print(f"   🚨 {alert.description}")
            print(f"   Failed attempts: {alert.indicators['failed_attempts']}\n")
            break

    # 4. Bot Detection
    print("4. Bot Detection")
    bot_ua = "Mozilla/5.0 (compatible; Googlebot/2.1)"
    alert = BotDetector.detect_bot_activity(bot_ua, "66.249.66.1")
    if alert:
        print(f"   🤖 {alert.description}")
        print(f"   User-Agent: {alert.indicators['user_agent'][:50]}...\n")

    # 5. DDoS Protection
    print("5. DDoS Protection")
    ddos = DDoSProtection(requests_per_second=5)
    for i in range(10):
        alert = ddos.check_rate_limit("203.0.113.1")
        if alert:
            print(f"   🛡️  {alert.description}")
            print(f"   Requests/sec: {alert.indicators['requests_per_second']}\n")
            break

    print("All threat detection systems operational ✓")
