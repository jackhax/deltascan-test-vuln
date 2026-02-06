/**
 * Jest tests for JWT validation
 */

describe('JWT Validator', () => {
  test('should validate correct token', () => {
    const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjN9.signature';
    expect(validateToken(token)).toBe(true);
  });

  test('should reject invalid token', () => {
    const token = 'invalid.token';
    expect(validateToken(token)).toBe(false);
  });

  test('should reject expired token', () => {
    const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjB9.signature';
    expect(validateToken(token)).toBe(false);
  });
});
