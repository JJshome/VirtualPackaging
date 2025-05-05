"""API routes for LLM integration."""

import logging
from typing import List, Optional, Dict, Any, Union
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()


class TextGenerationRequest(BaseModel):
    """Request to generate text content for packaging."""
    project_id: str
    product_info: Dict[str, Any]
    text_types: List[str]
    language: str = "en"
    style: str = "standard"


class LLMInteraction(BaseModel):
    """User interaction with the LLM system."""
    design_id: Optional[str] = None
    project_id: Optional[str] = None
    message: str
    context: Optional[Dict[str, Any]] = None


class Message(BaseModel):
    """A message in the conversation history."""
    role: str  # "user" or "assistant"
    content: str
    created_at: datetime


class LLMResponse(BaseModel):
    """Response from the LLM system."""
    message: str
    design_changes: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None
    questions: Optional[List[str]] = None


@router.post("/generate-text", response_model=Dict[str, str])
async def generate_packaging_text(request: TextGenerationRequest):
    """Generate text content for packaging elements."""
    try:
        # Validate project exists (mock implementation)
        if request.project_id not in ["1", "2"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {request.project_id} not found"
            )
        
        # Validate text types
        valid_text_types = [
            "product_description", "usage_instructions", "safety_warnings",
            "regulatory_info", "ingredients", "marketing_content", "sustainability_info"
        ]
        
        invalid_types = [t for t in request.text_types if t not in valid_text_types]
        if invalid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid text types: {', '.join(invalid_types)}"
            )
        
        # Mock response with generated text
        result = {}
        
        # Add sample text for each requested type
        if "product_description" in request.text_types:
            result["product_description"] = f"A premium {request.product_info.get('product_type', 'product')} designed for superior performance and reliability. Features advanced technology for enhanced user experience."
        
        if "usage_instructions" in request.text_types:
            result["usage_instructions"] = "1. Unpack the product carefully.\n2. Remove all protective packaging.\n3. Connect to power source.\n4. Press the power button to start.\n5. Refer to user manual for detailed operating instructions."
        
        if "safety_warnings" in request.text_types:
            result["safety_warnings"] = "WARNING: To reduce the risk of fire or electric shock, do not expose this product to rain or moisture. No user-serviceable parts inside. Refer servicing to qualified service personnel."
        
        if "regulatory_info" in request.text_types:
            result["regulatory_info"] = "This device complies with Part 15 of the FCC Rules. Operation is subject to the following two conditions: (1) This device may not cause harmful interference, and (2) this device must accept any interference received, including interference that may cause undesired operation."
        
        if "ingredients" in request.text_types:
            result["ingredients"] = "Components: Circuit board, plastic housing, metal heat sink, copper wiring, lithium-ion battery."
        
        if "marketing_content" in request.text_types:
            result["marketing_content"] = f"Experience the next generation of {request.product_info.get('product_type', 'technology')}. Our innovative design combines form and function for an unparalleled user experience. Don't settle for less—choose excellence."
        
        if "sustainability_info" in request.text_types:
            result["sustainability_info"] = "This product uses 30% recycled materials in its construction. The packaging is 100% recyclable and made from sustainable sources. We are committed to reducing our environmental footprint."
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate text content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate text content: {str(e)}"
        )


