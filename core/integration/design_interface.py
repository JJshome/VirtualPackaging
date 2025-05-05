"""
Interface between intelligence module and design module.

This module provides utilities for converting design recommendations from 
the intelligence module into formats that can be used by the design module 
for 3D model generation.
"""

import logging
import json
import numpy as np
from typing import Dict, Any, List, Tuple, Optional, Union
from pathlib import Path

try:
    import open3d as o3d
except ImportError:
    logging.warning("open3d not available. 3D model processing functions will be limited.")

logger = logging.getLogger(__name__)


class DesignInterfaceError(Exception):
    """Exception for errors in the design interface."""
    pass


def create_design_spec(
    product_info: Dict[str, Any],
    box_type: str,
    material: str,
    dimensions: Tuple[float, float, float],
    internal_structure: Optional[str] = "negative",
    padding: float = 10.0,
    output_path: Optional[Union[str, Path]] = None
) -> Dict[str, Any]:
    """Create design specification for the design module.
    
    Args:
        product_info: Dictionary with product information
        box_type: Type of box to generate
        material: Material for the box
        dimensions: (width, height, depth) in mm
        internal_structure: Type of internal structure ("negative", "cradle", "clip")
        padding: Padding around product in mm
        output_path: Path to save the design specification (optional)
        
    Returns:
        Dictionary with design specification
    """
    # Extract product mesh path
    product_mesh_path = product_info.get("mesh_path")
    if not product_mesh_path:
        raise DesignInterfaceError("Product mesh path not found in product_info")
    
    # Convert dimensions to internal format
    width, height, depth = dimensions
    
    # Create design spec
    design_spec = {
        "product": {
            "name": product_info.get("name", "Unnamed Product"),
            "category": product_info.get("category", "General"),
            "mesh_path": product_mesh_path
        },
        "box": {
            "type": box_type,
            "material": material,
            "dimensions": {
                "width": width,
                "height": height,
                "depth": depth,
                "unit": "mm"
            },
            "internal_structure": {
                "type": internal_structure,
                "padding": padding
            }
        },
        "manufacturing": {
            "wall_thickness": get_wall_thickness(material),
            "corner_radius": 2.0,
            "tolerance": 0.5
        },
        "metadata": {
            "generated_by": "VirtualPackaging",
            "version": "0.1.0"
        }
    }
    
    # Save to file if output path provided
    if output_path:
        output_path = Path(output_path)
        with open(output_path, 'w') as f:
            json.dump(design_spec, f, indent=2)
        logger.info(f"Saved design specification to {output_path}")
    
    return design_spec


def get_wall_thickness(material: str) -> float:
    """Determine appropriate wall thickness based on material.
    
    Args:
        material: Material type
        
    Returns:
        Wall thickness in mm
    """
    # Simple mapping of materials to typical wall thicknesses
    thickness_map = {
        "cardboard": 1.5,
        "corrugate": 3.0,
        "plastic": 1.0,
        "biodegradable": 2.0,
        "paperboard": 0.7,
        "molded_pulp": 3.5,
        "foam": 5.0,
        "wood": 3.0
    }
    
    # Default to cardboard if material not found
    return thickness_map.get(material.lower(), 1.5)


def generate_box_mesh(
    design_spec: Dict[str, Any],
    output_path: Optional[Union[str, Path]] = None
) -> o3d.geometry.TriangleMesh:
    """Generate a 3D mesh for a box based on design specification.
    
    Args:
        design_spec: Dictionary with design specification
        output_path: Path to save the generated mesh (optional)
        
    Returns:
        Box mesh as an Open3D TriangleMesh
    """
    # Extract dimensions
    dimensions = design_spec["box"]["dimensions"]
    width = dimensions["width"]
    height = dimensions["height"]
    depth = dimensions["depth"]
    
    # Extract manufacturing parameters
    manufacturing = design_spec["manufacturing"]
    wall_thickness = manufacturing["wall_thickness"]
    corner_radius = manufacturing["corner_radius"]
    
    # Create outer box mesh
    outer_box = o3d.geometry.TriangleMesh.create_box(
        width=width, 
        height=height, 
        depth=depth
    )
    
    # Create inner box mesh for hollowing
    inner_width = width - (2 * wall_thickness)
    inner_height = height - (2 * wall_thickness)
    inner_depth = depth - (2 * wall_thickness)
    
    inner_box = o3d.geometry.TriangleMesh.create_box(
        width=inner_width,
        height=inner_height,
        depth=inner_depth
    )
    
    # Move inner box to center of outer box
    inner_box.translate([wall_thickness, wall_thickness, wall_thickness])
    
    # Boolean difference to create hollow box
    # Note: Open3D doesn't directly support boolean operations
    # In a real implementation, this would use a CAD library
    # This is a simplified placeholder
    box_mesh = outer_box
    logger.warning("generate_box_mesh is simplified. No actual hollow box is created.")
    
    # Save to file if output path provided
    if output_path:
        o3d.io.write_triangle_mesh(str(output_path), box_mesh)
        logger.info(f"Saved box mesh to {output_path}")
    
    return box_mesh


