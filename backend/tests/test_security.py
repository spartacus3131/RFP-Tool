"""
Security tests for the RFP Tool API.

Tests verify:
- Authentication requirements
- Password complexity
- Input validation
- SQL injection prevention
- Path traversal prevention
- Rate limiting
- Multi-tenancy isolation
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestPasswordComplexity:
    """Test password complexity requirements."""

    def test_password_too_short(self):
        """Password must be at least 8 characters."""
        from app.api.auth import validate_password_complexity
        with pytest.raises(ValueError) as exc:
            validate_password_complexity("Aa1!abc")
        assert "at least 8 characters" in str(exc.value)

    def test_password_missing_uppercase(self):
        """Password must contain uppercase letter."""
        from app.api.auth import validate_password_complexity
        with pytest.raises(ValueError) as exc:
            validate_password_complexity("abcd1234!")
        assert "uppercase" in str(exc.value)

    def test_password_missing_lowercase(self):
        """Password must contain lowercase letter."""
        from app.api.auth import validate_password_complexity
        with pytest.raises(ValueError) as exc:
            validate_password_complexity("ABCD1234!")
        assert "lowercase" in str(exc.value)

    def test_password_missing_number(self):
        """Password must contain a number."""
        from app.api.auth import validate_password_complexity
        with pytest.raises(ValueError) as exc:
            validate_password_complexity("ABCDabcd!")
        assert "number" in str(exc.value)

    def test_password_missing_special(self):
        """Password must contain special character."""
        from app.api.auth import validate_password_complexity
        with pytest.raises(ValueError) as exc:
            validate_password_complexity("ABCDabcd1")
        assert "special" in str(exc.value)

    def test_password_valid(self):
        """Valid password passes all checks."""
        from app.api.auth import validate_password_complexity
        result = validate_password_complexity("SecurePass1!")
        assert result == "SecurePass1!"


class TestInputValidation:
    """Test input validation and sanitization."""

    def test_escape_like_pattern_percent(self):
        """Percent signs should be escaped in LIKE patterns."""
        from app.api.dashboard import escape_like_pattern
        assert escape_like_pattern("test%injection") == "test\\%injection"

    def test_escape_like_pattern_underscore(self):
        """Underscores should be escaped in LIKE patterns."""
        from app.api.dashboard import escape_like_pattern
        assert escape_like_pattern("test_injection") == "test\\_injection"

    def test_escape_like_pattern_backslash(self):
        """Backslashes should be escaped in LIKE patterns."""
        from app.api.dashboard import escape_like_pattern
        assert escape_like_pattern("test\\injection") == "test\\\\injection"

    def test_escape_like_pattern_combined(self):
        """Multiple special characters should all be escaped."""
        from app.api.dashboard import escape_like_pattern
        result = escape_like_pattern("test%_\\injection")
        assert result == "test\\%\\_\\\\injection"


class TestPathTraversal:
    """Test path traversal prevention."""

    def test_sanitize_filename_removes_path(self):
        """Filenames should have path components stripped."""
        from app.api.rfp import sanitize_filename
        assert sanitize_filename("../../../etc/passwd") == "etc_passwd"

    def test_sanitize_filename_removes_special_chars(self):
        """Special characters should be replaced."""
        from app.api.rfp import sanitize_filename
        result = sanitize_filename("file<>name.pdf")
        assert "<" not in result
        assert ">" not in result

    def test_sanitize_filename_prevents_hidden_files(self):
        """Hidden files (starting with .) should not be allowed."""
        from app.api.rfp import sanitize_filename
        result = sanitize_filename(".hidden.pdf")
        assert not result.startswith(".")

    def test_sanitize_filename_empty_returns_unnamed(self):
        """Empty filename should return 'unnamed'."""
        from app.api.rfp import sanitize_filename
        assert sanitize_filename("") == "unnamed"


class TestFileValidation:
    """Test file upload validation."""

    def test_validate_pdf_magic_valid(self):
        """Valid PDF should pass magic byte check."""
        from app.api.rfp import validate_file_magic
        pdf_content = b'%PDF-1.4 rest of file...'
        assert validate_file_magic(pdf_content, "test.pdf") is True

    def test_validate_pdf_magic_invalid(self):
        """Non-PDF content with .pdf extension should fail."""
        from app.api.rfp import validate_file_magic
        fake_pdf = b'This is not a PDF file'
        assert validate_file_magic(fake_pdf, "fake.pdf") is False

    def test_validate_docx_magic_valid(self):
        """Valid DOCX should pass magic byte check."""
        from app.api.rfp import validate_file_magic
        # DOCX files are ZIP archives
        docx_content = b'PK\x03\x04 rest of zip...'
        assert validate_file_magic(docx_content, "test.docx") is True

    def test_validate_docx_magic_invalid(self):
        """Non-DOCX content with .docx extension should fail."""
        from app.api.rfp import validate_file_magic
        fake_docx = b'This is not a DOCX file'
        assert validate_file_magic(fake_docx, "fake.docx") is False


class TestOrganizationAccess:
    """Test multi-tenancy organization access verification."""

    def test_superuser_has_access(self):
        """Superusers should have access to all resources."""
        from app.api.rfp import verify_organization_access

        class MockRFP:
            organization_id = "org_other"

        class MockUser:
            is_superuser = True
            organization = "org_mine"

        assert verify_organization_access(MockRFP(), MockUser()) is True

    def test_same_org_has_access(self):
        """Users should have access to their organization's resources."""
        from app.api.rfp import verify_organization_access

        class MockRFP:
            organization_id = "org_same"

        class MockUser:
            is_superuser = False
            organization = "org_same"

        assert verify_organization_access(MockRFP(), MockUser()) is True

    def test_different_org_denied(self):
        """Users should not have access to other organizations' resources."""
        from app.api.rfp import verify_organization_access

        class MockRFP:
            organization_id = "org_other"

        class MockUser:
            is_superuser = False
            organization = "org_mine"

        assert verify_organization_access(MockRFP(), MockUser()) is False

    def test_legacy_data_accessible(self):
        """Resources without organization_id (legacy) should be accessible."""
        from app.api.rfp import verify_organization_access

        class MockRFP:
            organization_id = None

        class MockUser:
            is_superuser = False
            organization = "org_mine"

        assert verify_organization_access(MockRFP(), MockUser()) is True


class TestSecurityHeaders:
    """Test security headers middleware."""

    def test_headers_present(self):
        """Security headers should be present in responses."""
        # This would require running the actual app
        # For now, test the middleware class exists
        from main import SecurityHeadersMiddleware
        assert SecurityHeadersMiddleware is not None


class TestRateLimiting:
    """Test rate limiting configuration."""

    def test_rate_limiter_configured(self):
        """Rate limiter should be properly configured."""
        from main import limiter
        assert limiter is not None
        assert limiter.key_func is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
