"""3D Reconstruction algorithms from multiple 2D images."""

import numpy as np
import open3d as o3d
import cv2
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Union
from ..config import settings

logger = logging.getLogger(__name__)


class ReconstructionError(Exception):
    """Exception raised for errors in the reconstruction process."""
    pass


def preprocess_images(image_paths: List[Path]) -> List[np.ndarray]:
    """Preprocess input images for 3D reconstruction.
    
    Args:
        image_paths: List of paths to input images
        
    Returns:
        List of preprocessed images as numpy arrays
    """
    logger.info(f"Preprocessing {len(image_paths)} images for reconstruction")
    processed_images = []
    
    for img_path in image_paths:
        try:
            # Read image
            img = cv2.imread(str(img_path))
            if img is None:
                logger.warning(f"Could not read image: {img_path}")
                continue
                
            # Convert to RGB (OpenCV uses BGR)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Resize if needed
            max_dimension = 1024  # Maximum width or height
            height, width = img.shape[:2]
            if max(height, width) > max_dimension:
                scale = max_dimension / max(height, width)
                img = cv2.resize(img, (int(width * scale), int(height * scale)))
            
            # Apply preprocessing (optional enhancements)
            # - Enhance contrast
            # - Reduce noise
            # - Normalize lighting
            
            processed_images.append(img)
            
        except Exception as e:
            logger.error(f"Error processing image {img_path}: {str(e)}")
    
    if not processed_images:
        raise ReconstructionError("No valid images found for reconstruction")
    
    logger.info(f"Successfully preprocessed {len(processed_images)} images")
    return processed_images


def extract_features(images: List[np.ndarray]) -> Tuple[List[np.ndarray], List[np.ndarray]]:
    """Extract features from preprocessed images.
    
    Args:
        images: List of preprocessed images
        
    Returns:
        Tuple of (keypoints, descriptors) for all images
    """
    logger.info("Extracting features from images")
    keypoints_list = []
    descriptors_list = []
    
    # Use SIFT for feature detection
    sift = cv2.SIFT_create()
    
    for img in images:
        keypoints, descriptors = sift.detectAndCompute(img, None)
        keypoints_list.append(keypoints)
        descriptors_list.append(descriptors)
        logger.debug(f"Extracted {len(keypoints)} features from image")
    
    logger.info(f"Feature extraction complete for {len(images)} images")
    return keypoints_list, descriptors_list


def match_features(keypoints_list: List[np.ndarray], 
                  descriptors_list: List[np.ndarray]) -> Dict[Tuple[int, int], List]:
    """Match features between images.
    
    Args:
        keypoints_list: List of keypoints for each image
        descriptors_list: List of descriptors for each image
        
    Returns:
        Dictionary mapping image pairs to feature matches
    """
    logger.info("Matching features between images")
    matches_dict = {}
    
    # FLANN parameters for fast matching
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    
    # Match features between all image pairs
    num_images = len(descriptors_list)
    for i in range(num_images):
        for j in range(i+1, num_images):
            if descriptors_list[i] is None or descriptors_list[j] is None:
                logger.warning(f"Cannot match images {i} and {j} - missing descriptors")
                continue
                
            # Match descriptors
            matches = flann.knnMatch(descriptors_list[i], descriptors_list[j], k=2)
            
            # Apply ratio test to filter good matches
            good_matches = []
            for m, n in matches:
                if m.distance < 0.7 * n.distance:
                    good_matches.append(m)
            
            matches_dict[(i, j)] = good_matches
            logger.debug(f"Found {len(good_matches)} good matches between images {i} and {j}")
    
    logger.info(f"Feature matching complete with {len(matches_dict)} image pairs")
    return matches_dict


def reconstruct_from_images(image_paths: List[Path], output_path: Path) -> o3d.geometry.TriangleMesh:
    """Reconstruct 3D model from a set of images.
    
    This function performs the following steps:
    1. Preprocess the images
    2. Extract features
    3. Match features
    4. Estimate camera poses
    5. Generate point cloud
    6. Create mesh from point cloud
    
    Args:
        image_paths: List of paths to input images
        output_path: Path to save the reconstructed 3D model
        
    Returns:
        The reconstructed 3D mesh
    """
    logger.info(f"Starting 3D reconstruction from {len(image_paths)} images")
    
    # Create output directory if it doesn't exist
    output_path.parent.mkdir(exist_ok=True, parents=True)
    
    try:
        # Preprocess images
        processed_images = preprocess_images(image_paths)
        
        # Extract features from images
        keypoints_list, descriptors_list = extract_features(processed_images)
        
        # Match features between images
        matches_dict = match_features(keypoints_list, descriptors_list)
        
        # TODO: Estimate camera poses using Structure from Motion (SfM)
        
        # TODO: Generate dense point cloud using Multi-View Stereo (MVS)
        
        # Create a temporary point cloud for demonstrating functionality
        # This should be replaced with actual reconstruction logic
        point_cloud = o3d.geometry.PointCloud()
        points = np.random.rand(1000, 3)
        point_cloud.points = o3d.utility.Vector3dVector(points)
        
        # Generate mesh from point cloud
        mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(
            point_cloud, alpha=0.05)
        
        # Save the mesh
        o3d.io.write_triangle_mesh(str(output_path), mesh)
        logger.info(f"Saved reconstructed mesh to {output_path}")
        
        return mesh
        
    except Exception as e:
        logger.error(f"Reconstruction failed: {str(e)}")
        raise ReconstructionError(f"3D reconstruction failed: {str(e)}")


def estimate_volume(mesh: o3d.geometry.TriangleMesh) -> float:
    """Estimate the volume of a 3D mesh.
    
    Args:
        mesh: Input 3D mesh
        
    Returns:
        Estimated volume in cubic units
    """
    logger.info("Estimating volume of 3D mesh")
    
    try:
        # Make sure the mesh is watertight
        mesh = mesh.compute_vertex_normals()
        
        # Check if mesh is watertight
        if not mesh.is_watertight():
            logger.warning("Mesh is not watertight, volume estimate may be inaccurate")
            # Try to make the mesh watertight
            mesh = mesh.filter_smooth_simple(number_of_iterations=5)
            mesh = mesh.filter_smooth_laplacian(number_of_iterations=5)
            
        # Compute the mesh volume
        volume = mesh.get_volume()
        logger.info(f"Estimated volume: {volume:.2f} cubic units")
        
        return volume
        
    except Exception as e:
        logger.error(f"Volume estimation failed: {str(e)}")
        return -1.0  # Indicate failure