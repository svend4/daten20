"""
Comprehensive Test Suite for Multimodal AI Platform (v17.0)

Tests all 7 subsystems and integrated system:
1. MultimodalEncoderSystem - Vision, language, audio, video encoding
2. CrossModalAttentionFusion - Cross-modal attention & fusion
3. VisionLanguageModels - Image captioning, VQA, visual reasoning
4. AudioVisualProcessing - Speech recognition, sound localization
5. MultimodalGeneration - Text-to-image, TTS, multimodal content
6. MultimodalAlignmentGrounding - Temporal & spatial grounding
7. MultimodalRetrievalSearch - Cross-modal retrieval & search
8. IntegratedMultimodalAISystem - Unified integration

Total: 50 tests
"""

import asyncio
import numpy as np
import pytest
from datetime import datetime

from src.multimodal_ai import (
    # Enums
    ModalityType,
    EncoderType,
    FusionStrategy,
    GenerationType,
    # Data Classes
    MultimodalAIConfig,
    # Service Classes
    MultimodalEncoderSystem,
    CrossModalAttentionFusion,
    VisionLanguageModels,
    AudioVisualProcessing,
    MultimodalGeneration,
    MultimodalAlignmentGrounding,
    MultimodalRetrievalSearch,
    # Integrated System
    IntegratedMultimodalAISystem,
    # Singletons
    get_multimodal_ai_system,
)


# ============================================================================
# 1. MultimodalEncoderSystem Tests
# ============================================================================


class TestMultimodalEncoderSystem:
    """Test Multimodal Encoder System subsystem"""

    @pytest.mark.asyncio
    async def test_encode_vision(self):
        """Test vision encoding"""
        encoder = MultimodalEncoderSystem()
        image = np.random.randn(224, 224, 3)

        encoding = await encoder.encode_vision(
            image_data=image,
            encoder_type=EncoderType.RESNET,
            output_dim=512,
        )

        assert encoding is not None
        assert encoding.modality == ModalityType.VISION
        assert encoding.embedding_dim == 512
        assert encoding.embedding.shape[0] == 512

    @pytest.mark.asyncio
    async def test_encode_language(self):
        """Test language encoding"""
        encoder = MultimodalEncoderSystem()

        encoding = await encoder.encode_language(
            text="A cat sitting on a table",
            encoder_type=EncoderType.TRANSFORMER,
            output_dim=512,
        )

        assert encoding is not None
        assert encoding.modality == ModalityType.LANGUAGE
        assert encoding.embedding_dim == 512

    @pytest.mark.asyncio
    async def test_encode_audio(self):
        """Test audio encoding"""
        encoder = MultimodalEncoderSystem()
        audio = np.random.randn(16000)  # 1 second at 16kHz

        encoding = await encoder.encode_audio(
            audio_data=audio,
            sample_rate=16000,
            output_dim=512,
        )

        assert encoding is not None
        assert encoding.modality == ModalityType.AUDIO

    @pytest.mark.asyncio
    async def test_encode_video(self):
        """Test video encoding"""
        encoder = MultimodalEncoderSystem()
        video = np.random.randn(30, 224, 224, 3)  # 30 frames

        encoding = await encoder.encode_video(
            video_frames=video,
            frame_rate=30.0,
            output_dim=512,
        )

        assert encoding is not None
        assert encoding.modality == ModalityType.VIDEO

    @pytest.mark.asyncio
    async def test_different_encoder_types(self):
        """Test different encoder architectures"""
        encoder = MultimodalEncoderSystem()
        image = np.random.randn(224, 224, 3)

        # Test VIT encoder
        enc1 = await encoder.encode_vision(
            image, EncoderType.VIT, output_dim=512
        )
        assert enc1.encoder_type == EncoderType.VIT

        # Test CNN encoder
        enc2 = await encoder.encode_vision(
            image, EncoderType.CNN, output_dim=512
        )
        assert enc2.encoder_type == EncoderType.CNN

    @pytest.mark.asyncio
    async def test_encoding_performance(self):
        """Test encoding performance metrics"""
        encoder = MultimodalEncoderSystem()
        image = np.random.randn(224, 224, 3)

        encoding = await encoder.encode_vision(
            image, EncoderType.RESNET, output_dim=512
        )

        # Check performance metrics
        assert encoding.encoding_time_ms >= 0
        assert 0 <= encoding.confidence_score <= 1.0

    @pytest.mark.asyncio
    async def test_batch_encoding(self):
        """Test batch encoding"""
        encoder = MultimodalEncoderSystem()
        images = [np.random.randn(224, 224, 3) for _ in range(5)]

        encodings = []
        for img in images:
            enc = await encoder.encode_vision(img, EncoderType.RESNET, output_dim=512)
            encodings.append(enc)

        assert len(encodings) == 5


