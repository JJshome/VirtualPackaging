"""Automated packaging labeling and text generation.

This module handles the automated generation and optimal placement of text elements
on packaging designs, including regulatory information, product descriptions, and
branding elements.
"""

import logging
import json
import os
from typing import Dict, List, Any, Optional, Union, Tuple
from enum import Enum
import numpy as np

from .llm import PackagingLLM, ModelProvider
from .regulatory import verify_compliance, generate_regulatory_text

logger = logging.getLogger(__name__)


class TextElementType(Enum):
    """Types of text elements that can be placed on packaging."""
    PRODUCT_NAME = "product_name"
    DESCRIPTION = "description"
    FEATURES = "features"
    INSTRUCTIONS = "instructions"
    INGREDIENTS = "ingredients"
    REGULATORY = "regulatory"
    BRAND = "brand"
    WARNING = "warning"
    NUTRITION = "nutrition"
    SUSTAINABILITY = "sustainability"
    CONTACT = "contact"
    BARCODE = "barcode"
    RECYCLING = "recycling"


class TextPlacement(Enum):
    """Possible placement locations for text on packaging."""
    FRONT = "front"
    BACK = "back"
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"
    FRONT_TOP = "front_top"
    FRONT_BOTTOM = "front_bottom"
    BACK_TOP = "back_top"
    BACK_BOTTOM = "back_bottom"


class TextOrientation(Enum):
    """Text orientation options."""
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    ROTATED_90 = "rotated_90"
    ROTATED_270 = "rotated_270"


