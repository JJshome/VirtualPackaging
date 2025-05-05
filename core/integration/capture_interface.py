"""
Interface between 3D capture module and intelligence module.

This module provides utilities for converting 3D scan data into formats
that can be used by the intelligence module for design recommendations.
"""

import json
import logging
import numpy as np
from typing import Dict, Any, List, Tuple, Optional, Union
from pathlib import Path

try:
    import open3d as o3d
except ImportError:
    logging.warning("open3d not available. 3D model processing functions will be limited.")

logger = logging.getLogger(__name__)


class CaptureInterfaceError(Exception):
    """Exception for errors in the capture interface."""
    pass


def mesh_to_product_info(
    mesh_path: Union[str, Path],
    product_name: Optional[str] = None,
    category: Optional[str] = None,
    additional_info: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Convert a 3D mesh to product information dictionary.
    
    Args:
        mesh_path: Path to the 3D mesh file
        product_name: Name of the product (optional)
        category: Product category (optional)
        additional_info: Additional product information (optional)
        
    Returns:
        Dictionary with product information
    """
    mesh_path = Path(mesh_path)
    
    try:
        # Load mesh
        mesh = o3d.io.read_triangle_mesh(str(mesh_path))
        
        # Calculate basic properties
        volume = mesh.get_volume()
        surface_area = mesh.get_surface_area()
        
        # Get bounding box
        bbox = mesh.get_axis_aligned_bounding_box()
        min_bound = np.asarray(bbox.min_bound)
        max_bound = np.asarray(bbox.max_bound)
        
        # Calculate dimensions
        dimensions = max_bound - min_bound
        width, height, depth = dimensions
        
        # Calculate center of mass (approximate)
        center = mesh.get_center()
        
        # Prepare product info
        product_info = {
            "name": product_name or mesh_path.stem,
            "category": category or "unknown",
            "dimensions": {
                "width": float(width),
                "height": float(height),
                "depth": float(depth),
                "unit": "mm"
            },
            "volume": float(volume),
            "surface_area": float(surface_area),
            "center_of_mass": {
                "x": float(center[0]),
                "y": float(center[1]),
                "z": float(center[2])
            },
            "mesh_path": str(mesh_path),
            "num_vertices": len(mesh.vertices),
            "num_triangles": len(mesh.triangles)
        }
        
        # Add additional info if provided
        if additional_info:
            for key, value in additional_info.items():
                if key not in product_info:  # Don't overwrite computed values
                    product_info[key] = value
        
        return product_info
        
    except Exception as e:
        logger.error(f"Error processing mesh {mesh_path}: {str(e)}")
        raise CaptureInterfaceError(f"Failed to process mesh: {str(e)}")


def extract_features_for_llm(
    product_info: Dict[str, Any]
) -> Dict[str, Any]:
    """Extract relevant features from product info for LLM input.
    
    Args:
        product_info: Dictionary with product information
        
    Returns:
        Dictionary with features formatted for LLM input
    """
    # Get dimensions in user-friendly format
    dims = product_info.get("dimensions", {})
    dimensions_str = f"{dims.get('width', 0):.1f} x {dims.get('height', 0):.1f} x {dims.get('depth', 0):.1f} {dims.get('unit', 'mm')}"
    
    # Estimate weight (very rough approximation based on volume)
    # Assuming average density of plastic (1.2 g/cm³)
    volume_cm3 = product_info.get("volume", 0) / 1000  # Convert mm³ to cm³
    estimated_weight = volume_cm3 * 1.2  # g
    
    # Determine fragility based on dimensions and volume
    # This is a very simplified heuristic
    max_dim = max(dims.get('width', 0), dims.get('height', 0), dims.get('depth', 0))
    min_dim = min(dims.get('width', 0), dims.get('height', 0), dims.get('depth', 0))
    
    if min_dim < 2:  # Very thin in one dimension
        fragility = "High"
    elif volume_cm3 < 10:  # Small volume
        fragility = "Medium-High"
    elif max_dim > 200:  # Large in one dimension
        fragility = "Medium"
    else:
        fragility = "Low"
    
    # Extract key features for LLM
    llm_features = {
        "name": product_info.get("name", "Unnamed Product"),
        "category": product_info.get("category", "General"),
        "dimensions": dimensions_str,
        "weight": f"{estimated_weight:.1f}g (estimated)",
        "fragility": fragility,
    }
    
    # Add any additional features from product_info that might be useful
    for key in ["key_features", "benefits", "materials", "description"]:
        if key in product_info:
            llm_features[key] = product_info[key]
    
    return llm_features


def scan_to_mesh(
    scan_data_path: Union[str, Path],
    output_mesh_path: Optional[Union[str, Path]] = None,
    mesh_simplification: float = 0.5
) -> str:
    """Convert raw scan data to a processed 3D mesh.
    
    Args:
        scan_data_path: Path to raw scan data (point cloud, images, etc.)
        output_mesh_path: Path to save the output mesh (optional)
        mesh_simplification: Level of mesh simplification (0-1)
        
    Returns:
        Path to the processed mesh file
    """
    scan_data_path = Path(scan_data_path)
    
    if output_mesh_path is None:
        output_mesh_path = scan_data_path.with_suffix(".obj")
    else:
        output_mesh_path = Path(output_mesh_path)
    
    # This is a placeholder for actual scan processing logic
    # In a real implementation, this would use photogrammetry or other techniques
    logger.info(f"Processing scan data from {scan_data_path} to mesh {output_mesh_path}")
    logger.warning("scan_to_mesh is a placeholder. No actual processing is performed.")
    
    # Mock processing steps (for demonstration)
    try:
        # For demonstration, if the input is already a mesh, just copy it
        if scan_data_path.suffix in ['.obj', '.ply', '.stl']:
            import shutil
            shutil.copy(scan_data_path, output_mesh_path)
            logger.info(f"Copied existing mesh from {scan_data_path} to {output_mesh_path}")
        else:
            # Create a dummy mesh (in a real implementation this would be actual processing)
            # This is just to provide a working example
            mesh = o3d.geometry.TriangleMesh.create_sphere()
            o3d.io.write_triangle_mesh(str(output_mesh_path), mesh)
            logger.info(f"Created placeholder mesh at {output_mesh_path}")
        
        return str(output_mesh_path)
    
    except Exception as e:
        logger.error(f"Error processing scan data: {str(e)}")
        raise CaptureInterfaceError(f"Failed to process scan data: {str(e)}")