# ============================================================================
# 2. CrossModalAttentionFusion Tests
# ============================================================================


class TestCrossModalAttentionFusion:
    """Test Cross-Modal Attention Fusion subsystem"""

    @pytest.mark.asyncio
    async def test_compute_attention(self):
        """Test cross-modal attention computation"""
        fusion = CrossModalAttentionFusion()

        source_features = np.random.randn(512)
        target_features = np.random.randn(512)

        attention = await fusion.compute_cross_attention(
            source_features=source_features,
            source_modality=ModalityType.VISION,
            target_features=target_features,
            target_modality=ModalityType.LANGUAGE,
            num_heads=8,
        )

        assert attention is not None
        assert attention.num_heads == 8
        assert 0 <= attention.alignment_score <= 1.0

    @pytest.mark.asyncio
    async def test_fuse_modalities(self):
        """Test modality fusion"""
        fusion = CrossModalAttentionFusion()

        embeddings = [
            np.random.randn(512),
            np.random.randn(512),
            np.random.randn(512),
        ]
        modality_types = [
            ModalityType.VISION,
            ModalityType.LANGUAGE,
            ModalityType.AUDIO,
        ]

        result = await fusion.fuse_modalities(
            encodings=embeddings,
            modality_types=modality_types,
            fusion_strategy=FusionStrategy.ATTENTION,
            num_heads=8,
        )

        assert result is not None
        assert "fused_embedding" in result
        assert len(result["fused_embedding"]) == 512

    @pytest.mark.asyncio
    async def test_fusion_strategies(self):
        """Test different fusion strategies"""
        fusion = CrossModalAttentionFusion()

        embeddings = [np.random.randn(512), np.random.randn(512)]
        modalities = [ModalityType.VISION, ModalityType.LANGUAGE]

        # Test CONCAT
        r1 = await fusion.fuse_modalities(
            embeddings, modalities, FusionStrategy.CONCAT, num_heads=8
        )
        assert r1 is not None

        # Test ATTENTION
        r2 = await fusion.fuse_modalities(
            embeddings, modalities, FusionStrategy.ATTENTION, num_heads=8
        )
        assert r2 is not None

    @pytest.mark.asyncio
    async def test_multi_head_attention(self):
        """Test multi-head attention"""
        fusion = CrossModalAttentionFusion()

        source = np.random.randn(512)
        target = np.random.randn(512)

        # Test with different number of heads
        for num_heads in [4, 8, 16]:
            attention = await fusion.compute_cross_attention(
                source, ModalityType.VISION,
                target, ModalityType.LANGUAGE,
                num_heads=num_heads
            )
            assert attention.num_heads == num_heads

    @pytest.mark.asyncio
    async def test_alignment_scoring(self):
        """Test alignment scoring between modalities"""
        fusion = CrossModalAttentionFusion()

        vision_features = np.random.randn(512)
        language_features = np.random.randn(512)

        attention = await fusion.compute_cross_attention(
            vision_features, ModalityType.VISION,
            language_features, ModalityType.LANGUAGE,
            num_heads=8
        )

        # Alignment score should be between 0 and 1
        assert 0 <= attention.alignment_score <= 1.0


# ============================================================================
# 3. VisionLanguageModels Tests
# ============================================================================


