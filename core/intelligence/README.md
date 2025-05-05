# Intelligence Module for VirtualPackaging

This directory contains the intelligence components for the VirtualPackaging system, providing AI-enhanced capabilities for automated packaging design, text generation, and regulatory compliance.

## Overview

The intelligence module leverages Large Language Models (LLMs) and other AI techniques to automate and optimize packaging design and content generation. The system is designed to:

1. Generate optimal packaging designs based on product characteristics
2. Create appropriate text content for packaging
3. Verify compliance with regulatory requirements
4. Provide intelligent recommendations throughout the design process

## Components

### LLM Integration (`llm.py`)

Core module for interacting with large language models (LLMs) to provide intelligent assistance throughout the packaging design process.

- **Features:**
  - Unified interface for multiple LLM providers (OpenAI, Anthropic, HuggingFace)
  - Text generation for packaging content
  - Design recommendations and suggestions
  - Contextual conversation capabilities

### Design Automation (`design_automation.py`)

Automated generation of packaging designs based on product specifications and requirements.

- **Features:**
  - Box type recommendation based on product characteristics
  - Material selection optimization
  - Dimension calculation and optimization
  - Parametric design generation
  - Design improvement suggestions

### Packaging Labeling (`labeling.py`)

Automated generation and optimal placement of text elements on packaging designs.

- **Features:**
  - Generation of product descriptions, features, and instructions
  - Regulatory text and warning generation
  - Optimal text element placement on packaging surfaces
  - Multi-language support
  - Export to manufacturing formats

### Regulatory Compliance (`regulatory.py`)

Verification of packaging designs against regulatory requirements for different markets and product types.

- **Features:**
  - Comprehensive regulation database for different regions
  - Compliance verification for packaging content
  - Generation of required regulatory text
  - Symbol and label requirements
  - Compliance reporting

## Usage Examples

### Design Recommendation

```python
from core.intelligence.design_automation import DesignAutomation, DesignPriority

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

# Get material recommendations
material, material_reasoning = design_system.recommend_material(
    product_info,
    box_type=box_type,
    priority=DesignPriority.SUSTAINABILITY
)
```

### Text Generation

```python
from core.intelligence.labeling import PackagingLabeling, TextElementType

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
    ]
}

# Brand information
brand_info = {
    "name": "EcoTech",
    "tagline": "Technology in Harmony with Nature"
}

# Generate packaging text
text_content = labeling.generate_packaging_text(
    product_info,
    target_audience="Eco-conscious tech enthusiasts",
    brand_info=brand_info,
    regulatory_regions=["US", "EU"]
)
```

### Regulatory Compliance

```python
from core.intelligence.regulatory import verify_compliance, generate_regulatory_text

# Product information
product_type = "electronics"
target_regions = ["US", "EU"]

# Packaging details
packaging_details = {
    "warnings": ["Keep away from children under 3 years of age"],
    "labels": ["CE Mark", "Recyclable"]
}

# Verify compliance
compliance = verify_compliance(product_type, target_regions, packaging_details)

# Generate required regulatory text
regulatory_text = generate_regulatory_text(product_type, target_regions)
```

## Integration with Other Modules

The intelligence module integrates with other components of the VirtualPackaging system:

- **Capture Module**: Uses 3D product models to inform packaging design decisions
- **Design Module**: Provides optimized parameters for packaging generation
- **Web Interface**: Enables interactive design through natural language
- **Production Module**: Generates manufacturing-ready specifications

## Requirements

- Python 3.8+
- Required packages:
  - `openai` for OpenAI API integration
  - `anthropic` for Anthropic API integration
  - `huggingface_hub` for HuggingFace models
  - `numpy` for numerical operations
  - `open3d` for 3D geometry processing

## Configuration

LLM API keys should be configured through environment variables:
- `OPENAI_API_KEY` for OpenAI models
- `ANTHROPIC_API_KEY` for Anthropic models
- `HF_API_KEY` for HuggingFace models

## Future Enhancements

- Integration with more LLM providers
- Fine-tuning models on packaging-specific data
- More comprehensive regulatory database
- Advanced optimization algorithms for material usage
- Enhanced visualization of design recommendations