from fastmcp.server.auth.providers.auth0 import Auth0Provider
from fastmcp.server.auth.oidc_proxy import OIDCProxy
from fastmcp import FastMCP


# Create the OIDC proxy
auth = OIDCProxy(
    # Provider's configuration URL
    config_url="https://idcs-9dc693e80d9b469480d7afe00e743931.identity.oraclecloud.com/.well-known/openid-configuration",

    # Your registered app credentials
    client_id="7998bfa38da041e0b975e7020a3086a5",
    client_secret="idcscs-3b597e5d-f5ab-4971-b18f-a9c035c26c91",

    # Your FastMCP server's public URL
    base_url="http://localhost:8000",

    # Optional: customize the callback path (default is "/auth/callback")
    redirect_path="https://localhost:8000/auth/callback",
)

mcp = FastMCP(name="Auth0 Secured App", auth=auth)

# Add a protected tool to test authentication
@mcp.tool
async def get_token_info() -> dict:
    """Returns information about the Auth0 token."""
    from fastmcp.server.dependencies import get_access_token

    token = get_access_token()

    return {
        "issuer": token.claims.get("iss"),
        "audience": token.claims.get("aud"),
        "scope": token.claims.get("scope"),
        "client_id": token.claims.get("client_id")
    }