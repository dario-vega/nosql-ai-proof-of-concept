"""
PRIVACY, COMPLIANCE, AND USE-AT-YOUR-OWN-RISK NOTICE:
-----------------------------------------------------
This script is intended as an example for generating anonymized or synthetic data 
using open-source tools such as Faker. It is licensed under the MIT License.

**USE THIS SCRIPT AT YOUR OWN RISK.**

- This is NOT a substitute for professionally reviewed, enterprise data anonymization or masking solutions.
- The script does not guarantee compliance with data privacy regulations (such as GDPR, CCPA, etc.) 
  or internal corporate security policies.
- It is YOUR responsibility to review and adapt both the anonymization logic and any third-party libraries 
  to your organization’s specific data, risk tolerance, regulatory environment, and security requirements.
- Always consult your privacy, legal, and compliance teams before using anonymized or synthetic data 
  outside of approved, nonproduction environments or for any sharing beyond your organization.
- Inadequate or incorrect anonymization can lead to accidental data leaks or re-identification risk.

OPEN SOURCE, THIRD-PARTY, AND PROFESSIONAL TOOLS:
-------------------------------------------------
- Open-source libraries such as Faker are powerful but must be vetted for security, licensing, 
  and compliance, especially when handling regulated or sensitive data.
- Use of any third-party or external tools should align with your organization's approved software lists 
  and risk management processes.
- For critical use cases, consider professionally supported, enterprise-class anonymization, 
  masking, or synthetic data generation solutions recommended by your organization.

"""

import random
import string
import json
from faker import Faker

# Initialize Faker
fake = Faker()

# ---- Anonymizer Functions ----
def random_name():
    return fake.name()
def random_phone():
    return f"555-{random.randint(100, 999)}-{random.randint(1000,9999)}"
def random_address():
    return fake.address().replace('\n', ', ')
def random_credit_card():
    return fake.credit_card_number(card_type=None)
def random_email():
    return fake.email()
def random_ssn():
    return fake.ssn()
def anonymize_value(value):
    if isinstance(value, str):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=len(value)))
    elif isinstance(value, int):
        return random.randint(1000, 999999)
    elif isinstance(value, float):
        return float(random.randint(1000, 999999)) / 100
    elif isinstance(value, bool):
        return random.choice([True, False])
    else:
        return value

ANONYMIZER_FN_LOOKUP = {
    "random_name": random_name,
    "random_phone": random_phone,
    "random_address": random_address,
    "random_credit_card": random_credit_card,
    "random_email": random_email,
    "random_ssn": random_ssn,
    "anonymize_value": anonymize_value
}

class DataAnonymizer:
    def __init__(self, field_mapping: dict, except_fields=None):
        self.except_fields = set(except_fields or [])
        self.anonymizers = {}
        self.default_anonymizer = None
        for field, func_name in field_mapping.items():
            if field == "*":
                self.default_anonymizer = ANONYMIZER_FN_LOOKUP.get(func_name, anonymize_value)
            else:
                fn = ANONYMIZER_FN_LOOKUP.get(func_name)
                if fn is None:
                    print(f"WARNING: anonymizer function '{func_name}' for field '{field}' not found, using anonymize_value instead.")
                    self.anonymizers[field.lower()] = anonymize_value
                else:
                    self.anonymizers[field.lower()] = fn

    def anonymize(self, data):
        if isinstance(data, str):
            try:
                data_obj = json.loads(data)
                anon_data = self._anonymize_core(data_obj)
                return json.dumps(anon_data, indent=2)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON string.")
        return self._anonymize_core(data)

    def _anonymize_core(self, data):
        if isinstance(data, dict):
            new_data = {}
            for k, v in data.items():
                kl = k.lower()
                if kl in self.except_fields:
                    new_data[k] = v
                elif kl in self.anonymizers:
                    if self.anonymizers[kl] == anonymize_value:
                        new_data[k] = anonymize_value(v)
                    else:
                        new_data[k] = self.anonymizers[kl]()
                elif isinstance(v, (dict, list)):
                    new_data[k] = self._anonymize_core(v)
                elif self.default_anonymizer:
                    new_data[k] = self.default_anonymizer(v)
                else:
                    new_data[k] = v
            return new_data
        elif isinstance(data, list):
            return [self._anonymize_core(i) for i in data]
        else:
            if self.default_anonymizer:
                return self.default_anonymizer(data)
            else:
                return data

# --- EXAMPLE USAGE ---
if __name__ == "__main__":

     # Load config from JSON file
     with open('config.json', 'r') as f:
         config = json.load(f)
     
     # Extract dicts
     field_mapping = config['field_mapping']
     except_fields = set(config['except_fields'])
    
     anonymizer = DataAnonymizer(field_mapping=field_mapping, except_fields=except_fields)
     
     original = {
         "id": 123,
         "status": "active",
         "name": "Jane Doe",
         "phone": "123-456-7890",
         "username": "janed",
         "custom_field": "Sensitive",
         "employee_id": 1002,
         "amount": 999.99,
         "is_active": True,
         "address": "1 Infinite Loop",
         "credit_card": "4111111111111111",
         "email": "test@example.com",
         "ssn": "111-11-1111",
         "details": {
             "favorite_color": "Blue",
             "lucky_number": 7,
             "phone_number": "555-000-1111",
             "internal_id": 999
         },
         "records": [
             {"username": "johnsmith", "mail": "john@example.com", "social_security": "123-45-6789", "notes": "See file"}
         ]
     }
     
     print("Original:")
     print(json.dumps(original, indent=2))
     print("\nAnonymized (dict):")
     print(json.dumps(anonymizer.anonymize(original), indent=2))
     
     # Test with JSON string input:
     json_input = json.dumps(original)
     print("\nAnonymized (JSON string input):")
     print(anonymizer.anonymize(json_input))
     