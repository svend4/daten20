"""Document parser for template analysis"""

import re
from typing import List, Dict, Tuple, Optional
from ..models.template import (
    TemplateStructure, Block, Section, Variable,
    TemplateStats, ValidationResult
)
from ..utils.constants import TEMPLATE_BLOCKS, VARIABLE_PATTERN
from ..utils.helpers import extract_variables


class TemplateParser:
    """Parser for mega-template documents"""

    def __init__(self, template_path: str):
        """
        Initialize parser

        Args:
            template_path: Path to template file
        """
        self.template_path = template_path
        self.lines: List[str] = []
        self.structure: Optional[TemplateStructure] = None

    def load(self) -> None:
        """Load template file into memory"""
        with open(self.template_path, 'r', encoding='utf-8') as f:
            self.lines = f.readlines()

    def parse(self) -> TemplateStructure:
        """
        Parse template and extract structure

        Returns:
            TemplateStructure object
        """
        if not self.lines:
            self.load()

        structure = TemplateStructure()
        structure.total_lines = len(self.lines)

        # Parse blocks
        blocks = self._parse_blocks()
        structure.blocks = blocks
        structure.total_blocks = len(blocks)

        # Extract all variables
        all_vars = []
        for block in blocks:
            all_vars.extend(block.variables)
        structure.all_variables = all_vars
        structure.total_variables = len(all_vars)

        # Count sections
        total_sections = sum(len(block.sections) for block in blocks)
        structure.total_sections = total_sections

        # Metadata
        structure.metadata = self._extract_metadata()

        self.structure = structure
        return structure

    def _parse_blocks(self) -> List[Block]:
        """Parse all blocks from template"""
        blocks = []
        current_block = None
        current_section_lines = []
        in_block = False

        for i, line in enumerate(self.lines):
            line_stripped = line.strip()

            # Check for block headers
            block_match = self._match_block_header(line_stripped)
            if block_match is not None:
                # Save previous block
                if current_block is not None:
                    if current_section_lines:
                        self._add_section_to_block(current_block, current_section_lines)
                    blocks.append(current_block)

                # Start new block
                block_id, block_title = block_match
                current_block = Block(
                    id=block_id,
                    title=block_title,
                    description=""
                )
                current_section_lines = []
                in_block = True
                continue

            # Collect lines for sections
            if in_block and current_block is not None:
                # Check for section divider
                if line_stripped == "---" or line_stripped.startswith("---"):
                    if current_section_lines:
                        self._add_section_to_block(current_block, current_section_lines)
                        current_section_lines = []
                    continue

                current_section_lines.append(line)

        # Save last block
        if current_block is not None:
            if current_section_lines:
                self._add_section_to_block(current_block, current_section_lines)
            blocks.append(current_block)

        return blocks

    def _match_block_header(self, line: str) -> Optional[Tuple[int, str]]:
        """
        Match block header and extract ID and title

        Args:
            line: Line to match

        Returns:
            Tuple of (block_id, title) or None
        """
        # Match "0. ПАСПОРТ..." or "БЛОК I: ..."
        if line.startswith("0. "):
            title = line[3:].strip()
            if "ПАСПОРТ" in title:
                return (0, title)

        # Roman numerals for blocks I-X
        roman_map = {
            "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5,
            "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10
        }

        for roman, num in roman_map.items():
            if line.startswith(f"БЛОК {roman}:"):
                title = line.split(":", 1)[1].strip()
                return (num, title)

        return None

    def _add_section_to_block(self, block: Block, section_lines: List[str]) -> None:
        """
        Add section to block and extract variables

        Args:
            block: Block to add section to
            section_lines: Lines of the section
        """
        content = "".join(section_lines)

        # Extract section header (first non-empty line)
        section_title = ""
        for line in section_lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("---"):
                section_title = stripped
                break

        # Create section
        section_id = f"{block.id}.{len(block.sections) + 1}"
        section = Section(
            id=section_id,
            title=section_title,
            content=content
        )

        # Extract variables from section
        var_names = extract_variables(content)
        for var_name in var_names:
            var = Variable(
                name=var_name,
                block_id=block.id,
                section=section_id
            )
            section.variables.append(var)
            block.variables.append(var)

        block.sections.append(section)

    def _extract_metadata(self) -> Dict[str, str]:
        """Extract metadata from template"""
        metadata = {}

        # Get title from first line
        if self.lines:
            metadata["title"] = self.lines[0].strip()

        # Look for description in first few lines
        if len(self.lines) > 2:
            metadata["description"] = self.lines[2].strip()

        return metadata

    def get_block_content(self, block_id: int) -> str:
        """
        Get content of a specific block

        Args:
            block_id: ID of block to retrieve

        Returns:
            Block content as string
        """
        if self.structure is None:
            self.parse()

        block = self.structure.get_block(block_id)
        if block is None:
            return ""

        # Combine all section contents
        content_parts = [f"БЛОК {block_id}: {block.title}\n\n"]
        for section in block.sections:
            content_parts.append(section.content)

        return "".join(content_parts)

    def get_all_variables(self) -> List[Variable]:
        """
        Get all variables from template

        Returns:
            List of all variables
        """
        if self.structure is None:
            self.parse()

        return self.structure.all_variables

    def get_variables_by_block(self, block_id: int) -> List[Variable]:
        """
        Get variables for specific block

        Args:
            block_id: Block ID

        Returns:
            List of variables in that block
        """
        if self.structure is None:
            self.parse()

        block = self.structure.get_block(block_id)
        if block is None:
            return []

        return block.variables

    def get_statistics(self) -> TemplateStats:
        """
        Get template statistics

        Returns:
            TemplateStats object
        """
        if self.structure is None:
            self.parse()

        stats = TemplateStats()
        stats.total_lines = self.structure.total_lines
        stats.total_blocks = self.structure.total_blocks
        stats.total_sections = self.structure.total_sections
        stats.total_variables = len(self.structure.all_variables)

        # Count unique variables
        unique_vars = set(var.name for var in self.structure.all_variables)
        stats.unique_variables = len(unique_vars)

        # Count by block
        for block in self.structure.blocks:
            stats.blocks_summary[block.id] = block.title
            stats.variables_by_block[block.id] = len(block.variables)

        # Calculate total characters
        stats.total_characters = sum(len(line) for line in self.lines)

        return stats

    def search_content(self, query: str, case_sensitive: bool = False) -> List[Tuple[int, str]]:
        """
        Search for text in template

        Args:
            query: Search query
            case_sensitive: Whether search is case-sensitive

        Returns:
            List of (line_number, line_content) tuples
        """
        results = []
        search_query = query if case_sensitive else query.lower()

        for i, line in enumerate(self.lines, 1):
            search_line = line if case_sensitive else line.lower()
            if search_query in search_line:
                results.append((i, line.strip()))

        return results
