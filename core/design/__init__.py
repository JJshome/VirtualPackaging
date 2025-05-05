"""Package Design Module for VirtualPackaging.

This module handles the generation and optimization of packaging designs
based on 3D product models, including internal structure for product stabilization,
external box design, and customization options.
"""

from .box_generator import generate_box, optimize_box_dimensions
from .internal_structure import generate_holder_structure
from .design_optimization import optimize_design