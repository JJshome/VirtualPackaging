"""Regulatory compliance verification and text generation.

This module provides functionality to verify packaging designs against 
regulatory requirements and generate appropriate regulatory text for packaging.
"""

import logging
import re
from typing import List, Dict, Tuple, Optional, Any, Union

logger = logging.getLogger(__name__)


class RegulatoryError(Exception):
    """Exception raised for errors in regulatory processing."""
    pass


# Database of regulations by region and product type
# In a real implementation, this would be a much more comprehensive database
# loaded from an external service or database
REGULATIONS_DB = {
    "US": {
        "electronics": [
            {
                "id": "fcc-part-15",
                "name": "FCC Part 15",
                "description": "FCC regulations for electronic devices regarding electromagnetic interference",
                "required_labels": ["FCC ID", "FCC compliance statement"],
                "required_warnings": [
                    "This device complies with Part 15 of the FCC Rules. Operation is subject to the following two conditions: (1) This device may not cause harmful interference, and (2) this device must accept any interference received, including interference that may cause undesired operation."
                ],
            },
            {
                "id": "ul-certification",
                "name": "UL Certification",
                "description": "Safety certification for electronic devices",
                "required_labels": ["UL Mark"],
                "required_warnings": [],
            }
        ],
        "food": [
            {
                "id": "fda-nutrition",
                "name": "FDA Nutrition Labeling",
                "description": "FDA requirements for nutrition information on food packaging",
                "required_labels": ["Nutrition Facts"],
                "required_warnings": [],
            },
            {
                "id": "fda-allergens",
                "name": "FDA Allergen Labeling",
                "description": "FDA requirements for allergen information on food packaging",
                "required_labels": ["Contains: [allergens]"],
                "required_warnings": [],
            }
        ],
        "cosmetics": [
            {
                "id": "fda-cosmetics",
                "name": "FDA Cosmetics Labeling",
                "description": "FDA requirements for cosmetics packaging",
                "required_labels": ["Ingredients list"],
                "required_warnings": [
                    "Warning: For external use only."
                ],
            }
        ],
        "toys": [
            {
                "id": "cpsc-small-parts",
                "name": "CPSC Small Parts Warning",
                "description": "Consumer Product Safety Commission warning for toys with small parts",
                "required_labels": [],
                "required_warnings": [
                    "WARNING: CHOKING HAZARD – Small parts. Not for children under 3 years."
                ],
            }
        ],
        "packaging": [
            {
                "id": "recyclability",
                "name": "Recyclability Labeling",
                "description": "Requirements for indicating recyclability of packaging",
                "required_labels": ["Recycling symbol with material code"],
                "required_warnings": [],
            }
        ],
    },
    "EU": {
        "electronics": [
            {
                "id": "ce-marking",
                "name": "CE Marking",
                "description": "European conformity marking for products sold in the European Economic Area",
                "required_labels": ["CE Mark"],
                "required_warnings": [],
            },
            {
                "id": "weee",
                "name": "WEEE Directive",
                "description": "Waste Electrical and Electronic Equipment Directive",
                "required_labels": ["WEEE Symbol"],
                "required_warnings": [],
            }
        ],
        "food": [
            {
                "id": "eu-nutrition",
                "name": "EU Nutrition Labeling",
                "description": "EU requirements for nutrition information on food packaging",
                "required_labels": ["Nutrition declaration"],
                "required_warnings": [],
            }
        ],
        "packaging": [
            {
                "id": "green-dot",
                "name": "Green Dot",
                "description": "Symbol used to indicate that the manufacturer contributes to the cost of recovery and recycling",
                "required_labels": ["Green Dot symbol"],
                "required_warnings": [],
            }
        ],
    },
    "Global": {
        "packaging": [
            {
                "id": "iso-packaging",
                "name": "ISO Packaging Symbols",
                "description": "International standards for packaging symbols",
                "required_labels": [],
                "required_warnings": [],
            }
        ],
    }
}


