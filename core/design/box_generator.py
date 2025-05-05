"""Generate packaging boxes based on product 3D models."""

import numpy as np
import open3d as o3d
import trimesh
import logging
from pathlib import Path
from typing import Tuple, Dict, List, Optional, Any
from enum import Enum
from ..config import settings

logger = logging.getLogger(__name__)


class BoxType(Enum):
    """Types of packaging boxes."""
    STANDARD = "standard"  # Regular rectangular box
    SLEEVE = "sleeve"      # Box with a sliding sleeve
    CLAMSHELL = "clamshell"  # Hinged box that opens like a clamshell
    TRAY = "tray"         # Open tray with a lid
    CUSTOM = "custom"     # Custom-shaped box


class BoxGeneratorError(Exception):
    """Exception raised for errors in box generation."""
    pass


def calculate_bounding_box(mesh: o3d.geometry.TriangleMesh) -> Tuple[np.ndarray, np.ndarray]:
    """Calculate the axis-aligned bounding box of a mesh.
    
    Args:
        mesh: Input 3D mesh
        
    Returns:
        Tuple of (min_bound, max_bound) as numpy arrays
    """
    logger.debug("Calculating bounding box for mesh")
    
    try:
        # Get the axis-aligned bounding box
        aabb = mesh.get_axis_aligned_bounding_box()
        min_bound = np.asarray(aabb.min_bound)
        max_bound = np.asarray(aabb.max_bound)
        
        dimensions = max_bound - min_bound
        logger.debug(f"Bounding box dimensions: {dimensions}")
        
        return min_bound, max_bound
        
    except Exception as e:
        logger.error(f"Error calculating bounding box: {str(e)}")
        raise BoxGeneratorError(f"Failed to calculate bounding box: {str(e)}")


def add_padding(min_bound: np.ndarray, max_bound: np.ndarray, padding: float = 10.0) -> Tuple[np.ndarray, np.ndarray]:
    """Add padding to a bounding box.
    
    Args:
        min_bound: Minimum corner of the bounding box
        max_bound: Maximum corner of the bounding box
        padding: Padding amount in millimeters
        
    Returns:
        Tuple of (padded_min_bound, padded_max_bound)
    """
    logger.debug(f"Adding {padding}mm padding to bounding box")
    
    padded_min = min_bound - padding
    padded_max = max_bound + padding
    
    dimensions = padded_max - padded_min
    logger.debug(f"Padded box dimensions: {dimensions}")
    
    return padded_min, padded_max


def generate_box(product_mesh: o3d.geometry.TriangleMesh, 
                box_type: BoxType = BoxType.STANDARD,
                padding: float = 10.0,
                wall_thickness: float = 2.0) -> o3d.geometry.TriangleMesh:
    """Generate a packaging box for a product.
    
    Args:
        product_mesh: 3D mesh of the product
        box_type: Type of box to generate
        padding: Padding between product and box walls (mm)
        wall_thickness: Thickness of box walls (mm)
        
    Returns:
        3D mesh of the generated box
    """
    logger.info(f"Generating {box_type.value} box with {padding}mm padding")
    
    try:
        # Calculate product bounding box
        min_bound, max_bound = calculate_bounding_box(product_mesh)
        
        # Add padding
        padded_min, padded_max = add_padding(min_bound, max_bound, padding)
        
        # Calculate dimensions
        dimensions = padded_max - padded_min
        width, height, depth = dimensions
        
        # Generate box based on type
        if box_type == BoxType.STANDARD:
            box_mesh = generate_standard_box(padded_min, padded_max, wall_thickness)
        elif box_type == BoxType.SLEEVE:
            box_mesh = generate_sleeve_box(padded_min, padded_max, wall_thickness)
        elif box_type == BoxType.CLAMSHELL:
            box_mesh = generate_clamshell_box(padded_min, padded_max, wall_thickness)
        elif box_type == BoxType.TRAY:
            box_mesh = generate_tray_box(padded_min, padded_max, wall_thickness)
        elif box_type == BoxType.CUSTOM:
            # Custom boxes would require more parameters and logic
            box_mesh = generate_standard_box(padded_min, padded_max, wall_thickness)
        else:
            # Default to standard box
            box_mesh = generate_standard_box(padded_min, padded_max, wall_thickness)
        
        logger.info(f"Box generation complete: {len(box_mesh.vertices)} vertices, {len(box_mesh.triangles)} triangles")
        return box_mesh
        
    except Exception as e:
        logger.error(f"Box generation failed: {str(e)}")
        raise BoxGeneratorError(f"Failed to generate box: {str(e)}")


