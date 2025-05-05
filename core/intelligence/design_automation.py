"""Automated package design generation and optimization.

This module integrates LLM capabilities with 3D design processes to automatically
generate optimized packaging designs based on product specifications.
"""

import logging
import json
from typing import Dict, List, Any, Optional, Union, Tuple
from enum import Enum
import numpy as np
import os
import time

from .llm import PackagingLLM, DesignMode, ModelProvider
from ..utils.geometry_utils import calculate_volume, calculate_surface_area, get_mesh_dimensions

logger = logging.getLogger(__name__)


class DesignPriority(Enum):
    """Design priorities for optimization."""
    PROTECTION = "protection"              # Maximize product protection
    MATERIAL_EFFICIENCY = "material"       # Minimize material usage
    COST = "cost"                          # Minimize production cost
    SUSTAINABILITY = "sustainability"      # Maximize environmental friendliness
    AESTHETICS = "aesthetics"              # Maximize visual appeal
    SHIPPING_EFFICIENCY = "shipping"       # Optimize for shipping (weight/space)


class MaterialType(Enum):
    """Material types for packaging."""
    CARDBOARD = "cardboard"
    CORRUGATE = "corrugate"
    PLASTIC = "plastic"
    BIODEGRADABLE = "biodegradable"
    PAPERBOARD = "paperboard"
    MOLDED_PULP = "molded_pulp"
    FOAM = "foam"
    WOOD = "wood"


class BoxType(Enum):
    """Common box types for packaging."""
    REGULAR_SLOTTED_CONTAINER = "rsc"      # Standard shipping box
    FULL_OVERLAP_SLOTTED_CONTAINER = "fosc"  # Stronger box with overlapping flaps
    FIVE_PANEL_FOLDER = "5pf"              # Box with dust flaps and one outer flap
    DIE_CUT_DISPLAY_BOX = "dcdb"           # Retail-oriented display box
    TELESCOPE_BOX = "telescope"            # Two-piece box with separate lid
    MAILER_BOX = "mailer"                  # E-commerce style box with tear strip
    RIGID_BOX = "rigid"                    # Premium rigid box (high-end)
    PILLOW_BOX = "pillow"                  # Curved, pillow-shaped box
    DRAWER_BOX = "drawer"                  # Box with sliding drawer
    HEXAGONAL_BOX = "hexagon"              # Six-sided box
    TRIANGULAR_BOX = "triangle"            # Triangular prism box