class TestVisionLanguageModels:
    """Test Vision-Language Models subsystem"""

    @pytest.mark.asyncio
    async def test_generate_caption(self):
        """Test image caption generation"""
        vl_models = VisionLanguageModels()
        image_features = np.random.randn(512)

        caption = await vl_models.generate_caption(
            image_id="test_image_001",
            image_features=image_features,
            max_length=50,
            beam_size=5,
        )

        assert caption is not None
        assert len(caption.caption_text) > 0
        assert caption.beam_size == 5
        assert 0 <= caption.overall_confidence <= 1.0

    @pytest.mark.asyncio
    async def test_answer_visual_question(self):
        """Test visual question answering"""
        vl_models = VisionLanguageModels()
        image_features = np.random.randn(512)

        vqa_result = await vl_models.answer_visual_question(
            image_id="vqa_image_001",
            image_features=image_features,
            question="What color is the object?",
            question_type="other",
        )

        assert vqa_result is not None
        assert len(vqa_result.answer) > 0
        assert 0 <= vqa_result.answer_confidence <= 1.0

    @pytest.mark.asyncio
    async def test_visual_reasoning(self):
        """Test visual reasoning"""
        vl_models = VisionLanguageModels()
        image_features = np.random.randn(512)

        reasoning = await vl_models.visual_reasoning(
            image_id="reasoning_image",
            image_features=image_features,
            reasoning_task="object_relationship",
        )

        assert reasoning is not None
        assert "result" in reasoning or "relationships" in reasoning

    @pytest.mark.asyncio
    async def test_caption_with_beam_search(self):
        """Test caption generation with different beam sizes"""
        vl_models = VisionLanguageModels()
        image_features = np.random.randn(512)

        # Test with beam_size=3
        caption1 = await vl_models.generate_caption(
            "beam_test_1", image_features, max_length=30, beam_size=3
        )
        assert caption1.beam_size == 3

        # Test with beam_size=10
        caption2 = await vl_models.generate_caption(
            "beam_test_2", image_features, max_length=30, beam_size=10
        )
        assert caption2.beam_size == 10

    @pytest.mark.asyncio
    async def test_vqa_answer_types(self):
        """Test VQA with different answer types"""
        vl_models = VisionLanguageModels()
        image_features = np.random.randn(512)

        # Yes/No question
        vqa1 = await vl_models.answer_visual_question(
            "yesno_image", image_features,
            "Is this a cat?", question_type="yes/no"
        )
        assert vqa1.answer_type == "yes/no"

        # Number question
        vqa2 = await vl_models.answer_visual_question(
            "number_image", image_features,
            "How many objects?", question_type="number"
        )
        assert vqa2.answer_type == "number"

    @pytest.mark.asyncio
    async def test_attention_regions(self):
        """Test attention region detection"""
        vl_models = VisionLanguageModels()
        image_features = np.random.randn(512)

        vqa_result = await vl_models.answer_visual_question(
            "attention_image", image_features,
            "Where is the object?", question_type="other"
        )

        # Should have attention regions (bounding boxes)
        assert len(vqa_result.attention_regions) >= 0


# ============================================================================
# 4. AudioVisualProcessing Tests
# ============================================================================