def verify_compliance(
    product_type: str,
    regions: List[str],
    packaging_details: Dict[str, Any]
) -> Dict[str, Any]:
    """Verify compliance of packaging with regulations for specified regions.
    
    Args:
        product_type: Type of product (electronics, food, etc.)
        regions: List of regions to check compliance for (US, EU, etc.)
        packaging_details: Dictionary with packaging details
        
    Returns:
        Dictionary with compliance verification results
    """
    logger.info(f"Verifying compliance for {product_type} product in regions: {', '.join(regions)}")
    
    try:
        # Initialize results
        compliance_results = {
            "compliant": True,
            "regions": {},
            "missing_elements": [],
            "suggested_additions": [],
        }
        
        # Process each region
        for region in regions:
            region_results = {
                "compliant": True,
                "regulations": [],
                "missing_elements": [],
            }
            
            # Get applicable regulations for this region and product type
            region_regs = REGULATIONS_DB.get(region, {})
            product_regs = region_regs.get(product_type, [])
            packaging_regs = region_regs.get("packaging", [])
            
            # Also check global regulations
            global_regs = REGULATIONS_DB.get("Global", {})
            global_product_regs = global_regs.get(product_type, [])
            global_packaging_regs = global_regs.get("packaging", [])
            
            # Combine all applicable regulations
            applicable_regs = product_regs + packaging_regs + global_product_regs + global_packaging_regs
            
            # Check each regulation for compliance
            for reg in applicable_regs:
                reg_result = {
                    "id": reg["id"],
                    "name": reg["name"],
                    "compliant": True,
                    "missing_elements": [],
                }
                
                # Check for required labels
                for label in reg["required_labels"]:
                    if "labels" not in packaging_details or label not in packaging_details["labels"]:
                        reg_result["compliant"] = False
                        reg_result["missing_elements"].append(f"Required label: {label}")
                        region_results["missing_elements"].append(f"Missing required label for {reg['name']}: {label}")
                
                # Check for required warnings
                for warning in reg["required_warnings"]:
                    warning_present = False
                    if "warnings" in packaging_details:
                        for pkg_warning in packaging_details["warnings"]:
                            if warning.lower() in pkg_warning.lower():
                                warning_present = True
                                break
                    
                    if not warning_present:
                        reg_result["compliant"] = False
                        reg_result["missing_elements"].append(f"Required warning: {warning}")
                        region_results["missing_elements"].append(f"Missing required warning for {reg['name']}: {warning}")
                
                # Update region compliance status
                if not reg_result["compliant"]:
                    region_results["compliant"] = False
                
                # Add regulation result to region results
                region_results["regulations"].append(reg_result)
            
            # Update overall compliance status
            if not region_results["compliant"]:
                compliance_results["compliant"] = False
                compliance_results["missing_elements"].extend(region_results["missing_elements"])
            
            # Add region results to overall results
            compliance_results["regions"][region] = region_results
        
        # Generate suggested additions
        for missing in compliance_results["missing_elements"]:
            if "label" in missing.lower():
                compliance_results["suggested_additions"].append({
                    "type": "label",
                    "content": missing.split(": ", 1)[1] if ": " in missing else missing
                })
            elif "warning" in missing.lower():
                compliance_results["suggested_additions"].append({
                    "type": "warning",
                    "content": missing.split(": ", 1)[1] if ": " in missing else missing
                })
        
        logger.info(f"Compliance verification complete. Compliant: {compliance_results['compliant']}")
        if not compliance_results["compliant"]:
            logger.debug(f"Missing elements: {compliance_results['missing_elements']}")
        
        return compliance_results
    
    except Exception as e:
        logger.error(f"Compliance verification failed: {str(e)}")
        raise RegulatoryError(f"Compliance verification failed: {str(e)}")


