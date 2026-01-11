"""
Workflow Engine

Provides visual workflow designer and execution engine for business processes:
- Workflow definition with nodes and transitions
- State management and execution
- Task assignment and notifications
- Parallel and sequential execution
- Conditional branching
- Workflow templates and monitoring
"""

from typing import Optional, List, Dict, Any, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import json


class NodeType(str, Enum):
    """Workflow node types"""
    START = "start"
    END = "end"
    TASK = "task"
    DECISION = "decision"
    PARALLEL = "parallel"
    JOIN = "join"
    SCRIPT = "script"
    EMAIL = "email"
    APPROVAL = "approval"
    TIMER = "timer"


class TaskStatus(str, Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class WorkflowStatus(str, Enum):
    """Workflow instance status"""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AssignmentType(str, Enum):
    """Task assignment types"""
    USER = "user"
    ROLE = "role"
    GROUP = "group"
    AUTO = "auto"


@dataclass
class WorkflowNode:
    """Workflow node definition"""
    id: str
    type: NodeType
    name: str
    description: str = ""
    config: Dict[str, Any] = field(default_factory=dict)
    position: Dict[str, int] = field(default_factory=dict)  # x, y for visual designer


@dataclass
class WorkflowTransition:
    """Transition between nodes"""
    id: str
    from_node: str
    to_node: str
    condition: Optional[str] = None  # Expression to evaluate
    label: str = ""


@dataclass
class WorkflowDefinition:
    """Workflow definition"""
    id: str
    name: str
    description: str
    version: str
    nodes: List[WorkflowNode] = field(default_factory=list)
    transitions: List[WorkflowTransition] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[int] = None
    active: bool = True


@dataclass
class TaskInstance:
    """Task instance in workflow execution"""
    id: str
    workflow_instance_id: str
    node_id: str
    node_name: str
    status: TaskStatus
    assigned_to: Optional[int] = None
    assigned_type: AssignmentType = AssignmentType.AUTO
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    data: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Any] = None
    error: Optional[str] = None


@dataclass
class WorkflowInstance:
    """Workflow execution instance"""
    id: str
    workflow_id: str
    workflow_name: str
    status: WorkflowStatus
    current_nodes: List[str]  # Current active nodes (for parallel execution)
    variables: Dict[str, Any] = field(default_factory=dict)
    tasks: List[TaskInstance] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    started_by: Optional[int] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


@dataclass
class WorkflowTemplate:
    """Pre-built workflow template"""
    id: str
    name: str
    description: str
    category: str
    definition: WorkflowDefinition
    icon: str = "📋"
    tags: List[str] = field(default_factory=list)


class ConditionEvaluator:
    """Evaluates conditions for transitions"""

    def evaluate(self, condition: str, variables: Dict[str, Any]) -> bool:
        """Evaluate condition expression"""
        if not condition:
            return True

        # Simple expression evaluator
        # In production, use safer evaluation (e.g., ast.literal_eval with restrictions)

        try:
            # Replace variable references
            for var_name, var_value in variables.items():
                if isinstance(var_value, str):
                    condition = condition.replace(f"{{{var_name}}}", f"'{var_value}'")
                else:
                    condition = condition.replace(f"{{{var_name}}}", str(var_value))

            # Evaluate
            result = eval(condition, {"__builtins__": {}}, {})
            return bool(result)

        except Exception as e:
            print(f"Error evaluating condition '{condition}': {e}")
            return False


