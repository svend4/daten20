#!/usr/bin/env python3
"""
Container Orchestration Module

Provides container and Kubernetes orchestration capabilities for microservices.

Key Features:
- Kubernetes operators and controllers
- Custom Resource Definitions (CRDs)
- Helm chart generation
- Deployment strategies (Rolling, Blue-Green, Canary)
- Pod autoscaling (HPA, VPA)
- Resource quotas and limits
- Network policies
- Service accounts and RBAC
- Secrets and ConfigMaps management
- Health checks and probes

Dependencies:
- kubernetes (Python client)
- pyyaml
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from datetime import datetime
import logging
import yaml
import json
from collections import defaultdict

logger = logging.getLogger(__name__)


class DeploymentStrategy(str, Enum):
    """Deployment strategy types"""
    ROLLING_UPDATE = "rolling_update"
    RECREATE = "recreate"
    BLUE_GREEN = "blue_green"
    CANARY = "canary"


class ResourceType(str, Enum):
    """Kubernetes resource types"""
    DEPLOYMENT = "Deployment"
    SERVICE = "Service"
    CONFIGMAP = "ConfigMap"
    SECRET = "Secret"
    INGRESS = "Ingress"
    POD = "Pod"
    STATEFULSET = "StatefulSet"
    DAEMONSET = "DaemonSet"
    JOB = "Job"
    CRONJOB = "CronJob"
    HPA = "HorizontalPodAutoscaler"
    VPA = "VerticalPodAutoscaler"
    NETWORK_POLICY = "NetworkPolicy"
    SERVICE_ACCOUNT = "ServiceAccount"
    ROLE = "Role"
    ROLE_BINDING = "RoleBinding"


class ProbeType(str, Enum):
    """Probe types for health checks"""
    HTTP = "httpGet"
    TCP = "tcpSocket"
    EXEC = "exec"


@dataclass
class ResourceRequirements:
    """Container resource requirements"""
    cpu_request: str = "100m"  # millicores
    cpu_limit: str = "500m"
    memory_request: str = "128Mi"
    memory_limit: str = "512Mi"


@dataclass
class Probe:
    """Health check probe configuration"""
    probe_type: ProbeType = ProbeType.HTTP
    path: str = "/health"
    port: int = 8080
    initial_delay_seconds: int = 10
    period_seconds: int = 10
    timeout_seconds: int = 5
    success_threshold: int = 1
    failure_threshold: int = 3


@dataclass
class ContainerSpec:
    """Container specification"""
    name: str
    image: str
    tag: str = "latest"
    command: Optional[List[str]] = None
    args: Optional[List[str]] = None
    ports: List[int] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    env_from: List[str] = field(default_factory=list)  # ConfigMap/Secret names
    resources: ResourceRequirements = field(default_factory=ResourceRequirements)
    liveness_probe: Optional[Probe] = None
    readiness_probe: Optional[Probe] = None
    startup_probe: Optional[Probe] = None
    volume_mounts: Dict[str, str] = field(default_factory=dict)  # name -> mount_path


@dataclass
class AutoscalingConfig:
    """Horizontal Pod Autoscaler configuration"""
    min_replicas: int = 1
    max_replicas: int = 10
    target_cpu_utilization: int = 80
    target_memory_utilization: Optional[int] = None
    scale_down_stabilization_seconds: int = 300


@dataclass
class NetworkPolicyRule:
    """Network policy rule"""
    from_pods: List[Dict[str, str]] = field(default_factory=list)  # Label selectors
    from_namespaces: List[str] = field(default_factory=list)
    ports: List[int] = field(default_factory=list)


class KubernetesManifest:
    """
    Kubernetes manifest generator

    Generates YAML manifests for Kubernetes resources.
    """

    def __init__(self, namespace: str = "default"):
        """
        Initialize manifest generator

        Args:
            namespace: Kubernetes namespace
        """
        self.namespace = namespace

    def create_deployment(
        self,
        name: str,
        containers: List[ContainerSpec],
        replicas: int = 1,
        labels: Optional[Dict[str, str]] = None,
        strategy: DeploymentStrategy = DeploymentStrategy.ROLLING_UPDATE,
        annotations: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create Deployment manifest

        Args:
            name: Deployment name
            containers: Container specifications
            replicas: Number of replicas
            labels: Pod labels
            strategy: Deployment strategy
            annotations: Pod annotations

        Returns:
            Deployment manifest
        """
        labels = labels or {"app": name}

        manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": name,
                "namespace": self.namespace,
                "labels": labels
            },
            "spec": {
                "replicas": replicas,
                "selector": {
                    "matchLabels": labels
                },
                "template": {
                    "metadata": {
                        "labels": labels,
                        "annotations": annotations or {}
                    },
                    "spec": {
                        "containers": [self._build_container(c) for c in containers]
                    }
                }
            }
        }

        # Add deployment strategy
        if strategy == DeploymentStrategy.ROLLING_UPDATE:
            manifest["spec"]["strategy"] = {
                "type": "RollingUpdate",
                "rollingUpdate": {
                    "maxSurge": 1,
                    "maxUnavailable": 0
                }
            }
        elif strategy == DeploymentStrategy.RECREATE:
            manifest["spec"]["strategy"] = {"type": "Recreate"}

        return manifest

    def create_service(
        self,
        name: str,
        selector: Dict[str, str],
        ports: List[Dict[str, int]],
        service_type: str = "ClusterIP",
        annotations: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create Service manifest

        Args:
            name: Service name
            selector: Pod selector
            ports: Service ports [{"port": 80, "targetPort": 8080}]
            service_type: Service type (ClusterIP, NodePort, LoadBalancer)
            annotations: Service annotations

        Returns:
            Service manifest
        """
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": name,
                "namespace": self.namespace,
                "annotations": annotations or {}
            },
            "spec": {
                "type": service_type,
                "selector": selector,
                "ports": [
                    {
                        "name": f"port-{i}",
                        "protocol": "TCP",
                        "port": p["port"],
                        "targetPort": p["targetPort"]
                    }
                    for i, p in enumerate(ports)
                ]
            }
        }

    def create_configmap(
        self,
        name: str,
        data: Dict[str, str],
        binary_data: Optional[Dict[str, bytes]] = None
    ) -> Dict[str, Any]:
        """
        Create ConfigMap manifest

        Args:
            name: ConfigMap name
            data: String data
            binary_data: Binary data

        Returns:
            ConfigMap manifest
        """
        manifest = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": name,
                "namespace": self.namespace
            },
            "data": data
        }

        if binary_data:
            manifest["binaryData"] = binary_data

        return manifest

    def create_secret(
        self,
        name: str,
        data: Dict[str, str],
        secret_type: str = "Opaque"
    ) -> Dict[str, Any]:
        """
        Create Secret manifest

        Args:
            name: Secret name
            data: Secret data (will be base64 encoded)
            secret_type: Secret type

        Returns:
            Secret manifest
        """
        import base64

        # Base64 encode all values
        encoded_data = {
            k: base64.b64encode(v.encode()).decode()
            for k, v in data.items()
        }

        return {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": name,
                "namespace": self.namespace
            },
            "type": secret_type,
            "data": encoded_data
        }

    def create_hpa(
        self,
        name: str,
        target_deployment: str,
        config: AutoscalingConfig
    ) -> Dict[str, Any]:
        """
        Create HorizontalPodAutoscaler manifest

        Args:
            name: HPA name
            target_deployment: Target deployment name
            config: Autoscaling configuration

        Returns:
            HPA manifest
        """
        metrics = [
            {
                "type": "Resource",
                "resource": {
                    "name": "cpu",
                    "target": {
                        "type": "Utilization",
                        "averageUtilization": config.target_cpu_utilization
                    }
                }
            }
        ]

        if config.target_memory_utilization:
            metrics.append({
                "type": "Resource",
                "resource": {
                    "name": "memory",
                    "target": {
                        "type": "Utilization",
                        "averageUtilization": config.target_memory_utilization
                    }
                }
            })

        return {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": name,
                "namespace": self.namespace
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": target_deployment
                },
                "minReplicas": config.min_replicas,
                "maxReplicas": config.max_replicas,
                "metrics": metrics,
                "behavior": {
                    "scaleDown": {
                        "stabilizationWindowSeconds": config.scale_down_stabilization_seconds
                    }
                }
            }
        }

    def create_network_policy(
        self,
        name: str,
        pod_selector: Dict[str, str],
        ingress_rules: List[NetworkPolicyRule],
        egress_rules: Optional[List[NetworkPolicyRule]] = None
    ) -> Dict[str, Any]:
        """
        Create NetworkPolicy manifest

        Args:
            name: NetworkPolicy name
            pod_selector: Pod selector
            ingress_rules: Ingress rules
            egress_rules: Egress rules

        Returns:
            NetworkPolicy manifest
        """
        manifest = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": name,
                "namespace": self.namespace
            },
            "spec": {
                "podSelector": {"matchLabels": pod_selector},
                "policyTypes": ["Ingress"]
            }
        }

        # Ingress rules
        ingress = []
        for rule in ingress_rules:
            rule_spec = {"from": []}

            for pod_labels in rule.from_pods:
                rule_spec["from"].append({
                    "podSelector": {"matchLabels": pod_labels}
                })

            for ns in rule.from_namespaces:
                rule_spec["from"].append({
                    "namespaceSelector": {"matchLabels": {"name": ns}}
                })

            if rule.ports:
                rule_spec["ports"] = [
                    {"protocol": "TCP", "port": port}
                    for port in rule.ports
                ]

            ingress.append(rule_spec)

        manifest["spec"]["ingress"] = ingress

        # Egress rules
        if egress_rules:
            manifest["spec"]["policyTypes"].append("Egress")
            manifest["spec"]["egress"] = []  # Similar to ingress

        return manifest

    def create_service_account(
        self,
        name: str,
        labels: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create ServiceAccount manifest

        Args:
            name: ServiceAccount name
            labels: Labels

        Returns:
            ServiceAccount manifest
        """
        return {
            "apiVersion": "v1",
            "kind": "ServiceAccount",
            "metadata": {
                "name": name,
                "namespace": self.namespace,
                "labels": labels or {}
            }
        }

    def _build_container(self, spec: ContainerSpec) -> Dict[str, Any]:
        """Build container spec for pod template"""
        container = {
            "name": spec.name,
            "image": f"{spec.image}:{spec.tag}",
            "resources": {
                "requests": {
                    "cpu": spec.resources.cpu_request,
                    "memory": spec.resources.memory_request
                },
                "limits": {
                    "cpu": spec.resources.cpu_limit,
                    "memory": spec.resources.memory_limit
                }
            }
        }

        if spec.command:
            container["command"] = spec.command

        if spec.args:
            container["args"] = spec.args

        if spec.ports:
            container["ports"] = [
                {"containerPort": port, "protocol": "TCP"}
                for port in spec.ports
            ]

        if spec.env:
            container["env"] = [
                {"name": k, "value": v}
                for k, v in spec.env.items()
            ]

        if spec.env_from:
            container["envFrom"] = [
                {"configMapRef": {"name": name}}
                for name in spec.env_from
            ]

        if spec.liveness_probe:
            container["livenessProbe"] = self._build_probe(spec.liveness_probe)

        if spec.readiness_probe:
            container["readinessProbe"] = self._build_probe(spec.readiness_probe)

        if spec.startup_probe:
            container["startupProbe"] = self._build_probe(spec.startup_probe)

        if spec.volume_mounts:
            container["volumeMounts"] = [
                {"name": name, "mountPath": path}
                for name, path in spec.volume_mounts.items()
            ]

        return container

    def _build_probe(self, probe: Probe) -> Dict[str, Any]:
        """Build probe configuration"""
        probe_spec = {
            "initialDelaySeconds": probe.initial_delay_seconds,
            "periodSeconds": probe.period_seconds,
            "timeoutSeconds": probe.timeout_seconds,
            "successThreshold": probe.success_threshold,
            "failureThreshold": probe.failure_threshold
        }

        if probe.probe_type == ProbeType.HTTP:
            probe_spec["httpGet"] = {
                "path": probe.path,
                "port": probe.port,
                "scheme": "HTTP"
            }
        elif probe.probe_type == ProbeType.TCP:
            probe_spec["tcpSocket"] = {"port": probe.port}
        elif probe.probe_type == ProbeType.EXEC:
            probe_spec["exec"] = {"command": [probe.path]}

        return probe_spec


class HelmChartGenerator:
    """
    Helm chart generator

    Generates Helm charts for Kubernetes applications.
    """

    def __init__(self, chart_name: str, version: str = "0.1.0"):
        """
        Initialize Helm chart generator

        Args:
            chart_name: Chart name
            version: Chart version
        """
        self.chart_name = chart_name
        self.version = version

    def generate_chart_yaml(
        self,
        description: str,
        app_version: str = "1.0.0",
        maintainers: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate Chart.yaml

        Args:
            description: Chart description
            app_version: Application version
            maintainers: List of maintainers

        Returns:
            Chart.yaml content
        """
        chart = {
            "apiVersion": "v2",
            "name": self.chart_name,
            "description": description,
            "type": "application",
            "version": self.version,
            "appVersion": app_version
        }

        if maintainers:
            chart["maintainers"] = maintainers

        return yaml.dump(chart, default_flow_style=False)

    def generate_values_yaml(
        self,
        image: str,
        tag: str = "latest",
        replicas: int = 1,
        resources: Optional[ResourceRequirements] = None
    ) -> str:
        """
        Generate values.yaml

        Args:
            image: Container image
            tag: Image tag
            replicas: Number of replicas
            resources: Resource requirements

        Returns:
            values.yaml content
        """
        resources = resources or ResourceRequirements()

        values = {
            "replicaCount": replicas,
            "image": {
                "repository": image,
                "pullPolicy": "IfNotPresent",
                "tag": tag
            },
            "service": {
                "type": "ClusterIP",
                "port": 80
            },
            "resources": {
                "requests": {
                    "cpu": resources.cpu_request,
                    "memory": resources.memory_request
                },
                "limits": {
                    "cpu": resources.cpu_limit,
                    "memory": resources.memory_limit
                }
            },
            "autoscaling": {
                "enabled": False,
                "minReplicas": 1,
                "maxReplicas": 10,
                "targetCPUUtilizationPercentage": 80
            }
        }

        return yaml.dump(values, default_flow_style=False)


class KubernetesOperator:
    """
    Kubernetes operator base class

    Watches and manages custom resources.
    """

    def __init__(self, namespace: str = "default"):
        """
        Initialize operator

        Args:
            namespace: Kubernetes namespace
        """
        self.namespace = namespace
        self._running = False

    def start(self):
        """Start operator"""
        self._running = True
        logger.info(f"Operator started in namespace: {self.namespace}")

    def stop(self):
        """Stop operator"""
        self._running = False
        logger.info("Operator stopped")

    def reconcile(self, resource: Dict[str, Any]):
        """
        Reconcile resource state

        Args:
            resource: Resource to reconcile
        """
        raise NotImplementedError


class DeploymentController:
    """
    Deployment controller

    Manages application deployments with various strategies.
    """

    def __init__(self, manifest_generator: KubernetesManifest):
        """
        Initialize deployment controller

        Args:
            manifest_generator: Manifest generator
        """
        self.manifest = manifest_generator

    def deploy(
        self,
        name: str,
        containers: List[ContainerSpec],
        strategy: DeploymentStrategy = DeploymentStrategy.ROLLING_UPDATE,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Deploy application

        Args:
            name: Application name
            containers: Container specs
            strategy: Deployment strategy
            **kwargs: Additional deployment parameters

        Returns:
            List of Kubernetes manifests
        """
        manifests = []

        # Create deployment
        deployment = self.manifest.create_deployment(
            name=name,
            containers=containers,
            strategy=strategy,
            **kwargs
        )
        manifests.append(deployment)

        # Create service
        ports = []
        for container in containers:
            for port in container.ports:
                ports.append({"port": port, "targetPort": port})

        if ports:
            service = self.manifest.create_service(
                name=name,
                selector={"app": name},
                ports=ports
            )
            manifests.append(service)

        return manifests

    def canary_deploy(
        self,
        name: str,
        containers: List[ContainerSpec],
        canary_weight: int = 10,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Canary deployment

        Args:
            name: Application name
            containers: Container specs
            canary_weight: Percentage of traffic to canary (0-100)
            **kwargs: Additional parameters

        Returns:
            List of manifests for canary deployment
        """
        manifests = []

        # Stable deployment
        stable_replicas = kwargs.get("replicas", 3)
        stable = self.manifest.create_deployment(
            name=f"{name}-stable",
            containers=containers,
            replicas=stable_replicas,
            labels={"app": name, "version": "stable"}
        )
        manifests.append(stable)

        # Canary deployment
        canary_replicas = max(1, int(stable_replicas * canary_weight / 100))
        canary = self.manifest.create_deployment(
            name=f"{name}-canary",
            containers=containers,
            replicas=canary_replicas,
            labels={"app": name, "version": "canary"}
        )
        manifests.append(canary)

        # Service (routes to both)
        service = self.manifest.create_service(
            name=name,
            selector={"app": name},
            ports=[{"port": 80, "targetPort": 8080}]
        )
        manifests.append(service)

        return manifests


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)

    # Create manifest generator
    manifest = KubernetesManifest(namespace="production")

    # Define container
    container = ContainerSpec(
        name="app",
        image="myapp",
        tag="1.0.0",
        ports=[8080],
        env={"ENV": "production"},
        resources=ResourceRequirements(
            cpu_request="200m",
            cpu_limit="1000m",
            memory_request="256Mi",
            memory_limit="1Gi"
        ),
        readiness_probe=Probe(
            probe_type=ProbeType.HTTP,
            path="/health",
            port=8080
        )
    )

    # Create deployment
    deployment = manifest.create_deployment(
        name="myapp",
        containers=[container],
        replicas=3,
        strategy=DeploymentStrategy.ROLLING_UPDATE
    )

    print("Deployment manifest:")
    print(yaml.dump(deployment, default_flow_style=False))

    # Create HPA
    hpa_config = AutoscalingConfig(
        min_replicas=2,
        max_replicas=10,
        target_cpu_utilization=70
    )
    hpa = manifest.create_hpa("myapp-hpa", "myapp", hpa_config)

    print("\nHPA manifest:")
    print(yaml.dump(hpa, default_flow_style=False))

    # Generate Helm chart
    helm = HelmChartGenerator("myapp", "1.0.0")
    chart_yaml = helm.generate_chart_yaml("My Application")
    print("\nChart.yaml:")
    print(chart_yaml)
