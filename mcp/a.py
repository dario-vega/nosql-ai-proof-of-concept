# json_field_remover.py

class JSONFieldRemover:
    def __init__(self, targets):
        """
        targets: list of tuples (path, key), where path is a list of keys and/or "*" for wildcards,
                 and key is the key name to delete at that path.
        Example: [ (["users", "*", "profile"], "name"), (["customers", "*", "contact"], "phone") ]
        """
        self.targets = targets

    def match_path(self, path, target):
        if len(path) != len(target):
            return False
        for p, t in zip(path, target):
            if t == "*":
                continue
            if p != t:
                return False
        return True

    def _delete_fields(self, data, path=None):
        if path is None:
            path = []
        if isinstance(data, dict):
            for key in list(data.keys()):
                for target_path, target_key in self.targets:
                    if self.match_path(path + [key], target_path + [target_key]):
                        del data[key]
                        break
                else:
                    self._delete_fields(data[key], path + [key])
        elif isinstance(data, list):
            for idx, item in enumerate(data):
                self._delete_fields(item, path + [idx])

    def remove_fields(self, data):
        """
        Deletes the specified fields in-place from the data.
        """
        self._delete_fields(data)


import json

data= [
     {
       "compartment_id": "ocid1.tenancy.oc1..aaaaaaaaj4ccqe763dizkrcdbs5x7ufvmmojd24mb6utvkymyo4xwxyv3gfa",
       "defined_tags": {
         "Administration": {
           "Creator": "oracleidentitycloudservice/dario.vega@oracle.com"
         }
       },
       "description": "Dario VEGA",
       "freeform_tags": {},
       "id": "ocid1.compartment.oc1..aaaaaaaa4mlehopmvdluv2wjcdp4tnh2ypjz3nhhpahb4ss7yvxaa3be3diq",
       "inactive_status": None,
       "is_accessible": True,
       "lifecycle_state": "ACTIVE",
       "name": "davega",
       "time_created": "2021-04-29T10:26:36.629000+00:00"
     },
     {
       "compartment_id": "ocid1.tenancy.oc1..aaaaaaaaj4ccqe763dizkrcdbs5x7ufvmmojd24mb6utvkymyo4xwxyv3gfa",
       "defined_tags": {
         "Administration": {
           "Creator": "oracleidentitycloudservice/dario.vega@oracle.com"
         }
       },
       "description": "Dario VEGA",
       "freeform_tags": {},
       "id": "ocid1.compartment.oc1..aaaaaaaa4mlehopmvdluv2wjcdp4tnh2ypjz3nhhpahb4ss7yvxaa3be3diq",
       "inactive_status": None,
       "is_accessible": True,
       "lifecycle_state": "ACTIVE",
       "name": "davega",
       "time_created": "2021-04-29T10:26:36.629000+00:00"
     }
]

targets = [
    (["*"], "defined_tags"),
    (["*"], "freeform_tags"),
    (["*"], "description")
]

remover = JSONFieldRemover(targets)
remover.remove_fields(data)

print(json.dumps(data, indent=2))        