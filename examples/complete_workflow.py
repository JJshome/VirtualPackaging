#!/usr/bin/env python3
"""
Complete workflow example for VirtualPackaging.

This script demonstrates the full pipeline from 3D scan to packaging design:
1. Process 3D scan data to product mesh
2. Extract product information
3. Get AI recommendations for packaging
4. Generate packaging design
5. Add text content to packaging
6. Export manufacturing files

Usage:
    python complete_workflow.py <scan_data_path> [options]
    
Options:
    --output-dir PATH       Directory to save output files
    --product-name NAME     Name of the product
    --category CATEGORY     Product category
    --target-market MARKET  Target market description
    --priority PRIORITY     Design priority (sustainability, protection, cost)
"""

import os
import sys
import argparse
import logging
from pathlib import Path
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path to import from core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import VirtualPackaging modules
from core.intelligence import (
    PackagingLLM, DesignAutomation, PackagingLabeling, 
    DesignPriority, BoxType, MaterialType
)
from core.integration.capture_interface import (
    scan_to_mesh, mesh_to_product_info, extract_features_for_llm
)
from core.integration.design_interface import (
    create_design_spec, generate_box_mesh, generate_internal_structure, combine_meshes
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='VirtualPackaging complete workflow example')
    
    parser.add_argument(
        'scan_data_path', 
        type=str, 
        help='Path to scan data (3D model or directory of images)'
    )
    
    parser.add_argument(
        '--output-dir', 
        type=str, 
        default='output',
        help='Directory to save output files'
    )
    
    parser.add_argument(
        '--product-name', 
        type=str, 
        default=None,
        help='Name of the product'
    )
    
    parser.add_argument(
        '--category', 
        type=str, 
        default=None,
        help='Product category'
    )
    
    parser.add_argument(
        '--target-market', 
        type=str, 
        default='General consumers',
        help='Target market description'
    )
    
    parser.add_argument(
        '--priority', 
        type=str, 
        choices=['sustainability', 'protection', 'cost', 'aesthetics'],
        default='sustainability',
        help='Design priority'
    )
    
    return parser.parse_args()