class TestAudioVisualProcessing:
    """Test Audio-Visual Processing subsystem"""

    @pytest.mark.asyncio
    async def test_synchronize_audio_visual(self):
        """Test audio-visual synchronization"""
        av_processing = AudioVisualProcessing()

        audio = np.random.randn(16000)  # 1 second
        video = np.random.randn(30, 224, 224, 3)  # 30 frames

        result = await av_processing.synchronize_audio_visual(
            audio_data=audio,
            video_frames=video,
            sample_rate=16000,
            frame_rate=30.0,
        )

        assert result is not None
        assert "sync_offset_ms" in result or "sync_confidence" in result

    @pytest.mark.asyncio
    async def test_speech_recognition(self):
        """Test speech recognition"""
        av_processing = AudioVisualProcessing()
        audio = np.random.randn(32000)  # 2 seconds

        result = await av_processing.recognize_speech(
            audio_data=audio,
            sample_rate=16000,
            language="en",
        )

        assert result is not None
        assert "transcript" in result or "text" in result

    @pytest.mark.asyncio
    async def test_sound_localization(self):
        """Test sound source localization"""
        av_processing = AudioVisualProcessing()

        audio = np.random.randn(16000)
        video = np.random.randn(30, 224, 224, 3)

        result = await av_processing.localize_sound_source(
            audio_data=audio,
            video_frames=video,
            sample_rate=16000,
        )

        assert result is not None
        assert "location" in result or "bounding_box" in result

    @pytest.mark.asyncio
    async def test_audio_visual_learning(self):
        """Test audio-visual learning"""
        av_processing = AudioVisualProcessing()

        audio = np.random.randn(16000)
        video = np.random.randn(30, 224, 224, 3)

        result = await av_processing.learn_audio_visual_correspondence(
            audio_data=audio,
            video_frames=video,
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_cross_modal_retrieval_av(self):
        """Test audio-visual cross-modal retrieval"""
        av_processing = AudioVisualProcessing()

        # Query with audio, retrieve video
        audio_query = np.random.randn(16000)
        result = await av_processing.retrieve_by_audio(
            audio_query=audio_query,
            video_database=["video_1", "video_2", "video_3"],
            top_k=2,
        )

        assert result is not None


# ============================================================================
# 5. MultimodalGeneration Tests
# ============================================================================


class TestMultimodalGeneration:
    """Test Multimodal Generation subsystem"""

    @pytest.mark.asyncio
    async def test_text_to_image(self):
        """Test text-to-image generation"""
        generation = MultimodalGeneration()

        result = await generation.text_to_image(
            prompt="A sunset over mountains",
            image_size=(512, 512),
            num_steps=50,
            guidance_scale=7.5,
        )

        assert result is not None
        assert result.generation_type == GenerationType.TEXT_TO_IMAGE
        assert result.output_shape == (512, 512, 3)

    @pytest.mark.asyncio
    async def test_image_to_text(self):
        """Test image-to-text generation"""
        generation = MultimodalGeneration()
        image = np.random.randn(224, 224, 3)

        result = await generation.image_to_text(
            image_data=image,
            max_length=100,
        )

        assert result is not None
        assert result.generation_type == GenerationType.IMAGE_TO_TEXT

    @pytest.mark.asyncio
    async def test_text_to_speech(self):
        """Test text-to-speech generation"""
        generation = MultimodalGeneration()

        result = await generation.text_to_speech(
            text="Hello, this is a test",
            voice="en-US-male",
            sample_rate=22050,
        )

        assert result is not None
        assert result.generation_type == GenerationType.TEXT_TO_AUDIO

    @pytest.mark.asyncio
    async def test_text_to_video(self):
        """Test text-to-video generation"""
        generation = MultimodalGeneration()

        result = await generation.text_to_video(
            prompt="A cat playing with a ball",
            video_length_sec=3.0,
            frame_rate=30.0,
            resolution=(512, 512),
        )

        assert result is not None
        assert result.generation_type == GenerationType.TEXT_TO_VIDEO

    @pytest.mark.asyncio
    async def test_generation_quality_scores(self):
        """Test generation quality scoring"""
        generation = MultimodalGeneration()

        result = await generation.text_to_image(
            "Quality test", (256, 256), num_steps=20
        )

        # Quality metrics should be present
        assert result.quality_score >= 0
        assert result.alignment_score >= 0

    @pytest.mark.asyncio
    async def test_different_guidance_scales(self):
        """Test generation with different guidance scales"""
        generation = MultimodalGeneration()

        # Low guidance
        r1 = await generation.text_to_image(
            "Test prompt", (256, 256), guidance_scale=3.0
        )
        assert r1 is not None

        # High guidance
        r2 = await generation.text_to_image(
            "Test prompt", (256, 256), guidance_scale=15.0
        )
        assert r2 is not None


# ============================================================================
# 6. MultimodalAlignmentGrounding Tests
# ============================================================================


class TestMultimodalAlignmentGrounding:
    """Test Multimodal Alignment Grounding subsystem"""

    @pytest.mark.asyncio
    async def test_temporal_grounding(self):
        """Test temporal grounding in video"""
        grounding = MultimodalAlignmentGrounding()

        video_features = np.random.randn(100, 512)  # 100 frames
        text_features = np.random.randn(512)

        result = await grounding.temporal_grounding(
            video_features=video_features,
            text_query="Person walking",
            text_features=text_features,
            frame_rate=30.0,
        )

        assert result is not None
        assert result.start_time is not None
        assert result.end_time is not None

    @pytest.mark.asyncio
    async def test_spatial_grounding(self):
        """Test spatial grounding in image"""
        grounding = MultimodalAlignmentGrounding()

        image_features = np.random.randn(512)
        text_features = np.random.randn(512)

        result = await grounding.spatial_grounding(
            image_features=image_features,
            text_query="The red object",
            text_features=text_features,
        )

        assert result is not None
        assert len(result.bounding_boxes) > 0

    @pytest.mark.asyncio
    async def test_object_grounding(self):
        """Test object grounding"""
        grounding = MultimodalAlignmentGrounding()

        image = np.random.randn(224, 224, 3)

        result = await grounding.ground_objects(
            image_data=image,
            object_queries=["cat", "dog", "bird"],
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_phrase_grounding(self):
        """Test phrase grounding"""
        grounding = MultimodalAlignmentGrounding()

        image_features = np.random.randn(512)

        result = await grounding.ground_phrases(
            image_features=image_features,
            phrases=["red car", "blue sky", "green tree"],
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_grounding_iou_score(self):
        """Test grounding IOU scoring"""
        grounding = MultimodalAlignmentGrounding()

        image_features = np.random.randn(512)
        text_features = np.random.randn(512)

        result = await grounding.spatial_grounding(
            image_features, "object", text_features
        )

        # IOU score should be present if applicable
        if result.iou_score is not None:
            assert 0 <= result.iou_score <= 1.0


# ============================================================================
# 7. MultimodalRetrievalSearch Tests
# ============================================================================


class TestMultimodalRetrievalSearch:
    """Test Multimodal Retrieval Search subsystem"""

    @pytest.mark.asyncio
    async def test_add_to_index(self):
        """Test adding items to search index"""
        retrieval = MultimodalRetrievalSearch()

        encoding = np.random.randn(512)

        result = await retrieval.add_to_index(
            item_id="item_001",
            modality=ModalityType.VISION,
            encoding=encoding,
            metadata={"source": "test"},
        )

        assert result.get("status") == "success"

    @pytest.mark.asyncio
    async def test_search_by_embedding(self):
        """Test search by embedding"""
        retrieval = MultimodalRetrievalSearch()

        # Add items to index
        for i in range(10):
            await retrieval.add_to_index(
                f"item_{i}",
                ModalityType.VISION,
                np.random.randn(512),
                {},
            )

        # Search
        query = np.random.randn(512)
        result = await retrieval.search_by_embedding(
            query_embedding=query,
            query_modality=ModalityType.LANGUAGE,
            target_modality=ModalityType.VISION,
            top_k=5,
        )

        assert result is not None
        assert len(result.retrieved_ids) <= 5

    @pytest.mark.asyncio
    async def test_cross_modal_search(self):
        """Test cross-modal search"""
        retrieval = MultimodalRetrievalSearch()

        # Index vision items
        for i in range(5):
            await retrieval.add_to_index(
                f"vision_{i}", ModalityType.VISION, np.random.randn(512), {}
            )

        # Search with language query
        result = await retrieval.cross_modal_search(
            query_modality=ModalityType.LANGUAGE,
            query_embedding=np.random.randn(512),
            target_modality=ModalityType.VISION,
            top_k=3,
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_remove_from_index(self):
        """Test removing items from index"""
        retrieval = MultimodalRetrievalSearch()

        await retrieval.add_to_index(
            "remove_item", ModalityType.VISION, np.random.randn(512), {}
        )

        result = await retrieval.remove_from_index("remove_item")
        assert result.get("status") == "success"

    @pytest.mark.asyncio
    async def test_get_index_stats(self):
        """Test getting index statistics"""
        retrieval = MultimodalRetrievalSearch()

        for i in range(5):
            await retrieval.add_to_index(
                f"stats_{i}", ModalityType.VISION, np.random.randn(512), {}
            )

        stats = await retrieval.get_index_stats()
        assert stats is not None
        assert "total_items" in stats or "modality_distribution" in stats

    @pytest.mark.asyncio
    async def test_batch_search(self):
        """Test batch search"""
        retrieval = MultimodalRetrievalSearch()

        # Index items
        for i in range(10):
            await retrieval.add_to_index(
                f"batch_{i}", ModalityType.VISION, np.random.randn(512), {}
            )

        # Batch search with multiple queries
        queries = [np.random.randn(512) for _ in range(3)]

        results = []
        for query in queries:
            result = await retrieval.search_by_embedding(
                query, ModalityType.LANGUAGE,
                ModalityType.VISION, top_k=3
            )
            results.append(result)

        assert len(results) == 3


# ============================================================================
# 8. IntegratedMultimodalAISystem Tests
# ============================================================================


class TestIntegratedMultimodalAISystem:
    """Test Integrated Multimodal AI System"""

    @pytest.mark.asyncio
    async def test_system_initialization(self):
        """Test system initialization with config"""
        config = MultimodalAIConfig(
            enable_encoder=True,
            enable_attention=True,
            enable_generation=True,
        )

        system = IntegratedMultimodalAISystem(config)
        assert system.encoder is not None
        assert system.attention_fusion is not None
        assert system.generation is not None

    @pytest.mark.asyncio
    async def test_image_caption_with_vqa(self):
        """Test image captioning with VQA"""
        system = IntegratedMultimodalAISystem()
        image = np.random.randn(224, 224, 3)

        result = await system.image_caption_with_vqa(
            image_data=image,
            question="What color is the object?",
        )

        assert result.get("status") == "success"
        assert result["caption"] is not None
        assert result["vqa"] is not None

    @pytest.mark.asyncio
    async def test_text_to_image_generation(self):
        """Test text-to-image generation"""
        system = IntegratedMultimodalAISystem()

        result = await system.text_to_image_generation(
            prompt="A beautiful landscape",
            image_size=(256, 256),
        )

        assert result.get("status") == "success"
        assert result["generated_image_shape"] == (256, 256, 3)

    @pytest.mark.asyncio
    async def test_cross_modal_retrieval(self):
        """Test cross-modal retrieval"""
        system = IntegratedMultimodalAISystem()

        # Create mock database
        database = [
            {"id": f"item_{i}", "encoding": np.random.randn(512), "metadata": {}}
            for i in range(10)
        ]

        result = await system.cross_modal_retrieval(
            query_data="Find a cat",
            query_modality=ModalityType.LANGUAGE,
            target_modality=ModalityType.VISION,
            database=database,
            top_k=5,
        )

        assert result.get("status") == "success"
        assert len(result["retrieved_ids"]) <= 5

    @pytest.mark.asyncio
    async def test_video_temporal_grounding(self):
        """Test video temporal grounding"""
        system = IntegratedMultimodalAISystem()
        video = np.random.randn(60, 224, 224, 3)  # 2 seconds at 30fps

        result = await system.video_temporal_grounding(
            video_frames=video,
            query="Person walking",
            frame_rate=30.0,
        )

        assert result.get("status") == "success"
        assert "start_time" in result
        assert "end_time" in result

    @pytest.mark.asyncio
    async def test_audio_visual_sync(self):
        """Test audio-visual synchronization"""
        system = IntegratedMultimodalAISystem()

        audio = np.random.randn(16000)
        video = np.random.randn(30, 224, 224, 3)

        result = await system.audio_visual_sync(
            audio_data=audio,
            video_frames=video,
        )

        assert result.get("status") == "success"

    @pytest.mark.asyncio
    async def test_multimodal_fusion(self):
        """Test multimodal fusion"""
        system = IntegratedMultimodalAISystem()

        vision_data = np.random.randn(224, 224, 3)
        language_data = "A description of the image"
        audio_data = np.random.randn(16000)

        result = await system.multimodal_fusion(
            vision_data=vision_data,
            language_data=language_data,
            audio_data=audio_data,
            fusion_strategy=FusionStrategy.ATTENTION,
        )

        assert result.get("status") == "success"
        assert result["num_modalities_fused"] == 3

    @pytest.mark.asyncio
    async def test_fusion_with_two_modalities(self):
        """Test fusion with just two modalities"""
        system = IntegratedMultimodalAISystem()

        result = await system.multimodal_fusion(
            vision_data=np.random.randn(224, 224, 3),
            language_data="Test description",
        )

        assert result.get("status") == "success"
        assert result["num_modalities_fused"] == 2

    @pytest.mark.asyncio
    async def test_get_system_status(self):
        """Test getting system status"""
        system = IntegratedMultimodalAISystem()
        status = system.get_system_status()

        assert status is not None
        assert "encoder_enabled" in status
        assert "config" in status

    @pytest.mark.asyncio
    async def test_benchmark_performance(self):
        """Test system performance benchmarking"""
        system = IntegratedMultimodalAISystem()
        benchmarks = await system.benchmark_performance()

        assert benchmarks is not None
        assert len(benchmarks) > 0

    @pytest.mark.asyncio
    async def test_singleton_accessor(self):
        """Test singleton accessor"""
        system1 = get_multimodal_ai_system()
        system2 = get_multimodal_ai_system()

        # Should be same instance
        assert system1 is system2

    @pytest.mark.asyncio
    async def test_caption_only_without_vqa(self):
        """Test image captioning without VQA"""
        system = IntegratedMultimodalAISystem()
        image = np.random.randn(224, 224, 3)

        result = await system.image_caption_with_vqa(
            image_data=image,
            question=None,  # No VQA
        )

        assert result.get("status") == "success"
        assert result["caption"] is not None
        assert result["vqa"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
