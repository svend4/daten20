"""
Content Generation Module

AI-powered content creation including document templates, auto-completion,
title generation, translation, paraphrasing, and grammar correction.

Part of v3.5 AI/ML Services implementation.
"""

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from .llm_integration import get_llm_client, PromptTemplate

logger = logging.getLogger(__name__)


class GenerationType(Enum):
    """Content generation types."""
    TEMPLATE = "template"
    COMPLETION = "completion"
    TITLE = "title"
    SUMMARY = "summary"
    TRANSLATION = "translation"
    PARAPHRASE = "paraphrase"
    GRAMMAR_FIX = "grammar_fix"
    STYLE_TRANSFER = "style_transfer"


class ContentStyle(Enum):
    """Content writing styles."""
    FORMAL = "formal"
    CASUAL = "casual"
    TECHNICAL = "technical"
    CREATIVE = "creative"
    BUSINESS = "business"
    ACADEMIC = "academic"


@dataclass
class GenerationConfig:
    """Configuration for content generation."""
    max_tokens: int = 500
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    style: ContentStyle = ContentStyle.FORMAL


@dataclass
class GeneratedContent:
    """Generated content result."""
    content: str
    generation_type: GenerationType
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.8


class TemplateGenerator:
    """Generate document templates."""

    TEMPLATES = {
        'business_letter': """[Your Name]
[Your Title]
[Your Company]
[Date]

[Recipient Name]
[Recipient Title]
[Recipient Company]
[Recipient Address]

Dear [Recipient Name],

{body}

Sincerely,
[Your Name]
""",
        'meeting_minutes': """Meeting Minutes
Date: {date}
Time: {time}
Location: {location}
Attendees: {attendees}

Agenda:
{agenda}

Discussion:
{discussion}

Action Items:
{action_items}

Next Meeting: {next_meeting}
""",
        'project_proposal': """Project Proposal: {title}

Executive Summary:
{executive_summary}

Background:
{background}

Objectives:
{objectives}

Methodology:
{methodology}

Timeline:
{timeline}

Budget:
{budget}

Conclusion:
{conclusion}
""",
        'technical_doc': """# {title}

## Overview
{overview}

## Requirements
{requirements}

## Architecture
{architecture}

## Implementation
{implementation}

## Testing
{testing}

## Deployment
{deployment}

## Maintenance
{maintenance}
""",
        'report': """# {title}

**Date:** {date}
**Author:** {author}

## Executive Summary
{executive_summary}

## Introduction
{introduction}

## Methodology
{methodology}

## Findings
{findings}

## Analysis
{analysis}

## Conclusions
{conclusions}

## Recommendations
{recommendations}
"""
    }

    async def generate(
        self,
        template_type: str,
        context: Optional[Dict[str, str]] = None,
        use_llm: bool = True
    ) -> GeneratedContent:
        """Generate document from template."""
        if template_type not in self.TEMPLATES:
            raise ValueError(f"Unknown template type: {template_type}")

        template = self.TEMPLATES[template_type]

        if use_llm and context:
            # Use LLM to generate content for placeholders
            filled_content = await self._fill_with_llm(template, context, template_type)
        elif context:
            # Simple placeholder replacement
            filled_content = template.format(**context)
        else:
            # Return template as-is
            filled_content = template

        return GeneratedContent(
            content=filled_content,
            generation_type=GenerationType.TEMPLATE,
            metadata={'template_type': template_type}
        )

    async def _fill_with_llm(
        self,
        template: str,
        context: Dict[str, str],
        template_type: str
    ) -> str:
        """Fill template placeholders using LLM."""
        client = get_llm_client()

        # Find placeholders
        placeholders = re.findall(r'\{(\w+)\}', template)

        filled = template

        for placeholder in placeholders:
            if placeholder in context:
                # Use provided value
                filled = filled.replace(f'{{{placeholder}}}', context[placeholder])
            else:
                # Generate with LLM
                prompt = f"""Generate content for the '{placeholder}' section of a {template_type}.
Context: {context}

Write 2-3 sentences for the {placeholder} section:"""

                try:
                    response = await client.complete(prompt, max_tokens=150)
                    generated_text = response.content.strip()
                    filled = filled.replace(f'{{{placeholder}}}', generated_text)
                except Exception as e:
                    logger.warning(f"Failed to generate {placeholder}: {e}")
                    filled = filled.replace(f'{{{placeholder}}}', f'[{placeholder}]')

        return filled


