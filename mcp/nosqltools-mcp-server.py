from fastmcp import FastMCP
import oci
from oci.signer import Signer
import os.path

from borneo import (Regions, NoSQLHandle, NoSQLHandleConfig, QueryRequest, QueryIterableResult  )
from borneo.iam import SignatureProvider
import json


mcp = FastMCP("OCI NoSQL MCP Server")

profile_name = os.getenv("PROFILE_NAME", "DEFAULT")
config = oci.config.from_file(profile_name=profile_name)
tenancy_id = os.getenv("TENANCY_ID_OVERRIDE", config['tenancy'])

identity_client = oci.identity.IdentityClient(config)
nosql_client = oci.nosql.NosqlClient(config)


provider = SignatureProvider(profile_name=profile_name);
configN = NoSQLHandleConfig(config['region'], provider).set_logger(None)
handle = NoSQLHandle(configN)

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
    
    request = QueryRequest().set_statement(sql_script).set_compartment(compartment.id)
    #rows = []
    #ru = 0
    #wu = 0
    #qiresult = handle.query_iterable(request)
    #for row in qiresult:
    #   rows.append(row)
    #   ru += qiresult.get_read_units()
    #   wu += qiresult.get_write_units()
    #usageIt = {"read_units_consumed":qiresult.get_read_units(), "write_units_consumed":qiresult.get_write_units()} 
    #usageIt2 = {"read_units_consumed":ru, "write_units_consumed":wu} 


    rows = []
    ru = 0
    wu = 0
    while True:
        result = handle.query(request)
        results = result.get_results()
        ru += result.get_read_units()
        wu += result.get_write_units()
        for row in results:
            rows.append(row)
        if request.is_done():
            break
    usagePt = {"read_units_consumed":ru, "write_units_consumed":wu} 
    
    #return json.dumps({"items":rows, "usage":usageIt, "usage2":usageIt2})
    return json.dumps({"items":rows, "usage":usagePt})

@mcp.tool()
def execute_query_internal(compartment_name: str, sql_script: str) -> str:
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
    
    #query_details = QueryDetails(
    #     compartment_id = compartment,
    #     statement = query_statement
    #)

    #page=None
    #has_next_page=True
    #while has_next_page:
    #   query_response = client.query(query_details, page = page)
    #   print('Query results')
    #   print(len(query_response.data.items))
    #   print(query_response.has_next_page)
    #   page=query_response.next_page
    #   has_next_page=query_response.has_next_page


if __name__ == "__main__":
   mcp.run()