class DesignAutomation:
    """Packaging design automation using LLM and parametric design."""

    def __init__(
        self,
        llm: Optional[PackagingLLM] = None,
        design_templates_path: str = "data/design_templates",
        materials_db_path: str = "data/materials_database.json"
    ):
        """Initialize the design automation system.
        
        Args:
            llm: PackagingLLM instance (created if None)
            design_templates_path: Path to design templates directory
            materials_db_path: Path to materials database
        """
        # Initialize or use provided LLM
        self.llm = llm or PackagingLLM(
            provider=ModelProvider.OPENAI, 
            model_name="gpt-4-turbo"
        )
        
        # Load design templates
        self.templates_path = design_templates_path
        self.templates = self._load_templates()
        
        # Load materials database
        self.materials_path = materials_db_path
        self.materials_db = self._load_materials_db()
    
    def _load_templates(self) -> Dict[str, Any]:
        """Load parametric design templates.
        
        Returns:
            Dictionary of templates
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
                        template_id = filename.split('.')[0]
                        templates[template_id] = template_data
            
            logger.info(f"Loaded {len(templates)} design templates")
            return templates
            
        except Exception as e:
            logger.error(f"Error loading templates: {str(e)}")
            return {}
    
    def _load_materials_db(self) -> Dict[str, Any]:
        """Load materials database.
        
        Returns:
            Dictionary of material properties
        """
        try:
            if not os.path.exists(self.materials_path):
                logger.warning(f"Materials database not found: {self.materials_path}")
                return {}
            
            with open(self.materials_path, 'r') as f:
                materials = json.load(f)
            
            logger.info(f"Loaded data for {len(materials)} materials")
            return materials
            
        except Exception as e:
            logger.error(f"Error loading materials database: {str(e)}")
            return {}
    
    def recommend_box_type(
        self, 
        product_info: Dict[str, Any],
        target_market: str,
        priority: DesignPriority
    ) -> Tuple[BoxType, Dict[str, Any]]:
        """Recommend optimal box type based on product and market.
        
        Args:
            product_info: Dictionary with product details
            target_market: Target market description
            priority: Design priority
            
        Returns:
            Tuple of (recommended box type, reasoning dictionary)
        """
        # Prepare inputs for LLM to get recommendations
        prompt = f"""
        As a packaging expert, recommend the ideal box type for the following product:
        
        Product: {product_info.get('name', 'Unnamed')}
        Dimensions: {product_info.get('dimensions', 'Unknown')}
        Weight: {product_info.get('weight', 'Unknown')}
        Fragility: {product_info.get('fragility', 'Medium')}
        Category: {product_info.get('category', 'General')}
        Target Market: {target_market}
        Design Priority: {priority.value}
        
        List the top 3 recommended box types from these options:
        - Regular Slotted Container (RSC)
        - Full Overlap Slotted Container (FOSC)
        - Five Panel Folder (5PF)
        - Die Cut Display Box
        - Telescope Box
        - Mailer Box
        - Rigid Box
        - Pillow Box
        - Drawer Box
        - Hexagonal Box
        - Triangular Box
        
        For each recommended type, provide:
        1. Reasoning for this recommendation
        2. Advantages for this specific product
        3. Potential disadvantages
        4. Sustainability score (1-10)
        5. Cost score (1-10, where 10 is least expensive)
        
        Format your response as a structured JSON object.
        """
        
        # Get recommendations from LLM
        response = self.llm.generate_response(prompt)
        
        # Extract JSON from response
        try:
            # Find JSON in the response (in case the LLM included other text)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                recommendations = json.loads(json_str)
            else:
                # Fallback parsing for non-JSON formatted responses
                logger.warning("LLM did not return properly formatted JSON")
                recommendations = self._parse_unstructured_recommendation(response)
                
            # Get the top recommendation
            if "recommendations" in recommendations and len(recommendations["recommendations"]) > 0:
                top_rec = recommendations["recommendations"][0]
                box_type_str = top_rec.get("type", "").lower().replace(" ", "_")
                
                # Map to BoxType enum
                for bt in BoxType:
                    if bt.value in box_type_str or box_type_str in bt.value:
                        return bt, top_rec
                
                # If no match found, default to RSC
                logger.warning(f"Could not map recommendation to known box type: {box_type_str}")
                return BoxType.REGULAR_SLOTTED_CONTAINER, top_rec
            else:
                logger.error("No recommendations found in LLM response")
                return BoxType.REGULAR_SLOTTED_CONTAINER, {"reasoning": "Default recommendation due to processing error"}
                
        except Exception as e:
            logger.error(f"Error processing box type recommendations: {str(e)}")
            return BoxType.REGULAR_SLOTTED_CONTAINER, {"reasoning": f"Default recommendation due to error: {str(e)}"}
    
    def _parse_unstructured_recommendation(self, text: str) -> Dict[str, Any]:
        """Parse unstructured text response into a structured format.
        
        Args:
            text: Unstructured text response from LLM
            
        Returns:
            Structured dictionary of recommendations
        """
        # Very basic parsing - in production would use more robust methods
        recommendations = []
        current_rec = {}
        current_section = None
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
                
            # Look for box type headers
            if "Box" in line or "Container" in line or "RSC" in line or "Mailer" in line:
                # Save previous recommendation if it exists
                if current_rec:
                    recommendations.append(current_rec)
                    current_rec = {}
                
                current_rec["type"] = line
                current_section = "type"
                continue
                
            # Look for section headers
            if "Reasoning" in line or "reason" in line:
                current_section = "reasoning"
                current_rec[current_section] = ""
                continue
                
            if "Advantages" in line or "advantages" in line or "Pros" in line:
                current_section = "advantages"
                current_rec[current_section] = ""
                continue
                
            if "Disadvantages" in line or "disadvantages" in line or "Cons" in line:
                current_section = "disadvantages"
                current_rec[current_section] = ""
                continue
                
            if "Sustainability" in line:
                try:
                    score = int(line.split(':')[-1].strip().split('/')[0].strip())
                    current_rec["sustainability_score"] = score
                except:
                    current_rec["sustainability_score"] = 5
                current_section = None
                continue
                
            if "Cost" in line:
                try:
                    score = int(line.split(':')[-1].strip().split('/')[0].strip())
                    current_rec["cost_score"] = score
                except:
                    current_rec["cost_score"] = 5
                current_section = None
                continue
                
            # Add content to current section
            if current_section and current_section in current_rec:
                current_rec[current_section] += line + " "
        
        # Add the last recommendation
        if current_rec:
            recommendations.append(current_rec)
        
        return {"recommendations": recommendations}
    
    def recommend_material(
        self, 
        product_info: Dict[str, Any],
        box_type: BoxType,
        priority: DesignPriority
    ) -> Tuple[MaterialType, Dict[str, Any]]:
        """Recommend optimal packaging material.
        
        Args:
            product_info: Dictionary with product details
            box_type: Selected box type
            priority: Design priority
            
        Returns:
            Tuple of (recommended material type, reasoning dictionary)
        """
        # Similar to recommend_box_type - get LLM recommendations
        prompt = f"""
        As a packaging materials expert, recommend the ideal material for the following product and box type:
        
        Product: {product_info.get('name', 'Unnamed')}
        Weight: {product_info.get('weight', 'Unknown')}
        Fragility: {product_info.get('fragility', 'Medium')}
        Category: {product_info.get('category', 'General')}
        Box Type: {box_type.name}
        Design Priority: {priority.value}
        
        Consider these materials:
        - Cardboard
        - Corrugated Board
        - Plastic
        - Biodegradable Materials
        - Paperboard
        - Molded Pulp
        - Foam
        - Wood
        
        For each recommended material, provide:
        1. Reasoning for this recommendation
        2. Advantages for this specific product
        3. Sustainability considerations
        4. Cost considerations
        5. Protection level provided
        
        Format your response as a structured JSON object.
        """
        
        # Get recommendations from LLM
        response = self.llm.generate_response(prompt)
        
        # Process response - similar to box type recommendation
        try:
            # Find JSON in the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                recommendations = json.loads(json_str)
            else:
                # Fallback parsing
                logger.warning("LLM did not return properly formatted JSON for material recommendation")
                recommendations = {"recommendations": [{"material": "cardboard", "reasoning": "Default recommendation"}]}
                
            # Get the top recommendation
            if "recommendations" in recommendations and len(recommendations["recommendations"]) > 0:
                top_rec = recommendations["recommendations"][0]
                material_str = top_rec.get("material", "").lower().replace(" ", "_")
                
                # Map to MaterialType enum
                for mt in MaterialType:
                    if mt.value in material_str or material_str in mt.value:
                        return mt, top_rec
                
                # If no match found, default to cardboard
                logger.warning(f"Could not map recommendation to known material type: {material_str}")
                return MaterialType.CARDBOARD, top_rec
            else:
                logger.error("No material recommendations found in LLM response")
                return MaterialType.CARDBOARD, {"reasoning": "Default recommendation due to processing error"}
                
        except Exception as e:
            logger.error(f"Error processing material recommendations: {str(e)}")
            return MaterialType.CARDBOARD, {"reasoning": f"Default recommendation due to error: {str(e)}"}
    
    def calculate_optimal_dimensions(
        self,
        product_dimensions: Tuple[float, float, float],
        box_type: BoxType,
        padding_mm: float = 10.0
    ) -> Tuple[float, float, float]:
        """Calculate optimal dimensions for the packaging.
        
        Args:
            product_dimensions: (width, height, depth) of product in mm
            box_type: Selected box type
            padding_mm: Padding around product in mm
            
        Returns:
            Tuple of (width, height, depth) for packaging in mm
        """
        # Add padding to each dimension
        width, height, depth = product_dimensions
        
        # Different box types need different dimension calculations
        if box_type == BoxType.TELESCOPE_BOX:
            # Telescope boxes need additional height for the lid
            padded_width = width + (padding_mm * 2)
            padded_height = height + (padding_mm * 3)  # Extra padding for lid
            padded_depth = depth + (padding_mm * 2)
        elif box_type == BoxType.MAILER_BOX:
            # Mailer boxes often have less padding to minimize shipping costs
            padded_width = width + (padding_mm * 1.5)
            padded_height = height + (padding_mm * 1.5)
            padded_depth = depth + (padding_mm * 1.5)
        elif box_type in [BoxType.RIGID_BOX, BoxType.DRAWER_BOX]:
            # Rigid boxes need more padding for premium feel
            padded_width = width + (padding_mm * 2.5)
            padded_height = height + (padding_mm * 2.5)
            padded_depth = depth + (padding_mm * 2.5)
        elif box_type in [BoxType.HEXAGONAL_BOX, BoxType.TRIANGULAR_BOX]:
            # Geometric boxes need special calculations
            # For simplicity, we'll use a bounding box approach
            diagonal = np.sqrt(width**2 + depth**2)
            padded_width = diagonal + (padding_mm * 2)
            padded_height = height + (padding_mm * 2)
            padded_depth = diagonal + (padding_mm * 2)
        else:
            # Standard padding for regular box types
            padded_width = width + (padding_mm * 2)
            padded_height = height + (padding_mm * 2)
            padded_depth = depth + (padding_mm * 2)
        
        return (padded_width, padded_height, padded_depth)
    
    def generate_parametric_design(
        self,
        box_type: BoxType,
        material: MaterialType,
        dimensions: Tuple[float, float, float],
        product_mesh_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate parametric 3D model for the packaging.
        
        Args:
            box_type: Type of box to generate
            material: Material for the box
            dimensions: (width, height, depth) in mm
            product_mesh_path: Optional path to product mesh for internal structure
            
        Returns:
            Dictionary with design parameters and paths to generated files
        """
        # In a full implementation, this would generate actual CAD models
        # For now, we'll return design parameters that would be used for generation
        
        width, height, depth = dimensions
        
        # Calculate material thickness based on material type and box dimensions
        material_thickness = self._calculate_material_thickness(material, width * height * depth, box_type)
        
        # Get parameters for the specific box type
        template_key = f"{box_type.value}_{material.value}"
        if template_key in self.templates:
            template = self.templates[template_key]
        else:
            # Fallback to generic template
            template = {
                "score_lines": [],
                "fold_angles": [],
                "panel_structure": "default",
                "closure_type": "tuck_in_flap"
            }
        
        # Calculate additional parameters based on dimensions
        result = {
            "box_type": box_type.value,
            "material": material.value,
            "dimensions": {
                "width": width,
                "height": height,
                "depth": depth
            },
            "material_thickness": material_thickness,
            "template_parameters": template,
            "estimated_material_area": self._calculate_material_area(box_type, width, height, depth),
            "estimated_weight": self._estimate_weight(material, width, height, depth, material_thickness),
            # In a real implementation, these would be actual file paths
            "output_files": {
                "3d_model": f"output/models/{box_type.value}_{width}x{height}x{depth}.obj",
                "2d_dieline": f"output/dielines/{box_type.value}_{width}x{height}x{depth}.svg",
                "manufacturing_specs": f"output/specs/{box_type.value}_{width}x{height}x{depth}.pdf"
            }
        }
        
        # For internal structure, we'd generate a custom holder based on the product mesh
        if product_mesh_path:
            result["internal_structure"] = {
                "type": "custom_negative",
                "mesh_path": f"output/internal/{box_type.value}_internal_{width}x{height}x{depth}.obj"
            }
        
        return result
    
    def _calculate_material_thickness(
        self, 
        material: MaterialType, 
        volume: float, 
        box_type: BoxType
    ) -> float:
        """Calculate appropriate material thickness based on product attributes.
        
        Args:
            material: Material type
            volume: Volume of the product (mm³)
            box_type: Type of box
            
        Returns:
            Material thickness in mm
        """
        # Basic calculations - in production would use more sophisticated models
        base_thickness = {
            MaterialType.CARDBOARD: 0.5,
            MaterialType.CORRUGATE: 3.0,
            MaterialType.PLASTIC: 0.8,
            MaterialType.BIODEGRADABLE: 2.0,
            MaterialType.PAPERBOARD: 0.4,
            MaterialType.MOLDED_PULP: 3.5,
            MaterialType.FOAM: 5.0,
            MaterialType.WOOD: 3.0
        }.get(material, 1.0)
        
        # Adjust thickness based on volume
        volume_factor = min(max(np.log10(volume) / 6, 0.8), 1.5)
        
        # Adjust thickness based on box type
        box_factor = {
            BoxType.REGULAR_SLOTTED_CONTAINER: 1.0,
            BoxType.FULL_OVERLAP_SLOTTED_CONTAINER: 1.1,
            BoxType.FIVE_PANEL_FOLDER: 1.0,
            BoxType.DIE_CUT_DISPLAY_BOX: 0.9,
            BoxType.TELESCOPE_BOX: 1.0,
            BoxType.MAILER_BOX: 0.95,
            BoxType.RIGID_BOX: 1.5,
            BoxType.PILLOW_BOX: 0.9,
            BoxType.DRAWER_BOX: 1.3,
            BoxType.HEXAGONAL_BOX: 1.1,
            BoxType.TRIANGULAR_BOX: 1.1
        }.get(box_type, 1.0)
        
        return base_thickness * volume_factor * box_factor
    
    def _calculate_material_area(self, box_type: BoxType, width: float, height: float, depth: float) -> float:
        """Calculate the material area needed for the box.
        
        Args:
            box_type: Type of box
            width: Width in mm
            height: Height in mm
            depth: Depth in mm
            
        Returns:
            Material area in mm²
        """
        # Basic calculations - in production would use actual dieline templates
        if box_type == BoxType.REGULAR_SLOTTED_CONTAINER:
            # RSC pattern: two width×height panels, two depth×height panels, and flaps
            panel_area = 2 * (width * height) + 2 * (depth * height)
            flap_area = 2 * (width * (depth/2)) + 2 * (depth * (width/2))
            return panel_area + flap_area
            
        elif box_type == BoxType.TELESCOPE_BOX:
            # Telescope box has two parts (base and lid)
            base_area = self._calculate_material_area(BoxType.REGULAR_SLOTTED_CONTAINER, width, height*0.7, depth)
            lid_area = self._calculate_material_area(BoxType.REGULAR_SLOTTED_CONTAINER, width+5, height*0.4, depth+5)
            return base_area + lid_area
            
        elif box_type in [BoxType.HEXAGONAL_BOX, BoxType.TRIANGULAR_BOX]:
            # Geometric shapes require special calculations
            # This is a simplification
            circumference = box_type == BoxType.HEXAGONAL_BOX and 6 * width/2 or 3 * width/2
            panel_area = circumference * height
            end_area = box_type == BoxType.HEXAGONAL_BOX and 2 * (3*np.sqrt(3)/2 * (width/2)**2) or 2 * (np.sqrt(3)/4 * width**2)
            return panel_area + end_area
            
        else:
            # Default calculation for other box types
            # This is a simplification - real calculations would be more complex
            return 2 * (width * height + width * depth + height * depth) * 1.2  # 20% extra for flaps/overlap
    
    def _estimate_weight(
        self, 
        material: MaterialType, 
        width: float, 
        height: float, 
        depth: float, 
        thickness: float
    ) -> float:
        """Estimate the weight of the packaging.
        
        Args:
            material: Material type
            width: Width in mm
            height: Height in mm
            depth: Depth in mm
            thickness: Material thickness in mm
            
        Returns:
            Estimated weight in grams
        """
        # Material densities in g/cm³
        densities = {
            MaterialType.CARDBOARD: 0.6,
            MaterialType.CORRUGATE: 0.1,
            MaterialType.PLASTIC: 1.0,
            MaterialType.BIODEGRADABLE: 0.7,
            MaterialType.PAPERBOARD: 0.8,
            MaterialType.MOLDED_PULP: 0.25,
            MaterialType.FOAM: 0.03,
            MaterialType.WOOD: 0.7
        }.get(material, 0.5)
        
        # Calculate volume of material in cm³
        area_mm2 = self._calculate_material_area(BoxType.REGULAR_SLOTTED_CONTAINER, width, height, depth)
        volume_cm3 = area_mm2 * thickness / 1000  # Convert to cm³
        
        # Calculate weight
        weight_g = volume_cm3 * densities
        
        return weight_g
    
    def suggest_design_improvements(
        self,
        design_params: Dict[str, Any],
        product_info: Dict[str, Any],
        priority: DesignPriority
    ) -> List[Dict[str, Any]]:
        """Suggest improvements to the packaging design.
        
        Args:
            design_params: Current design parameters
            product_info: Product information
            priority: Design priority
            
        Returns:
            List of suggested improvements with reasoning
        """
        # Format current design info for LLM
        design_json = json.dumps(design_params, indent=2)
        
        # Create prompt for suggestions
        prompt = f"""
        As a packaging optimization expert, review this packaging design and suggest improvements.
        
        Current design parameters:
        {design_json}
        
        Product information:
        - Name: {product_info.get('name', 'Unnamed')}
        - Category: {product_info.get('category', 'General')}
        - Fragility: {product_info.get('fragility', 'Medium')}
        
        Design priority: {priority.value}
        
        Suggest 3-5 specific improvements that would better align with the design priority.
        For each suggestion:
        1. Describe the specific change to make
        2. Explain how it improves the design for the given priority
        3. Quantify the expected improvement if possible (e.g., "15% material reduction")
        4. Note any trade-offs or potential drawbacks
        
        Format your response as a JSON array of improvement objects.
        """
        
        # Get suggestions from LLM
        response = self.llm.generate_response(prompt)
        
        # Process response to extract suggestions
        try:
            # Find JSON in the response
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                improvements = json.loads(json_str)
                return improvements
            else:
                # Fallback parsing for non-JSON formatted responses
                logger.warning("LLM did not return properly formatted JSON for improvement suggestions")
                return self._parse_unstructured_improvements(response)
                
        except Exception as e:
            logger.error(f"Error processing improvement suggestions: {str(e)}")
            return [{"suggestion": "Review design for optimization opportunities", "reasoning": "Unable to process detailed suggestions"}]
    
    def _parse_unstructured_improvements(self, text: str) -> List[Dict[str, Any]]:
        """Parse unstructured text into a list of improvement suggestions.
        
        Args:
            text: Unstructured text response from LLM
            
        Returns:
            List of improvement dictionaries
        """
        # Basic parsing for when LLM doesn't return properly formatted JSON
        improvements = []
        current_suggestion = {}
        
        lines = text.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
                
            # Look for numbered suggestions (1., 2., etc.)
            if line[0].isdigit() and line[1:].startswith('. '):
                # Save previous suggestion if it exists
                if current_suggestion and "suggestion" in current_suggestion:
                    improvements.append(current_suggestion)
                
                current_suggestion = {"suggestion": line[3:], "reasoning": ""}
                
            # If we're in a suggestion and find keywords, categorize the line
            elif current_suggestion:
                lower_line = line.lower()
                if "improv" in lower_line or "benefit" in lower_line:
                    current_suggestion["reasoning"] = line
                elif "trade" in lower_line or "drawback" in lower_line:
                    current_suggestion["tradeoffs"] = line
                elif "expect" in lower_line or "%" in line or "percent" in lower_line:
                    current_suggestion["expected_impact"] = line
                else:
                    # If not categorized, append to suggestion
                    current_suggestion["suggestion"] += " " + line
        
        # Add the last suggestion
        if current_suggestion and "suggestion" in current_suggestion:
            improvements.append(current_suggestion)
            
        # If nothing was parsed successfully, create a default suggestion
        if not improvements:
            improvements = [{"suggestion": "Review overall dimensions", "reasoning": "Optimization opportunity identified"}]
            
        return improvements


