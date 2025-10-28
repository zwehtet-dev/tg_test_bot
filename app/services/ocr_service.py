"""
OCR service for receipt processing using OpenAI Vision
Improved with better error handling and caching
"""
import base64
import json
import logging
from typing import Optional, Dict
from PIL import Image
import io

logger = logging.getLogger(__name__)


class OCRService:
    """Handle OCR operations using OpenAI Vision"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Initialize OCR service
        
        Args:
            api_key: OpenAI API key
            model: OpenAI model to use
        """
        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import HumanMessage
            
            self.api_key = api_key
            self.model = model
            self.llm = ChatOpenAI(
                model=model,
                api_key=api_key,
                temperature=0,
                max_tokens=1000
            )
            self.HumanMessage = HumanMessage
            logger.info(f"OCR Service initialized with {model}")
            
        except ImportError as e:
            logger.error(f"Required packages not installed: {e}")
            raise
        except Exception as e:
            logger.error(f"Error initializing OCR service: {e}")
            raise
    
    def image_to_base64(self, image_path: str) -> str:
        """
        Convert image to base64
        
        Args:
            image_path: Path to image file
        
        Returns:
            Base64 encoded image string
        """
        try:
            with Image.open(image_path) as img:
                # Convert to RGB
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Resize if too large
                max_size = (2048, 2048)
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Convert to base64
                buffered = io.BytesIO()
                img.save(buffered, format="JPEG", quality=90)
                return base64.b64encode(buffered.getvalue()).decode()
                
        except Exception as e:
            logger.error(f"Error converting image to base64: {e}")
            raise
    
    def extract_receipt_info(self, image_path: str) -> Optional[Dict]:
        """
        Extract information from receipt using OpenAI Vision
        
        Args:
            image_path: Path to receipt image
        
        Returns:
            Dictionary with extracted information or None if failed
        """
        try:
            image_base64 = self.image_to_base64(image_path)
            
            prompt_text = """Analyze this bank transfer receipt and extract the following information:

1. Transfer amount (numeric value only, no currency symbols)
2. Sender bank name
3. Receiver bank name
4. Sender account name
5. Receiver account name
6. Transaction status (successful, pending, or failed)
7. Transaction reference number

Important:
- For bank names, use common abbreviations if visible (e.g., SCB, KTB, KBank)
- For names, extract exactly as shown (including titles like MISS, MR, etc.)
- For amount, extract only the numeric value
- Look for keywords like "สำเร็จ" (successful), "Success", "Completed"

Return ONLY valid JSON format with no additional text:
{
    "amount": <number or null>,
    "sender_bank": "<bank name or null>",
    "receiver_bank": "<bank name or null>",
    "sender_name": "<name or null>",
    "receiver_name": "<name or null>",
    "status": "<status or null>",
    "reference": "<ref or null>"
}"""
            
            # Create message with image
            message = self.HumanMessage(
                content=[
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}",
                            "detail": "high"
                        }
                    }
                ]
            )
            
            # Invoke the model
            response = self.llm.invoke([message])
            content = response.content
            
            # Parse JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            result = json.loads(content)
            logger.info(f"OCR extraction successful: amount={result.get('amount')}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.error(f"Response content: {content if 'content' in locals() else 'N/A'}")
            return None
        except Exception as e:
            logger.error(f"OCR Error: {e}")
            return None