def generate_regulatory_text(
    product_type: str,
    regions: List[str],
    language: str = "en"
) -> Dict[str, List[str]]:
    """Generate regulatory text for packaging based on product type and regions.
    
    Args:
        product_type: Type of product (electronics, food, etc.)
        regions: List of regions to generate text for (US, EU, etc.)
        language: Language code for the generated text
        
    Returns:
        Dictionary mapping text types to lists of generated text strings
    """
    logger.info(f"Generating regulatory text for {product_type} product in regions: {', '.join(regions)}")
    
    try:
        # Initialize result structure
        result = {
            "labels": [],
            "warnings": [],
            "statements": [],
            "symbols": [],
        }
        
        # For each region, collect the required regulatory elements
        for region in regions:
            # Get applicable regulations for this region and product type
            region_regs = REGULATIONS_DB.get(region, {})
            product_regs = region_regs.get(product_type, [])
            packaging_regs = region_regs.get("packaging", [])
            
            # Also check global regulations
            global_regs = REGULATIONS_DB.get("Global", {})
            global_product_regs = global_regs.get(product_type, [])
            global_packaging_regs = global_regs.get("packaging", [])
            
            # Combine all applicable regulations
            applicable_regs = product_regs + packaging_regs + global_product_regs + global_packaging_regs
            
            # Extract required elements from each regulation
            for reg in applicable_regs:
                # Add labels
                for label in reg["required_labels"]:
                    if label not in result["labels"]:
                        result["labels"].append(f"{label} ({region})")
                
                # Add warnings
                for warning in reg["required_warnings"]:
                    if warning not in result["warnings"]:
                        result["warnings"].append(warning)
                
                # Add symbols based on regulation ID
                if reg["id"] == "ce-marking":
                    result["symbols"].append("CE Mark")
                elif reg["id"] == "weee":
                    result["symbols"].append("WEEE Symbol")
                elif reg["id"] == "green-dot":
                    result["symbols"].append("Green Dot Symbol")
                elif reg["id"] == "recyclability":
                    result["symbols"].append("Recycling Symbol")
                
                # Add compliance statements
                if reg["id"] == "fcc-part-15":
                    result["statements"].append("FCC Compliance Statement: This device complies with Part 15 of the FCC Rules.")
        
        # Remove duplicates and sort
        for key in result:
            result[key] = sorted(list(set(result[key])))
        
        logger.info(f"Generated {sum(len(v) for v in result.values())} regulatory elements")
        return result
    
    except Exception as e:
        logger.error(f"Regulatory text generation failed: {str(e)}")
        raise RegulatoryError(f"Regulatory text generation failed: {str(e)}")


def check_package_measurements(
    dimensions: Dict[str, float],
    product_type: str,
    target_regions: List[str]
) -> Dict[str, Any]:
    """Check if package dimensions comply with regulations for specified regions.
    
    Args:
        dimensions: Dictionary with package dimensions
        product_type: Type of product
        target_regions: List of regions to check
        
    Returns:
        Dictionary with compliance results
    """
    # This would check specific dimensional requirements
    # For example, some regions have limits on packaging-to-product ratios
    
    # Example implementation (would be more comprehensive in production)
    results = {
        "compliant": True,
        "issues": [],
        "regions": {}
    }
    
    # EU has specific requirements for packaging-to-product volume ratio
    if "EU" in target_regions:
        # Calculate volume
        if all(key in dimensions for key in ["width", "height", "depth"]):
            package_volume = dimensions["width"] * dimensions["height"] * dimensions["depth"]
            
            # Example check (fictional requirement)
            if product_type == "electronics" and package_volume > 5000:
                results["compliant"] = False
                results["issues"].append("Package volume exceeds EU recommendations for electronics")
                results["regions"]["EU"] = {
                    "compliant": False,
                    "issues": ["Package volume exceeds recommendations"]
                }
    
    # Return results
    return results


