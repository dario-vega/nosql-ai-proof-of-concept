"""
Copyright (c) 2025, Oracle and/or its affiliates.
Licensed under the Universal Permissive License v1.0 as shown at http://oss.oracle.com/licenses/upl.
"""

import os.path
import json

import oci
from oci.resource_search.models import StructuredSearchDetails

from borneo import (Regions, NoSQLHandle, NoSQLHandleConfig, QueryRequest, QueryIterableResult , ListTablesRequest, GetTableRequest, TableLimits )
from borneo.iam import SignatureProvider

from fastmcp import FastMCP

# MCP Code
profile_name = os.getenv("PROFILE_NAME", "DEFAULT")
mcp = FastMCP("OCI NoSQL MCP Server - " + profile_name)


# OCI SDK
config = oci.config.from_file(profile_name=profile_name)
tenancy_id = config['tenancy']
identity_client = oci.identity.IdentityClient(config)
nosql_client = oci.nosql.NosqlClient(config)
search_client = oci.resource_search.ResourceSearchClient(config)
# NoSQL SDK - Borneo
provider = SignatureProvider(profile_name=profile_name);
configN = NoSQLHandleConfig(config['region'], provider).set_logger(None)
handle = NoSQLHandle(configN)


# Using OCI SDK

def list_all_compartments_internal(only_one_page: bool , limit = 100  ):
    """Internal function to get List all compartments in a tenancy"""
    response = identity_client.list_compartments(
            compartment_id=tenancy_id,
            compartment_id_in_subtree=True,
            access_level="ACCESSIBLE",
            lifecycle_state="ACTIVE",
            limit = limit
       )
    compartments = response.data
    compartments.append(identity_client.get_compartment(compartment_id=tenancy_id).data)
    if only_one_page : # limiting the number of items returned
        return  compartments   
    while response.has_next_page:
        response = identity_client.list_compartments(
            compartment_id=tenancy_id,
            compartment_id_in_subtree=True,
            access_level="ACCESSIBLE",
            lifecycle_state="ACTIVE",
            page=response.next_page,
            limit = limit
        )
        compartments.extend(response.data)
    
    return compartments

def get_compartment_by_name(compartment_name: str):
    """Internal function to get compartment by name with caching"""
    compartments = list_all_compartments_internal(False)
    # Search for the compartment by name
    for compartment in compartments:
        if compartment.name.lower() == compartment_name.lower():
            return compartment

    return None

def get_compartment_by_name_v2(compartment_name: str):
    """Internal function to get compartment by name using the query API"""
    search_details = StructuredSearchDetails(
        query=f"query compartment resources where displayName = '{compartment_name}'",
        type="Structured",
        matching_context_type="NONE"
    )
    try:
        resp = search_client.search_resources(search_details=search_details, tenant_id=config['tenancy']).data
        if not hasattr(resp, 'items') or len(resp.items) == 0:
            return None
        
        # emulating get_compartment_by_name behavior - retrieving a Compartment
        # TODO what if multiples records matching the given name, e.g same name at different levels of the hierarchy
        # current behavior - returning the 1st compartment
        compartment = identity_client.get_compartment( compartment_id= resp.items[0].identifier )
        return compartment.data
        
    except Exception as e:
        return None

# @mcp.tool()
def list_all_compartments() -> str:
    """List all compartments in a tenancy with clear formatting"""
    return str(list_all_compartments_internal(True))

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
    compartment = get_compartment_by_name_v2(compartment_name)
    if not compartment:
        return json.dumps({"error": f"Compartment '{compartment_name}' not found. Use list_compartment_names() to see available compartments."})
    
    response = nosql_client.list_tables(compartment_id=compartment.id,)
    tables = response.data  
    while response.has_next_page:
        response = nosql_client.list_tables(compartment_id=compartment.id,  page=response.next_page,)
        tables.extend(response.data)
    return str(tables)

@mcp.tool()
def describe_nosql_table(compartment_name: str, table_name: str ) -> str:
    """describe a NoSQL table in a given compartment name"""
    compartment = get_compartment_by_name(compartment_name)
    if not compartment:
        return json.dumps({"error": f"Compartment '{compartment_name}' not found. Use list_compartment_names() to see available compartments."})
    
    nosql_info = nosql_client.get_table(table_name_or_id=table_name, compartment_id=compartment.id).data
    return str(nosql_info)