class AutoCompleter:
    """Text auto-completion."""

    async def complete(
        self,
        text: str,
        num_suggestions: int = 3,
        max_tokens: int = 50
    ) -> List[str]:
        """Generate auto-complete suggestions."""
        client = get_llm_client()

        prompt = f"""Continue this text with a natural completion:

{text}

Provide {num_suggestions} different completions:"""

        try:
            response = await client.complete(prompt, max_tokens=max_tokens * num_suggestions)

            # Parse suggestions
            suggestions = self._parse_suggestions(response.content, num_suggestions)

            return suggestions

        except Exception as e:
            logger.error(f"Auto-completion failed: {e}")
            return []

    def _parse_suggestions(self, response: str, num: int) -> List[str]:
        """Parse multiple suggestions from response."""
        # Split by newlines and filter empty
        lines = [line.strip() for line in response.split('\n') if line.strip()]

        # Remove numbering if present
        suggestions = []
        for line in lines[:num]:
            # Remove patterns like "1. ", "- ", etc.
            clean_line = re.sub(r'^\d+\.\s*', '', line)
            clean_line = re.sub(r'^[-*•]\s*', '', clean_line)
            suggestions.append(clean_line)

        return suggestions


class TitleGenerator:
    """Generate titles for documents."""

    async def generate(
        self,
        content: str,
        num_suggestions: int = 5,
        style: ContentStyle = ContentStyle.FORMAL
    ) -> List[str]:
        """Generate title suggestions."""
        client = get_llm_client()

        # Truncate content for prompt
        content_preview = content[:500]

        prompt = f"""Generate {num_suggestions} {style.value} titles for this document:

{content_preview}

Titles:"""

        try:
            response = await client.complete(prompt, max_tokens=100)

            # Parse titles
            titles = self._parse_titles(response.content)

            return titles[:num_suggestions]

        except Exception as e:
            logger.error(f"Title generation failed: {e}")
            return [self._generate_simple_title(content)]

    def _parse_titles(self, response: str) -> List[str]:
        """Parse titles from response."""
        lines = [line.strip() for line in response.split('\n') if line.strip()]

        titles = []
        for line in lines:
            # Remove numbering and quotes
            clean_title = re.sub(r'^\d+\.\s*', '', line)
            clean_title = re.sub(r'^[-*•]\s*', '', clean_title)
            clean_title = clean_title.strip('"\'')

            if clean_title:
                titles.append(clean_title)

        return titles

    def _generate_simple_title(self, content: str) -> str:
        """Generate simple title from first sentence."""
        sentences = re.split(r'[.!?]', content)
        first_sentence = sentences[0].strip() if sentences else "Untitled Document"

        # Truncate to reasonable length
        if len(first_sentence) > 60:
            first_sentence = first_sentence[:57] + "..."

        return first_sentence


class Translator:
    """Text translation."""

    LANGUAGES = {
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'zh': 'Chinese',
        'ja': 'Japanese',
        'ko': 'Korean'
    }

    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> GeneratedContent:
        """Translate text between languages."""
        if source_lang not in self.LANGUAGES:
            raise ValueError(f"Unsupported source language: {source_lang}")
        if target_lang not in self.LANGUAGES:
            raise ValueError(f"Unsupported target language: {target_lang}")

        client = get_llm_client()

        source_name = self.LANGUAGES[source_lang]
        target_name = self.LANGUAGES[target_lang]

        prompt = f"""Translate this text from {source_name} to {target_name}:

{text}

Translation:"""

        try:
            response = await client.complete(prompt, max_tokens=len(text.split()) * 2)

            return GeneratedContent(
                content=response.content.strip(),
                generation_type=GenerationType.TRANSLATION,
                metadata={
                    'source_lang': source_lang,
                    'target_lang': target_lang
                }
            )

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise


