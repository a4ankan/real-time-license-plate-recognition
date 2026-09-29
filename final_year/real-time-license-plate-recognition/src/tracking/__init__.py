"""
Plate tracking and temporal stabilization module.
Implements multi-frame observation aggregation and confidence voting.
"""

from .plate_tracker import PlateTracker

__all__ = ['PlateTracker']