def check_material_compliance(
    material_type: str,
    product_type: str,
    target_regions: List[str]
) -> Dict[str, Any]:
    """Check if packaging material complies with regulations for specified regions.
    
    Args:
        material_type: Type of packaging material
        product_type: Type of product
        target_regions: List of regions to check
        
    Returns:
        Dictionary with compliance results
    """
    # This would check material-specific regulations
    # For example, restrictions on certain plastics
    
    # Example implementation (would be more comprehensive in production)
    results = {
        "compliant": True,
        "issues": [],
        "regions": {}
    }
    
    # EU plastics directive example
    if "EU" in target_regions and material_type.lower() == "plastic":
        # Check for specific plastic restrictions
        results["regions"]["EU"] = {
            "compliant": True,
            "requirements": ["Must include plastic recycling symbol"]
        }
    
    # California example
    if "US" in target_regions and "california" in target_regions:
        if material_type.lower() == "plastic":
            results["regions"]["california"] = {
                "compliant": True,
                "requirements": ["Must display 'Recyclable' or recycling symbol if applicable"]
            }
    
    # Return results
    return results


def get_country_specific_requirements(
    country: str,
    product_type: str
) -> List[Dict[str, Any]]:
    """Get specific regulatory requirements for a country and product type.
    
    Args:
        country: Country code
        product_type: Type of product
        
    Returns:
        List of specific requirements
    """
    # This would provide detailed country-specific requirements
    # A real implementation would have a comprehensive database
    
    requirements = []
    
    # Common countries examples
    if country == "US":
        if product_type == "food":
            requirements.append({
                "name": "FDA Food Labeling",
                "description": "FDA requirements for food labeling",
                "details_url": "https://www.fda.gov/food/food-labeling-nutrition"
            })
        elif product_type == "toys":
            requirements.append({
                "name": "CPSC Requirements",
                "description": "Consumer Product Safety Commission requirements for toys",
                "details_url": "https://www.cpsc.gov/Business--Manufacturing/Business-Education/Toy-Safety"
            })
    elif country == "EU":
        if product_type == "electronics":
            requirements.append({
                "name": "RoHS Compliance",
                "description": "Restriction of Hazardous Substances Directive",
                "details_url": "https://ec.europa.eu/environment/topics/waste-and-recycling/rohs-directive_en"
            })
        elif product_type == "food":
            requirements.append({
                "name": "EU Food Information Regulation",
                "description": "Regulation on the provision of food information to consumers",
                "details_url": "https://ec.europa.eu/food/safety/labelling_nutrition/labelling_legislation_en"
            })
    elif country == "UK":
        if product_type == "electronics":
            requirements.append({
                "name": "UKCA Marking",
                "description": "UK Conformity Assessed marking",
                "details_url": "https://www.gov.uk/guidance/using-the-ukca-marking"
            })
    elif country == "JP":
        if product_type == "electronics":
            requirements.append({
                "name": "PSE Mark",
                "description": "Product Safety Electrical Appliance & Material mark",
                "details_url": "https://www.jetro.go.jp/en/reports/regulations/"
            })
    
    # Return requirements
    return requirements


def check_language_requirements(
    regions: List[str],
    languages_included: List[str]
) -> Dict[str, Any]:
    """Check if the packaging includes all required languages for specified regions.
    
    Args:
        regions: List of regions to check
        languages_included: List of languages included on packaging
        
    Returns:
        Dictionary with compliance results
    """
    # This would check language requirements for different regions
    # A real implementation would have a comprehensive database
    
    results = {
        "compliant": True,
        "issues": [],
        "regions": {}
    }
    
    # Define language requirements for regions
    language_requirements = {
        "CA": ["en", "fr"],  # Canada requires English and French
        "BE": ["nl", "fr", "de"],  # Belgium requires Dutch, French, and German
        "CH": ["de", "fr", "it"],  # Switzerland requires German, French, and Italian
        "EU": ["local"],  # EU generally requires local language(s)
    }
    
    # Check each region
    for region in regions:
        if region in language_requirements:
            required_languages = language_requirements[region]
            
            # Special case for EU "local" requirement
            if required_languages == ["local"]:
                # This would need more specific checking in a real implementation
                continue
            
            # Check if all required languages are included
            missing_languages = [lang for lang in required_languages if lang not in languages_included]
            
            if missing_languages:
                results["compliant"] = False
                issue = f"Missing required language(s) for {region}: {', '.join(missing_languages)}"
                results["issues"].append(issue)
                results["regions"][region] = {
                    "compliant": False,
                    "issues": [issue],
                    "missing_languages": missing_languages
                }
    
    # Return results
    return results


