"""
Intelligence modules for VirtualPackaging system.

This package contains AI/ML-powered components for:
- LLM integration for design assistance
- Packaging design optimization
- Regulatory compliance verification
- Text generation for packaging labeling

Usage:
    from core.intelligence import PackagingLLM, DesignAutomation, PackagingLabeling
    
    # Initialize LLM
    llm = PackagingLLM()
    
    # Create design automation system
    design_system = DesignAutomation(llm=llm)
    
    # Get packaging recommendations
    box_type, box_reasoning = design_system.recommend_box_type(
        product_info,
        target_market="Premium consumer electronics",
        priority=DesignPriority.SUSTAINABILITY
    )
"""

# Version information
__version__ = '0.1.0'

# Export main classes from modules for easier access
from .llm import PackagingLLM, ModelProvider, DesignMode, LLMError
from .design_automation import (
    DesignAutomation, DesignPriority, MaterialType, 
    BoxType
)
from .labeling import (
    PackagingLabeling, TextElementType, TextPlacement, 
    TextOrientation
)
from .regulatory import (
    verify_compliance, generate_regulatory_text, 
    check_material_compliance, generate_compliance_report,
    RegulatoryError
)

# Define all modules that should be imported with "from intelligence import *"
__all__ = [
    # LLM module
    'PackagingLLM', 'ModelProvider', 'DesignMode', 'LLMError',
    
    # Design automation module
    'DesignAutomation', 'DesignPriority', 'MaterialType', 'BoxType',
    
    # Labeling module
    'PackagingLabeling', 'TextElementType', 'TextPlacement', 'TextOrientation',
    
    # Regulatory module
    'verify_compliance', 'generate_regulatory_text', 'check_material_compliance',
    'generate_compliance_report', 'RegulatoryError',
]