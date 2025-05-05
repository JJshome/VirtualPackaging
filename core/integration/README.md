# Integration Module for VirtualPackaging

This module provides interfaces and utilities for connecting different components of the VirtualPackaging system, focusing on smooth data flow between modules.

## Overview

The integration module serves as a bridge between:
- **Capture Module**: 3D scanning and reconstruction
- **Intelligence Module**: LLM-powered design recommendations
- **Design Module**: 3D modeling and packaging creation
- **Production Module**: Manufacturing output generation

## Components

### Capture Interface

`capture_interface.py` provides utilities for:
- Converting 3D scans into product information
- Processing raw scan data into 3D meshes
- Extracting relevant features for LLM input

```python
from core.integration.capture_interface import mesh_to_product_info, extract_features_for_llm

# Convert 3D mesh to product info
product_info = mesh_to_product_info(
    "path/to/product.obj",
    product_name="Wireless Earbuds",
    category="Electronics"
)

# Extract features suitable for LLM prompts
llm_features = extract_features_for_llm(product_info)
```

### Design Interface

`design_interface.py` provides utilities for:
- Converting design recommendations into design specifications
- Generating 3D models based on specifications
- Creating internal support structures

```python
from core.integration.design_interface import create_design_spec, generate_box_mesh

# Create design specification
design_spec = create_design_spec(
    product_info,
    box_type="mailer",
    material="cardboard",
    dimensions=(120, 80, 40)
)

# Generate 3D model
box_mesh = generate_box_mesh(design_spec, output_path="box.obj")
```

## Complete Workflow

The integration module enables a complete workflow from 3D scan to manufacturing output:

1. **Scan Processing**: Convert raw scan data into 3D product mesh
2. **Feature Extraction**: Extract relevant product features for LLM input
3. **Design Recommendation**: Use LLM to recommend optimal packaging design
4. **3D Model Generation**: Create 3D models of the packaging design
5. **Text Generation**: Generate and position text on the packaging
6. **Export**: Create manufacturing-ready files

A complete example can be found in `examples/complete_workflow.py`.

## Extending the Integration Module

### Adding New Interfaces

To create a new interface between modules:

1. Create a new file in the `core/integration` directory
2. Define clear input/output data structures
3. Provide conversion functions between formats
4. Add proper error handling and logging

### Handling Alternative Data Formats

To support additional 3D file formats or data structures:

1. Add appropriate import logic in capture_interface.py
2. Extend conversion functions to handle the new format
3. Update documentation with supported formats

## Dependencies

The integration module relies on:
- `open3d` for 3D mesh processing
- `numpy` for numerical operations
- Core VirtualPackaging modules for business logic

See the project's `requirements.txt` for full dependency list.