def generate_compliance_report(
    product_info: Dict[str, Any],
    packaging_design: Dict[str, Any],
    target_regions: List[str]
) -> Dict[str, Any]:
    """Generate a comprehensive compliance report for a packaging design.
    
    Args:
        product_info: Dictionary with product information
        packaging_design: Dictionary with packaging design details
        target_regions: List of target markets/regions
        
    Returns:
        Dictionary with comprehensive compliance report
    """
    # This would generate a detailed compliance report
    # A real implementation would be more comprehensive
    
    # Extract relevant information
    product_type = product_info.get("category", "general")
    dimensions = packaging_design.get("dimensions", {})
    material = packaging_design.get("material", "")
    text_content = packaging_design.get("text_content", {})
    
    # Extract languages from text content
    languages = []
    if "languages" in packaging_design:
        languages = packaging_design["languages"]
    
    # Prepare warning and label lists
    warnings = []
    labels = []
    if "text_content" in packaging_design:
        if "warnings" in packaging_design["text_content"]:
            warnings = packaging_design["text_content"]["warnings"]
        if "labels" in packaging_design["text_content"]:
            labels = packaging_design["text_content"]["labels"]
    
    # Packaging details for compliance check
    packaging_details = {
        "warnings": warnings,
        "labels": labels,
        "dimensions": dimensions,
        "material": material,
        "languages": languages
    }
    
    # Run various compliance checks
    compliance = verify_compliance(product_type, target_regions, packaging_details)
    measurement_compliance = check_package_measurements(dimensions, product_type, target_regions)
    material_compliance = check_material_compliance(material, product_type, target_regions)
    language_compliance = check_language_requirements(target_regions, languages)
    
    # Combine all results
    report = {
        "overall_compliance": (
            compliance["compliant"] and 
            measurement_compliance["compliant"] and 
            material_compliance["compliant"] and 
            language_compliance["compliant"]
        ),
        "regulatory_compliance": compliance,
        "measurement_compliance": measurement_compliance,
        "material_compliance": material_compliance,
        "language_compliance": language_compliance,
        "suggested_improvements": []
    }
    
    # Add suggestions for improvements
    if not compliance["compliant"]:
        report["suggested_improvements"].extend(compliance["suggested_additions"])
    
    if not measurement_compliance["compliant"]:
        for issue in measurement_compliance["issues"]:
            report["suggested_improvements"].append({
                "type": "dimension",
                "content": issue
            })
    
    if not language_compliance["compliant"]:
        for issue in language_compliance["issues"]:
            report["suggested_improvements"].append({
                "type": "language",
                "content": issue
            })
    
    # Return the report
    return report


