"""Template data models"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class Variable:
    """Represents a template variable"""

    name: str
    description: str = ""
    value: Optional[str] = None
    required: bool = False
    data_type: str = "string"  # string, number, date, email, phone, etc.
    block_id: Optional[int] = None
    section: Optional[str] = None


@dataclass
class Section:
    """Represents a section within a block"""

    id: str
    title: str
    content: str
    variables: List[Variable] = field(default_factory=list)
    subsections: List["Section"] = field(default_factory=list)


@dataclass
class Block:
    """Represents a major block in the template"""

    id: int
    title: str
    description: str = ""
    sections: List[Section] = field(default_factory=list)
    variables: List[Variable] = field(default_factory=list)


@dataclass
class TemplateStructure:
    """Complete template structure"""

    blocks: List[Block] = field(default_factory=list)
    all_variables: List[Variable] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)
    total_lines: int = 0
    total_blocks: int = 0
    total_sections: int = 0
    total_variables: int = 0

    def get_block(self, block_id: int) -> Optional[Block]:
        """Get block by ID"""
        for block in self.blocks:
            if block.id == block_id:
                return block
        return None

    def get_variable(self, var_name: str) -> Optional[Variable]:
        """Get variable by name"""
        for var in self.all_variables:
            if var.name == var_name:
                return var
        return None

    def get_unfilled_variables(self) -> List[Variable]:
        """Get list of variables that haven't been filled"""
        return [var for var in self.all_variables if var.value is None and var.required]

    def get_completion_percentage(self) -> float:
        """Calculate completion percentage"""
        if not self.all_variables:
            return 100.0

        filled = sum(1 for var in self.all_variables if var.value is not None)
        return (filled / len(self.all_variables)) * 100


@dataclass
class TemplateStats:
    """Statistics about a template"""

    total_lines: int = 0
    total_characters: int = 0
    total_blocks: int = 0
    total_sections: int = 0
    total_variables: int = 0
    unique_variables: int = 0
    required_variables: int = 0
    filled_variables: int = 0
    completion_percentage: float = 0.0
    blocks_summary: Dict[int, str] = field(default_factory=dict)
    variables_by_block: Dict[int, int] = field(default_factory=dict)
    variables_by_type: Dict[str, int] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Result of template validation"""

    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    missing_required: List[str] = field(default_factory=list)
    invalid_values: Dict[str, str] = field(default_factory=dict)

    def add_error(self, message: str):
        """Add an error"""
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str):
        """Add a warning"""
        self.warnings.append(message)

    def add_missing(self, field: str):
        """Add missing required field"""
        self.missing_required.append(field)
        self.is_valid = False

    def add_invalid(self, field: str, reason: str):
        """Add invalid value"""
        self.invalid_values[field] = reason
        self.is_valid = False