@mcp.tool()
def execute_query(compartment_name: str, sql_script: str) -> str:
    """Execute a SQL query in Oracle NoSQL database using standard endpoint.
    
    USAGE GUIDELINES:
    - Always add a comment in the SQL queries : '/* AI Tool: [your-name] - Query */'
    - Use this for basic queries and standard operations
    - For complex queries or when experiencing issues, prefer the Borneo endpoint (_borneo variant)
    - Use alias '$t' for table references in queries
    - Do not use '$t.*' just '$t' if you want to have all the information or just '*'
    - for LIKE expresions use regex_like expressions
    - Oracle NoSQL supports Function on Rows including modification_time and expiration_time (more https://docs.oracle.com/en/database/other-databases/nosql-database/25.1/sqlreferencefornosql/functions-rows.html)
    - Always CAST timestamp functions to STRING: modification_time(t),expirationtime(t) due to JSON serialization
    
    Example:
    SELECT /*  AI Tool: Claude - Query*/ * FROM users $t    
    SELECT /*  AI Tool: GPT-4 - Query*/ * FROM users $t    
    
    Args:
        compartment_name: The compartment name to query
        sql_script: The SQL script to execute
    """
    compartment = get_compartment_by_name(compartment_name)
    if not compartment:
        return json.dumps({"error": f"Compartment '{compartment_name}' not found. Use list_compartment_names() to see available compartments."})
 
    query_details=oci.nosql.models.QueryDetails(
        compartment_id=compartment.id,
        statement=sql_script,
        is_prepared=False,
    )
    response = nosql_client.query(query_details)
    rows = response.data
    while response.has_next_page:
        response = nosql_client.query(query_details, page = response.next_page)
        rows.extend(response.data)
    
    return str(rows)

# Using NoSQL SDK Borneo

@mcp.tool()
def list_nosql_tables_borneo(compartment_name: str) -> str:
    """List all tables in a given compartment using Borneo endpoint.
    
    REMINDER: This uses Borneo endpoint. 
    - It provides only table names. 
    - Use list_nosql_tables if you want details. Or better ask the details for a specific table using describe_nosql_table_borneo
    
    Args:
        compartment_name: The compartment name to list tables from
    """
    ltr = ListTablesRequest().set_compartment(compartment_name)
    lt_result = handle.list_tables(ltr)
    return( json.dumps(lt_result.get_tables()) )


@mcp.tool()
def describe_nosql_table_borneo(compartment_name: str, table_name: str ) -> str:
    """Describe a NoSQL table structure using Borneo endpoint.
    
    NOTE: When querying this table later, use Borneo endpoint and see IMPORTANT INSTRUCTIONS.
    
    Args:
        compartment_name: The compartment name
        table_name: The table name to describe
    """
    gtr = GetTableRequest().set_table_name(table_name).set_compartment(compartment_name)
    gr_result = handle.get_table(gtr)
    limits = None if not gr_result.get_table_limits() else dict(
                            {
                              "capacity_mode": gr_result.get_table_limits().get_mode(),  # TableLimits.CAPACITY_MODE
                              "max_read_units": gr_result.get_table_limits().get_read_units(),
                              "max_storage_in_g_bs": gr_result.get_table_limits().get_storage_gb(),
                              "max_write_units": gr_result.get_table_limits().get_write_units()
                            }
                )
    replicas = []
    if gr_result.get_replicas() is not None:
        for replicat in gr_result.get_replicas() :
             replicas.append (dict (
                            {
                              "replicat": replicat.get_name(),
                              "table_id": replicat.get_ocid(),
                              "capacity_mode": replicat.get_capacity_mode(),
                              "lifecycle_state": replicat.get_state(),
                              "max_write_units": replicat.get_write_units()
                            } )
                            )
    return json.dumps(
             {
               "compartment_id": gr_result.get_compartment_id(),
               "ddl_statement": gr_result.get_ddl(), 
               "defined_tags": gr_result.get_defined_tags(), 
               "freeform_tags": gr_result.get_free_form_tags()  ,
               "id": gr_result.get_table_id(),
               "is_multi_region": gr_result.is_replicated(),
               "lifecycle_state": gr_result.get_state(),
               "local_replica_initialization_in_percent" : gr_result.is_local_replica_initialized(),
               "name":table_name,
               "replicas": replicas,
               "schema": json.loads(gr_result.get_schema()),
               "table_limits": limits
             }
         )


@mcp.tool()
def execute_query_borneo(compartment_name: str, sql_script: str) -> str:
    """execute a SQL query in a given compartment name
       
    IMPORTANT INSTRUCTIONS:
    - Always add a comment in the SQL queries : '/* AI Tool: [your-name] - Query */' 
    - Use the Borneo endpoint for queries by default
    - Use alias '$t' for table references in queries
    - Do not use '$t.*' just '$t' if you want to have all the information or just '*'
    - for LIKE expresions use regex_like expressions
    - Oracle NoSQL supports Function on Rows including modification_time and expiration_time (more https://docs.oracle.com/en/database/other-databases/nosql-database/25.1/sqlreferencefornosql/functions-rows.html)
    - Always CAST timestamp functions to STRING: modification_time(t),expirationtime(t) due to JSON serialization
    
    Example:
    SELECT /*  AI Tool: Claude - Query*/ * FROM users $t    
    SELECT /*  AI Tool: GPT-4 - Query*/ * FROM users $t    
    
    Args:
        compartment_name: The compartment name to query
        sql_script: The SQL script to execute
    """
    
    request = QueryRequest().set_statement(sql_script).set_compartment(compartment_name) ## compartment.id
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


if __name__ == "__main__":
   mcp.run()