# Example usage
if __name__ == "__main__":
    # Initialize the design automation system
    design_system = DesignAutomation()
    
    # Product information
    product_info = {
        "name": "Wireless Headphones",
        "dimensions": "180 x 170 x 80 mm",
        "weight": "350g",
        "fragility": "Medium",
        "category": "Electronics",
    }
    
    # Get packaging recommendations
    box_type, box_reasoning = design_system.recommend_box_type(
        product_info,
        target_market="Premium consumer electronics",
        priority=DesignPriority.SUSTAINABILITY
    )
    
    print(f"Recommended box type: {box_type.name}")
    print(f"Reasoning: {box_reasoning.get('reasoning', 'No reasoning provided')}")
    
    # Get material recommendations
    material, material_reasoning = design_system.recommend_material(
        product_info,
        box_type=box_type,
        priority=DesignPriority.SUSTAINABILITY
    )
    
    print(f"Recommended material: {material.name}")
    print(f"Reasoning: {material_reasoning.get('reasoning', 'No reasoning provided')}")
    
    # Calculate dimensions and generate design
    product_dimensions = (180, 170, 80)  # mm
    package_dimensions = design_system.calculate_optimal_dimensions(
        product_dimensions,
        box_type,
        padding_mm=15.0
    )
    
    design = design_system.generate_parametric_design(
        box_type,
        material,
        package_dimensions
    )
    
    print(f"Design generated: {design['dimensions']}")
    print(f"Estimated weight: {design['estimated_weight']:.1f}g")
