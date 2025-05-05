"""Optimize and clean up 3D meshes for packaging design."""

import numpy as np
import open3d as o3d
import trimesh
import logging
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
from ..config import settings

logger = logging.getLogger(__name__)


class MeshOptimizationError(Exception):
    """Exception raised for errors in mesh optimization."""
    pass


def optimize_mesh(mesh: o3d.geometry.TriangleMesh, 
                quality_level: str = "medium") -> o3d.geometry.TriangleMesh:
    """Optimize a mesh for packaging design.
    
    Performs operations like hole filling, smoothing, and simplification.
    
    Args:
        mesh: Input triangle mesh
        quality_level: Optimization quality level (low, medium, high)
        
    Returns:
        Optimized triangle mesh
    """
    logger.info(f"Optimizing mesh with quality level: {quality_level}")
    
    try:
        # Set parameters based on quality level
        params = {
            "low": {
                "simplify_target_ratio": 0.25,
                "smoothing_iterations": 1
            },
            "medium": {
                "simplify_target_ratio": 0.5,
                "smoothing_iterations": 3
            },
            "high": {
                "simplify_target_ratio": 0.75,
                "smoothing_iterations": 5
            }
        }.get(quality_level.lower(), {
            "simplify_target_ratio": 0.5,
            "smoothing_iterations": 3
        })
        
        # Compute vertex normals
        mesh = mesh.compute_vertex_normals()
        
        # Fill holes
        mesh = fill_holes(mesh)
        
        # Smooth the mesh
        mesh = mesh.filter_smooth_taubin(number_of_iterations=params["smoothing_iterations"])
        
        # Simplify the mesh
        target_triangles = int(len(mesh.triangles) * params["simplify_target_ratio"])
        mesh = mesh.simplify_quadric_decimation(target_number_of_triangles=target_triangles)
        
        # Remove degenerate triangles
        mesh.remove_degenerate_triangles()
        
        # Remove duplicate vertices
        mesh.remove_duplicated_vertices()
        
        # Recompute normals
        mesh = mesh.compute_vertex_normals()
        
        logger.info(f"Mesh optimization complete: {len(mesh.vertices)} vertices, {len(mesh.triangles)} triangles")
        return mesh
        
    except Exception as e:
        logger.error(f"Mesh optimization failed: {str(e)}")
        raise MeshOptimizationError(f"Failed to optimize mesh: {str(e)}")


def fill_holes(mesh: o3d.geometry.TriangleMesh) -> o3d.geometry.TriangleMesh:
    """Fill holes in a mesh.
    
    Args:
        mesh: Input triangle mesh
        
    Returns:
        Mesh with holes filled
    """
    logger.debug("Filling holes in mesh")
    
    try:
        # Convert to trimesh for hole filling
        vertices = np.asarray(mesh.vertices)
        triangles = np.asarray(mesh.triangles)
        
        # Check if mesh is empty
        if len(vertices) == 0 or len(triangles) == 0:
            logger.warning("Empty mesh, cannot fill holes")
            return mesh
        
        # Create trimesh object
        tri_mesh = trimesh.Trimesh(vertices=vertices, faces=triangles)
        
        # Fill holes
        tri_mesh.fill_holes()
        
        # Convert back to Open3D mesh
        result_mesh = o3d.geometry.TriangleMesh()
        result_mesh.vertices = o3d.utility.Vector3dVector(np.asarray(tri_mesh.vertices))
        result_mesh.triangles = o3d.utility.Vector3iVector(np.asarray(tri_mesh.faces))
        
        return result_mesh
        
    except Exception as e:
        logger.error(f"Hole filling failed: {str(e)}")
        # Return the original mesh if hole filling fails
        return mesh


def reduce_vertices(mesh: o3d.geometry.TriangleMesh, target_count: int) -> o3d.geometry.TriangleMesh:
    """Reduce the number of vertices in a mesh.
    
    Args:
        mesh: Input triangle mesh
        target_count: Target number of vertices
        
    Returns:
        Simplified mesh
    """
    logger.info(f"Reducing mesh from {len(mesh.vertices)} vertices to {target_count} vertices")
    
    try:
        current_count = len(mesh.vertices)
        
        # If the mesh already has fewer vertices than the target, return it unchanged
        if current_count <= target_count:
            logger.info(f"Mesh already has fewer vertices ({current_count}) than target ({target_count})")
            return mesh
        
        # Target triangle count based on vertex count
        # This is a rough approximation; for most meshes triangles ≈ 2 * vertices
        target_triangles = int(target_count * 2)
        
        # Simplify mesh
        simplified_mesh = mesh.simplify_quadric_decimation(target_number_of_triangles=target_triangles)
        
        # Recompute normals
        simplified_mesh = simplified_mesh.compute_vertex_normals()
        
        logger.info(f"Mesh reduction complete: {len(simplified_mesh.vertices)} vertices, {len(simplified_mesh.triangles)} triangles")
        return simplified_mesh
        
    except Exception as e:
        logger.error(f"Mesh reduction failed: {str(e)}")
        raise MeshOptimizationError(f"Failed to reduce mesh vertices: {str(e)}")