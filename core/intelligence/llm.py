"""LLM integration for intelligent packaging design and labeling.

This module provides functionality to leverage Large Language Models for:
1. Package design recommendations based on product characteristics
2. Automated text generation for packaging
3. Context-aware suggestions and design improvements
4. Regulatory compliance assistance
"""

import logging
import os
import json
import time
from typing import Dict, List, Any, Optional, Union, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class ModelProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    HUGGINGFACE = "huggingface"
    INTERNAL = "internal"


class DesignMode(Enum):
    """Design modes for package generation."""
    MINIMAL = "minimal"        # Minimalist design with essential elements
    DETAILED = "detailed"      # Comprehensive design with detailed elements
    ELEGANT = "elegant"        # Premium, high-end aesthetic
    SUSTAINABLE = "sustainable"  # Eco-friendly design emphasis
    TECHNICAL = "technical"    # Technical/industrial design style
    PLAYFUL = "playful"        # Colorful, engaging design for toys/games


class LLMError(Exception):
    """Exception raised for errors in LLM processing."""
    pass


class PackagingLLM:
    """Interface for LLM-powered packaging design and text generation."""

    def __init__(
        self,
        provider: ModelProvider = ModelProvider.OPENAI,
        model_name: str = "gpt-4-turbo",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ):
        """Initialize the LLM interface.
        
        Args:
            provider: LLM provider to use
            model_name: Name of the model to use
            api_key: API key for the provider (defaults to env var lookup)
            temperature: Creativity control (0-1)
            max_tokens: Maximum tokens in response
        """
        self.provider = provider
        self.model_name = model_name
        self.api_key = api_key or self._get_api_key_from_env()
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = self._initialize_client()
        
        # Cache of previous interactions for context
        self.conversation_history = []
        
    def _get_api_key_from_env(self) -> str:
        """Get API key from environment variables."""
        env_var_name = {
            ModelProvider.OPENAI: "OPENAI_API_KEY",
            ModelProvider.ANTHROPIC: "ANTHROPIC_API_KEY",
            ModelProvider.HUGGINGFACE: "HF_API_KEY",
            ModelProvider.INTERNAL: "INTERNAL_API_KEY",
        }[self.provider]
        
        api_key = os.environ.get(env_var_name)
        if not api_key:
            raise LLMError(f"API key not found in environment variable {env_var_name}")
        
        return api_key
    
    def _initialize_client(self) -> Any:
        """Initialize the appropriate client based on provider."""
        try:
            if self.provider == ModelProvider.OPENAI:
                import openai
                openai.api_key = self.api_key
                return openai.OpenAI()
            
            elif self.provider == ModelProvider.ANTHROPIC:
                import anthropic
                return anthropic.Anthropic(api_key=self.api_key)
            
            elif self.provider == ModelProvider.HUGGINGFACE:
                from huggingface_hub import InferenceClient
                return InferenceClient(token=self.api_key)
            
            elif self.provider == ModelProvider.INTERNAL:
                # Custom internal implementation could go here
                return None
            
        except ImportError as e:
            raise LLMError(f"Failed to import required library: {str(e)}")
        except Exception as e:
            raise LLMError(f"Failed to initialize client: {str(e)}")
    
    def _generate_prompt(self, task: str, inputs: Dict[str, Any]) -> str:
        """Generate a prompt for the specified task using the provided inputs.
        
        Args:
            task: The type of task ("design_suggestion", "text_generation", etc.)
            inputs: Dictionary of task-specific inputs
            
        Returns:
            Formatted prompt string
        """
        base_prompts = {
            "design_suggestion": """
            You are an expert packaging designer with extensive knowledge of materials, 
            sustainability, and manufacturing constraints. Please provide detailed 
            packaging design recommendations for the following product:
            
            Product: {product_name}
            Dimensions: {dimensions}
            Weight: {weight}
            Fragility: {fragility}
            Product Category: {category}
            Target Market: {target_market}
            Design Style Preference: {design_mode}
            Key Considerations: {considerations}
            
            Please provide specific recommendations for:
            1. Overall packaging form factor and dimensions
            2. Material selection with sustainability considerations
            3. Internal support structures for product protection
            4. Visual design elements and branding opportunities
            5. Practical considerations for manufacturing and shipping
            """,
            
            "text_generation": """
            Generate professional copy for the following packaging elements:
            
            Product: {product_name}
            Category: {category}
            Target Audience: {target_audience}
            Brand Voice: {brand_voice}
            Key Benefits: {key_benefits}
            Required Regulatory Information: {regulatory_info}
            
            Please provide text for:
            1. Front panel headline (10 words or less)
            2. Marketing description (50-100 words)
            3. Product features/benefits (3-5 bullet points)
            4. Usage instructions (step-by-step)
            5. Warranty/guarantee statement
            """,
            
            "regulatory_check": """
            You are a regulatory compliance expert for product packaging. Review the 
            following packaging design and identify any compliance issues or required 
            labeling for these markets: {markets}.
            
            Product: {product_name}
            Category: {category}
            Current Package Text: {package_text}
            Materials Used: {materials}
            
            Please identify:
            1. Missing required warnings or statements
            2. Compliance issues with format or placement
            3. Material-specific regulatory requirements
            4. Category-specific regulatory requirements
            5. Market-specific requirements for each listed market
            """
        }
        
        # Get the base prompt for this task
        prompt_template = base_prompts.get(task)
        if not prompt_template:
            raise LLMError(f"Unknown task type: {task}")
        
        # Format the prompt with the provided inputs
        try:
            prompt = prompt_template.format(**inputs)
            return prompt
        except KeyError as e:
            raise LLMError(f"Missing required input for prompt: {str(e)}")
    
    def generate_response(self, prompt: str) -> str:
        """Generate a response from the LLM based on the prompt.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            Generated text response
        """
        try:
            if self.provider == ModelProvider.OPENAI:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                return response.choices[0].message.content
                
            elif self.provider == ModelProvider.ANTHROPIC:
                response = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
                
            elif self.provider == ModelProvider.HUGGINGFACE:
                response = self.client.text_generation(
                    prompt,
                    max_new_tokens=self.max_tokens,
                    temperature=self.temperature
                )
                return response
                
            elif self.provider == ModelProvider.INTERNAL:
                # Custom internal implementation could go here
                raise NotImplementedError("Internal provider not implemented")
                
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            raise LLMError(f"Failed to generate response: {str(e)}")
    
    def get_design_suggestions(
        self, 
        product_info: Dict[str, Any],
        design_mode: DesignMode = DesignMode.DETAILED
    ) -> Dict[str, Any]:
        """Get packaging design suggestions for a product.
        
        Args:
            product_info: Dictionary containing product details
            design_mode: Design style preference
            
        Returns:
            Dictionary with design suggestions
        """
        # Prepare inputs for the prompt
        inputs = {
            "product_name": product_info.get("name", "Unnamed Product"),
            "dimensions": product_info.get("dimensions", "Unknown"),
            "weight": product_info.get("weight", "Unknown"),
            "fragility": product_info.get("fragility", "Medium"),
            "category": product_info.get("category", "General"),
            "target_market": product_info.get("target_market", "General consumers"),
            "design_mode": design_mode.value,
            "considerations": product_info.get("considerations", "Cost-effectiveness, sustainability")
        }
        
        # Generate and send the prompt
        prompt = self._generate_prompt("design_suggestion", inputs)
        response_text = self.generate_response(prompt)
        
        # Process and structure the response
        # This is a simplified version - in production this would parse the response more thoroughly
        sections = response_text.split("\n\n")
        result = {
            "form_factor": sections[0] if len(sections) > 0 else "",
            "materials": sections[1] if len(sections) > 1 else "",
            "internal_support": sections[2] if len(sections) > 2 else "",
            "visual_design": sections[3] if len(sections) > 3 else "",
            "manufacturing_notes": sections[4] if len(sections) > 4 else "",
            "raw_response": response_text
        }
        
        return result
    
    def generate_packaging_text(
        self,
        product_info: Dict[str, Any],
        target_audience: str,
        brand_voice: str,
        regulatory_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """Generate text content for packaging.
        
        Args:
            product_info: Dictionary with product details
            target_audience: Description of the target audience
            brand_voice: Description of the brand voice/tone
            regulatory_info: Dictionary with regulatory requirements
            
        Returns:
            Dictionary with generated text elements
        """
        # Prepare inputs for the prompt
        inputs = {
            "product_name": product_info.get("name", "Unnamed Product"),
            "category": product_info.get("category", "General"),
            "target_audience": target_audience,
            "brand_voice": brand_voice,
            "key_benefits": ", ".join(product_info.get("benefits", ["Unknown"])),
            "regulatory_info": json.dumps(regulatory_info or {})
        }
        
        # Generate and send the prompt
        prompt = self._generate_prompt("text_generation", inputs)
        response_text = self.generate_response(prompt)
        
        # Process and extract sections from the response
        # A more robust implementation would use regex or specific markers
        sections = response_text.split("\n\n")
        
        result = {
            "headline": "",
            "description": "",
            "features": [],
            "instructions": "",
            "warranty": "",
            "raw_response": response_text
        }
        
        # Simple parsing logic - would be more robust in production
        for section in sections:
            if "headline" in section.lower():
                result["headline"] = section.split(":")[-1].strip()
            elif "description" in section.lower():
                result["description"] = section.split(":")[-1].strip()
            elif "features" in section.lower() or "benefits" in section.lower():
                bullet_points = [bp.strip() for bp in section.split("\n") if bp.strip().startswith("•") or bp.strip().startswith("-")]
                result["features"] = bullet_points
            elif "instructions" in section.lower() or "directions" in section.lower():
                result["instructions"] = section.split(":")[-1].strip()
            elif "warranty" in section.lower() or "guarantee" in section.lower():
                result["warranty"] = section.split(":")[-1].strip()
        
        return result
    
    def check_regulatory_compliance(
        self,
        product_info: Dict[str, Any],
        package_text: str,
        materials: List[str],
        markets: List[str]
    ) -> Dict[str, Any]:
        """Check packaging design and text for regulatory compliance issues.
        
        Args:
            product_info: Dictionary with product details
            package_text: Current text on the packaging
            materials: List of materials used in the packaging
            markets: List of target markets to check compliance for
            
        Returns:
            Dictionary with compliance issues and suggestions
        """
        # Prepare inputs for the prompt
        inputs = {
            "product_name": product_info.get("name", "Unnamed Product"),
            "category": product_info.get("category", "General"),
            "package_text": package_text,
            "materials": ", ".join(materials),
            "markets": ", ".join(markets)
        }
        
        # Generate and send the prompt
        prompt = self._generate_prompt("regulatory_check", inputs)
        response_text = self.generate_response(prompt)
        
        # Process and structure the response
        issues = []
        requirements = []
        
        # Very basic parsing - a production system would use more robust extraction
        for line in response_text.split("\n"):
            line = line.strip()
            if line.startswith("- ") or line.startswith("* "):
                if "required" in line.lower() or "must include" in line.lower():
                    requirements.append(line[2:].strip())
                elif "issue" in line.lower() or "missing" in line.lower() or "non-compliant" in line.lower():
                    issues.append(line[2:].strip())
        
        result = {
            "has_issues": len(issues) > 0,
            "issues": issues,
            "requirements": requirements,
            "raw_response": response_text
        }
        
        return result


# Example usage
if __name__ == "__main__":
    # This example requires appropriate API keys to be set in environment variables
    llm = PackagingLLM(provider=ModelProvider.OPENAI, model_name="gpt-4-turbo")
    
    # Example product information
    product_info = {
        "name": "EcoTech Wireless Earbuds",
        "dimensions": "6.5 x 4.8 x 2.2 cm",
        "weight": "58g",
        "fragility": "High",
        "category": "Electronics",
        "target_market": "Tech-savvy environmentally conscious consumers",
        "benefits": [
            "40-hour battery life", 
            "Noise cancellation", 
            "Waterproof IPX7",
            "Made with 70% recycled materials"
        ]
    }
    
    # Get design suggestions
    design = llm.get_design_suggestions(
        product_info, 
        design_mode=DesignMode.SUSTAINABLE
    )
    
    print("Design Suggestions:")
    print(design["form_factor"])
    print(design["materials"])
    
    # Generate packaging text
    text = llm.generate_packaging_text(
        product_info,
        target_audience="Eco-conscious tech enthusiasts, 25-45 years old",
        brand_voice="Modern, eco-friendly, premium but approachable"
    )
    
    print("\nGenerated Headline:")
    print(text["headline"])
    
    print("\nGenerated Description:")
    print(text["description"])