def generate_internal_structure(
    design_spec: Dict[str, Any],
    product_mesh: o3d.geometry.TriangleMesh,
    output_path: Optional[Union[str, Path]] = None
) -> o3d.geometry.TriangleMesh:
    """Generate internal structure mesh based on product and design specification.
    
    Args:
        design_spec: Dictionary with design specification
        product_mesh: Mesh of the product
        output_path: Path to save the generated mesh (optional)
        
    Returns:
        Internal structure mesh as an Open3D TriangleMesh
    """
    # Extract relevant information
    internal_structure_type = design_spec["box"]["internal_structure"]["type"]
    padding = design_spec["box"]["internal_structure"]["padding"]
    
    # Get product dimensions
    product_bbox = product_mesh.get_axis_aligned_bounding_box()
    product_center = product_mesh.get_center()
    
    # Create a placeholder structure
    # In a real implementation, this would generate actual support structures
    # For now, just create a simple mesh to demonstrate
    if internal_structure_type == "negative":
        # For "negative" type, create a box slightly larger than the product
        structure = o3d.geometry.TriangleMesh.create_box(
            width=product_bbox.get_extent()[0] + padding,
            height=product_bbox.get_extent()[1] + padding,
            depth=product_bbox.get_extent()[2] + padding
        )
        
        # Center the structure
        structure.translate([
            product_center[0] - (product_bbox.get_extent()[0] + padding) / 2,
            product_center[1] - (product_bbox.get_extent()[1] + padding) / 2,
            product_center[2] - (product_bbox.get_extent()[2] + padding) / 2
        ])
        
    elif internal_structure_type == "cradle":
        # For "cradle" type, create a simple platform
        structure = o3d.geometry.TriangleMesh.create_box(
            width=product_bbox.get_extent()[0] + padding,
            height=padding / 2,
            depth=product_bbox.get_extent()[2] + padding
        )
        
        # Position at the bottom
        structure.translate([
            product_center[0] - (product_bbox.get_extent()[0] + padding) / 2,
            product_center[1] - product_bbox.get_extent()[1] / 2 - padding / 2,
            product_center[2] - (product_bbox.get_extent()[2] + padding) / 2
        ])
        
    else:
        # Default to a simple platform
        structure = o3d.geometry.TriangleMesh.create_box(
            width=product_bbox.get_extent()[0],
            height=padding / 2,
            depth=product_bbox.get_extent()[2]
        )
        
        # Position at the bottom
        structure.translate([
            product_center[0] - product_bbox.get_extent()[0] / 2,
            product_center[1] - product_bbox.get_extent()[1] / 2 - padding / 2,
            product_center[2] - product_bbox.get_extent()[2] / 2
        ])
    
    # Save to file if output path provided
    if output_path:
        o3d.io.write_triangle_mesh(str(output_path), structure)
        logger.info(f"Saved internal structure mesh to {output_path}")
    
    return structure


def combine_meshes(
    box_mesh: o3d.geometry.TriangleMesh,
    internal_structure: o3d.geometry.TriangleMesh,
    output_path: Optional[Union[str, Path]] = None
) -> o3d.geometry.TriangleMesh:
    """Combine box and internal structure meshes.
    
    Args:
        box_mesh: Mesh of the box
        internal_structure: Mesh of the internal structure
        output_path: Path to save the combined mesh (optional)
        
    Returns:
        Combined mesh as an Open3D TriangleMesh
    """
    # In a real implementation, this would use boolean operations
    # Open3D doesn't support boolean operations natively, so we'll just combine the meshes
    
    # Create a new mesh that combines both
    combined = box_mesh + internal_structure
    
    # Save to file if output path provided
    if output_path:
        o3d.io.write_triangle_mesh(str(output_path), combined)
        logger.info(f"Saved combined mesh to {output_path}")
    
    return combined