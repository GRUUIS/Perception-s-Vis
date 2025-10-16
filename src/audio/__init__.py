"""
Audio module initialization
"""

from .analyzer import AudioAnalyzer, db_to_linear, linear_to_db, smooth_value

__all__ = ['AudioAnalyzer', 'db_to_linear', 'linear_to_db', 'smooth_value']
