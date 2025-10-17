"""
CAUTION
This MCP server is designed **for hands-on experimentation and is not suitable for production use**.

Granting a large language model (LLM) access to your database introduces significant security risks.
LLMs may use input data to generate responses, potentially exposing unintended tables or sensitive details.

To mitigate these risks:
- Use a private LLM when possible (self-hosted or controlled).
- Assign minimum permissions—use an account with only necessary access.
- Avoid production data—use sanitized, read-only replicas or subsets.
- Audit LLM activity; review queries for anomalies or unauthorized data.
- Use provided anonymization scripts at your own risk; these do not guarantee compliance or complete anonymization. Always review the code and outputs.

No warranty is provided. Use of this project is at your own risk and subject to your organization’s legal, privacy, and security requirements.
For questions, consult your legal, security, or compliance team.
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

@mcp.tool()
def list_all_compartments() -> str:
    """List all compartments in a tenancy with clear formatting"""
    compartments= list_all_compartments_internal(True)
    filtered = [{'name': c.name, 'parent_compartment_id': c.compartment_id} for c in compartments]
    return json.dumps(filtered)

# Using NoSQL SDK Borneo

@mcp.tool()
def list_nosql_tables(compartment_name: str) -> str:
    """List all tables in a given compartment using Borneo endpoint.
    
    REMINDER: This uses Borneo endpoint. 
    - It provides only table names. 
    - Ask the details for a specific table using describe_nosql_table
    
    Args:
        compartment_name: The compartment name to list tables from
    """
    ltr = ListTablesRequest().set_compartment(compartment_name)
    lt_result = handle.list_tables(ltr)
    return( json.dumps(lt_result.get_tables()) )


@mcp.tool()
def describe_nosql_table(compartment_name: str, table_name: str ) -> str:
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

"""
!!! SECURITY/DATA USAGE WARNING !!!
This function may interact with large language models (LLMs). Review the full disclaimer regarding data exposure risks and best practices above (or in README).
Never send production, sensitive, or regulated data to LLMs without explicit organizational approval. See your privacy and security team for details.
"""
@mcp.tool()
def execute_query(compartment_name: str, sql_script: str) -> str:
    """execute a SQL query in a given compartment name
       
    IMPORTANT SQL QUERY REQUIREMENTS:
    
    1. QUERY IDENTIFICATION (Required for all queries)
       - Add this comment at the start: /* AI Tool: [your-name] - Query */
       - Example: /* AI Tool: Claude - Query */
       - Purpose: Tracks which AI tool generated the query for auditing
    
    2. TABLE REFERENCES (Critical for Oracle NoSQL Borneo syntax)
       - Always use table alias '$t' after the table name
       - ✓ Correct: FROM users $t
       - ✗ Wrong: FROM users
       
    3. COLUMN SELECTION
       When selecting all columns, choose ONE of these patterns:
       - Option A: SELECT * FROM users $t (preferred for readability)
       - Option B: SELECT $t FROM users $t (NoSQL-specific, returns all fields)
       - ✗ Never use: SELECT $t.* FROM users $t (not supported)
       
    4. PATTERN MATCHING
       - Use regex_like() instead of LIKE operator
       - ✓ Correct: WHERE regex_like(name, '.*Smith.*')
       - ✗ Wrong: WHERE name LIKE '%Smith%'
       - Reason: Oracle NoSQL uses regex for pattern matching
    
    5. FUNCTION NAMING (Strict lowercase requirement)
       - All SQL functions MUST be lowercase
       - ✓ Correct: count(*), avg(price), sum(total)
       - ✗ Wrong: COUNT(*), AVG(price), SUM(total)
       - Reason: NoSQL parser is case-sensitive for functions
    
    6. TIMESTAMP HANDLING (Critical for JSON serialization)
       - Always CAST modification_time() and expiration_time() to STRING
       - ✓ Correct: CAST(modification_time($t) AS STRING)
       - ✗ Wrong: modification_time($t)
       - Note: Always use $t as the parameter for row functions
       - Reason: Prevents JSON serialization errors in results
       - Documentation: https://docs.oracle.com/en/database/other-databases/nosql-database/25.1/sqlreferencefornosql/functions-rows.html
    
    7. HIERARCHICAL TABLES (Parent-Child Relationships)
       
       Child tables use dot notation: ParentTable.childname (e.g., Movie.child)
       Two methods available for querying hierarchies:
    
       METHOD A - NESTED TABLES (Recommended for complex hierarchies):
       
       Syntax: NESTED TABLES(target_table alias 
                             [ANCESTORS(table alias [ON condition])]
                             [DESCENDANTS(table alias [ON condition])])
       
       Rules:
       - Use FULL table names (Movie.child not $m.child)
       - Join predicates are implicit (based on primary keys)
       - ANCESTORS: decorates target rows with parent data
       - DESCENDANTS: expands to child rows (NULL if none)
       - ON conditions are for filtering only, not joining
       
       Example:
       SELECT /* AI Tool: Claude - Query */
              $m.movieid, $m.data, $c.childid, $c.childdata
       FROM NESTED TABLES(Movie $m DESCENDANTS(Movie.child $c))
    
       METHOD B - LEFT OUTER JOIN (Traditional SQL):
       
       Syntax: FROM table1 alias LEFT OUTER JOIN table2 alias ON condition
       
       Rules:
       - Tables must be in same hierarchy
       - Must specify explicit ON conditions with inherited primary keys
       - Results ordered top-down (ancestor first) regardless of join order
       - Produces flat result structure
       
       Example:
       SELECT /* AI Tool: Claude - Query */
              $m.movieid, $m.data, $c.childid, $c.childdata
       FROM Movie $m
            LEFT OUTER JOIN Movie.child $c ON $m.movieid = $c.movieid
       
       When to use which:
       - Use NESTED TABLES: Multi-level hierarchies, multiple branches, want concise syntax
       - Use LOJ: Familiar with SQL, want explicit join control, simple parent-child
    
    COMPLETE EXAMPLES:
    
    Example 1 - Simple select all:
    SELECT /* AI Tool: Claude - Query */ * FROM users $t
    SELECT /* AI Tool: Claude - Query */ $t FROM users $t
    
    Example 2 - With conditions and functions:
    SELECT /* AI Tool: Claude - Query */ 
           $t.name, 
           count(*) as user_count,
           CAST(modification_time($t) AS STRING) as last_modified
    FROM users $t
    WHERE regex_like($t.email, '.*@example\\.com')
    GROUP BY $t.name
    
    Example 3 - NESTED TABLES with filtering:
    SELECT /* AI Tool: Claude - Query */
           $m.movieid,
           $c.idchild,
           $c.json
    FROM NESTED TABLES(Movie $m 
         DESCENDANTS(Movie.child $c ON $c.idchild > 100))
    
    Example 4 - LEFT OUTER JOIN multi-level:
    SELECT /* AI Tool: Claude - Query */
           $a.ida,
           $b.idb,
           $c.idc
    FROM A $a
         LEFT OUTER JOIN A.B $b ON $a.ida = $b.ida
         LEFT OUTER JOIN A.B.C $c ON $b.ida = $c.ida AND $b.idb = $c.idb
    
    
  
    
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