def generate_standard_box(min_bound: np.ndarray, max_bound: np.ndarray, 
                        wall_thickness: float) -> o3d.geometry.TriangleMesh:
    """Generate a standard rectangular box.
    
    Args:
        min_bound: Minimum corner of the bounding box
        max_bound: Maximum corner of the bounding box
        wall_thickness: Thickness of box walls
        
    Returns:
        3D mesh of the box
    """
    logger.debug("Generating standard rectangular box")
    
    try:
        # Calculate dimensions
        dimensions = max_bound - min_bound
        width, height, depth = dimensions
        
        # Create outer box
        outer_box = o3d.geometry.TriangleMesh.create_box(
            width=width + (2 * wall_thickness),
            height=height + (2 * wall_thickness),
            depth=depth + (2 * wall_thickness)
        )
        
        # Create inner box (cavity)
        inner_box = o3d.geometry.TriangleMesh.create_box(
            width=width,
            height=height,
            depth=depth
        )
        
        # Position inner box correctly
        inner_box = inner_box.translate([wall_thickness, wall_thickness, wall_thickness])
        
        # Boolean difference to create hollow box
        # Note: Open3D doesn't directly support boolean operations
        # Convert to trimesh for boolean operation
        outer_trimesh = trimesh.Trimesh(
            vertices=np.asarray(outer_box.vertices),
            faces=np.asarray(outer_box.triangles)
        )
        inner_trimesh = trimesh.Trimesh(
            vertices=np.asarray(inner_box.vertices),
            faces=np.asarray(inner_box.triangles)
        )
        
        # Perform boolean difference
        hollow_box_trimesh = outer_trimesh.difference(inner_trimesh)
        
        # Convert back to Open3D mesh
        hollow_box = o3d.geometry.TriangleMesh()
        hollow_box.vertices = o3d.utility.Vector3dVector(hollow_box_trimesh.vertices)
        hollow_box.triangles = o3d.utility.Vector3iVector(hollow_box_trimesh.faces)
        
        # Position box centered on the origin
        center = (min_bound + max_bound) / 2
        translation = -center
        hollow_box = hollow_box.translate(translation)
        
        # Compute normals
        hollow_box = hollow_box.compute_vertex_normals()
        
        return hollow_box
        
    except Exception as e:
        logger.error(f"Error generating standard box: {str(e)}")
        raise BoxGeneratorError(f"Failed to generate standard box: {str(e)}")


def generate_sleeve_box(min_bound: np.ndarray, max_bound: np.ndarray, 
                      wall_thickness: float) -> o3d.geometry.TriangleMesh:
    """Generate a box with a sliding sleeve.
    
    Args:
        min_bound: Minimum corner of the bounding box
        max_bound: Maximum corner of the bounding box
        wall_thickness: Thickness of box walls
        
    Returns:
        3D mesh of the box
    """
    logger.debug("Generating sleeve box")
    
    # Simplified implementation - in a real-world scenario, this would be more complex
    # For now, we'll just return a standard box as a placeholder
    # TODO: Implement actual sleeve box generation
    return generate_standard_box(min_bound, max_bound, wall_thickness)


def generate_clamshell_box(min_bound: np.ndarray, max_bound: np.ndarray, 
                         wall_thickness: float) -> o3d.geometry.TriangleMesh:
    """Generate a hinged clamshell box.
    
    Args:
        min_bound: Minimum corner of the bounding box
        max_bound: Maximum corner of the bounding box
        wall_thickness: Thickness of box walls
        
    Returns:
        3D mesh of the box
    """
    logger.debug("Generating clamshell box")
    
    # Simplified implementation - placeholder
    # TODO: Implement actual clamshell box generation
    return generate_standard_box(min_bound, max_bound, wall_thickness)


def generate_tray_box(min_bound: np.ndarray, max_bound: np.ndarray, 
                    wall_thickness: float) -> o3d.geometry.TriangleMesh:
    """Generate a tray with a lid.
    
    Args:
        min_bound: Minimum corner of the bounding box
        max_bound: Maximum corner of the bounding box
        wall_thickness: Thickness of box walls
        
    Returns:
        3D mesh of the box
    """
    logger.debug("Generating tray box")
    
    # Simplified implementation - placeholder
    # TODO: Implement actual tray box generation
    return generate_standard_box(min_bound, max_bound, wall_thickness)


def optimize_box_dimensions(product_mesh: o3d.geometry.TriangleMesh,
                          padding: float = 10.0,
                          constraints: Optional[Dict[str, float]] = None) -> Tuple[float, float, float]:
    """Optimize box dimensions based on product mesh and constraints.
    
    Args:
        product_mesh: 3D mesh of the product
        padding: Padding between product and box walls (mm)
        constraints: Dict with optional constraints (max_width, max_height, max_depth, max_volume)
        
    Returns:
        Tuple of optimized (width, height, depth)
    """
    logger.info("Optimizing box dimensions")
    
    try:
        # Set default constraints if not provided
        if constraints is None:
            constraints = {}
        
        # Calculate product bounding box
        min_bound, max_bound = calculate_bounding_box(product_mesh)
        
        # Add padding
        padded_min, padded_max = add_padding(min_bound, max_bound, padding)
        
        # Get initial dimensions
        dimensions = padded_max - padded_min
        width, height, depth = dimensions
        
        # Check constraints
        max_width = constraints.get('max_width')
        max_height = constraints.get('max_height')
        max_depth = constraints.get('max_depth')
        max_volume = constraints.get('max_volume')
        
        # Apply constraints if specified
        if max_width and width > max_width:
            scale = max_width / width
            width = max_width
            height *= scale
            depth *= scale
            logger.debug(f"Scaled dimensions to meet max_width constraint: {width, height, depth}")
        
        if max_height and height > max_height:
            scale = max_height / height
            height = max_height
            width *= scale
            depth *= scale
            logger.debug(f"Scaled dimensions to meet max_height constraint: {width, height, depth}")
        
        if max_depth and depth > max_depth:
            scale = max_depth / depth
            depth = max_depth
            width *= scale
            height *= scale
            logger.debug(f"Scaled dimensions to meet max_depth constraint: {width, height, depth}")
        
        # Check volume constraint
        if max_volume:
            volume = width * height * depth
            if volume > max_volume:
                scale = (max_volume / volume) ** (1/3)  # Cubic root to maintain proportions
                width *= scale
                height *= scale
                depth *= scale
                logger.debug(f"Scaled dimensions to meet max_volume constraint: {width, height, depth}")
        
        logger.info(f"Optimized box dimensions: {width:.2f} x {height:.2f} x {depth:.2f} mm")
        return width, height, depth
        
    except Exception as e:
        logger.error(f"Box dimension optimization failed: {str(e)}")
        raise BoxGeneratorError(f"Failed to optimize box dimensions: {str(e)}")