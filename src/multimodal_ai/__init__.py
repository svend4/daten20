"""
Multimodal AI Platform v17.0

Comprehensive system for processing, understanding, and generating content
across multiple modalities (vision, language, audio, video).

This module provides:
- Multimodal encoders for vision, language, audio, video
- Cross-modal attention and fusion mechanisms
- Vision-language models (captioning, VQA, visual reasoning)
- Audio-visual processing (speech recognition, sound localization)
- Multimodal generation (text-to-image, image-to-text, TTS)
- Multimodal alignment and grounding (temporal/spatial)
- Multimodal retrieval and search (cross-modal search)

Example usage:
    from multimodal_ai import get_multimodal_encoder_system

    encoder = get_multimodal_encoder_system()

    # Encode image
    image_encoding = await encoder.encode_vision(image_data)

    # Encode text
    text_encoding = await encoder.encode_language("A cat sitting on a table")

    # Compute cross-modal similarity
    similarity = np.dot(image_encoding.embedding, text_encoding.embedding)
"""

__version__ = "17.0.0"
__author__ = "Document Management System Team"

# Import main service classes
from .multimodal_ai_services import (  # Core Systems; Enums; Data Classes; Singleton Getters
    AudioVisualProcessing,
    CrossModalAttention,
    CrossModalAttentionFusion,
    EncoderType,
    FusionStrategy,
    GeneratedContent,
    GenerationType,
    GroundingResult,
    ImageCaption,
    ModalityEncoding,
    ModalityType,
    MultimodalAlignmentGrounding,
    MultimodalEncoderSystem,
    MultimodalGeneration,
    MultimodalRetrievalSearch,
    RetrievalResult,
    VisionLanguageModels,
    VQAResult,
    get_audio_visual_processing,
    get_cross_modal_attention_fusion,
    get_multimodal_alignment_grounding,
    get_multimodal_encoder_system,
    get_multimodal_generation,
    get_multimodal_retrieval_search,
    get_vision_language_models,
)

__all__ = [
    # Version
    "__version__",
    # Core Systems
    "MultimodalEncoderSystem",
    "CrossModalAttentionFusion",
    "VisionLanguageModels",
    "AudioVisualProcessing",
    "MultimodalGeneration",
    "MultimodalAlignmentGrounding",
    "MultimodalRetrievalSearch",
    # Enums
    "ModalityType",
    "EncoderType",
    "FusionStrategy",
    "GenerationType",
    # Data Classes
    "ModalityEncoding",
    "CrossModalAttention",
    "ImageCaption",
    "VQAResult",
    "GeneratedContent",
    "GroundingResult",
    "RetrievalResult",
    # Singleton Getters
    "get_multimodal_encoder_system",
    "get_cross_modal_attention_fusion",
    "get_vision_language_models",
    "get_audio_visual_processing",
    "get_multimodal_generation",
    "get_multimodal_alignment_grounding",
    "get_multimodal_retrieval_search",
]
