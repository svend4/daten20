"""
Edge Computing Platform

Edge nodes management, local data processing, Lambda functions at edge,
stream processing, and cloud synchronization.

Part of v3.6 IoT & Edge Computing implementation.
"""

import asyncio
import hashlib
import logging
import pickle
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from uuid import uuid4

logger = logging.getLogger(__name__)


class EdgeNodeStatus(Enum):
    """Edge node status."""
    ONLINE = "online"
    OFFLINE = "offline"
    SYNCING = "syncing"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class FunctionStatus(Enum):
    """Edge function status."""
    DEPLOYED = "deployed"
    RUNNING = "running"
    STOPPED = "stopped"
    FAILED = "failed"


class SyncStatus(Enum):
    """Cloud sync status."""
    SYNCED = "synced"
    PENDING = "pending"
    SYNCING = "syncing"
    FAILED = "failed"


@dataclass
class EdgeResources:
    """Edge node resource usage."""
    cpu_percent: float = 0.0
    memory_mb: int = 0
    disk_mb: int = 0
    network_mbps: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class EdgeNode:
    """Edge computing node."""
    node_id: str
    node_name: str
    location: str
    status: EdgeNodeStatus = EdgeNodeStatus.ONLINE
    ip_address: Optional[str] = None
    resources: EdgeResources = field(default_factory=EdgeResources)
    capabilities: Set[str] = field(default_factory=set)
    functions: Dict[str, 'EdgeFunction'] = field(default_factory=dict)
    cache: Dict[str, Any] = field(default_factory=dict)
    last_seen: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EdgeFunction:
    """Lambda function deployed at edge."""
    function_id: str
    function_name: str
    code: str
    trigger: str  # mqtt:topic, http:path, cron:schedule
    runtime: str = "python3"
    timeout: int = 30  # seconds
    memory_limit: int = 128  # MB
    status: FunctionStatus = FunctionStatus.DEPLOYED
    invocations: int = 0
    errors: int = 0
    last_invocation: Optional[datetime] = None
    deployed_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessingResult:
    """Edge processing result."""
    function_id: str
    input_data: Any
    output_data: Any
    success: bool
    execution_time_ms: float
    timestamp: datetime = field(default_factory=datetime.now)
    error: Optional[str] = None


@dataclass
class CacheEntry:
    """Edge cache entry."""
    key: str
    value: Any
    ttl: int  # seconds
    created_at: datetime = field(default_factory=datetime.now)
    accessed_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0

    def is_expired(self) -> bool:
        """Check if cache entry expired."""
        age = (datetime.now() - self.created_at).total_seconds()
        return age > self.ttl


class EdgeCache:
    """Local caching at edge for offline capability."""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: Dict[str, CacheEntry] = {}
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        entry = self.cache.get(key)

        if entry is None:
            self.misses += 1
            return None

        if entry.is_expired():
            del self.cache[key]
            self.misses += 1
            return None

        entry.accessed_at = datetime.now()
        entry.access_count += 1
        self.hits += 1

        return entry.value

    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache."""
        # Evict if at capacity
        if len(self.cache) >= self.max_size:
            self._evict_lru()

        self.cache[key] = CacheEntry(key=key, value=value, ttl=ttl)

    def delete(self, key: str):
        """Delete from cache."""
        self.cache.pop(key, None)

    def clear(self):
        """Clear all cache."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def _evict_lru(self):
        """Evict least recently used entry."""
        if not self.cache:
            return

        lru_key = min(
            self.cache.items(),
            key=lambda x: x[1].accessed_at
        )[0]

        del self.cache[lru_key]
        logger.debug(f"Evicted cache entry: {lru_key}")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0.0

        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate
        }


