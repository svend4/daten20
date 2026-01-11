"""
Next-Generation Platform Services - v4.0

Future-ready services with serverless, multi-cloud, quantum crypto, and more.
"""

import asyncio
import hashlib
import json
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from threading import Lock
from typing import Any, Callable, Dict, List, Optional, Set, Union
from uuid import uuid4


# ============================================================================
# Serverless Platform
# ============================================================================


class FunctionRuntime(Enum):
    """Function runtimes"""
    PYTHON_3_9 = "python3.9"
    PYTHON_3_11 = "python3.11"
    NODEJS_18 = "nodejs18"
    NODEJS_20 = "nodejs20"
    GO_1_21 = "go1.21"
    JAVA_17 = "java17"
    DOTNET_6 = "dotnet6"


class TriggerType(Enum):
    """Function trigger types"""
    HTTP = "http"
    SCHEDULE = "schedule"
    QUEUE = "queue"
    STREAM = "stream"
    WEBHOOK = "webhook"


@dataclass
class ServerlessFunction:
    """Serverless function"""
    function_id: str
    name: str
    runtime: FunctionRuntime
    handler: str
    memory_mb: int = 512
    timeout_seconds: int = 30
    environment: Dict[str, str] = field(default_factory=dict)
    triggers: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class FunctionExecution:
    """Function execution"""
    execution_id: str
    function_id: str
    status: str = "running"
    duration_ms: Optional[int] = None
    memory_used_mb: Optional[int] = None
    cold_start: bool = False
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None


