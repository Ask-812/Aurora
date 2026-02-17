"""Intelligence layer for user segmentation and analysis"""

from .data_ingestion import DataIngestionEngine
from .segmentation import SegmentationEngine
from .goal_builder import GoalBuilder

__all__ = ['DataIngestionEngine', 'SegmentationEngine', 'GoalBuilder']

