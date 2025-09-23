from fastmcp.server.auth.providers.jwt import StaticTokenVerifier
from fastmcp import FastMCP, Context
from fastmcp.server.dependencies import get_access_token, AccessToken
import os.path

# Define development tokens and their associated claims
verifier = StaticTokenVerifier(
    tokens={
        "dev-alice-token": {
            "client_id": "alice@company.com",
            "scopes": ["read:data", "write:data", "admin:users"]
        },
        "dev-guest-token": {
            "client_id": "guest-user@company.com",
            "scopes": ["read:data"]
        },
        "guest-without-priv-token": {
            "client_id": "guest-user@company.com",
            "scopes": ["explore:data"]
        }
    }
    ,required_scopes=["read:data"]
)


#Initialize MPC with auth
with_token_verif = os.getenv("Static_Token_Verification", "FALSE")

print (with_token_verif)
if with_token_verif == "TRUE":
   mcp = FastMCP(name="Development Server", auth=verifier)
else:
   mcp = FastMCP(name="Development Server")


#MCP tools
@mcp.tool()
async def get_weather(city: str = "London") -> dict[str, str]:
    """Get weather data for a city"""
    s = await get_user_info()
    print(s)
    return {
        "city": city,
        "temperature": "22",
        "condition": "Partly cloudy",
        "humidity": "65%",
    }

# This is particularly useful when you need to:
# - Access user identification - Get the client_id or subject from token claims
# - Check permissions - Verify scopes or custom claims before performing operations
# - Multi-tenant applications - Extract tenant information from token claims
# - Audit logging - Track which user performed which actions

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
    