class Paraphraser:
    """Text paraphrasing."""

    async def paraphrase(
        self,
        text: str,
        num_variations: int = 1,
        style: Optional[ContentStyle] = None
    ) -> List[str]:
        """Generate paraphrases of text."""
        client = get_llm_client()

        style_instruction = f" in a {style.value} style" if style else ""

        prompt = f"""Paraphrase this text{style_instruction}. Provide {num_variations} different version(s):

Original: {text}

Paraphrases:"""

        try:
            response = await client.complete(prompt, max_tokens=len(text.split()) * num_variations * 2)

            # Parse paraphrases
            paraphrases = self._parse_paraphrases(response.content, num_variations)

            return paraphrases

        except Exception as e:
            logger.error(f"Paraphrasing failed: {e}")
            return [text]

    def _parse_paraphrases(self, response: str, num: int) -> List[str]:
        """Parse paraphrases from response."""
        lines = [line.strip() for line in response.split('\n') if line.strip()]

        paraphrases = []
        for line in lines[:num]:
            # Remove numbering
            clean_line = re.sub(r'^\d+\.\s*', '', line)
            clean_line = re.sub(r'^[-*•]\s*', '', clean_line)

            if clean_line and not clean_line.lower().startswith(('original:', 'paraphrase:')):
                paraphrases.append(clean_line)

        return paraphrases


class GrammarCorrector:
    """Grammar and spelling correction."""

    async def correct(self, text: str) -> GeneratedContent:
        """Correct grammar and spelling."""
        client = get_llm_client()

        prompt = f"""Correct any grammar and spelling errors in this text. Only output the corrected text:

{text}

Corrected:"""

        try:
            response = await client.complete(prompt, max_tokens=len(text.split()) * 2)

            corrected_text = response.content.strip()

            # Calculate changes
            changes = self._find_changes(text, corrected_text)

            return GeneratedContent(
                content=corrected_text,
                generation_type=GenerationType.GRAMMAR_FIX,
                metadata={'changes': changes}
            )

        except Exception as e:
            logger.error(f"Grammar correction failed: {e}")
            return GeneratedContent(
                content=text,
                generation_type=GenerationType.GRAMMAR_FIX,
                metadata={'error': str(e)}
            )

    def _find_changes(self, original: str, corrected: str) -> List[Dict[str, str]]:
        """Find differences between original and corrected text."""
        # Simple word-level diff
        original_words = original.split()
        corrected_words = corrected.split()

        changes = []

        if original_words != corrected_words:
            changes.append({
                'type': 'modification',
                'description': 'Text was modified for grammar/spelling'
            })

        return changes


class StyleTransfer:
    """Transfer text to different writing styles."""

    async def transfer(
        self,
        text: str,
        target_style: ContentStyle
    ) -> GeneratedContent:
        """Transfer text to target style."""
        client = get_llm_client()

        prompt = f"""Rewrite this text in a {target_style.value} style:

Original: {text}

{target_style.value.capitalize()} version:"""

        try:
            response = await client.complete(prompt, max_tokens=len(text.split()) * 2)

            return GeneratedContent(
                content=response.content.strip(),
                generation_type=GenerationType.STYLE_TRANSFER,
                metadata={'target_style': target_style.value}
            )

        except Exception as e:
            logger.error(f"Style transfer failed: {e}")
            return GeneratedContent(
                content=text,
                generation_type=GenerationType.STYLE_TRANSFER,
                metadata={'error': str(e)}
            )


