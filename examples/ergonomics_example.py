#!/usr/bin/env python3
"""
Ergonomics optimization example for VirtualPackaging.

This script demonstrates how to use the ergonomics module to optimize
packaging designs for human interaction, showing the integration with
the DynPose dataset concepts.

Usage:
    python ergonomics_example.py [options]
    
Options:
    --output-dir PATH       Directory to save output files
    --product-file PATH     Path to product mesh file
    --user-group GROUP      Target user group (general, elderly, children)
"""

import os
import sys
import argparse
import logging
from pathlib import Path
import json

# Add parent directory to path to import from core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import VirtualPackaging modules
from core.intelligence.ergonomics import ErgonomicsAnalyzer, get_optimal_box_dimensions
from core.integration.capture_interface import mesh_to_product_info

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='VirtualPackaging ergonomics example')
    
    parser.add_argument(
        '--output-dir', 
        type=str, 
        default='output',
        help='Directory to save output files'
    )
    
    parser.add_argument(
        '--product-file', 
        type=str, 
        default=None,
        help='Path to product mesh file'
    )
    
    parser.add_argument(
        '--user-group', 
        type=str, 
        choices=['general', 'elderly', 'children', 'limited_mobility'],
        default='general',
        help='Target user group'
    )
    
    return parser.parse_args()


def create_sample_product():
    """Create a sample product for demonstration."""
    return {
        "name": "Portable Speaker",
        "category": "Electronics",
        "dimensions": {
            "width": 120,
            "height": 180,
            "depth": 80,
            "unit": "mm"
        },
        "weight": "850g",
        "fragility": "Medium",
    }


def main():
    """Run the ergonomics example."""
    # Parse arguments
    args = parse_arguments()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Initialize product information
    logger.info("Step 1: Getting product information...")
    
    if args.product_file and os.path.exists(args.product_file):
        # Get product info from mesh file
        product_info = mesh_to_product_info(
            args.product_file,
            product_name="Sample Product",
            category="General"
        )
        logger.info(f"Extracted product info from {args.product_file}")
    else:
        # Use sample product
        product_info = create_sample_product()
        logger.info("Using sample product data")
    
    # Get product dimensions
    dimensions = (
        product_info["dimensions"]["width"],
        product_info["dimensions"]["height"],
        product_info["dimensions"]["depth"]
    )
    
    # Step 2: Initialize ergonomics analyzer
    logger.info("Step 2: Initializing ergonomics analyzer...")
    ergonomics = ErgonomicsAnalyzer()
    
    # Step 3: Get handle recommendations
    logger.info("Step 3: Generating handle recommendations...")
    
    # Determine if handles are needed based on weight
    weight_str = product_info.get("weight", "0g")
    weight_g = float(weight_str.replace("g", "").strip())
    
    handle_types = ["cutout", "strap", "grip"]
    handle_results = {}
    
    for handle_type in handle_types:
        handle_info = ergonomics.optimize_handle_dimensions(
            dimensions,
            handle_type=handle_type,
            target_percentile="5th_percentile",
            user_group=args.user_group
        )
        handle_results[handle_type] = handle_info
    
    # Save handle recommendations
    handle_file = output_dir / "handle_recommendations.json"
    with open(handle_file, 'w') as f:
        json.dump(handle_results, f, indent=2)
    logger.info(f"Saved handle recommendations to {handle_file}")
    
    # Step 4: Calculate weight limits
    logger.info("Step 4: Calculating weight limits...")
    
    weight_limits = {}
    for handle_type in handle_types + ["none"]:
        max_weight = ergonomics.estimate_max_weight(
            handle_type,
            user_group=args.user_group
        )
        weight_limits[handle_type] = max_weight
    
    # Save weight limits
    weight_file = output_dir / "weight_limits.json"
    with open(weight_file, 'w') as f:
        json.dump(weight_limits, f, indent=2)
    logger.info(f"Saved weight limits to {weight_file}")
    
    # Step 5: Get general packaging recommendations
    logger.info("Step 5: Generating ergonomic recommendations...")
    
    recommendations = ergonomics.recommend_box_improvements(
        product_info,
        dimensions,
        target_user_group=args.user_group
    )
    
    # Save recommendations
    recommendations_file = output_dir / "ergonomic_recommendations.json"
    with open(recommendations_file, 'w') as f:
        json.dump(recommendations, f, indent=2)
    logger.info(f"Saved ergonomic recommendations to {recommendations_file}")
    
    # Step 6: Calculate optimal packaging dimensions
    logger.info("Step 6: Calculating optimal packaging dimensions...")
    
    # Default anthropometry data
    anthropometry = ergonomics.anthropometry
    
    # Calculate optimal dimensions for different handling scenarios
    optimal_dimensions = {}
    for scenario in ["direct_grip", "two_handed", "default"]:
        optimal = get_optimal_box_dimensions(
            dimensions,
            anthropometry,
            handling_scenario=scenario
        )
        optimal_dimensions[scenario] = {
            "width": optimal[0],
            "height": optimal[1],
            "depth": optimal[2]
        }
    
    # Save optimal dimensions
    dimensions_file = output_dir / "optimal_dimensions.json"
    with open(dimensions_file, 'w') as f:
        json.dump(optimal_dimensions, f, indent=2)
    logger.info(f"Saved optimal dimensions to {dimensions_file}")
    
    # Step 7: Summary and visualization (simplified)
    logger.info("\nErgonomics Analysis Summary:")
    logger.info(f"Product: {product_info['name']} ({product_info['category']})")
    logger.info(f"Dimensions: {dimensions[0]} x {dimensions[1]} x {dimensions[2]} mm")
    logger.info(f"Weight: {weight_str}")
    logger.info(f"Target user group: {args.user_group}")
    
    logger.info("\nKey findings:")
    
    # Determine best handle type
    best_handle = "none"
    if weight_g > 2000:  # More than 2kg
        if weight_g > weight_limits["cutout"] * 1000:
            best_handle = "strap"
        else:
            best_handle = "cutout"
    
    logger.info(f"- Recommended handle type: {best_handle}")
    
    handling_scenario = "direct_grip"
    if weight_g > 1500:
        handling_scenario = "two_handed"
    
    optimal = optimal_dimensions[handling_scenario]
    logger.info(f"- Optimal package dimensions: {optimal['width']:.1f} x {optimal['height']:.1f} x {optimal['depth']:.1f} mm")
    
    if weight_g > weight_limits["cutout"] * 1000:
        logger.info(f"- WARNING: Weight ({weight_g/1000:.1f} kg) exceeds recommended single-person lift for {args.user_group} users")
    
    # Summary of all results
    logger.info("\nAll results have been saved to the following files:")
    logger.info(f"- Handle recommendations: {handle_file}")
    logger.info(f"- Weight limits: {weight_file}")
    logger.info(f"- Ergonomic recommendations: {recommendations_file}")
    logger.info(f"- Optimal dimensions: {dimensions_file}")
    
    logger.info("\nNOTE: For more accurate ergonomic analysis, integrate with the DynPose-100K dataset")
    logger.info("(https://huggingface.co/datasets/nvidia/dynpose-100k) to leverage human pose data for")
    logger.info("package interaction optimization.")


if __name__ == "__main__":
    main()