class EdgeProcessor:
    """Local data processing at edge."""

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.processing_queue: asyncio.Queue = asyncio.Queue()
        self.results: deque = deque(maxlen=1000)
        self.running = False

    async def process(
        self,
        function: EdgeFunction,
        data: Any
    ) -> ProcessingResult:
        """Process data with edge function."""
        start_time = datetime.now()

        try:
            # Execute function code (simplified - in production would use sandbox)
            result = await self._execute_function(function, data)

            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            processing_result = ProcessingResult(
                function_id=function.function_id,
                input_data=data,
                output_data=result,
                success=True,
                execution_time_ms=execution_time
            )

            # Update function stats
            function.invocations += 1
            function.last_invocation = datetime.now()

            return processing_result

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            logger.error(f"Edge function {function.function_id} failed: {e}")

            function.errors += 1
            function.status = FunctionStatus.FAILED

            return ProcessingResult(
                function_id=function.function_id,
                input_data=data,
                output_data=None,
                success=False,
                execution_time_ms=execution_time,
                error=str(e)
            )

    async def _execute_function(self, function: EdgeFunction, data: Any) -> Any:
        """Execute edge function code."""
        # Create execution environment
        local_vars = {'data': data, 'result': None}

        try:
            # Execute function code with timeout
            exec(function.code, {}, local_vars)

            # Call process function if defined
            if 'process' in local_vars:
                process_func = local_vars['process']
                if asyncio.iscoroutinefunction(process_func):
                    result = await asyncio.wait_for(
                        process_func(data),
                        timeout=function.timeout
                    )
                else:
                    result = process_func(data)
            else:
                result = local_vars.get('result')

            return result

        except asyncio.TimeoutError:
            raise Exception(f"Function execution timeout ({function.timeout}s)")
        except Exception as e:
            raise Exception(f"Function execution error: {e}")

    async def start_processing(self):
        """Start processing queue."""
        self.running = True

        while self.running:
            try:
                # Get item from queue
                function, data = await asyncio.wait_for(
                    self.processing_queue.get(),
                    timeout=1.0
                )

                # Process
                result = await self.process(function, data)
                self.results.append(result)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Processing error: {e}")

    async def stop_processing(self):
        """Stop processing queue."""
        self.running = False

    async def enqueue(self, function: EdgeFunction, data: Any):
        """Enqueue data for processing."""
        await self.processing_queue.put((function, data))


class StreamProcessor:
    """Stream processing at edge."""

    def __init__(self):
        self.streams: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.aggregations: Dict[str, Any] = {}

    def add_to_stream(self, stream_id: str, data: Any):
        """Add data to stream."""
        self.streams[stream_id].append({
            'data': data,
            'timestamp': datetime.now()
        })

    def get_stream_window(
        self,
        stream_id: str,
        window_seconds: int = 60
    ) -> List[Any]:
        """Get stream data within time window."""
        stream = self.streams.get(stream_id, deque())
        cutoff = datetime.now() - timedelta(seconds=window_seconds)

        return [
            item['data'] for item in stream
            if item['timestamp'] >= cutoff
        ]

    def aggregate(
        self,
        stream_id: str,
        aggregation_func: Callable,
        window_seconds: int = 60
    ) -> Any:
        """Aggregate stream data."""
        window_data = self.get_stream_window(stream_id, window_seconds)

        if not window_data:
            return None

        try:
            result = aggregation_func(window_data)
            self.aggregations[stream_id] = {
                'result': result,
                'timestamp': datetime.now()
            }
            return result
        except Exception as e:
            logger.error(f"Stream aggregation error: {e}")
            return None


