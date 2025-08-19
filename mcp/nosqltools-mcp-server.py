from fastmcp import FastMCP
import oci
from oci.signer import Signer
import os.path


mcp = FastMCP("OCI NoSQL MCP Server")

profile_name = os.getenv("PROFILE_NAME", "DEFAULT")

config = oci.config.from_file(profile_name=profile_name)
identity_client = oci.identity.IdentityClient(config)
nosql_client = oci.nosql.NosqlClient(config)

auth_signer = Signer(
    tenancy=config['tenancy'],
    user=config['user'],
    fingerprint=config['fingerprint'],
    private_key_file_location=config['key_file'],
    pass_phrase=config['pass_phrase']
)
tenancy_id = os.getenv("TENANCY_ID_OVERRIDE", config['tenancy'])

@mcp.tool()
def list_all_compartments() -> str:
    """List all compartments in a tenancy with clear formatting"""
    compartments = identity_client.list_compartments(tenancy_id).data
    compartments.append(identity_client.get_compartment(compartment_id=tenancy_id).data)
    return str(compartments)

def get_compartment_by_name(compartment_name: str):
    """Internal function to get compartment by name with caching"""
    compartments = identity_client.list_compartments(
        compartment_id=tenancy_id,
        compartment_id_in_subtree=True,
        access_level="ACCESSIBLE",
        lifecycle_state="ACTIVE"
    )
    compartments.data.append(identity_client.get_compartment(compartment_id=tenancy_id).data)
 
    # Search for the compartment by name
    for compartment in compartments.data:
        if compartment.name.lower() == compartment_name.lower():
            return compartment

    return None

@mcp.tool()
def get_compartment_by_name_tool(name: str) -> str:
    """Return a compartment matching the provided name"""
    compartment = get_compartment_by_name(name)
    if compartment:
        return str(compartment)
    else:
        return str({"error": f"Compartment '{name}' not found."})

@mcp.tool()
def list_nosql_tables(compartment_name: str) -> str:
    """List all tables in a given compartment name"""
    compartment = get_compartment_by_name(compartment_name)
    if not compartment:
        return json.dumps({"error": f"Compartment '{compartment_name}' not found. Use list_compartment_names() to see available compartments."})
    nosql = nosql_client.list_tables(compartment_id=compartment.id).data
    return str(nosql.items)

@mcp.tool()
def execute_query(compartment_name: str, sql_script: str) -> str:
    """execute a SQL query in a given compartment name"""
    compartment = get_compartment_by_name(compartment_name)
    if not compartment:
        return json.dumps({"error": f"Compartment '{compartment_name}' not found. Use list_compartment_names() to see available compartments."})

    query_response = nosql_client.query(
        query_details=oci.nosql.models.QueryDetails(
            compartment_id=compartment.id,
            statement=sql_script,
            is_prepared=False,
        )
    );    
    return str(query_response.data)

@mcp.tool
def greet(name: str) -> str:
        return f"Hello, {name}!"

if __name__ == "__main__":
   #mcp.run(transport="sse", host="127.0.0.1", port=8000)
   mcp.run()