"""Process depth camera data for 3D reconstruction."""

import numpy as np
import open3d as o3d
import logging
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from ..config import settings

logger = logging.getLogger(__name__)


class DepthProcessingError(Exception):
    """Exception raised for errors in depth processing."""
    pass


def load_depth_image(depth_path: Path, color_path: Optional[Path] = None) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    """Load a depth image and corresponding color image.
    
    Args:
        depth_path: Path to the depth image file
        color_path: Optional path to the corresponding color image file
        
    Returns:
        Tuple of (depth_image, color_image)
    """
    logger.debug(f"Loading depth image from {depth_path}")
    
    try:
        # Load depth image based on file extension
        if depth_path.suffix.lower() in ('.png', '.jpg', '.jpeg'):
            # Load as a regular image and convert
            depth_img = o3d.io.read_image(str(depth_path))
        elif depth_path.suffix.lower() == '.bin':
            # Load as binary file
            depth_data = np.fromfile(str(depth_path), dtype=np.float32)
            # Reshape based on expected dimensions (this may need adjustment)
            depth_img = depth_data.reshape(480, 640)  # Typical depth dimensions
            # Convert to open3d image
            depth_img = o3d.geometry.Image(depth_img)
        else:
            raise DepthProcessingError(f"Unsupported depth image format: {depth_path.suffix}")
        
        # Load color image if provided
        color_img = None
        if color_path:
            logger.debug(f"Loading color image from {color_path}")
            color_img = o3d.io.read_image(str(color_path))
            
        return depth_img, color_img
        
    except Exception as e:
        logger.error(f"Error loading depth image {depth_path}: {str(e)}")
        raise DepthProcessingError(f"Failed to load depth image: {str(e)}")


def create_rgbd_image(depth_img: np.ndarray, color_img: Optional[np.ndarray] = None) -> o3d.geometry.RGBDImage:
    """Create an RGBD image from depth and color images.
    
    Args:
        depth_img: Depth image
        color_img: Optional color image
        
    Returns:
        RGBD image
    """
    logger.debug("Creating RGBD image from depth and color data")
    
    try:
        # Set default parameters for depth conversion
        depth_scale = 1000.0  # Depth is in millimeters
        depth_trunc = 3.0     # Truncate depths beyond 3 meters
        
        # Create RGBD image
        if color_img is not None:
            rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(
                color_img, depth_img, depth_scale=depth_scale, depth_trunc=depth_trunc,
                convert_rgb_to_intensity=False)
        else:
            # Create a grayscale image if no color is provided
            rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(
                depth_img, depth_img, depth_scale=depth_scale, depth_trunc=depth_trunc,
                convert_rgb_to_intensity=True)
            
        return rgbd_image
        
    except Exception as e:
        logger.error(f"Error creating RGBD image: {str(e)}")
        raise DepthProcessingError(f"Failed to create RGBD image: {str(e)}")


def create_point_cloud_from_rgbd(rgbd_image: o3d.geometry.RGBDImage, 
                               intrinsics: Optional[o3d.camera.PinholeCameraIntrinsic] = None) -> o3d.geometry.PointCloud:
    """Create a point cloud from an RGBD image.
    
    Args:
        rgbd_image: RGBD image
        intrinsics: Optional camera intrinsics
        
    Returns:
        Point cloud
    """
    logger.debug("Creating point cloud from RGBD image")
    
    try:
        # Use default intrinsics if not provided
        if intrinsics is None:
            intrinsics = o3d.camera.PinholeCameraIntrinsic(
                o3d.camera.PinholeCameraIntrinsicParameters.PrimeSenseDefault)
            
        # Create point cloud
        pcd = o3d.geometry.PointCloud.create_from_rgbd_image(
            rgbd_image, intrinsics)
            
        # Flip the orientation to align with conventional coordinate system
        pcd.transform([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]])
        
        return pcd
        
    except Exception as e:
        logger.error(f"Error creating point cloud from RGBD image: {str(e)}")
        raise DepthProcessingError(f"Failed to create point cloud: {str(e)}")


def process_depth_images(depth_paths: List[Path], 
                       color_paths: Optional[List[Path]] = None,
                       output_path: Optional[Path] = None) -> o3d.geometry.PointCloud:
    """Process multiple depth images to create a consolidated point cloud.
    
    Args:
        depth_paths: List of paths to depth images
        color_paths: Optional list of paths to corresponding color images
        output_path: Optional path to save the output point cloud
        
    Returns:
        Consolidated point cloud
    """
    logger.info(f"Processing {len(depth_paths)} depth images")
    
    try:
        combined_pcd = o3d.geometry.PointCloud()
        
        # Process each depth image
        for i, depth_path in enumerate(depth_paths):
            # Get corresponding color image if available
            color_path = color_paths[i] if color_paths and i < len(color_paths) else None
            
            # Load images
            depth_img, color_img = load_depth_image(depth_path, color_path)
            
            # Create RGBD image
            rgbd_image = create_rgbd_image(depth_img, color_img)
            
            # Create point cloud
            pcd = create_point_cloud_from_rgbd(rgbd_image)
            
            # Combine point clouds
            # For accurate registration, we should perform point cloud registration here
            # This is a simple concatenation for demonstration
            combined_pcd += pcd
            
            logger.debug(f"Processed depth image {i+1}/{len(depth_paths)}")
        
        # Downsample to reduce point count
        combined_pcd = combined_pcd.voxel_down_sample(voxel_size=0.01)
        
        # Remove outliers
        combined_pcd, _ = combined_pcd.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)
        
        if output_path:
            # Create output directory if it doesn't exist
            output_path.parent.mkdir(exist_ok=True, parents=True)
            
            # Save the point cloud
            o3d.io.write_point_cloud(str(output_path), combined_pcd)
            logger.info(f"Saved point cloud to {output_path}")
        
        return combined_pcd
        
    except Exception as e:
        logger.error(f"Failed to process depth images: {str(e)}")
        raise DepthProcessingError(f"Depth image processing failed: {str(e)}")