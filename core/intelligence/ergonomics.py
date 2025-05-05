"""
Ergonomics module for human-centric packaging design.

This module leverages human pose and anthropometry data to optimize 
packaging design for better user interaction and ergonomics.
"""

import logging
import numpy as np
from typing import Dict, List, Any, Tuple, Optional, Union
from pathlib import Path
import json
import os

logger = logging.getLogger(__name__)


class ErgonomicsError(Exception):
    """Exception raised for errors in the ergonomics module."""
    pass


class ErgonomicsAnalyzer:
    """Analyzer for ergonomic optimization of packaging designs."""
    
    def __init__(
        self,
        pose_data_path: Optional[str] = None,
        anthropometry_data_path: Optional[str] = None
    ):
        """Initialize the ergonomics analyzer.
        
        Args:
            pose_data_path: Path to pose dataset or model (optional)
            anthropometry_data_path: Path to anthropometry data (optional)
        """
        self.pose_data_path = pose_data_path
        self.anthropometry_data_path = anthropometry_data_path
        
        # Default anthropometry data (percentiles for adult populations)
        self.default_anthropometry = {
            "hand_length": {
                "5th_percentile": 163,  # mm (women)
                "50th_percentile": 184,  # mm (average)
                "95th_percentile": 211,  # mm (men)
            },
            "hand_breadth": {
                "5th_percentile": 74,  # mm (women)
                "50th_percentile": 87,  # mm (average)
                "95th_percentile": 100,  # mm (men)
            },
            "grip_diameter": {
                "5th_percentile": 29,  # mm (women)
                "50th_percentile": 38,  # mm (average)
                "95th_percentile": 49,  # mm (men)
            }
        }
        
        # Load custom data if paths provided
        self.anthropometry = self._load_anthropometry_data()
        self.pose_model_loaded = self._load_pose_model()
        
        logger.info("Ergonomics analyzer initialized")
    
    def _load_anthropometry_data(self) -> Dict[str, Any]:
        """Load anthropometry data from file or use defaults."""
        if self.anthropometry_data_path and os.path.exists(self.anthropometry_data_path):
            try:
                with open(self.anthropometry_data_path, 'r') as f:
                    data = json.load(f)
                logger.info(f"Loaded anthropometry data from {self.anthropometry_data_path}")
                return data
            except Exception as e:
                logger.warning(f"Failed to load anthropometry data: {str(e)}")
                logger.warning("Using default anthropometry data")
                return self.default_anthropometry
        else:
            return self.default_anthropometry
    
    def _load_pose_model(self) -> bool:
        """Load pose estimation model if available.
        
        Returns:
            True if model loaded successfully, False otherwise
        """
        if not self.pose_data_path:
            logger.info("No pose data path provided, skipping pose model loading")
            return False
            
        try:
            # This is a placeholder for actual model loading
            # In a real implementation, this would load a pose estimation model
            # from libraries like HuggingFace, PyTorch, etc.
            
            # Example using HuggingFace:
            # from transformers import AutoModelForPoseEstimation, AutoFeatureExtractor
            # self.pose_model = AutoModelForPoseEstimation.from_pretrained("nvidia/dynpose")
            # self.pose_feature_extractor = AutoFeatureExtractor.from_pretrained("nvidia/dynpose")
            
            logger.info(f"Pose model would be loaded from {self.pose_data_path}")
            logger.warning("Actual pose model loading is not implemented")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to load pose model: {str(e)}")
            return False
    
    def optimize_handle_dimensions(
        self,
        box_dimensions: Tuple[float, float, float],
        handle_type: str = "cutout",
        target_percentile: str = "5th_percentile",
        user_group: str = "general"
    ) -> Dict[str, Any]:
        """Optimize dimensions for package handles based on ergonomic data.
        
        Args:
            box_dimensions: (width, height, depth) in mm
            handle_type: Type of handle ("cutout", "strap", "grip")
            target_percentile: Target population percentile
            user_group: User population group
            
        Returns:
            Dictionary with optimized handle dimensions
        """
        width, height, depth = box_dimensions
        
        # Get appropriate anthropometry data
        if target_percentile not in ["5th_percentile", "50th_percentile", "95th_percentile"]:
            target_percentile = "5th_percentile"  # Design for smaller hands by default
            
        hand_length = self.anthropometry["hand_length"][target_percentile]
        hand_breadth = self.anthropometry["hand_breadth"][target_percentile]
        grip_diameter = self.anthropometry["grip_diameter"][target_percentile]
        
        # Calculate handle dimensions based on handle type
        if handle_type == "cutout":
            # Cutout handles should accommodate hand breadth plus clearance
            handle_width = hand_breadth * 1.2  # 20% extra for clearance
            handle_height = grip_diameter * 2  # Approximately oval shape
            
            # Ensure handle isn't too large for the box
            handle_width = min(handle_width, width * 0.4)  # Max 40% of box width
            handle_height = min(handle_height, height * 0.3)  # Max 30% of box height
            
            # Position the handle (centered horizontally, upper third vertically)
            position_x = (width - handle_width) / 2
            position_y = height * 0.25  # 25% from top
            
            return {
                "type": "cutout",
                "width": handle_width,
                "height": handle_height,
                "position_x": position_x,
                "position_y": position_y,
                "shape": "oval",
                "notes": f"Optimized for {target_percentile} hand breadth"
            }
            
        elif handle_type == "strap":
            # Strap handles need to accommodate full hand insertion
            strap_length = width * 0.6  # 60% of box width
            strap_width = grip_diameter * 1.5  # 1.5x grip diameter for comfort
            
            return {
                "type": "strap",
                "length": strap_length,
                "width": strap_width,
                "position": "top_centered",
                "notes": f"Optimized for {target_percentile} grip diameter"
            }
            
        elif handle_type == "grip":
            # Indented grip areas
            grip_width = hand_breadth * 0.7  # 70% of hand breadth
            grip_depth = grip_diameter * 0.5  # Half of optimal grip diameter
            
            return {
                "type": "grip",
                "width": grip_width,
                "depth": grip_depth,
                "position": "sides_centered",
                "notes": f"Optimized for {target_percentile} hand dimensions"
            }
            
        else:
            # Default handle
            return {
                "type": "cutout",
                "width": 80,  # mm
                "height": 30,  # mm
                "position_x": (width - 80) / 2,
                "position_y": height * 0.2,
                "shape": "rectangle",
                "notes": "Default dimensions, not ergonomically optimized"
            }
    
    def estimate_max_weight(
        self,
        handle_type: str,
        user_group: str = "general",
        safety_factor: float = 0.67
    ) -> float:
        """Estimate maximum recommended weight for a package based on handle type and user group.
        
        Args:
            handle_type: Type of handle ("cutout", "strap", "grip", "none")
            user_group: User population group
            safety_factor: Safety factor to apply (0-1)
            
        Returns:
            Maximum recommended weight in kg
        """
        # Base values for average adult lifting capacity by handle type
        base_weight_limits = {
            "cutout": 7.5,  # kg
            "strap": 10.0,  # kg
            "grip": 12.5,  # kg
            "none": 5.0,   # kg
        }
        
        # Adjustment factors for different user groups
        user_group_factors = {
            "general": 1.0,
            "elderly": 0.6,
            "children": 0.3,
            "limited_mobility": 0.5,
        }
        
        # Get base weight for handle type
        base_weight = base_weight_limits.get(handle_type, base_weight_limits["none"])
        
        # Apply user group factor
        user_factor = user_group_factors.get(user_group, user_group_factors["general"])
        
        # Calculate safe weight limit
        max_weight = base_weight * user_factor * safety_factor
        
        return max_weight
    
    def recommend_box_improvements(
        self,
        product_info: Dict[str, Any],
        box_dimensions: Tuple[float, float, float],
        target_user_group: str = "general"
    ) -> List[Dict[str, Any]]:
        """Recommend ergonomic improvements for a package design.
        
        Args:
            product_info: Dictionary with product information
            box_dimensions: (width, height, depth) in mm
            target_user_group: Target user population
            
        Returns:
            List of recommended improvements
        """
        width, height, depth = box_dimensions
        
        # Product weight
        product_weight = float(str(product_info.get("weight", "0")).split("g")[0]) / 1000  # Convert to kg
        
        # Calculate volume
        volume = width * height * depth / 1000000  # Convert to liters
        
        recommendations = []
        
        # Check if handle is needed based on weight
        if product_weight > 2.0:
            # Calculate optimal handle dimensions
            handle_info = self.optimize_handle_dimensions(
                box_dimensions,
                handle_type="cutout",
                target_percentile="5th_percentile",
                user_group=target_user_group
            )
            
            recommendations.append({
                "type": "handle_addition",
                "reason": f"Product weight ({product_weight:.1f} kg) exceeds 2 kg threshold",
                "details": handle_info,
                "priority": "high" if product_weight > 5.0 else "medium"
            })
        
        # Check box size relative to common shelving
        if any(dim > 600 for dim in box_dimensions):
            recommendations.append({
                "type": "size_adjustment",
                "reason": "Package exceeds common shelf dimensions",
                "details": "Consider reducing dimensions to improve shelf fit and handling",
                "priority": "medium"
            })
        
        # Check if box requires two-handed lifting
        if product_weight > self.estimate_max_weight("cutout", target_user_group):
            recommendations.append({
                "type": "handling_warning",
                "reason": f"Weight exceeds single-hand lift capacity for {target_user_group} users",
                "details": "Add 'Two-Person Lift' warning or improve handle design",
                "priority": "high"
            })
        
        # Check if weight distribution indicators are needed
        if volume > 10 and product_weight > 3:  # Large, somewhat heavy box
            recommendations.append({
                "type": "orientation_indicator",
                "reason": "Large package may be difficult to orient correctly",
                "details": "Add 'This Side Up' markings and center-of-gravity indicators",
                "priority": "medium"
            })
        
        return recommendations