def get_symbol_requirements(
    product_type: str,
    material_type: str,
    target_regions: List[str]
) -> Dict[str, List[Dict[str, Any]]]:
    """Get required symbols for packaging based on product type, material, and regions.
    
    Args:
        product_type: Type of product
        material_type: Type of packaging material
        target_regions: List of target markets/regions
        
    Returns:
        Dictionary mapping regions to lists of required symbols
    """
    # This would provide required symbols for different regions
    # A real implementation would have a comprehensive database
    
    symbols = {}
    
    # Define symbol requirements
    symbol_requirements = {
        "US": {
            "packaging": [
                {
                    "name": "Resin identification code",
                    "description": "Required for plastic packaging",
                    "applies_to": ["plastic"],
                    "image_path": "symbols/resin_code.svg"
                },
                {
                    "name": "Recycling symbol",
                    "description": "Recommended for recyclable materials",
                    "applies_to": ["paper", "cardboard", "plastic", "glass", "metal"],
                    "image_path": "symbols/recycling.svg"
                }
            ],
            "electronics": [
                {
                    "name": "FCC mark",
                    "description": "Required for electronic devices",
                    "applies_to": ["all"],
                    "image_path": "symbols/fcc.svg"
                }
            ]
        },
        "EU": {
            "packaging": [
                {
                    "name": "Green Dot",
                    "description": "Indicates producer has made a financial contribution to packaging recovery",
                    "applies_to": ["all"],
                    "image_path": "symbols/green_dot.svg"
                },
                {
                    "name": "Recycling symbol",
                    "description": "Required for recyclable materials",
                    "applies_to": ["paper", "cardboard", "plastic", "glass", "metal"],
                    "image_path": "symbols/recycling.svg"
                }
            ],
            "electronics": [
                {
                    "name": "CE mark",
                    "description": "Required for electronic devices sold in the EEA",
                    "applies_to": ["all"],
                    "image_path": "symbols/ce.svg"
                },
                {
                    "name": "WEEE symbol",
                    "description": "Required for electronic devices",
                    "applies_to": ["all"],
                    "image_path": "symbols/weee.svg"
                }
            ]
        }
    }
    
    # Collect required symbols for each region
    for region in target_regions:
        if region in symbol_requirements:
            region_symbols = []
            
            # Check product type requirements
            if product_type in symbol_requirements[region]:
                for symbol in symbol_requirements[region][product_type]:
                    if "all" in symbol["applies_to"] or material_type.lower() in symbol["applies_to"]:
                        region_symbols.append(symbol)
            
            # Check packaging requirements
            if "packaging" in symbol_requirements[region]:
                for symbol in symbol_requirements[region]["packaging"]:
                    if "all" in symbol["applies_to"] or material_type.lower() in symbol["applies_to"]:
                        region_symbols.append(symbol)
            
            # Add to results
            if region_symbols:
                symbols[region] = region_symbols
    
    # Return symbols
    return symbols


# Example usage
if __name__ == "__main__":
    # Example product information
    product_info = {
        "name": "Wireless Headphones",
        "category": "electronics",
        "description": "Bluetooth wireless headphones with noise cancellation"
    }
    
    # Example packaging design
    packaging_design = {
        "material": "cardboard",
        "dimensions": {
            "width": 180,
            "height": 220,
            "depth": 60
        },
        "text_content": {
            "warnings": [
                "Keep away from children under 3 years of age"
            ],
            "labels": [
                "CE Mark",
                "Recyclable"
            ]
        },
        "languages": ["en", "fr", "de"]
    }
    
    # Target regions
    target_regions = ["US", "EU"]
    
    # Verify compliance
    compliance = verify_compliance(
        product_info["category"],
        target_regions,
        packaging_design
    )
    
    print(f"Compliance verification results:")
    print(f"Overall compliance: {compliance['compliant']}")
    if not compliance['compliant']:
        print("Missing elements:")
        for element in compliance['missing_elements']:
            print(f"- {element}")
        
        print("\nSuggested additions:")
        for addition in compliance['suggested_additions']:
            print(f"- {addition['type']}: {addition['content']}")
    
    # Generate regulatory text
    regulatory_text = generate_regulatory_text(
        product_info["category"],
        target_regions
    )
    
    print("\nGenerated regulatory text:")
    for category, items in regulatory_text.items():
        if items:
            print(f"\n{category.upper()}:")
            for item in items:
                print(f"- {item}")