@router.post("/interaction", response_model=LLMResponse)
async def process_user_interaction(interaction: LLMInteraction):
    """Process user interaction with the LLM system."""
    try:
        # Validate project or design exists if provided (mock implementation)
        if interaction.project_id and interaction.project_id not in ["1", "2"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {interaction.project_id} not found"
            )
        
        if interaction.design_id and interaction.design_id != "design-1":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Design with ID {interaction.design_id} not found"
            )
        
        # Process the message (mock implementation)
        # In a real system, this would send the message to an LLM and process the response
        
        # Create mock responses based on the user's message
        if "dimension" in interaction.message.lower() or "size" in interaction.message.lower():
            return {
                "message": "I can help you adjust the dimensions of the packaging. Based on your product, I recommend a slightly more compact design to reduce material usage while still providing adequate protection. Would you like me to reduce the overall size by about 10%?",
                "design_changes": {
                    "dimensions_mm": [126.5, 94.8, 76.7],  # 10% smaller than original
                    "volume_cm3": 920.3  # Adjusted volume
                },
                "suggestions": [
                    "Reduce height for more efficient shipping",
                    "Increase padding in the base for better protection",
                    "Adjust internal support to accommodate the new dimensions"
                ],
                "questions": [
                    "Are there any specific areas where you'd like to maintain the current dimensions?",
                    "Is shipping efficiency or product protection more important for this design?"
                ]
            }
        elif "material" in interaction.message.lower() or "sustainable" in interaction.message.lower():
            return {
                "message": "I understand you're interested in more sustainable packaging materials. The current design uses regular cardboard, but we could switch to 100% recycled cardboard with minimal impact on strength. This would increase the cost slightly but reduce the environmental footprint by approximately 30%.",
                "design_changes": {
                    "material": "recycled-cardboard",
                    "estimated_cost": 1.35  # Slightly higher than original
                },
                "suggestions": [
                    "Use recycled cardboard for the main structure",
                    "Consider biodegradable inks for printing",
                    "Add sustainability messaging to the packaging design"
                ],
                "questions": [
                    "Would you like to include sustainability certification logos on the packaging?",
                    "Is the slight cost increase acceptable for the environmental benefits?"
                ]
            }
        elif "cost" in interaction.message.lower() or "price" in interaction.message.lower():
            return {
                "message": "Looking at cost optimization options, I can suggest a few changes to reduce the manufacturing cost. By simplifying the internal support structure and slightly reducing the cardboard thickness, we can lower the cost by about 15% while maintaining adequate protection.",
                "design_changes": {
                    "wall_thickness_mm": 1.8,  # Thinner than original
                    "has_complex_internal_support": False,
                    "estimated_cost": 1.06  # 15% reduction
                },
                "suggestions": [
                    "Simplify the internal support design",
                    "Reduce wall thickness from 2.0mm to 1.8mm",
                    "Consider bulk production to further reduce per-unit cost"
                ],
                "questions": [
                    "How important is premium feel versus cost efficiency for this product?",
                    "Are there specific areas where you don't want to compromise on quality?"
                ]
            }
        else:
            # Default response for other queries
            return {
                "message": f"I've reviewed your feedback about the packaging design. To better assist you, could you specify which aspects of the design you'd like to focus on? For example, we could optimize for cost, sustainability, aesthetics, or protection.",
                "design_changes": None,
                "suggestions": [
                    "Adjust dimensions for better efficiency",
                    "Explore alternative materials",
                    "Modify internal support structures",
                    "Optimize for shipping and logistics"
                ],
                "questions": [
                    "What is your primary goal for the packaging design?",
                    "Are there any specific constraints or requirements I should know about?"
                ]
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process user interaction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process user interaction: {str(e)}"
        )


