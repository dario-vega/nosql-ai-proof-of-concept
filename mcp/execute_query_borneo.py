
import os.path
import json


from borneo import (Regions, NoSQLHandle, NoSQLHandleConfig, QueryRequest, QueryIterableResult , ListTablesRequest, GetTableRequest, TableLimits )
from borneo.iam import SignatureProvider

profile_name = os.getenv("PROFILE_NAME", "DEFAULT")
provider = SignatureProvider(profile_name=profile_name);
configN = NoSQLHandleConfig('us-ashburn-1', provider).set_logger(None)
handle = NoSQLHandle(configN)


def execute_query_borneo(compartment_name: str, sql_script: str) -> str:
    """execute a SQL query in a given compartment name"""
    
    request = QueryRequest().set_statement(sql_script).set_compartment(compartment_name) ## compartment.id
    rows = []

    result = handle.query_iterable(request)
    for row in result:
       rows.append(row)
    
    
    print ( {
           "items":rows,
           "get_read_kb":result.get_read_kb(), 
           "get_read_units":result.get_read_units()         
           } 
    )

    rows = []
    ru = 0
    ru2 = 0
    while True:
        result = handle.query(request)
        results = result.get_results()
        ru += result.get_read_units()
        ru2 += result.get_read_kb()
        for row in results:
            rows.append(row)
        if request.is_done():
            break
    
    usagePt = {"items":rows, "read_units_consumed":ru, "get_read_kb":ru2} 
    #"items":rows, 
    print ( json.dumps({"usage":usagePt}) )

if __name__ == "__main__":
    try:
      execute_query_borneo ("davega", "select * from movie")
    except Exception as e:
        print(e)
    finally:
        # If the handle isn't closed Python will not exit properly
        if handle is not None:
            handle.close()   