# Utility functions for pose-based analysis

def analyze_interaction_sequence(
    pose_sequence: List[Dict[str, Any]],
    product_dimensions: Tuple[float, float, float]
) -> Dict[str, Any]:
    """Analyze a sequence of human poses interacting with a product.
    
    This is a placeholder for functionality that would use the DynPose dataset
    or similar pose datasets.
    
    Args:
        pose_sequence: List of pose data
        product_dimensions: (width, height, depth) of product in mm
        
    Returns:
        Dictionary with interaction analysis
    """
    # This is a placeholder implementation
    # In a real implementation, this would perform analysis of the pose data
    
    return {
        "interaction_zones": ["top", "sides"],
        "primary_grip_type": "power",
        "recommended_handle_position": "top",
        "recommended_handle_type": "cutout",
        "notes": "Placeholder analysis - actual pose analysis not implemented"
    }


def get_optimal_box_dimensions(
    product_dimensions: Tuple[float, float, float],
    anthropometry_data: Dict[str, Any],
    handling_scenario: str = "direct_grip"
) -> Tuple[float, float, float]:
    """Calculate optimal box dimensions based on product and human factors.
    
    Args:
        product_dimensions: (width, height, depth) of product in mm
        anthropometry_data: Dictionary with anthropometry data
        handling_scenario: How the package will be handled
        
    Returns:
        Tuple of (width, height, depth) for optimal box dimensions
    """
    # Extract product dimensions
    product_width, product_height, product_depth = product_dimensions
    
    # Get relevant anthropometry
    hand_breadth = anthropometry_data["hand_breadth"]["5th_percentile"]
    
    # Calculate dimensions based on handling scenario
    if handling_scenario == "direct_grip":
        # Add margin based on hand breadth
        width = product_width + max(20, hand_breadth * 0.5)
        height = product_height + 20  # Fixed padding
        depth = product_depth + max(20, hand_breadth * 0.5)
        
    elif handling_scenario == "two_handed":
        # Larger package, ensure enough space for two hands
        width = max(product_width + 40, hand_breadth * 2.5)
        height = product_height + 30
        depth = max(product_depth + 40, 100)  # Minimum depth for secure grip
        
    else:  # default padding
        width = product_width + 30
        height = product_height + 30
        depth = product_depth + 30
    
    return (width, height, depth)
