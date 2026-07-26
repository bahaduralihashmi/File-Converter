"""
Image AI - Generate images using Stable Diffusion
Fixed for CPU with better error handling
"""

import os
import sys
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Tuple, Callable

# REMOVED: Invalid import
# from dist.AllFilesConverterAI._internal.imageio.core.util import Image

from app.utils.logger import get_logger

logger = get_logger(__name__)

# Enable by default since model is downloaded
IMAGE_AI_ENABLED = False


class ImageAI:
    """Image generation using Stable Diffusion - Fixed for CPU"""
    
    _instance = None
    _pipe = None
    _model_loaded = False
    _loading = False
    _load_error = None
    _enabled = IMAGE_AI_ENABLED
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._enabled:
            self._initialize()
        else:
            logger.info("ℹ️ Image AI is disabled.")
    
    def _initialize(self):
        """Initialize the image generation model"""
        if self._model_loaded or self._loading:
            return
        
        # Check if diffusers is installed
        try:
            import diffusers
            import torch
            import transformers
        except ImportError as e:
            logger.warning(f"Image generation not available: {e}")
            logger.warning("Install: pip install diffusers transformers accelerate")
            self._model_loaded = False
            return
        
        # Start loading in background
        self._loading = True
        threading.Thread(target=self._load_model, daemon=True).start()
    
    def _load_model(self):
        """Load the model with better CPU handling"""
        try:
            from diffusers import StableDiffusionPipeline
            import torch
            
            # Check if CUDA is available
            if torch.cuda.is_available():
                device = "cuda"
                dtype = torch.float16
                logger.info("✅ CUDA (GPU) detected! Using GPU for faster generation.")
            else:
                device = "cpu"
                dtype = torch.float32
                logger.info("ℹ️ Using CPU for image generation. This will be slow but works.")
            
            logger.info(f"🔄 Loading Stable Diffusion model from cache...")
            
            # Use a smaller, faster model for CPU
            models_to_try = [
                "runwayml/stable-diffusion-v1-5",
                "CompVis/stable-diffusion-v1-4",
                "hakurei/waifu-diffusion",  # Smaller model
                "dreamlike-art/dreamlike-photoreal-2.0",  # Alternative
            ]
            
            for model_name in models_to_try:
                try:
                    logger.info(f"Trying model: {model_name}")
                    
                    self._pipe = StableDiffusionPipeline.from_pretrained(
                        model_name,
                        torch_dtype=dtype,
                        safety_checker=None,
                        requires_safety_checker=False,
                        low_cpu_mem_usage=True,
                        use_safetensors=True,
                        cache_dir=os.path.expanduser("~/.cache/huggingface")
                    )
                    
                    # Move to device
                    self._pipe = self._pipe.to(device)
                    
                    # Enable memory efficient features
                    if hasattr(self._pipe, "enable_attention_slicing"):
                        self._pipe.enable_attention_slicing()
                    
                    # For CPU, enable model offloading
                    if device == "cpu" and hasattr(self._pipe, "enable_model_cpu_offload"):
                        self._pipe.enable_model_cpu_offload()
                    
                    self._model_loaded = True
                    self._loading = False
                    logger.info(f"✅ Model loaded successfully: {model_name}")
                    return
                    
                except Exception as e:
                    logger.warning(f"Failed to load {model_name}: {e}")
                    continue
            
            # If all models fail
            self._model_loaded = False
            self._loading = False
            self._load_error = "All models failed to load"
            logger.error("❌ All models failed to load")
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to load Stable Diffusion: {error_msg}")
            self._model_loaded = False
            self._loading = False
            self._load_error = error_msg
    
    def is_available(self) -> bool:
        """Check if image generation is available"""
        return self._enabled and self._model_loaded and self._pipe is not None
    
    def is_loading(self) -> bool:
        """Check if model is currently loading"""
        return self._enabled and self._loading
    
    def is_enabled(self) -> bool:
        """Check if image AI is enabled"""
        return self._enabled
    
    def enable(self):
        """Enable image AI"""
        global IMAGE_AI_ENABLED
        IMAGE_AI_ENABLED = True
        self._enabled = True
        self._initialize()
    
    def disable(self):
        """Disable image AI"""
        self._enabled = False
        self._model_loaded = False
        self._pipe = None
    
    def get_status(self) -> Dict:
        """Get current status"""
        return {
            "enabled": self._enabled,
            "loaded": self._model_loaded,
            "loading": self._loading,
            "available": self.is_available(),
            "error": self._load_error
        }
    
    def generate_image(self, prompt: str, 
                       negative_prompt: str = "blurry, bad quality, deformed, ugly",
                       width: int = 256,  # Reduced for CPU
                       height: int = 256,  # Reduced for CPU
                       num_inference_steps: int = 10,  # Reduced for CPU
                       guidance_scale: float = 7.5,
                       progress_callback: Optional[Callable] = None) -> Tuple[bool, Optional[str], str]:
        """
        Generate an image from text prompt - Optimized for CPU
        """
        if not self._enabled:
            return False, None, "Image AI is disabled."
        
        if self._loading:
            return False, None, "Model is still loading. Please wait..."
        
        if not self.is_available():
            return False, None, f"Model not loaded. Error: {self._load_error or 'Unknown'}"
        
        try:
            if progress_callback:
                progress_callback(10, "Generating image...")
            
            logger.info(f"🎨 Generating image: {prompt[:100]}...")
            
            # Generate the image with optimized settings for CPU
            result = self._pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
            )
            
            if progress_callback:
                progress_callback(80, "Saving image...")
            
            # Get the image
            image = result.images[0]
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_image_{timestamp}.png"
            
            # Save in the generated_images folder
            output_dir = Path("generated_images")
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / filename
            
            image.save(str(output_path))
            
            if progress_callback:
                progress_callback(100, "Done!")
            
            logger.info(f"✅ Image generated and saved: {output_path}")
            return True, str(output_path), f"Image saved: {filename}"
            
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return False, None, f"Generation failed: {str(e)}"
    
    def generate_image_async(self, prompt: str, 
                             callback: Optional[Callable] = None,
                             **kwargs) -> threading.Thread:
        """
        Generate image asynchronously
        """
        def worker():
            result = self.generate_image(prompt, **kwargs)
            if callback:
                callback(result)
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        return thread
    
    def get_model_info(self) -> Dict:
        """Get information about the image AI model"""
        return {
            "enabled": self._enabled,
            "loaded": self._model_loaded,
            "loading": self._loading,
            "available": self.is_available(),
            "error": self._load_error,
            "model": "runwayml/stable-diffusion-v1-5" if self._model_loaded else None
        }

# ============================================================
# FIX: The convert method was incorrectly placed in this file
# It belongs in app/converters/image.py, not here
# ============================================================

# Global instance
image_ai = ImageAI()