class PackagingLabeling:
    """Automated labeling system for packaging designs."""

    def __init__(
        self,
        llm: Optional[PackagingLLM] = None,
        templates_path: str = "data/text_templates",
        language: str = "en"
    ):
        """Initialize the packaging labeling system.
        
        Args:
            llm: PackagingLLM instance (created if None)
            templates_path: Path to text templates directory
            language: Language code for generated text
        """
        # Initialize or use provided LLM
        self.llm = llm or PackagingLLM(
            provider=ModelProvider.OPENAI, 
            model_name="gpt-4-turbo"
        )
        
        # Load text templates
        self.templates_path = templates_path
        self.templates = self._load_templates()
        
        # Set language
        self.language = language
        
        # Text styling defaults
        self.default_styles = {
            TextElementType.PRODUCT_NAME: {
                "font_size": 24,
                "font_weight": "bold",
                "color": "#000000"
            },
            TextElementType.DESCRIPTION: {
                "font_size": 12,
                "font_weight": "normal",
                "color": "#333333"
            },
            TextElementType.FEATURES: {
                "font_size": 14,
                "font_weight": "normal",
                "color": "#333333"
            },
            TextElementType.INSTRUCTIONS: {
                "font_size": 10,
                "font_weight": "normal",
                "color": "#333333"
            },
            TextElementType.WARNING: {
                "font_size": 12,
                "font_weight": "bold",
                "color": "#FF0000"
            },
            TextElementType.REGULATORY: {
                "font_size": 8,
                "font_weight": "normal",
                "color": "#333333"
            }
        }
    
    def _load_templates(self) -> Dict[str, Any]:
        """Load text templates for different product categories.
        
        Returns:
            Dictionary of templates by category
        """
        templates = {}
        
        try:
            if not os.path.exists(self.templates_path):
                logger.warning(f"Templates directory not found: {self.templates_path}")
                return templates
            
            # Load each template file in the directory
            for filename in os.listdir(self.templates_path):
                if filename.endswith('.json'):
                    with open(os.path.join(self.templates_path, filename), 'r') as f:
                        template_data = json.load(f)
                        category = filename.split('.')[0]
                        templates[category] = template_data
            
            logger.info(f"Loaded {len(templates)} text templates")
            return templates
            
        except Exception as e:
            logger.error(f"Error loading text templates: {str(e)}")
            return {}
    
    def generate_packaging_text(
        self,
        product_info: Dict[str, Any],
        target_audience: str,
        brand_info: Dict[str, Any],
        elements: List[TextElementType] = None,
        regulatory_regions: List[str] = None
    ) -> Dict[TextElementType, str]:
        """Generate all required text for a packaging design.
        
        Args:
            product_info: Dictionary with product details
            target_audience: Description of the target audience
            brand_info: Dictionary with brand information
            elements: List of text elements to generate (all if None)
            regulatory_regions: List of regions for regulatory compliance
            
        Returns:
            Dictionary mapping text element types to generated content
        """
        if elements is None:
            elements = [
                TextElementType.PRODUCT_NAME,
                TextElementType.DESCRIPTION,
                TextElementType.FEATURES,
                TextElementType.INSTRUCTIONS,
                TextElementType.REGULATORY
            ]
        
        if regulatory_regions is None:
            regulatory_regions = ["US"]  # Default to US regulations
        
        result = {}
        
        # Product name (may be provided or generated)
        if TextElementType.PRODUCT_NAME in elements:
            if "name" in product_info and product_info["name"]:
                result[TextElementType.PRODUCT_NAME] = product_info["name"]
            else:
                result[TextElementType.PRODUCT_NAME] = self._generate_product_name(
                    product_info, brand_info
                )
        
        # Product description
        if TextElementType.DESCRIPTION in elements:
            result[TextElementType.DESCRIPTION] = self._generate_description(
                product_info, target_audience, brand_info
            )
        
        # Product features/benefits
        if TextElementType.FEATURES in elements:
            result[TextElementType.FEATURES] = self._generate_features(
                product_info, target_audience
            )
        
        # Usage instructions
        if TextElementType.INSTRUCTIONS in elements:
            result[TextElementType.INSTRUCTIONS] = self._generate_instructions(
                product_info
            )
        
        # Ingredients list (if applicable)
        if TextElementType.INGREDIENTS in elements and "ingredients" in product_info:
            result[TextElementType.INGREDIENTS] = self._format_ingredients(
                product_info["ingredients"]
            )
        
        # Nutrition information (if applicable)
        if TextElementType.NUTRITION in elements and "nutrition" in product_info:
            result[TextElementType.NUTRITION] = self._format_nutrition(
                product_info["nutrition"]
            )
        
        # Regulatory text
        if TextElementType.REGULATORY in elements:
            regulatory_text = generate_regulatory_text(
                product_info.get("category", "general"),
                regulatory_regions,
                self.language
            )
            
            result[TextElementType.REGULATORY] = self._format_regulatory_text(
                regulatory_text
            )
        
        # Warning text
        if TextElementType.WARNING in elements:
            result[TextElementType.WARNING] = self._generate_warnings(
                product_info, regulatory_regions
            )
        
        # Sustainability information
        if TextElementType.SUSTAINABILITY in elements:
            result[TextElementType.SUSTAINABILITY] = self._generate_sustainability_info(
                product_info
            )
        
        # Contact information
        if TextElementType.CONTACT in elements and "contact" in brand_info:
            result[TextElementType.CONTACT] = self._format_contact_info(
                brand_info["contact"]
            )
        
        # Recycling information
        if TextElementType.RECYCLING in elements:
            result[TextElementType.RECYCLING] = self._generate_recycling_info(
                product_info
            )
        
        return result
    
    def _generate_product_name(
        self,
        product_info: Dict[str, Any],
        brand_info: Dict[str, Any]
    ) -> str:
        """Generate a product name if not provided.
        
        Args:
            product_info: Dictionary with product details
            brand_info: Dictionary with brand information
            
        Returns:
            Generated product name
        """
        # If category and key features are provided, generate a name
        brand_name = brand_info.get("name", "")
        category = product_info.get("category", "")
        features = product_info.get("key_features", [])
        
        if not category:
            return brand_name + " Product"
        
        # Use LLM to generate a product name
        prompt = f"""
        Generate a concise, attractive product name for a {category} product from the brand {brand_name}.
        
        Key product features:
        {", ".join(features)}
        
        The name should be:
        - Short (1-4 words)
        - Memorable
        - Reflect the product's key benefit or feature
        - Align with the {brand_name} brand identity
        
        Return only the product name, with no additional explanation.
        """
        
        try:
            response = self.llm.generate_response(prompt)
            # Clean response: remove quotes and extra whitespace
            name = response.strip().strip('"\'').strip()
            
            # If the name is still too long, truncate it
            if len(name.split()) > 5:
                words = name.split()[:4]
                name = " ".join(words)
            
            # If brand name isn't in the product name, consider adding it
            if brand_name and brand_name.lower() not in name.lower():
                name = f"{brand_name} {name}"
            
            return name
            
        except Exception as e:
            logger.error(f"Error generating product name: {str(e)}")
            # Fallback to a basic name
            return f"{brand_name} {category.title()}"
    
    def _generate_description(
        self,
        product_info: Dict[str, Any],
        target_audience: str,
        brand_info: Dict[str, Any]
    ) -> str:
        """Generate a marketing description for the product.
        
        Args:
            product_info: Dictionary with product details
            target_audience: Target audience description
            brand_info: Dictionary with brand information
            
        Returns:
            Generated product description
        """
        # Try to use appropriate template if available
        category = product_info.get("category", "general").lower()
        
        if category in self.templates and "description_template" in self.templates[category]:
            template = self.templates[category]["description_template"]
        else:
            # Default template
            template = """
            Introducing {product_name}, the {adjective} {category} designed for {audience}.
            {benefit_statement}. {feature_statement}.
            {brand_statement}.
            """
        
        # If using template, try to fill it with available info
        try:
            # Prepare template variables
            variables = {
                "product_name": product_info.get("name", "our product"),
                "category": product_info.get("category", "product"),
                "audience": target_audience
            }
            
            # Add more variables if available
            if "key_features" in product_info and product_info["key_features"]:
                features = product_info["key_features"]
                variables["feature_statement"] = f"It features {', '.join(features[:-1])}{' and ' if len(features) > 1 else ''}{features[-1] if features else ''}"
            else:
                variables["feature_statement"] = "It features the latest technology"
            
            if "benefits" in product_info and product_info["benefits"]:
                benefits = product_info["benefits"]
                variables["benefit_statement"] = f"Experience {', '.join(benefits[:-1])}{' and ' if len(benefits) > 1 else ''}{benefits[-1] if benefits else ''}"
            else:
                variables["benefit_statement"] = "Experience quality like never before"
            
            if "name" in brand_info and "tagline" in brand_info:
                variables["brand_statement"] = f"From {brand_info['name']}: {brand_info['tagline']}"
            elif "name" in brand_info:
                variables["brand_statement"] = f"From {brand_info['name']}"
            else:
                variables["brand_statement"] = "From a brand you can trust"
            
            # If we need an adjective and don't have one, generate it
            if "{adjective}" in template and "adjective" not in variables:
                adjectives = ["innovative", "premium", "advanced", "essential", "versatile", "high-quality"]
                # Use LLM to pick an appropriate adjective
                prompt = f"""
                Select the most appropriate adjective for this product:
                
                Product: {variables['product_name']}
                Category: {variables['category']}
                Target audience: {variables['audience']}
                Features: {variables.get('feature_statement', '')}
                
                Choose ONE word from: {', '.join(adjectives)}
                
                Return only the adjective word, nothing else.
                """
                try:
                    variables["adjective"] = self.llm.generate_response(prompt).strip().lower()
                    if variables["adjective"] not in adjectives:
                        variables["adjective"] = "innovative"
                except:
                    variables["adjective"] = "innovative"
            
            # Format template with variables
            description = template.format(**variables)
            # Clean up whitespace
            description = ' '.join(line.strip() for line in description.split('\n')).strip()
            return description
            
        except Exception as e:
            logger.error(f"Error using template for description: {str(e)}")
            
            # Fallback to LLM generation
            prompt = f"""
            Write a concise marketing description for this product:
            
            Product Name: {product_info.get('name', 'Product')}
            Category: {product_info.get('category', 'General')}
            Target Audience: {target_audience}
            Key Features: {', '.join(product_info.get('key_features', []))}
            Brand: {brand_info.get('name', '')}
            
            The description should be:
            - Approximately 50-75 words
            - Highlight main benefits
            - Appeal to the target audience
            - Include a brand statement
            
            Write the description directly with no explanations or headers.
            """
            
            try:
                description = self.llm.generate_response(prompt)
                return description.strip()
            except Exception as e2:
                logger.error(f"Error generating description with LLM: {str(e2)}")
                # Simple fallback
                return f"A premium {product_info.get('category', 'product')} by {brand_info.get('name', 'our brand')}."
    
    def _generate_features(
        self,
        product_info: Dict[str, Any],
        target_audience: str
    ) -> List[str]:
        """Generate a list of product features/benefits.
        
        Args:
            product_info: Dictionary with product details
            target_audience: Target audience description
            
        Returns:
            List of feature statements
        """
        # If features are provided, use them
        if "key_features" in product_info and product_info["key_features"]:
            # Start with existing features
            features = product_info["key_features"]
            
            # If we need more features, generate them
            if len(features) < 3:
                # Use LLM to generate additional features
                existing = ", ".join(features)
                prompt = f"""
                Generate additional key features for this product to highlight on packaging:
                
                Product Name: {product_info.get('name', 'Product')}
                Category: {product_info.get('category', 'General')}
                Target Audience: {target_audience}
                Existing Features: {existing}
                
                Generate {3 - len(features)} more feature bullet points that:
                - Highlight benefits to the user
                - Are concise (5-8 words each)
                - Don't duplicate existing features
                - Are specific and credible
                
                Return only the feature points, one per line, with no numbers or bullet markers.
                """
                
                try:
                    response = self.llm.generate_response(prompt)
                    # Parse the response, each line is a feature
                    new_features = [line.strip() for line in response.strip().split("\n") if line.strip()]
                    features.extend(new_features)
                except Exception as e:
                    logger.error(f"Error generating additional features: {str(e)}")
            
            # Format features as bullet points
            return features
            
        else:
            # Generate features from scratch
            prompt = f"""
            Generate key product features to highlight on packaging:
            
            Product Name: {product_info.get('name', 'Product')}
            Category: {product_info.get('category', 'General')}
            Target Audience: {target_audience}
            
            Generate 3-5 feature bullet points that:
            - Highlight benefits to the user
            - Are concise (5-8 words each)
            - Are specific and credible
            - Appeal to the target audience
            
            Return only the feature points, one per line, with no numbers or bullet markers.
            """
            
            try:
                response = self.llm.generate_response(prompt)
                # Parse the response, each line is a feature
                features = [line.strip() for line in response.strip().split("\n") if line.strip()]
                return features
            except Exception as e:
                logger.error(f"Error generating features: {str(e)}")
                # Return basic fallback features
                return [
                    "Premium quality materials",
                    "Designed for everyday use",
                    "Satisfaction guaranteed"
                ]
    
    def _generate_instructions(
        self,
        product_info: Dict[str, Any]
    ) -> str:
        """Generate usage instructions for the product.
        
        Args:
            product_info: Dictionary with product details
            
        Returns:
            Formatted usage instructions
        """
        # If instructions are provided, use them
        if "instructions" in product_info:
            if isinstance(product_info["instructions"], list):
                # Format numbered steps
                instructions = "\n".join([f"{i+1}. {step}" for i, step in enumerate(product_info["instructions"])])
                return f"INSTRUCTIONS FOR USE:\n{instructions}"
            else:
                # Return as is
                return product_info["instructions"]
        
        # Generate instructions using LLM
        prompt = f"""
        Write clear, concise usage instructions for this product:
        
        Product Name: {product_info.get('name', 'Product')}
        Category: {product_info.get('category', 'General')}
        
        The instructions should:
        - Include 3-5 numbered steps
        - Be clear and easy to follow
        - Use simple, direct language
        - Include any necessary safety precautions
        
        Format as numbered steps. Be concise. Start with "INSTRUCTIONS FOR USE:" as a heading.
        """
        
        try:
            instructions = self.llm.generate_response(prompt)
            return instructions.strip()
        except Exception as e:
            logger.error(f"Error generating instructions: {str(e)}")
            # Basic fallback
            return "INSTRUCTIONS FOR USE:\n1. Remove product from packaging\n2. Follow manufacturer guidelines\n3. Store in a cool, dry place"
    
    def _format_ingredients(self, ingredients: Union[List[str], str]) -> str:
        """Format ingredients list for packaging.
        
        Args:
            ingredients: List of ingredients or pre-formatted string
            
        Returns:
            Formatted ingredients list
        """
        if isinstance(ingredients, str):
            # Already formatted
            return ingredients
        
        # Format list as comma-separated string
        formatted = ", ".join(ingredients)
        return f"INGREDIENTS: {formatted}"
    
    def _format_nutrition(self, nutrition: Dict[str, Any]) -> str:
        """Format nutrition information.
        
        Args:
            nutrition: Dictionary with nutrition information
            
        Returns:
            Formatted nutrition facts
        """
        # This would typically use specific regulatory formats
        # For now, a simple formatting
        lines = ["NUTRITION FACTS"]
        lines.append("Serving Size: " + nutrition.get("serving_size", "1 serving"))
        lines.append("Servings Per Container: " + str(nutrition.get("servings_per_container", 1)))
        lines.append("------------------")
        
        for nutrient, value in nutrition.get("nutrients", {}).items():
            if isinstance(value, dict):
                amount = value.get("amount", "")
                unit = value.get("unit", "")
                daily_value = value.get("daily_value", "")
                line = f"{nutrient}: {amount}{unit}"
                if daily_value:
                    line += f" ({daily_value}% Daily Value)"
                lines.append(line)
            else:
                lines.append(f"{nutrient}: {value}")
        
        return "\n".join(lines)
    
    def _format_regulatory_text(self, regulatory_text: Dict[str, List[str]]) -> str:
        """Format regulatory text for packaging.
        
        Args:
            regulatory_text: Dictionary of regulatory text elements
            
        Returns:
            Formatted regulatory text
        """
        lines = []
        
        # Add warnings first
        if "warnings" in regulatory_text and regulatory_text["warnings"]:
            lines.append("WARNING:")
            for warning in regulatory_text["warnings"]:
                lines.append(warning)
            lines.append("")
        
        # Add other statements
        if "statements" in regulatory_text and regulatory_text["statements"]:
            for statement in regulatory_text["statements"]:
                lines.append(statement)
            lines.append("")
        
        # Mention required symbols
        if "symbols" in regulatory_text and regulatory_text["symbols"]:
            symbols_text = ", ".join(regulatory_text["symbols"])
            lines.append(f"This package includes the following symbols: {symbols_text}")
        
        return "\n".join(lines).strip()
    
    def _generate_warnings(
        self,
        product_info: Dict[str, Any],
        regulatory_regions: List[str]
    ) -> str:
        """Generate warning text for the product.
        
        Args:
            product_info: Dictionary with product details
            regulatory_regions: List of regions for regulatory compliance
            
        Returns:
            Formatted warning text
        """
        # If warnings are provided, use them
        if "warnings" in product_info:
            if isinstance(product_info["warnings"], list):
                return "WARNING: " + "\n".join(product_info["warnings"])
            else:
                return product_info["warnings"]
        
        # Get warnings from regulatory text
        regulatory_text = generate_regulatory_text(
            product_info.get("category", "general"),
            regulatory_regions,
            self.language
        )
        
        if "warnings" in regulatory_text and regulatory_text["warnings"]:
            return "WARNING: " + "\n".join(regulatory_text["warnings"])
        
        # If no specific warnings, generate generic ones based on category
        category = product_info.get("category", "").lower()
        
        if "electronics" in category:
            return "WARNING: To reduce the risk of fire or electric shock, do not expose this product to rain or moisture. Do not open - no user-serviceable parts inside."
        elif "food" in category or "beverage" in category:
            return "ALLERGY INFORMATION: Manufactured in a facility that processes nuts, dairy, and wheat."
        elif "children" in category or "toy" in category:
            return "WARNING: CHOKING HAZARD - Small parts. Not for children under 3 years."
        elif "chemical" in category or "cleaning" in category:
            return "WARNING: Keep out of reach of children. Avoid contact with eyes. If swallowed, seek medical advice immediately."
        else:
            # Generic warning
            return "WARNING: Read all instructions before use. Use only as directed."
    
    def _generate_sustainability_info(self, product_info: Dict[str, Any]) -> str:
        """Generate sustainability information for the product.
        
        Args:
            product_info: Dictionary with product details
            
        Returns:
            Formatted sustainability information
        """
        # If sustainability info is provided, use it
        if "sustainability" in product_info:
            if isinstance(product_info["sustainability"], str):
                return product_info["sustainability"]
            elif isinstance(product_info["sustainability"], dict):
                # Format dictionary into text
                info = product_info["sustainability"]
                lines = ["SUSTAINABILITY INFORMATION:"]
                
                if "recycled_content" in info:
                    lines.append(f"Made with {info['recycled_content']}% recycled materials")
                
                if "recyclable" in info and info["recyclable"]:
                    lines.append("This packaging is recyclable")
                
                if "biodegradable" in info and info["biodegradable"]:
                    lines.append("Biodegradable materials")
                
                if "carbon_footprint" in info:
                    lines.append(f"Carbon footprint: {info['carbon_footprint']}")
                
                if "certifications" in info and info["certifications"]:
                    certs = ", ".join(info["certifications"])
                    lines.append(f"Certifications: {certs}")
                
                return "\n".join(lines)
        
        # Generate basic sustainability info based on category
        category = product_info.get("category", "").lower()
        
        # Use LLM to generate appropriate sustainability messaging
        prompt = f"""
        Generate brief sustainability information for this product packaging:
        
        Product Category: {category}
        
        Include:
        - A brief statement about sustainability commitment
        - Packaging recyclability information
        - Any appropriate eco-friendly messaging
        
        Keep it concise (2-3 sentences) and factual. Start with "SUSTAINABILITY INFORMATION:" as a heading.
        """
        
        try:
            sustainability_info = self.llm.generate_response(prompt)
            return sustainability_info.strip()
        except Exception as e:
            logger.error(f"Error generating sustainability info: {str(e)}")
            # Basic fallback
            return "SUSTAINABILITY INFORMATION:\nWe are committed to reducing our environmental impact. This packaging is made with recyclable materials where possible."
    
    def _format_contact_info(self, contact: Dict[str, str]) -> str:
        """Format contact information.
        
        Args:
            contact: Dictionary with contact information
            
        Returns:
            Formatted contact information
        """
        lines = ["CONTACT INFORMATION:"]
        
        if "company" in contact:
            lines.append(contact["company"])
        
        if "address" in contact:
            lines.append(contact["address"])
        
        if "phone" in contact:
            lines.append(f"Phone: {contact['phone']}")
        
        if "email" in contact:
            lines.append(f"Email: {contact['email']}")
        
        if "website" in contact:
            lines.append(f"Website: {contact['website']}")
        
        return "\n".join(lines)
    
    def _generate_recycling_info(self, product_info: Dict[str, Any]) -> str:
        """Generate recycling information.
        
        Args:
            product_info: Dictionary with product details
            
        Returns:
            Formatted recycling information
        """
        # If recycling info is provided, use it
        if "recycling" in product_info:
            return product_info["recycling"]
        
        # Generate basic recycling info
        category = product_info.get("category", "").lower()
        
        if "paper" in category or "cardboard" in category:
            return "♻️ RECYCLING: 100% recyclable paper/cardboard. Please recycle."
        elif "plastic" in category:
            return "♻️ RECYCLING: Check local recycling guidelines for plastic type acceptance."
        elif "electronics" in category:
            return "♻️ RECYCLING: Electronic waste should be disposed of at designated e-waste collection points."
        elif "glass" in category:
            return "♻️ RECYCLING: Glass is 100% recyclable and can be recycled endlessly without loss of quality."
        elif "metal" in category or "aluminum" in category:
            return "♻️ RECYCLING: Metal is recyclable. Please dispose of properly at recycling facilities."
        else:
            return "♻️ RECYCLING: Please check local recycling guidelines."
    
    def recommend_text_placement(
        self, 
        box_dimensions: Tuple[float, float, float],
        text_content: Dict[TextElementType, Union[str, List[str]]]
    ) -> Dict[TextElementType, Dict[str, Any]]:
        """Recommend optimal placement for text elements on packaging.
        
        Args:
            box_dimensions: (width, height, depth) of box in mm
            text_content: Dictionary of text content by element type
            
        Returns:
            Dictionary mapping element types to placement information
        """
        width, height, depth = box_dimensions
        
        # Define the surfaces and their dimensions
        surfaces = {
            TextPlacement.FRONT: (width, height),
            TextPlacement.BACK: (width, height),
            TextPlacement.TOP: (width, depth),
            TextPlacement.BOTTOM: (width, depth),
            TextPlacement.LEFT: (depth, height),
            TextPlacement.RIGHT: (depth, height)
        }
        
        # Define default placements based on element type
        default_placements = {
            TextElementType.PRODUCT_NAME: TextPlacement.FRONT,
            TextElementType.DESCRIPTION: TextPlacement.BACK,
            TextElementType.FEATURES: TextPlacement.BACK,
            TextElementType.INSTRUCTIONS: TextPlacement.BACK,
            TextElementType.INGREDIENTS: TextPlacement.BACK,
            TextElementType.REGULATORY: TextPlacement.BACK,
            TextElementType.BRAND: TextPlacement.FRONT,
            TextElementType.WARNING: TextPlacement.BACK,
            TextElementType.NUTRITION: TextPlacement.BACK,
            TextElementType.SUSTAINABILITY: TextPlacement.BACK,
            TextElementType.CONTACT: TextPlacement.BACK,
            TextElementType.BARCODE: TextPlacement.BOTTOM,
            TextElementType.RECYCLING: TextPlacement.BOTTOM
        }
        
        # Calculate approximate space requirements for each text element
        space_requirements = {}
        for element_type, content in text_content.items():
            if isinstance(content, list):
                # For lists (like features), join with newlines
                content_str = "\n".join(content)
            else:
                content_str = str(content)
                
            # Very rough estimate of space needed
            font_size = self.default_styles.get(element_type, {}).get("font_size", 12)
            chars_per_line = int(width / (font_size * 0.6))  # Rough approximation
            lines = len(content_str) / max(1, chars_per_line) + content_str.count("\n")
            height_needed = lines * font_size * 1.2  # Line height factor
            
            space_requirements[element_type] = {
                "width": width * 0.8,  # Use 80% of surface width
                "height": height_needed
            }
        
        # Initialize result with default placements
        result = {}
        for element_type in text_content.keys():
            # Get default placement
            placement = default_placements.get(element_type, TextPlacement.BACK)
            
            # Default position (centered)
            position = {
                "x": surfaces[placement][0] / 2,
                "y": surfaces[placement][1] / 2
            }
            
            # Default orientation
            orientation = TextOrientation.HORIZONTAL
            
            # Special case for side panels
            if placement in [TextPlacement.LEFT, TextPlacement.RIGHT]:
                if space_requirements[element_type]["width"] > surfaces[placement][0]:
                    # If text is too wide for the side panel, rotate it
                    orientation = TextOrientation.VERTICAL
            
            # Get style
            style = self.default_styles.get(element_type, {})
            
            result[element_type] = {
                "placement": placement.value,
                "position": position,
                "orientation": orientation.value,
                "style": style
            }
        
        # Refine placements to avoid overlaps
        result = self._refine_text_placements(result, surfaces, space_requirements)
        
        return result
    
    def _refine_text_placements(
        self,
        initial_placements: Dict[TextElementType, Dict[str, Any]],
        surfaces: Dict[TextPlacement, Tuple[float, float]],
        space_requirements: Dict[TextElementType, Dict[str, float]]
    ) -> Dict[TextElementType, Dict[str, Any]]:
        """Refine text placements to avoid overlaps.
        
        Args:
            initial_placements: Initial placement dictionary
            surfaces: Dictionary of surface dimensions
            space_requirements: Space needed by each element
            
        Returns:
            Refined placement dictionary
        """
        # Group elements by surface
        elements_by_surface = {}
        for element_type, placement_info in initial_placements.items():
            surface = TextPlacement(placement_info["placement"])
            if surface not in elements_by_surface:
                elements_by_surface[surface] = []
            elements_by_surface[surface].append(element_type)
        
        # For each surface, arrange elements
        result = initial_placements.copy()
        for surface, elements in elements_by_surface.items():
            surface_width, surface_height = surfaces[surface]
            
            # Skip if only one element on the surface
            if len(elements) <= 1:
                continue
            
            # Sort elements by priority (product name > brand > others)
            def element_priority(element_type):
                priorities = {
                    TextElementType.PRODUCT_NAME: 1,
                    TextElementType.BRAND: 2,
                    TextElementType.WARNING: 3
                }
                return priorities.get(element_type, 10)
            
            elements.sort(key=element_priority)
            
            # Simple vertical stacking
            y_position = 20  # Start from top with margin
            for element_type in elements:
                space = space_requirements[element_type]
                
                # Update position
                result[element_type]["position"]["y"] = y_position + (space["height"] / 2)
                
                # Move down for next element
                y_position += space["height"] + 10  # 10mm margin
                
                # If we're running out of space, switch to a different surface
                if y_position > surface_height - 20:
                    # Find alternative surface
                    if surface == TextPlacement.FRONT:
                        new_surface = TextPlacement.BACK
                    else:
                        new_surface = TextPlacement.BOTTOM
                    
                    # Update placement
                    result[element_type]["placement"] = new_surface.value
                    result[element_type]["position"]["x"] = surfaces[new_surface][0] / 2
                    result[element_type]["position"]["y"] = 20 + (space["height"] / 2)
                    
                    # Add to the new surface group
                    if new_surface not in elements_by_surface:
                        elements_by_surface[new_surface] = []
                    elements_by_surface[new_surface].append(element_type)
        
        return result
    
    def create_text_layout(
        self,
        box_dimensions: Tuple[float, float, float],
        text_content: Dict[TextElementType, Union[str, List[str]]],
        custom_placements: Optional[Dict[TextElementType, Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Create a complete text layout for packaging.
        
        Args:
            box_dimensions: (width, height, depth) of box in mm
            text_content: Dictionary of text content by element type
            custom_placements: Optional custom placement overrides
            
        Returns:
            Complete text layout specification
        """
        # Get recommended placements if not provided
        if custom_placements is None:
            placements = self.recommend_text_placement(box_dimensions, text_content)
        else:
            # Use provided placements, filling in defaults for missing elements
            recommended = self.recommend_text_placement(box_dimensions, text_content)
            placements = recommended.copy()
            placements.update(custom_placements)
        
        # Process text content into final format
        elements = []
        for element_type, content in text_content.items():
            placement_info = placements.get(element_type, {})
            
            if isinstance(content, list):
                # For lists (like features), format as bullet points
                formatted_content = "\n• " + "\n• ".join(content)
            else:
                formatted_content = str(content)
            
            # Create element specification
            element = {
                "id": element_type.value,
                "type": element_type.value,
                "content": formatted_content,
                "placement": placement_info.get("placement", "back"),
                "position": placement_info.get("position", {"x": 0, "y": 0}),
                "orientation": placement_info.get("orientation", "horizontal"),
                "style": placement_info.get("style", {})
            }
            
            elements.append(element)
        
        # Create layout specification
        layout = {
            "box_dimensions": {
                "width": box_dimensions[0],
                "height": box_dimensions[1],
                "depth": box_dimensions[2]
            },
            "units": "mm",
            "elements": elements
        }
        
        return layout
    
    def export_layout_to_svg(
        self,
        layout: Dict[str, Any],
        output_path: str
    ) -> None:
        """Export text layout to SVG files for each surface.
        
        Args:
            layout: Layout specification from create_text_layout
            output_path: Base path for output files
        """
        # This would create SVG files for each surface with text elements
        # For simplicity, this is a placeholder - a real implementation would
        # generate actual SVG files with text elements positioned correctly
        
        # Group elements by surface
        elements_by_surface = {}
        for element in layout["elements"]:
            surface = element["placement"]
            if surface not in elements_by_surface:
                elements_by_surface[surface] = []
            elements_by_surface[surface].append(element)
        
        # Get box dimensions
        dimensions = layout["box_dimensions"]
        
        # For each surface, create an SVG
        for surface, elements in elements_by_surface.items():
            # Determine surface dimensions
            if surface in ["front", "back"]:
                width, height = dimensions["width"], dimensions["height"]
            elif surface in ["top", "bottom"]:
                width, height = dimensions["width"], dimensions["depth"]
            elif surface in ["left", "right"]:
                width, height = dimensions["depth"], dimensions["height"]
            else:
                width, height = dimensions["width"], dimensions["height"]
            
            # Create SVG content
            svg_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
            <svg width="{width}mm" height="{height}mm" viewBox="0 0 {width} {height}"
                 xmlns="http://www.w3.org/2000/svg">
            <rect width="{width}" height="{height}" fill="white" stroke="black" stroke-width="1"/>
            """
            
            # Add elements
            for element in elements:
                content = element["content"].replace("\n", "<br/>")
                x = element["position"]["x"]
                y = element["position"]["y"]
                
                # Apply style
                style = element["style"]
                font_size = style.get("font_size", 12)
                font_weight = style.get("font_weight", "normal")
                color = style.get("color", "#000000")
                
                # Handle orientation
                transform = ""
                if element["orientation"] == "vertical":
                    transform = f"transform='rotate(90 {x} {y})'"
                elif element["orientation"] == "rotated_90":
                    transform = f"transform='rotate(90 {x} {y})'"
                elif element["orientation"] == "rotated_270":
                    transform = f"transform='rotate(270 {x} {y})'"
                
                # Add text element
                svg_content += f"""
                <text x="{x}" y="{y}" font-size="{font_size}" font-weight="{font_weight}" 
                      fill="{color}" text-anchor="middle" {transform}>
                    {content}
                </text>
                """
            
            # Close SVG
            svg_content += "</svg>"
            
            # Write to file
            with open(f"{output_path}_{surface}.svg", "w") as f:
                f.write(svg_content)


# Example usage
if __name__ == "__main__":
    # Initialize the labeling system
    labeling = PackagingLabeling()
    
    # Product information
    product_info = {
        "name": "EcoTech Wireless Earbuds",
        "category": "Electronics",
        "key_features": [
            "40-hour battery life", 
            "Noise cancellation", 
            "Waterproof IPX7"
        ],
        "benefits": [
            "Immersive sound quality",
            "All-day comfort",
            "Eco-friendly materials"
        ]
    }
    
    # Brand information
    brand_info = {
        "name": "EcoTech",
        "tagline": "Technology in Harmony with Nature",
        "contact": {
            "company": "EcoTech Audio Inc.",
            "address": "123 Green Street, Techville, CA 94043",
            "phone": "1-800-ECO-TECH",
            "email": "info@ecotechaudio.com",
            "website": "www.ecotechaudio.com"
        }
    }
    
    # Generate packaging text
    text_content = labeling.generate_packaging_text(
        product_info,
        target_audience="Eco-conscious tech enthusiasts, 25-45 years old",
        brand_info=brand_info,
        regulatory_regions=["US", "EU"]
    )
    
    print("Generated Text Content:")
    for element_type, content in text_content.items():
        print(f"\n{element_type.name}:")
        if isinstance(content, list):
            for item in content:
                print(f"• {item}")
        else:
            print(content)
    
    # Create text layout
    box_dimensions = (120, 80, 40)  # mm
    layout = labeling.create_text_layout(box_dimensions, text_content)
    
    print("\nText Layout:")
    print(f"Number of elements: {len(layout['elements'])}")
    for element in layout['elements']:
        print(f"- {element['id']} on {element['placement']} panel")
