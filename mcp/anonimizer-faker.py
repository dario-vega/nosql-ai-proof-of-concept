"""
PRIVACY, COMPLIANCE, AND USE-AT-YOUR-OWN-RISK NOTICE:
-----------------------------------------------------
This script is intended as an example for generating anonymized or synthetic data 
using open-source tools such as Faker.

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

fake = Faker()

# --- Fields to skip (preserve) during anonymization ---
FIELDS_TO_SKIP = {"id", "type", "status"}

def random_name():
    return fake.name()

def random_555_phone():
    return f"555-{random.randint(100, 999)}-{random.randint(1000,9999)}"

def random_address():
    return fake.address().replace('\n', ', ')  # Faker sometimes returns multiline addresses

def random_credit_card():
    return fake.credit_card_number(card_type=None)

def random_email():
    return fake.email()

def random_ssn():
    return fake.ssn()

def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def random_number():
    return random.randint(1000, 999999)

def random_bool():
    return random.choice([True, False])

def anonymize_value(value):
    if isinstance(value, str):
        return random_string(len(value))
    elif isinstance(value, int):
        return random_number()
    elif isinstance(value, float):
        return float(random_number()) / 100
    elif isinstance(value, bool):
        return random_bool()
    else:
        return value

ANONYMIZERS = {
    "name": random_name,
    "phone": random_555_phone,
    "phone_number": random_555_phone,
    "address": random_address,
    "credit_card": random_credit_card,
    "creditcard": random_credit_card,
    "cardnumber": random_credit_card,
    "email": random_email,
    "mail": random_email,
    "ssn": random_ssn,
    "social_security": random_ssn,
    "username": random_name  # or fake.user_name()
}

def anonymize_json(data, anonymizer_map=ANONYMIZERS):
    if isinstance(data, dict):
        new_data = {}
        for k, v in data.items():
            key_lower = k.lower()
            if key_lower in FIELDS_TO_SKIP:
                new_data[k] = v
                continue
            func = anonymizer_map.get(key_lower)
            if func and callable(func):
                new_data[k] = func()
            elif isinstance(v, (dict, list)):
                new_data[k] = anonymize_json(v, anonymizer_map)
            else:
                new_data[k] = anonymize_value(v)
        return new_data
    elif isinstance(data, list):
        return [anonymize_json(item, anonymizer_map) for item in data]
    else:
        return anonymize_value(data)

if __name__ == "__main__":
    # Example input
    data = {
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "address": "1 Infinite Loop",
        "credit_card": "4111111111111111",
        "records": [
            {"username": "johnsmith", "mail": "john@oracle.com", "ssn": "123-45-6789"}
        ]
    }
    print("Original:\n", json.dumps(data, indent=2))
    print("\nAnonymized (with Faker):\n", json.dumps(anonymize_json(data), indent=2))