class ContentExpander:
    """Expand brief content into detailed text."""

    async def expand(
        self,
        bullet_points: List[str],
        target_length: str = "medium"  # short, medium, long
    ) -> str:
        """Expand bullet points into detailed content."""
        client = get_llm_client()

        bullets_text = '\n'.join(f"- {point}" for point in bullet_points)

        length_instructions = {
            'short': '2-3 sentences per point',
            'medium': '4-5 sentences per point',
            'long': '6-8 sentences per point'
        }

        instruction = length_instructions.get(target_length, length_instructions['medium'])

        prompt = f"""Expand these bullet points into a detailed text. Write {instruction}:

{bullets_text}

Detailed text:"""

        try:
            response = await client.complete(prompt, max_tokens=500)
            return response.content.strip()

        except Exception as e:
            logger.error(f"Content expansion failed: {e}")
            return bullets_text


class ContentCondenser:
    """Condense detailed content into brief points."""

    async def condense(
        self,
        text: str,
        num_points: int = 5
    ) -> List[str]:
        """Condense text into key bullet points."""
        client = get_llm_client()

        prompt = f"""Condense this text into {num_points} concise bullet points:

{text}

Bullet points:"""

        try:
            response = await client.complete(prompt, max_tokens=200)

            # Parse bullet points
            lines = response.content.strip().split('\n')
            points = []

            for line in lines:
                line = line.strip()
                # Remove bullet markers
                line = re.sub(r'^[-*•]\s*', '', line)
                line = re.sub(r'^\d+\.\s*', '', line)

                if line:
                    points.append(line)

            return points[:num_points]

        except Exception as e:
            logger.error(f"Content condensing failed: {e}")
            return []


class ContentGenerator:
    """Main content generation service."""

    def __init__(self):
        self.template_generator = TemplateGenerator()
        self.auto_completer = AutoCompleter()
        self.title_generator = TitleGenerator()
        self.translator = Translator()
        self.paraphraser = Paraphraser()
        self.grammar_corrector = GrammarCorrector()
        self.style_transfer = StyleTransfer()
        self.expander = ContentExpander()
        self.condenser = ContentCondenser()

    async def generate_from_template(
        self,
        template_type: str,
        context: Optional[Dict[str, str]] = None
    ) -> GeneratedContent:
        """Generate content from template."""
        return await self.template_generator.generate(template_type, context)

    async def auto_complete(
        self,
        text: str,
        num_suggestions: int = 3
    ) -> List[str]:
        """Auto-complete text."""
        return await self.auto_completer.complete(text, num_suggestions)

    async def generate_title(
        self,
        content: str,
        num_suggestions: int = 5
    ) -> List[str]:
        """Generate title suggestions."""
        return await self.title_generator.generate(content, num_suggestions)

    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> GeneratedContent:
        """Translate text."""
        return await self.translator.translate(text, source_lang, target_lang)

    async def paraphrase(
        self,
        text: str,
        num_variations: int = 1
    ) -> List[str]:
        """Paraphrase text."""
        return await self.paraphraser.paraphrase(text, num_variations)

    async def correct_grammar(self, text: str) -> GeneratedContent:
        """Correct grammar and spelling."""
        return await self.grammar_corrector.correct(text)

    async def transfer_style(
        self,
        text: str,
        target_style: ContentStyle
    ) -> GeneratedContent:
        """Transfer text to different style."""
        return await self.style_transfer.transfer(text, target_style)

    async def expand_content(
        self,
        bullet_points: List[str],
        target_length: str = "medium"
    ) -> str:
        """Expand bullet points."""
        return await self.expander.expand(bullet_points, target_length)

    async def condense_content(
        self,
        text: str,
        num_points: int = 5
    ) -> List[str]:
        """Condense text to bullet points."""
        return await self.condenser.condense(text, num_points)


# Singleton instance
_content_generator: Optional[ContentGenerator] = None


def get_content_generator() -> ContentGenerator:
    """Get or create content generator."""
    global _content_generator

    if _content_generator is None:
        _content_generator = ContentGenerator()

    return _content_generator
