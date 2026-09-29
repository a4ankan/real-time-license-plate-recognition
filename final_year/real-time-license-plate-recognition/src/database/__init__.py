"""
Database module for storing license plate detections.
"""

from .db_connection import DatabaseConnection
from .plate_repository import PlateRepository

__all__ = ['DatabaseConnection', 'PlateRepository']
