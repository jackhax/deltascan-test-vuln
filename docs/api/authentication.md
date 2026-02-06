# Authentication API

## Overview

The authentication system uses JWT tokens for API access control.

## Endpoints

### POST /api/auth/login

Login with username and password to receive a JWT token.

**Request:**
```json
{
  "username": "user@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600
}
```

### GET /api/auth/verify

Verify a JWT token is valid.

**Headers:**
- `Authorization: Bearer <token>`

**Response:**
```json
{
  "valid": true,
  "user_id": 123,
  "role": "user"
}
```

## Security Considerations

- Tokens expire after 1 hour
- Use HTTPS in production
- Store tokens securely on client side
- Rotate secret keys regularly