class WorkflowExecutor:
    """Executes workflow instances"""

    def __init__(self):
        self.condition_evaluator = ConditionEvaluator()
        self.task_handlers: Dict[NodeType, Callable] = {}
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default task handlers"""
        self.task_handlers[NodeType.START] = self._handle_start
        self.task_handlers[NodeType.END] = self._handle_end
        self.task_handlers[NodeType.TASK] = self._handle_task
        self.task_handlers[NodeType.DECISION] = self._handle_decision
        self.task_handlers[NodeType.SCRIPT] = self._handle_script
        self.task_handlers[NodeType.EMAIL] = self._handle_email
        self.task_handlers[NodeType.APPROVAL] = self._handle_approval
        self.task_handlers[NodeType.TIMER] = self._handle_timer

    def register_handler(self, node_type: NodeType, handler: Callable):
        """Register custom task handler"""
        self.task_handlers[node_type] = handler

    def execute_node(
        self,
        workflow_def: WorkflowDefinition,
        instance: WorkflowInstance,
        node: WorkflowNode
    ) -> bool:
        """Execute a workflow node"""
        # Get handler
        handler = self.task_handlers.get(node.type)
        if not handler:
            print(f"No handler for node type: {node.type}")
            return False

        # Create task instance
        task = TaskInstance(
            id=str(uuid.uuid4()),
            workflow_instance_id=instance.id,
            node_id=node.id,
            node_name=node.name,
            status=TaskStatus.PENDING,
            started_at=datetime.now()
        )

        instance.tasks.append(task)

        # Execute handler
        try:
            task.status = TaskStatus.IN_PROGRESS
            result = handler(workflow_def, instance, node, task)

            if result:
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now()
                return True
            else:
                task.status = TaskStatus.FAILED
                return False

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            print(f"Error executing node '{node.name}': {e}")
            return False

    def _handle_start(
        self,
        workflow_def: WorkflowDefinition,
        instance: WorkflowInstance,
        node: WorkflowNode,
        task: TaskInstance
    ) -> bool:
        """Handle START node"""
        print(f"[Workflow] Starting workflow: {instance.workflow_name}")
        return True

    def _handle_end(
        self,
        workflow_def: WorkflowDefinition,
        instance: WorkflowInstance,
        node: WorkflowNode,
        task: TaskInstance
    ) -> bool:
        """Handle END node"""
        print(f"[Workflow] Completing workflow: {instance.workflow_name}")
        instance.status = WorkflowStatus.COMPLETED
        instance.completed_at = datetime.now()
        return True

    def _handle_task(
        self,
        workflow_def: WorkflowDefinition,
        instance: WorkflowInstance,
        node: WorkflowNode,
        task: TaskInstance
    ) -> bool:
        """Handle TASK node"""
        # Get assignment from config
        config = node.config
        assigned_to = config.get('assigned_to')
        assignment_type = AssignmentType(config.get('assignment_type', 'auto'))

        task.assigned_to = assigned_to
        task.assigned_type = assignment_type

        # Set due date if specified
        if 'due_days' in config:
            task.due_date = datetime.now() + timedelta(days=config['due_days'])

        print(f"[Workflow] Task created: {node.name} (assigned to: {assigned_to})")

        # Task waits for manual completion
        # Return True to allow workflow to continue (for auto tasks)
        # Return False to wait for manual completion
        return assignment_type == AssignmentType.AUTO

    def _handle_decision(
        self,
        workflow_def: WorkflowDefinition,
        instance: WorkflowInstance,
        node: WorkflowNode,
        task: TaskInstance
    ) -> bool:
        """Handle DECISION node"""
        print(f"[Workflow] Evaluating decision: {node.name}")
        # Decision logic handled in transition evaluation
        return True

    def _handle_script(
        self,
        workflow_def: WorkflowDefinition,
        instance: WorkflowInstance,
        node: WorkflowNode,
        task: TaskInstance
    ) -> bool:
        """Handle SCRIPT node"""
        script = node.config.get('script', '')
        print(f"[Workflow] Executing script: {node.name}")

        # In production, use sandboxed execution
        # For now, just log
        task.result = f"Script executed: {script[:50]}..."
        return True

    def _handle_email(
        self,
        workflow_def: WorkflowDefinition,
        instance: WorkflowInstance,
        node: WorkflowNode,
        task: TaskInstance
    ) -> bool:
        """Handle EMAIL node"""
        to = node.config.get('to', '')
        subject = node.config.get('subject', '')
        body = node.config.get('body', '')

        # Replace variables in email
        for var_name, var_value in instance.variables.items():
            subject = subject.replace(f"{{{var_name}}}", str(var_value))
            body = body.replace(f"{{{var_name}}}", str(var_value))

        print(f"[Workflow] Sending email to {to}: {subject}")
        # Would integrate with email notification system

        task.result = f"Email sent to {to}"
        return True

    def _handle_approval(
        self,
        workflow_def: WorkflowDefinition,
        instance: WorkflowInstance,
        node: WorkflowNode,
        task: TaskInstance
    ) -> bool:
        """Handle APPROVAL node"""
        approver = node.config.get('approver')
        task.assigned_to = approver
        task.assigned_type = AssignmentType.USER

        print(f"[Workflow] Approval required from user: {approver}")

        # Wait for manual approval
        return False

    def _handle_timer(
        self,
        workflow_def: WorkflowDefinition,
        instance: WorkflowInstance,
        node: WorkflowNode,
        task: TaskInstance
    ) -> bool:
        """Handle TIMER node"""
        duration_minutes = node.config.get('duration_minutes', 0)
        print(f"[Workflow] Timer set for {duration_minutes} minutes")

        # In production, schedule continuation
        return True

    def get_next_nodes(
        self,
        workflow_def: WorkflowDefinition,
        current_node_id: str,
        variables: Dict[str, Any]
    ) -> List[str]:
        """Get next nodes based on transitions and conditions"""
        next_nodes = []

        for transition in workflow_def.transitions:
            if transition.from_node != current_node_id:
                continue

            # Evaluate condition if present
            if transition.condition:
                if self.condition_evaluator.evaluate(transition.condition, variables):
                    next_nodes.append(transition.to_node)
            else:
                next_nodes.append(transition.to_node)

        return next_nodes


class WorkflowEngine:
    """Main workflow engine"""

    def __init__(self, database=None):
        self.database = database
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.instances: Dict[str, WorkflowInstance] = {}
        self.templates: Dict[str, WorkflowTemplate] = {}
        self.executor = WorkflowExecutor()

        # Create default templates
        self._create_default_templates()

    def create_workflow(
        self,
        name: str,
        description: str,
        created_by: Optional[int] = None
    ) -> str:
        """Create new workflow definition"""
        workflow_id = str(uuid.uuid4())

        workflow = WorkflowDefinition(
            id=workflow_id,
            name=name,
            description=description,
            version="1.0",
            created_by=created_by
        )

        self.workflows[workflow_id] = workflow
        return workflow_id

    def add_node(
        self,
        workflow_id: str,
        node_type: NodeType,
        name: str,
        description: str = "",
        config: Optional[Dict[str, Any]] = None,
        position: Optional[Dict[str, int]] = None
    ) -> str:
        """Add node to workflow"""
        if workflow_id not in self.workflows:
            return ""

        node_id = str(uuid.uuid4())

        node = WorkflowNode(
            id=node_id,
            type=node_type,
            name=name,
            description=description,
            config=config or {},
            position=position or {}
        )

        self.workflows[workflow_id].nodes.append(node)
        return node_id

    def add_transition(
        self,
        workflow_id: str,
        from_node_id: str,
        to_node_id: str,
        condition: Optional[str] = None,
        label: str = ""
    ) -> str:
        """Add transition between nodes"""
        if workflow_id not in self.workflows:
            return ""

        transition_id = str(uuid.uuid4())

        transition = WorkflowTransition(
            id=transition_id,
            from_node=from_node_id,
            to_node=to_node_id,
            condition=condition,
            label=label
        )

        self.workflows[workflow_id].transitions.append(transition)
        return transition_id

    def start_workflow(
        self,
        workflow_id: str,
        variables: Optional[Dict[str, Any]] = None,
        started_by: Optional[int] = None
    ) -> str:
        """Start workflow execution"""
        if workflow_id not in self.workflows:
            return ""

        workflow_def = self.workflows[workflow_id]

        # Find START node
        start_node = None
        for node in workflow_def.nodes:
            if node.type == NodeType.START:
                start_node = node
                break

        if not start_node:
            print("No START node found in workflow")
            return ""

        # Create instance
        instance_id = str(uuid.uuid4())

        instance = WorkflowInstance(
            id=instance_id,
            workflow_id=workflow_id,
            workflow_name=workflow_def.name,
            status=WorkflowStatus.RUNNING,
            current_nodes=[start_node.id],
            variables=variables or {},
            started_by=started_by
        )

        self.instances[instance_id] = instance

        # Execute START node
        self.executor.execute_node(workflow_def, instance, start_node)

        # Continue to next nodes
        self._continue_execution(instance_id)

        return instance_id

    def _continue_execution(self, instance_id: str):
        """Continue workflow execution"""
        if instance_id not in self.instances:
            return

        instance = self.instances[instance_id]
        workflow_def = self.workflows[instance.workflow_id]

        # Process current nodes
        while instance.current_nodes and instance.status == WorkflowStatus.RUNNING:
            current_node_id = instance.current_nodes.pop(0)

            # Find node
            current_node = None
            for node in workflow_def.nodes:
                if node.id == current_node_id:
                    current_node = node
                    break

            if not current_node:
                continue

            # Execute node
            success = self.executor.execute_node(workflow_def, instance, current_node)

            if not success:
                # Node failed or waiting
                if current_node.type in [NodeType.TASK, NodeType.APPROVAL]:
                    # Wait for manual completion
                    instance.status = WorkflowStatus.PAUSED
                    break
                else:
                    # Node failed
                    instance.status = WorkflowStatus.FAILED
                    break

            # Get next nodes
            next_node_ids = self.executor.get_next_nodes(
                workflow_def,
                current_node_id,
                instance.variables
            )

            # Add to queue
            instance.current_nodes.extend(next_node_ids)

    def complete_task(
        self,
        instance_id: str,
        task_id: str,
        result: Optional[Any] = None
    ) -> bool:
        """Complete a task and continue workflow"""
        if instance_id not in self.instances:
            return False

        instance = self.instances[instance_id]

        # Find task
        task = None
        for t in instance.tasks:
            if t.id == task_id:
                task = t
                break

        if not task:
            return False

        # Complete task
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now()
        task.result = result

        # Resume workflow
        if instance.status == WorkflowStatus.PAUSED:
            instance.status = WorkflowStatus.RUNNING

            # Get node that was waiting
            workflow_def = self.workflows[instance.workflow_id]
            next_node_ids = self.executor.get_next_nodes(
                workflow_def,
                task.node_id,
                instance.variables
            )

            instance.current_nodes.extend(next_node_ids)

            # Continue execution
            self._continue_execution(instance_id)

        return True

    def cancel_workflow(self, instance_id: str) -> bool:
        """Cancel workflow execution"""
        if instance_id not in self.instances:
            return False

        instance = self.instances[instance_id]
        instance.status = WorkflowStatus.CANCELLED

        return True

    def get_workflow_status(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow instance status"""
        if instance_id not in self.instances:
            return None

        instance = self.instances[instance_id]

        # Count tasks by status
        task_counts = {}
        for task in instance.tasks:
            status = task.status.value
            task_counts[status] = task_counts.get(status, 0) + 1

        # Get pending tasks
        pending_tasks = [
            {
                'id': t.id,
                'name': t.node_name,
                'assigned_to': t.assigned_to,
                'due_date': t.due_date.isoformat() if t.due_date else None
            }
            for t in instance.tasks
            if t.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]
        ]

        return {
            'instance_id': instance.id,
            'workflow_name': instance.workflow_name,
            'status': instance.status.value,
            'started_at': instance.started_at.isoformat(),
            'completed_at': instance.completed_at.isoformat() if instance.completed_at else None,
            'tasks_total': len(instance.tasks),
            'tasks_by_status': task_counts,
            'pending_tasks': pending_tasks
        }

    def _create_default_templates(self):
        """Create default workflow templates"""
        # Template 1: Document Approval
        approval_workflow = self.create_workflow(
            name="Document Approval",
            description="Standard document approval process"
        )

        start_node = self.add_node(approval_workflow, NodeType.START, "Start", position={'x': 100, 'y': 100})
        review_task = self.add_node(
            approval_workflow,
            NodeType.TASK,
            "Review Document",
            "Review document for accuracy",
            config={'assigned_to': None, 'assignment_type': 'role', 'role': 'reviewer'},
            position={'x': 300, 'y': 100}
        )
        approve_task = self.add_node(
            approval_workflow,
            NodeType.APPROVAL,
            "Manager Approval",
            "Requires manager approval",
            config={'approver': None},
            position={'x': 500, 'y': 100}
        )
        end_node = self.add_node(approval_workflow, NodeType.END, "End", position={'x': 700, 'y': 100})

        self.add_transition(approval_workflow, start_node, review_task)
        self.add_transition(approval_workflow, review_task, approve_task)
        self.add_transition(approval_workflow, approve_task, end_node)

        self.templates['doc_approval'] = WorkflowTemplate(
            id='doc_approval',
            name="Document Approval",
            description="Multi-step document approval workflow",
            category="Approval",
            definition=self.workflows[approval_workflow],
            icon="✅"
        )


# Global instance
_workflow_engine: Optional[WorkflowEngine] = None


def get_workflow_engine(database=None) -> WorkflowEngine:
    """Get global workflow engine instance"""
    global _workflow_engine

    if _workflow_engine is None:
        _workflow_engine = WorkflowEngine(database)

    return _workflow_engine


def configure_workflow_engine(database):
    """Configure workflow engine"""
    global _workflow_engine
    _workflow_engine = WorkflowEngine(database)