class EdgeSync:
    """Cloud synchronization for edge nodes."""

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.pending_sync: List[Dict[str, Any]] = []
        self.sync_status = SyncStatus.SYNCED
        self.last_sync: Optional[datetime] = None
        self.sync_failures = 0

    def add_to_sync(self, data: Dict[str, Any]):
        """Add data to sync queue."""
        data['node_id'] = self.node_id
        data['timestamp'] = datetime.now()
        self.pending_sync.append(data)
        self.sync_status = SyncStatus.PENDING

    async def sync_to_cloud(self, cloud_client: Optional[Callable] = None) -> bool:
        """Sync pending data to cloud."""
        if not self.pending_sync:
            self.sync_status = SyncStatus.SYNCED
            return True

        self.sync_status = SyncStatus.SYNCING

        try:
            # Mock cloud sync
            if cloud_client:
                await cloud_client(self.pending_sync)
            else:
                # Simulate sync
                await asyncio.sleep(0.1)

            # Clear pending
            synced_count = len(self.pending_sync)
            self.pending_sync.clear()

            self.sync_status = SyncStatus.SYNCED
            self.last_sync = datetime.now()
            self.sync_failures = 0

            logger.info(f"Synced {synced_count} items to cloud from node {self.node_id}")
            return True

        except Exception as e:
            logger.error(f"Cloud sync failed: {e}")
            self.sync_status = SyncStatus.FAILED
            self.sync_failures += 1
            return False

    def get_sync_stats(self) -> Dict[str, Any]:
        """Get sync statistics."""
        return {
            'status': self.sync_status.value,
            'pending_items': len(self.pending_sync),
            'last_sync': self.last_sync,
            'failures': self.sync_failures
        }


class EdgeOrchestrator:
    """Orchestrate edge nodes and functions."""

    def __init__(self):
        self.nodes: Dict[str, EdgeNode] = {}

    def register_node(
        self,
        node_id: str,
        node_name: str,
        location: str,
        **kwargs
    ) -> EdgeNode:
        """Register new edge node."""
        if node_id in self.nodes:
            raise ValueError(f"Node {node_id} already registered")

        node = EdgeNode(
            node_id=node_id,
            node_name=node_name,
            location=location,
            **kwargs
        )

        self.nodes[node_id] = node

        logger.info(f"Registered edge node {node_id} ({node_name})")
        return node

    def get_node(self, node_id: str) -> Optional[EdgeNode]:
        """Get edge node."""
        return self.nodes.get(node_id)

    def list_nodes(
        self,
        status: Optional[EdgeNodeStatus] = None
    ) -> List[EdgeNode]:
        """List edge nodes."""
        nodes = list(self.nodes.values())

        if status:
            nodes = [n for n in nodes if n.status == status]

        return nodes

    def deregister_node(self, node_id: str) -> bool:
        """Deregister edge node."""
        if node_id in self.nodes:
            del self.nodes[node_id]
            logger.info(f"Deregistered edge node {node_id}")
            return True
        return False

    async def deploy_function(
        self,
        node_id: str,
        function_name: str,
        code: str,
        trigger: str,
        **kwargs
    ) -> Optional[EdgeFunction]:
        """Deploy function to edge node."""
        node = self.nodes.get(node_id)
        if not node:
            logger.error(f"Node {node_id} not found")
            return None

        function_id = str(uuid4())
        function = EdgeFunction(
            function_id=function_id,
            function_name=function_name,
            code=code,
            trigger=trigger,
            **kwargs
        )

        node.functions[function_id] = function

        logger.info(f"Deployed function {function_name} to node {node_id}")
        return function

    async def undeploy_function(
        self,
        node_id: str,
        function_id: str
    ) -> bool:
        """Remove function from edge node."""
        node = self.nodes.get(node_id)
        if not node:
            return False

        if function_id in node.functions:
            del node.functions[function_id]
            logger.info(f"Undeployed function {function_id} from node {node_id}")
            return True

        return False

    def get_node_resources(self, node_id: str) -> Optional[EdgeResources]:
        """Get node resource usage."""
        node = self.nodes.get(node_id)
        return node.resources if node else None

    def update_node_resources(
        self,
        node_id: str,
        cpu_percent: float,
        memory_mb: int,
        disk_mb: int
    ):
        """Update node resource usage."""
        node = self.nodes.get(node_id)
        if node:
            node.resources = EdgeResources(
                cpu_percent=cpu_percent,
                memory_mb=memory_mb,
                disk_mb=disk_mb
            )

    def find_best_node(
        self,
        required_resources: Optional[Dict[str, Any]] = None
    ) -> Optional[EdgeNode]:
        """Find best edge node for deployment."""
        available_nodes = [
            n for n in self.nodes.values()
            if n.status == EdgeNodeStatus.ONLINE
        ]

        if not available_nodes:
            return None

        # Simple selection based on lowest CPU usage
        return min(available_nodes, key=lambda n: n.resources.cpu_percent)