def main():
    """Run the complete workflow."""
    # Parse arguments
    args = parse_arguments()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Process 3D scan data
    logger.info("Step 1: Processing 3D scan data...")
    scan_data_path = Path(args.scan_data_path)
    
    try:
        # If scan data is a 3D model, use it directly; otherwise process scan data
        if scan_data_path.suffix.lower() in ['.obj', '.ply', '.stl']:
            mesh_path = str(scan_data_path)
            logger.info(f"Using existing 3D model: {mesh_path}")
        else:
            mesh_path = scan_to_mesh(
                scan_data_path, 
                output_mesh_path=output_dir / "product.obj"
            )
            logger.info(f"Generated 3D mesh: {mesh_path}")
        
        # Step 2: Extract product information
        logger.info("Step 2: Extracting product information...")
        product_info = mesh_to_product_info(
            mesh_path,
            product_name=args.product_name,
            category=args.category
        )
        
        # Save product info
        product_info_path = output_dir / "product_info.json"
        with open(product_info_path, 'w') as f:
            json.dump(product_info, f, indent=2)
        logger.info(f"Saved product info to {product_info_path}")
        
        # Extract features for LLM
        llm_features = extract_features_for_llm(product_info)
        
        # Step 3: Get AI recommendations
        logger.info("Step 3: Getting AI recommendations...")
        
        # Initialize LLM
        llm = PackagingLLM()
        
        # Create design automation system
        design_system = DesignAutomation(llm=llm)
        
        # Map priority string to enum
        priority_map = {
            'sustainability': DesignPriority.SUSTAINABILITY,
            'protection': DesignPriority.PROTECTION,
            'cost': DesignPriority.COST,
            'aesthetics': DesignPriority.AESTHETICS
        }
        priority = priority_map.get(args.priority, DesignPriority.SUSTAINABILITY)
        
        # Get recommendations
        box_type, box_reasoning = design_system.recommend_box_type(
            llm_features,
            target_market=args.target_market,
            priority=priority
        )
        
        material, material_reasoning = design_system.recommend_material(
            llm_features,
            box_type=box_type,
            priority=priority
        )
        
        # Log recommendations
        logger.info(f"Recommended box type: {box_type.name}")
        logger.info(f"Reasoning: {box_reasoning.get('reasoning', 'No reasoning provided')}")
        logger.info(f"Recommended material: {material.name}")
        logger.info(f"Reasoning: {material_reasoning.get('reasoning', 'No reasoning provided')}")
        
        # Step 4: Generate packaging design
        logger.info("Step 4: Generating packaging design...")
        
        # Calculate optimal dimensions
        product_dimensions = (
            product_info["dimensions"]["width"],
            product_info["dimensions"]["height"],
            product_info["dimensions"]["depth"]
        )
        
        package_dimensions = design_system.calculate_optimal_dimensions(
            product_dimensions,
            box_type,
            padding_mm=15.0
        )
        
        # Create design specification
        design_spec = create_design_spec(
            product_info,
            box_type=box_type.value,
            material=material.value,
            dimensions=package_dimensions,
            output_path=output_dir / "design_spec.json"
        )
        
        # Generate 3D models
        import open3d as o3d
        
        # Load product mesh
        product_mesh = o3d.io.read_triangle_mesh(mesh_path)
        
        # Generate box mesh
        box_mesh = generate_box_mesh(
            design_spec,
            output_path=output_dir / "box.obj"
        )
        
        # Generate internal structure
        internal_structure = generate_internal_structure(
            design_spec,
            product_mesh,
            output_path=output_dir / "internal_structure.obj"
        )
        
        # Combine meshes
        combined_mesh = combine_meshes(
            box_mesh,
            internal_structure,
            output_path=output_dir / "complete_package.obj"
        )
        
        # Step 5: Generate packaging text
        logger.info("Step 5: Generating packaging text...")
        
        # Initialize labeling system
        labeling = PackagingLabeling(llm=llm)
        
        # Prepare brand info
        brand_info = {
            "name": "VirtualBrand",
            "tagline": "Innovation in Every Package",
            "contact": {
                "company": "VirtualBrand Inc.",
                "address": "123 Virtual Street, Techville, CA 94043",
                "phone": "1-800-VIRTUAL",
                "email": "info@virtualbrand.com",
                "website": "www.virtualbrand.com"
            }
        }
        
        # Generate text content
        text_content = labeling.generate_packaging_text(
            llm_features,
            target_audience=args.target_market,
            brand_info=brand_info,
            regulatory_regions=["US", "EU"]
        )
        
        # Save text content
        text_content_path = output_dir / "text_content.json"
        with open(text_content_path, 'w') as f:
            # Convert Enum keys to strings
            text_dict = {k.value if hasattr(k, 'value') else str(k): v for k, v in text_content.items()}
            json.dump(text_dict, f, indent=2)
        logger.info(f"Saved text content to {text_content_path}")
        
        # Create text layout
        layout = labeling.create_text_layout(
            package_dimensions,
            text_content
        )
        
        # Save layout
        layout_path = output_dir / "text_layout.json"
        with open(layout_path, 'w') as f:
            json.dump(layout, f, indent=2)
        logger.info(f"Saved text layout to {layout_path}")
        
        # Export SVG files for each surface
        labeling.export_layout_to_svg(
            layout,
            str(output_dir / "surface")
        )
        
        # Step 6: Summary and next steps
        logger.info("\nWorkflow completed successfully!")
        logger.info(f"All output files saved to {output_dir}")
        logger.info("\nGenerated files:")
        logger.info(f"- Product mesh: {mesh_path}")
        logger.info(f"- Product info: {product_info_path}")
        logger.info(f"- Design specification: {output_dir / 'design_spec.json'}")
        logger.info(f"- Box mesh: {output_dir / 'box.obj'}")
        logger.info(f"- Internal structure: {output_dir / 'internal_structure.obj'}")
        logger.info(f"- Complete package: {output_dir / 'complete_package.obj'}")
        logger.info(f"- Text content: {text_content_path}")
        logger.info(f"- Text layout: {layout_path}")
        logger.info(f"- Surface SVGs: {output_dir / 'surface_*.svg'}")
        
        logger.info("\nNext steps:")
        logger.info("1. Review the design in a 3D viewer")
        logger.info("2. Adjust design parameters if needed")
        logger.info("3. Send to manufacturing using the generated files")
        
    except Exception as e:
        logger.error(f"Error in workflow: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