@router.get("/conversation/{design_id}", response_model=List[Message])
async def get_conversation_history(design_id: str):
    """Get the conversation history for a design."""
    try:
        # Validate design exists (mock implementation)
        if design_id != "design-1":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Design with ID {design_id} not found"
            )
        
        # Mock conversation history
        now = datetime.utcnow()
        
        # Sample conversation about packaging design
        return [
            {
                "role": "user",
                "content": "I'd like to make this packaging more eco-friendly. Can you suggest some sustainable alternatives?",
                "created_at": now.replace(minute=now.minute - 20)
            },
            {
                "role": "assistant",
                "content": "I'd be happy to suggest some sustainable alternatives for your packaging. Based on your product, I recommend switching to recycled cardboard which would reduce the environmental impact by about 30%. We could also use soy-based inks for printing and minimize the use of plastic components. Would you like me to adjust the design to use these materials?",
                "created_at": now.replace(minute=now.minute - 19)
            },
            {
                "role": "user",
                "content": "Yes, please update the design with recycled cardboard. How will this affect the cost?",
                "created_at": now.replace(minute=now.minute - 15)
            },
            {
                "role": "assistant",
                "content": "I've updated the design to use recycled cardboard. This will increase the cost by approximately 8% (from $1.25 to $1.35 per unit), but it provides significant environmental benefits. The recycled cardboard has a slightly different texture but maintains 95% of the structural integrity of the original material. Would you like me to make any other adjustments to optimize the balance between sustainability and cost?",
                "created_at": now.replace(minute=now.minute - 14)
            },
            {
                "role": "user",
                "content": "That sounds good. Can we also reduce the overall size of the package to minimize material usage?",
                "created_at": now.replace(minute=now.minute - 10)
            },
            {
                "role": "assistant",
                "content": "I've analyzed your product dimensions and we can definitely reduce the overall package size. I recommend decreasing the dimensions by 10%, which would bring the dimensions to 126.5 × 94.8 × 76.7 mm. This would reduce material usage by approximately 27% and lower the carbon footprint further. It would also slightly offset the increased cost from using recycled materials. Would you like me to implement this change?",
                "created_at": now.replace(minute=now.minute - 9)
            }
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get conversation history for design {design_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation history: {str(e)}"
        )


@router.post("/design-suggestions", response_model=Dict[str, List[str]])
async def get_design_suggestions(request: Dict[str, Any]):
    """Get design suggestions for specific aspects of a packaging design."""
    try:
        # Check required fields
        if "product_type" not in request:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="product_type is required"
            )
        
        # Generate suggestions based on product type and request areas
        product_type = request["product_type"]
        areas = request.get("areas", ["materials", "structure", "aesthetics", "sustainability"])
        
        suggestions = {}
        
        # Mock suggestions for different areas
        if "materials" in areas:
            if product_type == "electronics":
                suggestions["materials"] = [
                    "Corrugated cardboard with anti-static properties",
                    "Recycled plastic with cushioning inserts",
                    "Molded pulp trays for internal component protection",
                    "Biodegradable foam for sensitive components"
                ]
            elif product_type == "fragile":
                suggestions["materials"] = [
                    "Double-wall corrugated cardboard for extra protection",
                    "Foam inserts custom-molded to product shape",
                    "Shock-absorbing corner protectors",
                    "Air pillows for void fill and cushioning"
                ]
            else:
                suggestions["materials"] = [
                    "Standard corrugated cardboard",
                    "Recycled cardboard",
                    "Biodegradable plastic",
                    "Kraft paper"
                ]
        
        if "structure" in areas:
            if product_type == "electronics":
                suggestions["structure"] = [
                    "Double-wall construction for durability",
                    "Internal dividers for component separation",
                    "Reinforced corners for impact protection",
                    "Cable management compartments"
                ]
            elif product_type == "fragile":
                suggestions["structure"] = [
                    "Suspension design to isolate product from outer walls",
                    "Multi-layered protection system",
                    "Cushioned base with reinforced edges",
                    "Form-fitting interior mold"
                ]
            else:
                suggestions["structure"] = [
                    "Simple rectangular box design",
                    "Tuck-top auto-bottom structure",
                    "Slide-out drawer with outer sleeve",
                    "Hinged lid design"
                ]
        
        if "aesthetics" in areas:
            if product_type == "electronics":
                suggestions["aesthetics"] = [
                    "Minimalist design with high-tech appearance",
                    "Clean white exterior with accent color",
                    "Embossed logo for premium feel",
                    "Color-coded setup instructions"
                ]
            elif product_type == "premium":
                suggestions["aesthetics"] = [
                    "Soft-touch matte finish",
                    "Gold or silver foil accents",
                    "Magnetic closure for elegant unboxing",
                    "Textured surface with subtle pattern"
                ]
            else:
                suggestions["aesthetics"] = [
                    "Bold color scheme with clear branding",
                    "Transparent window to display product",
                    "Modern typography and clean layout",
                    "Nature-inspired patterns and colors"
                ]
        
        if "sustainability" in areas:
            suggestions["sustainability"] = [
                "100% recycled and recyclable materials",
                "Soy-based or vegetable-based inks",
                "Minimal use of mixed materials for easier recycling",
                "Compact design to reduce material usage",
                "Water-soluble adhesives"
            ]
        
        return suggestions
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get design suggestions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get design suggestions: {str(e)}"
        )