class EdgePlatform:
    """Main edge computing platform."""

    def __init__(self):
        self.orchestrator = EdgeOrchestrator()
        self.processors: Dict[str, EdgeProcessor] = {}
        self.caches: Dict[str, EdgeCache] = {}
        self.syncs: Dict[str, EdgeSync] = {}
        self.stream_processors: Dict[str, StreamProcessor] = {}

    async def register_edge_node(
        self,
        node_id: str,
        node_name: str,
        location: str,
        **kwargs
    ) -> EdgeNode:
        """Register new edge node."""
        node = self.orchestrator.register_node(node_id, node_name, location, **kwargs)

        # Initialize components for node
        self.processors[node_id] = EdgeProcessor(node_id)
        self.caches[node_id] = EdgeCache()
        self.syncs[node_id] = EdgeSync(node_id)
        self.stream_processors[node_id] = StreamProcessor()

        # Start processor
        asyncio.create_task(self.processors[node_id].start_processing())

        return node

    async def deploy_function(
        self,
        function_name: str,
        code: str,
        trigger: str,
        node_id: Optional[str] = None,
        **kwargs
    ) -> Optional[EdgeFunction]:
        """Deploy function to edge node."""
        # Auto-select node if not specified
        if not node_id:
            node = self.orchestrator.find_best_node()
            if not node:
                logger.error("No available edge nodes")
                return None
            node_id = node.node_id

        return await self.orchestrator.deploy_function(
            node_id=node_id,
            function_name=function_name,
            code=code,
            trigger=trigger,
            **kwargs
        )

    async def process_at_edge(
        self,
        node_id: str,
        function_id: str,
        data: Any
    ) -> Optional[ProcessingResult]:
        """Process data at edge node."""
        node = self.orchestrator.get_node(node_id)
        if not node:
            return None

        function = node.functions.get(function_id)
        if not function:
            return None

        processor = self.processors.get(node_id)
        if not processor:
            return None

        return await processor.process(function, data)

    def cache_at_edge(
        self,
        node_id: str,
        key: str,
        value: Any,
        ttl: int = 3600
    ) -> bool:
        """Cache data at edge node."""
        cache = self.caches.get(node_id)
        if not cache:
            return False

        cache.set(key, value, ttl)
        return True

    def get_from_edge_cache(
        self,
        node_id: str,
        key: str
    ) -> Optional[Any]:
        """Get data from edge cache."""
        cache = self.caches.get(node_id)
        if not cache:
            return None

        return cache.get(key)

    async def sync_to_cloud(
        self,
        node_id: str,
        data: Dict[str, Any]
    ) -> bool:
        """Add data to cloud sync queue."""
        sync = self.syncs.get(node_id)
        if not sync:
            return False

        sync.add_to_sync(data)
        return True

    async def perform_sync(self, node_id: str) -> bool:
        """Perform cloud sync for node."""
        sync = self.syncs.get(node_id)
        if not sync:
            return False

        return await sync.sync_to_cloud()

    def get_node_stats(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get edge node statistics."""
        node = self.orchestrator.get_node(node_id)
        if not node:
            return None

        cache = self.caches.get(node_id)
        sync = self.syncs.get(node_id)

        return {
            'node_id': node_id,
            'status': node.status.value,
            'functions': len(node.functions),
            'resources': {
                'cpu_percent': node.resources.cpu_percent,
                'memory_mb': node.resources.memory_mb,
                'disk_mb': node.resources.disk_mb
            },
            'cache': cache.get_stats() if cache else None,
            'sync': sync.get_sync_stats() if sync else None
        }


# Singleton instance
_edge_platform: Optional[EdgePlatform] = None


def get_edge_platform() -> EdgePlatform:
    """Get or create edge platform."""
    global _edge_platform

    if _edge_platform is None:
        _edge_platform = EdgePlatform()

    return _edge_platform
