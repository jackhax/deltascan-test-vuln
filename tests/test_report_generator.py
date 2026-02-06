"""Tests for report generator - should be REJECTED by semantic filter."""

import pytest
from api.report_generator import ReportGenerator


class TestReportGenerator:
    """Test suite for report generator."""
    
    def test_get_user_reports(self):
        """Test fetching user reports."""
        generator = ReportGenerator()
        reports = generator.get_user_reports("admin", "monthly")
        assert isinstance(reports, list)
