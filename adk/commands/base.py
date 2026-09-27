"""
Base Strategy Interfaces for Pipeline Commands.
Defines the technology-agnostic contracts for Storage Ingestion and Warehouse Provisioning.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class IngestionStrategy(ABC):
    """
    Abstract Strategy for storage file detection, routing, and schema validation.
    Concrete implementations exist for GCS, S3, Azure Blob, etc.
    """

    @abstractmethod
    def ingest_file(self, uri: str, **kwargs) -> Dict[str, Any]:
        """Ingests storage asset and coordinates Fast Path vs Judgment Path routing."""
        pass


class WarehouseTableStrategy(ABC):
    """
    Abstract Strategy for analytical warehouse external table provisioning.
    Concrete implementations exist for BigQuery, Snowflake, Databricks, etc.
    """

    @abstractmethod
    def render_ddl(self, proposal: Dict[str, Any], **kwargs) -> str:
        """Renders technology-specific DDL from an approved SchemaProposalObject."""
        pass

    @abstractmethod
    def create_external_table(self, proposal: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Executes table provisioning against the target warehouse."""
        pass
