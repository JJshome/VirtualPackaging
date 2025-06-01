import pytest
import numpy as np
from core.design.box_generator import add_padding, calculate_bounding_box

# Test for add_padding function
def test_add_padding():
    min_bound = np.array([10, 20, 30])
    max_bound = np.array([40, 50, 60])
    padding = 5.0

    expected_min_padded = np.array([5, 15, 25])
    expected_max_padded = np.array([45, 55, 65])

    padded_min, padded_max = add_padding(min_bound, max_bound, padding)

    assert np.array_equal(padded_min, expected_min_padded)
    assert np.array_equal(padded_max, expected_max_padded)

# Test for add_padding with zero padding
def test_add_padding_zero():
    min_bound = np.array([10, 20, 30])
    max_bound = np.array([40, 50, 60])
    padding = 0.0

    expected_min_padded = min_bound
    expected_max_padded = max_bound

    padded_min, padded_max = add_padding(min_bound, max_bound, padding)

    assert np.array_equal(padded_min, expected_min_padded)
    assert np.array_equal(padded_max, expected_max_padded)

# Test for add_padding with negative padding (should still subtract/add correctly based on logic)
def test_add_padding_negative():
    min_bound = np.array([10, 20, 30])
    max_bound = np.array([40, 50, 60])
    padding = -5.0 # This is unusual, but tests the function's behavior

    expected_min_padded = np.array([15, 25, 35])
    expected_max_padded = np.array([35, 45, 55])

    padded_min, padded_max = add_padding(min_bound, max_bound, padding)

    assert np.array_equal(padded_min, expected_min_padded)
    assert np.array_equal(padded_max, expected_max_padded)