class ServerlessPlatform:
    """
    Serverless Computing Platform

    Function-as-a-Service with auto-scaling to zero.
    """

    def __init__(self):
        self._functions: Dict[str, ServerlessFunction] = {}
        self._executions: List[FunctionExecution] = []
        self._warm_instances: Dict[str, int] = defaultdict(int)
        self._lock = Lock()
        self._stats = {
            'total_invocations': 0,
            'cold_starts': 0,
            'total_duration_ms': 0
        }

    def deploy_function(
        self,
        name: str,
        runtime: FunctionRuntime,
        handler: str,
        memory_mb: int = 512,
        timeout_seconds: int = 30,
        environment: Optional[Dict[str, str]] = None
    ) -> ServerlessFunction:
        """Deploy serverless function"""
        function_id = str(uuid4())

        function = ServerlessFunction(
            function_id=function_id,
            name=name,
            runtime=runtime,
            handler=handler,
            memory_mb=memory_mb,
            timeout_seconds=timeout_seconds,
            environment=environment or {}
        )

        with self._lock:
            self._functions[function_id] = function

        return function

    async def invoke_function(
        self,
        function_id: str,
        event: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> FunctionExecution:
        """Invoke serverless function"""
        function = self._functions.get(function_id)
        if not function:
            raise ValueError(f"Function {function_id} not found")

        execution_id = str(uuid4())

        # Check if warm instance available
        cold_start = self._warm_instances[function_id] == 0

        if not cold_start:
            with self._lock:
                self._warm_instances[function_id] -= 1

        execution = FunctionExecution(
            execution_id=execution_id,
            function_id=function_id,
            cold_start=cold_start
        )

        # Simulate execution
        start_time = time.time()

        try:
            # Add cold start delay if needed
            if cold_start:
                await asyncio.sleep(0.1)  # 100ms cold start
                with self._lock:
                    self._stats['cold_starts'] += 1

            # Execute function (simulated)
            await asyncio.sleep(0.01)  # 10ms execution

            execution.status = "completed"
            execution.result = {"statusCode": 200, "body": "Success"}

        except Exception as e:
            execution.status = "failed"
            execution.error = str(e)

        # Record metrics
        duration_ms = int((time.time() - start_time) * 1000)
        execution.duration_ms = duration_ms
        execution.memory_used_mb = function.memory_mb // 2  # Simulated
        execution.completed_at = datetime.now()

        with self._lock:
            self._executions.append(execution)
            self._stats['total_invocations'] += 1
            self._stats['total_duration_ms'] += duration_ms

            # Keep instance warm for next call
            self._warm_instances[function_id] += 1

        return execution

    def add_trigger(
        self,
        function_id: str,
        trigger_type: TriggerType,
        config: Dict[str, Any]
    ) -> str:
        """Add trigger to function"""
        function = self._functions.get(function_id)
        if not function:
            raise ValueError(f"Function {function_id} not found")

        trigger_id = str(uuid4())

        with self._lock:
            function.triggers.append(trigger_id)

        return trigger_id

    def get_statistics(self) -> Dict[str, Any]:
        """Get platform statistics"""
        avg_duration = (
            self._stats['total_duration_ms'] / self._stats['total_invocations']
            if self._stats['total_invocations'] > 0 else 0
        )

        cold_start_rate = (
            self._stats['cold_starts'] / self._stats['total_invocations'] * 100
            if self._stats['total_invocations'] > 0 else 0
        )

        return {
            'total_functions': len(self._functions),
            'total_invocations': self._stats['total_invocations'],
            'cold_starts': self._stats['cold_starts'],
            'cold_start_rate': round(cold_start_rate, 1),
            'avg_duration_ms': round(avg_duration, 1),
            'warm_instances': sum(self._warm_instances.values())
        }


# Singleton instance
_serverless_platform: Optional[ServerlessPlatform] = None


def get_serverless_platform() -> ServerlessPlatform:
    """Get singleton serverless platform instance"""
    global _serverless_platform
    if _serverless_platform is None:
        _serverless_platform = ServerlessPlatform()
    return _serverless_platform


# ============================================================================
# Multi-Cloud Platform
# ============================================================================


class CloudProvider(Enum):
    """Cloud providers"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    DIGITALOCEAN = "digitalocean"
    ALIBABA = "alibaba"


class CloudResource(Enum):
    """Cloud resource types"""
    COMPUTE = "compute"
    STORAGE = "storage"
    DATABASE = "database"
    NETWORK = "network"
    CONTAINER = "container"


@dataclass
class CloudDeployment:
    """Cloud deployment"""
    deployment_id: str
    resource_type: CloudResource
    providers: List[CloudProvider]
    regions: List[str]
    instances: int
    status: str = "deploying"
    failover_enabled: bool = False
    created_at: datetime = field(default_factory=datetime.now)


class MultiCloudPlatform:
    """
    Multi-Cloud Deployment Manager

    Cloud-agnostic deployment across AWS, Azure, GCP and more.
    """

    def __init__(self):
        self._providers: Dict[CloudProvider, Dict[str, Any]] = {}
        self._deployments: Dict[str, CloudDeployment] = {}
        self._failovers: List[Dict[str, Any]] = []
        self._lock = Lock()

    def add_provider(
        self,
        provider: CloudProvider,
        credentials: Dict[str, Any]
    ):
        """Configure cloud provider"""
        with self._lock:
            self._providers[provider] = {
                'credentials': credentials,
                'configured_at': datetime.now()
            }

    async def deploy(
        self,
        resource: CloudResource,
        providers: List[CloudProvider],
        regions: List[str],
        instances: int = 1,
        failover_enabled: bool = False,
        **config
    ) -> CloudDeployment:
        """Deploy resource to multiple clouds"""
        deployment_id = str(uuid4())

        deployment = CloudDeployment(
            deployment_id=deployment_id,
            resource_type=resource,
            providers=providers,
            regions=regions,
            instances=instances,
            failover_enabled=failover_enabled
        )

        with self._lock:
            self._deployments[deployment_id] = deployment

        # Simulate deployment
        await asyncio.sleep(0.5)

        deployment.status = "running"

        return deployment

    async def failover(
        self,
        deployment_id: str,
        from_provider: CloudProvider,
        to_provider: CloudProvider
    ) -> bool:
        """Execute failover between clouds"""
        deployment = self._deployments.get(deployment_id)
        if not deployment or not deployment.failover_enabled:
            return False

        failover_record = {
            'deployment_id': deployment_id,
            'from_provider': from_provider.value,
            'to_provider': to_provider.value,
            'timestamp': datetime.now(),
            'duration_ms': 450  # Simulated
        }

        with self._lock:
            self._failovers.append(failover_record)

        return True

    async def optimize_costs(
        self,
        workload_type: str,
        requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Optimize costs across clouds"""
        # Simulated cost optimization
        recommendations = [
            {
                'provider': CloudProvider.AWS.value,
                'region': 'us-east-1',
                'cost_per_hour': 0.08,
                'performance_score': 95
            },
            {
                'provider': CloudProvider.GCP.value,
                'region': 'us-central1',
                'cost_per_hour': 0.09,
                'performance_score': 93
            },
            {
                'provider': CloudProvider.AZURE.value,
                'region': 'eastus',
                'cost_per_hour': 0.10,
                'performance_score': 94
            }
        ]

        # Sort by cost
        recommendations.sort(key=lambda x: x['cost_per_hour'])

        return recommendations

    def get_statistics(self) -> Dict[str, Any]:
        """Get multi-cloud statistics"""
        by_provider = defaultdict(int)
        for deployment in self._deployments.values():
            for provider in deployment.providers:
                by_provider[provider.value] += 1

        return {
            'total_deployments': len(self._deployments),
            'configured_providers': len(self._providers),
            'by_provider': dict(by_provider),
            'total_failovers': len(self._failovers)
        }


# Singleton instance
_multicloud_platform: Optional[MultiCloudPlatform] = None


def get_multicloud_platform() -> MultiCloudPlatform:
    """Get singleton multi-cloud platform instance"""
    global _multicloud_platform
    if _multicloud_platform is None:
        _multicloud_platform = MultiCloudPlatform()
    return _multicloud_platform


# ============================================================================
# Quantum Cryptography
# ============================================================================


class QuantumAlgorithm(Enum):
    """Post-quantum algorithms"""
    KYBER_512 = "kyber-512"
    KYBER_768 = "kyber-768"
    KYBER_1024 = "kyber-1024"
    DILITHIUM_2 = "dilithium-2"
    DILITHIUM_3 = "dilithium-3"
    DILITHIUM_5 = "dilithium-5"
    SPHINCS_PLUS = "sphincs+"


@dataclass
class QuantumKeypair:
    """Quantum-resistant keypair"""
    keypair_id: str
    algorithm: QuantumAlgorithm
    public_key: bytes
    private_key: bytes
    created_at: datetime = field(default_factory=datetime.now)


class QuantumCrypto:
    """
    Quantum-Ready Cryptography

    Post-quantum algorithms and hybrid encryption.
    """

    def __init__(self):
        self._keypairs: Dict[str, QuantumKeypair] = {}
        self._lock = Lock()
        self._stats = {
            'encryptions': 0,
            'signatures': 0,
            'verifications': 0
        }

    async def generate_keypair(
        self,
        algorithm: QuantumAlgorithm = QuantumAlgorithm.KYBER_1024
    ) -> QuantumKeypair:
        """Generate quantum-resistant keypair"""
        keypair_id = str(uuid4())

        # Simulated key generation
        public_key = hashlib.sha256(f"public_{keypair_id}".encode()).digest()
        private_key = hashlib.sha256(f"private_{keypair_id}".encode()).digest()

        keypair = QuantumKeypair(
            keypair_id=keypair_id,
            algorithm=algorithm,
            public_key=public_key,
            private_key=private_key
        )

        with self._lock:
            self._keypairs[keypair_id] = keypair

        return keypair

    async def hybrid_encrypt(
        self,
        plaintext: bytes,
        recipient_public_key: bytes,
        classical_algorithm: str = "RSA-2048",
        pq_algorithm: str = "Kyber-1024"
    ) -> bytes:
        """Hybrid encryption (classical + post-quantum)"""
        # Simulated hybrid encryption
        ciphertext = hashlib.sha256(plaintext + recipient_public_key).digest()

        with self._lock:
            self._stats['encryptions'] += 1

        return ciphertext

    async def hybrid_decrypt(
        self,
        ciphertext: bytes,
        private_key: bytes
    ) -> bytes:
        """Hybrid decryption"""
        # Simulated decryption
        plaintext = b"Decrypted: " + ciphertext[:16]

        return plaintext

    async def sign(
        self,
        message: bytes,
        private_key: bytes,
        algorithm: QuantumAlgorithm = QuantumAlgorithm.DILITHIUM_5
    ) -> bytes:
        """Quantum-resistant digital signature"""
        # Simulated signing
        signature = hashlib.sha256(message + private_key).digest()

        with self._lock:
            self._stats['signatures'] += 1

        return signature

    async def verify(
        self,
        message: bytes,
        signature: bytes,
        public_key: bytes
    ) -> bool:
        """Verify quantum-resistant signature"""
        # Simulated verification
        expected_sig = hashlib.sha256(message + public_key).digest()

        with self._lock:
            self._stats['verifications'] += 1

        # In real implementation, proper verification
        return len(signature) == len(expected_sig)

    def get_statistics(self) -> Dict[str, Any]:
        """Get cryptography statistics"""
        return {
            'total_keypairs': len(self._keypairs),
            'encryptions': self._stats['encryptions'],
            'signatures': self._stats['signatures'],
            'verifications': self._stats['verifications']
        }


# Singleton instance
_quantum_crypto: Optional[QuantumCrypto] = None


def get_quantum_crypto() -> QuantumCrypto:
    """Get singleton quantum crypto instance"""
    global _quantum_crypto
    if _quantum_crypto is None:
        _quantum_crypto = QuantumCrypto()
    return _quantum_crypto


# ============================================================================
# Edge AI Platform
# ============================================================================


@dataclass
class EdgeAIModel:
    """Edge AI model"""
    model_id: str
    name: str
    framework: str
    size_mb: float
    optimized: bool = False
    quantized: bool = False
    target_device: str = "mobile"
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class InferenceResult:
    """AI inference result"""
    result_id: str
    model_id: str
    inference_time_ms: float
    confidence: float
    prediction: Any
    device: str


class EdgeAI:
    """
    Edge AI Platform

    AI inference at the edge with model optimization.
    """

    def __init__(self):
        self._models: Dict[str, EdgeAIModel] = {}
        self._inferences: List[InferenceResult] = []
        self._lock = Lock()

    async def optimize_model(
        self,
        model_path: str,
        target_device: str = "mobile",
        optimization: str = "quantization",
        target_size_mb: float = 5.0
    ) -> EdgeAIModel:
        """Optimize model for edge deployment"""
        model_id = str(uuid4())

        # Simulated optimization
        original_size = 50.0  # MB
        optimized_size = min(target_size_mb, original_size * 0.1)

        model = EdgeAIModel(
            model_id=model_id,
            name=model_path.split('/')[-1],
            framework="tensorflow_lite",
            size_mb=optimized_size,
            optimized=True,
            quantized=(optimization == "quantization"),
            target_device=target_device
        )

        with self._lock:
            self._models[model_id] = model

        return model

    async def deploy_to_edge(
        self,
        model: EdgeAIModel,
        devices: List[str],
        fallback_to_cloud: bool = True
    ) -> Dict[str, Any]:
        """Deploy model to edge devices"""
        deployment = {
            'deployment_id': str(uuid4()),
            'model_id': model.model_id,
            'devices': devices,
            'fallback_enabled': fallback_to_cloud,
            'status': 'deployed'
        }

        return deployment

    async def infer(
        self,
        model_id: str,
        input_data: Any,
        device: str = "edge"
    ) -> InferenceResult:
        """Run inference at edge"""
        model = self._models.get(model_id)
        if not model:
            raise ValueError(f"Model {model_id} not found")

        result_id = str(uuid4())

        # Simulated inference
        start_time = time.time()
        await asyncio.sleep(0.05)  # 50ms inference
        inference_time = (time.time() - start_time) * 1000

        result = InferenceResult(
            result_id=result_id,
            model_id=model_id,
            inference_time_ms=inference_time,
            confidence=0.95,
            prediction="class_A",
            device=device
        )

        with self._lock:
            self._inferences.append(result)

        return result

    async def federated_train(
        self,
        model: EdgeAIModel,
        edge_devices: List[str],
        rounds: int = 10,
        min_devices_per_round: int = 5
    ) -> Dict[str, Any]:
        """Federated learning across edge devices"""
        training = {
            'training_id': str(uuid4()),
            'model_id': model.model_id,
            'rounds': rounds,
            'devices': edge_devices,
            'status': 'training',
            'current_round': 0
        }

        # Simulated federated training
        for round_num in range(rounds):
            await asyncio.sleep(0.1)
            training['current_round'] = round_num + 1

        training['status'] = 'completed'

        return training

    def get_statistics(self) -> Dict[str, Any]:
        """Get Edge AI statistics"""
        total_inference_time = sum(
            r.inference_time_ms for r in self._inferences
        )
        avg_inference_time = (
            total_inference_time / len(self._inferences)
            if self._inferences else 0
        )

        return {
            'total_models': len(self._models),
            'total_inferences': len(self._inferences),
            'avg_inference_time_ms': round(avg_inference_time, 1)
        }


# Singleton instance
_edge_ai: Optional[EdgeAI] = None


def get_edge_ai() -> EdgeAI:
    """Get singleton Edge AI instance"""
    global _edge_ai
    if _edge_ai is None:
        _edge_ai = EdgeAI()
    return _edge_ai


# ============================================================================
# Voice Interface
# ============================================================================


@dataclass
class VoiceCommand:
    """Voice command"""
    command_id: str
    transcript: str
    intent: str
    entities: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    language: str = "en-US"
    user_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class VoiceInterface:
    """
    Voice & Conversational Interface

    Voice commands and natural language processing.
    """

    def __init__(self):
        self._commands: List[VoiceCommand] = []
        self._intents = self._initialize_intents()
        self._lock = Lock()

    def _initialize_intents(self) -> Dict[str, List[str]]:
        """Initialize voice command intents"""
        return {
            'create_document': [
                r'create (a |an )?new document',
                r'make (a |an )?document',
                r'new document (titled|called|named)'
            ],
            'search_documents': [
                r'search for',
                r'find (documents?|files?)',
                r'show me (documents?|files?)'
            ],
            'show_report': [
                r'show (me )?(the )?report',
                r'display (the )?report',
                r'open (the )?report'
            ],
            'send_message': [
                r'send (this|it) to',
                r'email (this|it) to',
                r'share (this|it) with'
            ]
        }

    async def process_command(
        self,
        audio_data: bytes,
        language: str = "en-US",
        user_id: Optional[str] = None
    ) -> VoiceCommand:
        """Process voice command"""
        command_id = str(uuid4())

        # Simulated speech-to-text
        transcript = "Create a new document titled Budget 2026"

        # Parse intent
        intent = self._parse_intent(transcript)

        # Extract entities
        entities = self._extract_entities(transcript, intent)

        command = VoiceCommand(
            command_id=command_id,
            transcript=transcript,
            intent=intent,
            entities=entities,
            confidence=0.95,
            language=language,
            user_id=user_id
        )

        with self._lock:
            self._commands.append(command)

        return command

    def _parse_intent(self, transcript: str) -> str:
        """Parse intent from transcript"""
        transcript_lower = transcript.lower()

        for intent, patterns in self._intents.items():
            for pattern in patterns:
                import re
                if re.search(pattern, transcript_lower):
                    return intent

        return "unknown"

    def _extract_entities(
        self,
        transcript: str,
        intent: str
    ) -> Dict[str, Any]:
        """Extract entities from transcript"""
        entities = {}

        # Simple entity extraction
        if intent == "create_document":
            import re
            match = re.search(r'titled (.+?)$', transcript, re.IGNORECASE)
            if match:
                entities['title'] = match.group(1).strip()

        return entities

    async def authenticate(
        self,
        audio_sample: bytes,
        claimed_identity: str
    ) -> bool:
        """Voice biometric authentication"""
        # Simulated voice authentication
        return True

    async def synthesize(
        self,
        text: str,
        voice: str = "neural-female",
        language: str = "en-US"
    ) -> bytes:
        """Text-to-speech synthesis"""
        # Simulated TTS
        audio_data = text.encode('utf-8')

        return audio_data

    def get_statistics(self) -> Dict[str, Any]:
        """Get voice interface statistics"""
        by_intent = defaultdict(int)
        for command in self._commands:
            by_intent[command.intent] += 1

        avg_confidence = (
            sum(c.confidence for c in self._commands) / len(self._commands)
            if self._commands else 0
        )

        return {
            'total_commands': len(self._commands),
            'by_intent': dict(by_intent),
            'avg_confidence': round(avg_confidence, 2)
        }


# Singleton instance
_voice_interface: Optional[VoiceInterface] = None


def get_voice_interface() -> VoiceInterface:
    """Get singleton voice interface instance"""
    global _voice_interface
    if _voice_interface is None:
        _voice_interface = VoiceInterface()
    return _voice_interface


# ============================================================================
# AR/VR & Metaverse Platform
# ============================================================================


class VRSpaceType(Enum):
    """VR space types"""
    OFFICE = "office"
    CONFERENCE_ROOM = "conference_room"
    EXHIBITION = "exhibition"
    CLASSROOM = "classroom"
    CUSTOM = "custom"


@dataclass
class VirtualSpace:
    """Virtual reality space"""
    space_id: str
    name: str
    space_type: VRSpaceType
    capacity: int
    features: List[str] = field(default_factory=list)
    participants: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AROverlay:
    """Augmented reality overlay"""
    overlay_id: str
    document_id: str
    anchor_type: str
    display_mode: str
    created_at: datetime = field(default_factory=datetime.now)


class MetaversePlatform:
    """
    AR/VR & Metaverse Platform

    Virtual spaces and augmented reality experiences.
    """

    def __init__(self):
        self._spaces: Dict[str, VirtualSpace] = {}
        self._overlays: Dict[str, AROverlay] = {}
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()

    async def create_space(
        self,
        name: str,
        space_type: VRSpaceType,
        capacity: int = 20,
        features: Optional[List[str]] = None
    ) -> VirtualSpace:
        """Create virtual space"""
        space_id = str(uuid4())

        space = VirtualSpace(
            space_id=space_id,
            name=name,
            space_type=space_type,
            capacity=capacity,
            features=features or []
        )

        with self._lock:
            self._spaces[space_id] = space

        return space

    async def create_ar_overlay(
        self,
        document_id: str,
        anchor_type: str = "qr_code",
        display_mode: str = "floating"
    ) -> AROverlay:
        """Create AR overlay for document"""
        overlay_id = str(uuid4())

        overlay = AROverlay(
            overlay_id=overlay_id,
            document_id=document_id,
            anchor_type=anchor_type,
            display_mode=display_mode
        )

        with self._lock:
            self._overlays[overlay_id] = overlay

        return overlay

    async def join_vr_session(
        self,
        space_id: str,
        user_id: str,
        avatar_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Join VR session"""
        space = self._spaces.get(space_id)
        if not space:
            raise ValueError(f"Space {space_id} not found")

        if len(space.participants) >= space.capacity:
            raise ValueError("Space is at capacity")

        session_id = str(uuid4())

        session = {
            'session_id': session_id,
            'space_id': space_id,
            'user_id': user_id,
            'avatar_url': avatar_url,
            'joined_at': datetime.now()
        }

        with self._lock:
            space.participants.add(user_id)
            self._sessions[session_id] = session

        return session

    async def leave_vr_session(
        self,
        session_id: str
    ) -> bool:
        """Leave VR session"""
        session = self._sessions.get(session_id)
        if not session:
            return False

        space = self._spaces.get(session['space_id'])
        if space:
            with self._lock:
                space.participants.discard(session['user_id'])
                del self._sessions[session_id]

        return True

    def get_statistics(self) -> Dict[str, Any]:
        """Get metaverse statistics"""
        active_participants = sum(
            len(space.participants) for space in self._spaces.values()
        )

        return {
            'total_spaces': len(self._spaces),
            'total_overlays': len(self._overlays),
            'active_sessions': len(self._sessions),
            'active_participants': active_participants
        }


# Singleton instance
_metaverse_platform: Optional[MetaversePlatform] = None


def get_metaverse_platform() -> MetaversePlatform:
    """Get singleton metaverse platform instance"""
    global _metaverse_platform
    if _metaverse_platform is None:
        _metaverse_platform = MetaversePlatform()
    return _metaverse_platform
