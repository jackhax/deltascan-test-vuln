# DeltaScan Test Vulnerability Repository - SHOULD BE REJECTED

This repository contains intentional vulnerabilities for testing DeltaScan's detection capabilities.

## Latest Releases

### v6.4.0 - JWT "none" Algorithm Bypass (CRITICAL)
**Location:** `auth/jwt_validator.py`
**Description:** JWT validation accepts tokens with algorithm "none", allowing complete authentication bypass.

### v6.3.0 - SQL Injection & Path Traversal
**Location:** `api/report_generator.py`
**Description:** Multiple SQL injection points and path traversal in file export.

## Testing Instructions

Use this repository to test DeltaScan's ability to detect subtle security vulnerabilities.

## Files Structure

- `auth/` - Authentication modules (VULNERABLE in v6.4.0)
- `api/` - API endpoints (VULNERABLE in v6.3.0)
- `tests/` - Unit and integration tests (should be filtered)
- `docs/` - API documentation (should be filtered)
- `static/` - Images and fonts (should be filtered)
- `dist/` - Minified build artifacts (should be filtered)
