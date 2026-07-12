"""
Change Point Analysis Package

This package contains the core modules for analyzing Brent oil prices
and detecting structural breaks using Bayesian change point models.
"""

__version__ = "1.0.0"
__author__ = "Hawi Chala"

from .data_loader import load_brent_data, load_events_data
from .eda_analyzer import EDAnalyzer
from .change_point_model import ChangePointModel

__all__ = [
    "load_brent_data",
    "load_events_data",
    "EDAnalyzer",
    "ChangePointModel"
]