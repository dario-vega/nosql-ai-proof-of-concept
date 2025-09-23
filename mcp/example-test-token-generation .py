from fastmcp.server.auth.providers.jwt import JWTVerifier, RSAKeyPair

from fastmcp import FastMCP

from fastmcp.server.dependencies import get_access_token, AccessToken


# Generate a key pair for testing
key_pair = RSAKeyPair.generate()

# Configure your server with the public key
verifier = JWTVerifier(
    public_key=key_pair.public_key,
    issuer="https://test.yourcompany.com",
    audience="test-mcp-server"
)

# Generate a test token using the private key
test_token = key_pair.create_token(
    subject="test-user-123",
    issuer="https://test.yourcompany.com", 
    audience="test-mcp-server",
    scopes=["read", "write"]
)

print(f"Test token: {test_token}")

mcp = FastMCP(name="Development Server", auth=verifier)

#MCP tools
@mcp.tool()
async def get_weather(city: str = "London") -> dict[str, str]:
    """Get weather data for a city"""
    return {
        "city": city,
        "temperature": "22",
        "condition": "Partly cloudy",
        "humidity": "65%",
    }

@mcp.tool
async def get_user_info() -> dict:
    """Get information about the authenticated user."""
    # Get the access token (None if not authenticated)
    token: AccessToken | None = get_access_token()
    
    if token is None:
        return {"authenticated": False}
    
    return {
        "authenticated": True,
        "client_id": token.client_id,
        "scopes": token.scopes,
        "expires_at": token.expires_at,
        "token_claims": token.claims,  # JWT claims or custom token data
    }

#Start the application
if __name__ == "__main__":
    mcp.run()