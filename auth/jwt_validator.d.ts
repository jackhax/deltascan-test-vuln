/**
 * TypeScript type definitions for JWT validator
 */

export interface JWTPayload {
    user_id: number;
    role: string;
    exp?: number;
    iat?: number;
}

export interface JWTHeader {
    alg: string;
    typ: string;
}

export class JWTValidator {
    constructor(secretKey: string);
    decode_token(token: string): JWTPayload | null;
    validate_request(token: string, required_role: string): boolean;
}
