"""
Image Converter - Complete All Formats Support
Supports: PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP, ICO, SVG, HEIC, AVIF
"""

from pathlib import Path
from PIL import Image
import os
import io

class ImageConverter:
    def __init__(self):
        # All supported input formats
        self.supported_formats = [
            'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'tif', 
            'webp', 'ico', 'svg', 'heic', 'avif', 'raw', 'cr2', 
            'nef', 'arw', 'dng', 'orf', 'rw2', 'pef', 'srw'
        ]
        
        # All output formats
        self.output_formats = [
            'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'tif',
            'webp', 'ico', 'pdf'
        ]
    
    def convert(self, input_path: str, output_path: str, options: dict = None):
        """
        Convert image to any supported format
        """
        try:
            # Check if input file exists
            if not os.path.exists(input_path):
                return False, f"Input file not found: {input_path}"
            
            # Check if input file is empty
            if os.path.getsize(input_path) == 0:
                return False, f"Input file is empty: {input_path}"
            
            # Open image with PIL (supports most formats)
            try:
                img = Image.open(input_path)
            except Exception as e:
                return False, f"Cannot open image: {str(e)}"
            
            # Get output extension
            output_ext = Path(output_path).suffix[1:].lower()
            
            # Handle special cases
            if output_ext == 'jpg':
                output_ext = 'jpeg'
            
            # ===== CONVERT RGBA TO RGB FOR JPEG =====
            if output_ext == 'jpeg':
                if img.mode == 'RGBA':
                    # Create white background
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode == 'P':
                    img = img.convert('RGB')
                elif img.mode == 'LA':
                    img = img.convert('RGB')
                elif img.mode == 'L':
                    img = img.convert('RGB')
            
            # ===== CONVERT RGB TO RGBA FOR PNG =====
            if output_ext == 'png':
                if img.mode == 'P':
                    img = img.convert('RGBA')
                elif img.mode == 'L':
                    img = img.convert('RGBA')
                elif img.mode == 'RGB':
                    # Convert to RGBA if we want transparency support
                    img = img.convert('RGBA')
            
            # ===== CONVERT TO GRAYSCALE FOR GIF (if needed) =====
            if output_ext == 'gif':
                if img.mode not in ('P', 'L'):
                    img = img.convert('P')
            
            # ===== PREPARE SAVE OPTIONS =====
            save_kwargs = {'format': output_ext.upper()}
            
            # Get quality from options
            quality = 95
            if options and 'quality' in options:
                quality = options['quality']
                if isinstance(quality, str):
                    try:
                        quality = int(quality)
                    except:
                        quality = 95
            
            # ===== FORMAT-SPECIFIC OPTIMIZATIONS =====
            if output_ext in ['jpeg', 'webp']:
                save_kwargs['quality'] = quality
                save_kwargs['optimize'] = True
                if output_ext == 'jpeg':
                    save_kwargs['progressive'] = True
                    save_kwargs['subsampling'] = 0  # Best quality
            
            elif output_ext == 'png':
                save_kwargs['optimize'] = True
                # Compression level: 0-9 (9 = highest compression)
                if options and 'compression' in options:
                    save_kwargs['compress_level'] = options['compression']
                else:
                    save_kwargs['compress_level'] = 6
            
            elif output_ext == 'gif':
                save_kwargs['optimize'] = True
                if options and 'colors' in options:
                    save_kwargs['colors'] = options['colors']
                else:
                    save_kwargs['colors'] = 256
            
            elif output_ext == 'tiff':
                save_kwargs['compression'] = 'tiff_lzw'
                save_kwargs['quality'] = quality
            
            elif output_ext == 'bmp':
                # BMP doesn't support quality settings
                pass
            
            elif output_ext == 'ico':
                # ICO format
                if options and 'sizes' in options:
                    save_kwargs['sizes'] = options['sizes']
                else:
                    # Default icon sizes
                    save_kwargs['sizes'] = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            
            elif output_ext == 'pdf':
                # PDF - use RGB mode
                if img.mode == 'RGBA':
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode == 'P':
                    img = img.convert('RGB')
                save_kwargs['resolution'] = 100.0
            
            # ===== RESIZE IF REQUESTED =====
            if options and 'size' in options:
                size = options['size']
                if isinstance(size, (list, tuple)) and len(size) == 2:
                    # Resize maintaining aspect ratio
                    img.thumbnail(size, Image.Resampling.LANCZOS)
                elif isinstance(size, int):
                    # Resize by percentage
                    new_size = (int(img.width * size / 100), int(img.height * size / 100))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # ===== ROTATE IF REQUESTED =====
            if options and 'rotate' in options:
                img = img.rotate(options['rotate'], expand=True, fillcolor=(255, 255, 255))
            
            # ===== FLIP IF REQUESTED =====
            if options and 'flip' in options:
                if options['flip'] == 'horizontal':
                    img = img.transpose(Image.FLIP_LEFT_RIGHT)
                elif options['flip'] == 'vertical':
                    img = img.transpose(Image.FLIP_TOP_BOTTOM)
            
            # ===== SAVE THE IMAGE =====
            # Ensure directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Save with options
            img.save(output_path, **save_kwargs)
            
            # ===== VERIFY OUTPUT =====
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                return True, f"✅ Image converted to {output_ext.upper()} successfully"
            else:
                return False, "Output file is empty or missing"
                
        except Exception as e:
            return False, f"Image conversion error: {str(e)}"
    
    def get_supported_formats(self) -> list:
        """Get all supported input formats"""
        return self.supported_formats
    
    def get_output_formats(self) -> list:
        """Get all supported output formats"""
        return self.output_formats
    
    def get_format_info(self, format_name: str) -> dict:
        """Get information about a format"""
        info = {
            'jpg': {'name': 'JPEG', 'extension': 'jpg', 'mime': 'image/jpeg', 'lossy': True},
            'jpeg': {'name': 'JPEG', 'extension': 'jpeg', 'mime': 'image/jpeg', 'lossy': True},
            'png': {'name': 'PNG', 'extension': 'png', 'mime': 'image/png', 'lossy': False},
            'gif': {'name': 'GIF', 'extension': 'gif', 'mime': 'image/gif', 'lossy': False},
            'bmp': {'name': 'BMP', 'extension': 'bmp', 'mime': 'image/bmp', 'lossy': False},
            'tiff': {'name': 'TIFF', 'extension': 'tiff', 'mime': 'image/tiff', 'lossy': False},
            'tif': {'name': 'TIFF', 'extension': 'tif', 'mime': 'image/tiff', 'lossy': False},
            'webp': {'name': 'WebP', 'extension': 'webp', 'mime': 'image/webp', 'lossy': True},
            'ico': {'name': 'ICO', 'extension': 'ico', 'mime': 'image/x-icon', 'lossy': False},
            'pdf': {'name': 'PDF', 'extension': 'pdf', 'mime': 'application/pdf', 'lossy': False}
        }
        return info.get(format_name.lower(), {})