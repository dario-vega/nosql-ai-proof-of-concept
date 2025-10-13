"""
Anonymize JSON/dict data for development or demo purposes.

PRIVACY, COMPLIANCE, AND USE-AT-YOUR-OWN-RISK NOTICE:
-----------------------------------------------------
This script is intended as a generic example for anonymizing structured JSON-like data,
including specific handling for names, phone numbers, emails, credit cards, and addresses,
as well as support for global address formats.

**USE THIS SCRIPT AT YOUR OWN RISK.**

- This is NOT a substitute for a thorough, professionally reviewed data anonymization or
  data masking solution.
- The script does not guarantee compliance with data privacy laws (such as GDPR, CCPA, etc.)
  or internal corporate policies.
- It is YOUR RESPONSIBILITY to review and adapt the anonymization logic to your organization’s
  specific data, risk tolerance, regulatory environment, and security requirements.
- Always consult your privacy, legal, and compliance teams before using anonymized data
  outside of approved environments or for any external sharing.
- Remember that poor anonymization can lead to accidental data disclosure or re-identification risk.

OPEN SOURCE AND PROFESSIONAL TOOLS:
-----------------------------------
- For more robust, scalable, and configurable data masking or synthetic data generation, you may wish to 
  review open-source libraries (e.g. Python's `Faker`, `mimesis`, `anonypy`) or enterprise-class tools.
  These can offer locale-aware, industry-specific, and compliance-friendly options.
- **Important**: Before using any open-source or third-party tool with sensitive data, always review
  your internal security, privacy, and compliance policies, and confirm tool approval/allowlisting.
- Many large organizations (including Oracle) offer or recommend internal, professionally supported
  solutions for data anonymization and masking in software development and analytics.


"""

import random
import string
import json

# --- Configuration: fields to skip (preserve) during anonymization ---
FIELDS_TO_SKIP = {"id", "type", "status"}

# --- Specific anonymizers ---
FIRST_NAMES = [
    "Alice", "Bob", "Carol", "David", "Eve", "Frank", "Grace", "Heidi",
    "Ivan", "Julia", "Kumar", "Laila", "Mohammed", "Nina", "Oscar", "Priya"
]
LAST_NAMES = [
    "Smith", "Johnson", "Davis", "Lee", "Martinez", "Brown", "Garcia", "Wilson",
    "Suzuki", "Schmidt", "Dubois", "Singh", "Khan", "Silva", "Nguyen", "Kim"
]

FICTIONAL_ADDRESSES = [
    # USA
    "123 Imaginary Ave, Faketown, CA 94101, USA",
    "456 Nowhere Rd, Example City, TX 75001, USA",
    "789 Fictional Blvd, Testville, NY 10001, USA",
    # UK
    "10 Downing St, London SW1A 2AA, UK",
    "221B Baker St, London NW1 6XE, UK",
    "42 Fantasy Lane, Manchester M1 2AB, UK",
    # Germany
    "5 Musterstraße, 12345 Berlin, Germany",
    "12 Hauptstrasse, 50667 Köln, Germany",
    "36 Fiktive Allee, 80331 München, Germany",
    # France
    "14 Rue de l'Exemple, 75001 Paris, France",
    "25 Avenue Imaginaire, 69002 Lyon, France",
    "7 Boulevard Fictif, 13001 Marseille, France",
    # Japan
    "1-2-3 Sakura St, Minato, Tokyo 105-0011, Japan",
    "4-5-6 Fujimi, Chiyoda-ku, Tokyo 102-0071, Japan",
    "8-9-10 Umeda, Kita-ku, Osaka 530-0001, Japan",
    # India
    "101 MG Road, Bengaluru 560001, India",
    "202 Andheri West, Mumbai 400053, India",
    "303 Sector 18, Noida 201301, India",
    # Canada
    "88 Main St, Toronto, ON M5J 2N5, Canada",
    "77 Rue Sainte-Catherine, Montréal, QC H3B 1E3, Canada",
    "66 Granville St, Vancouver, BC V6C 1T2, Canada",
    # Brazil
    "12 Avenida Paulista, São Paulo, SP 01310-100, Brazil",
    "23 Rua Fictícia, Rio de Janeiro, RJ 20210-010, Brazil",
    # Australia
    "15 Queen St, Melbourne VIC 3000, Australia",
    "19 George St, Sydney NSW 2000, Australia",
    "21 Adelaide St, Brisbane QLD 4000, Australia",
    # South Africa
    "55 Nelson Mandela Ave, Johannesburg 2001, South Africa",
    "32 Table Mountain Rd, Cape Town 8001, South Africa"
]

def random_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def random_555_phone():
    return f"555-{random.randint(100, 999)}-{random.randint(1000,9999)}"

def random_address():
    return random.choice(FICTIONAL_ADDRESSES)

def random_credit_card():
    return "4" + "".join([str(random.randint(0, 9)) for _ in range(15)])

def random_email():
    return f"{random.choice(FIRST_NAMES).lower()}.{random.choice(LAST_NAMES).lower()}@example.com"

def random_ssn():
    return f"{random.randint(100, 999)}-{random.randint(10,99)}-{random.randint(1000,9999)}"

# --- Generic anonymizers ---
def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def random_number():
    return random.randint(1000, 999999)

def random_bool():
    return random.choice([True, False])

def anonymize_value(value):
    """Generic anonymizer for unrecognized fields based on type."""
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

# --- Field to anonymizer mapping ---
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
    "username": random_name
}

def anonymize_json(data, anonymizer_map=ANONYMIZERS):
    """Recursively anonymizes dict, list, or value."""
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

def anonymize_data(data):
    """
    Anonymize a dict/list or a JSON string.
    Returns the same type as input (dict or str).
    """
    if isinstance(data, str):
        try:
            data_obj = json.loads(data)
            anon_data = anonymize_json(data_obj)
            return json.dumps(anon_data)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON string.")
    else:
        return anonymize_json(data)

# --- Example usage ---
if __name__ == "__main__":
    # TEST: as Python dict
    original_dict = {
        "id": 101,
        "type": "employee",
        "status": "active",
        "name": "Jane Doe",
        "phone": "123-456-7890",
        "custom_field": "Sensitive",
        "employee_id": 1002,
        "amount": 999.99,
        "is_active": True,
        "address": "1 Infinite Loop",
        "credit_card": "4111111111111111",
        "email": "test@oracle.com",
        "ssn": "111-11-1111",
        "details": {
            "favorite_color": "Blue",
            "lucky_number": 7,
            "phone_number": "555-000-1111",
            "internal_id": 999
        },
        "records": [
            {"username": "johnsmith", "mail": "john@oracle.com", "social_security": "123-45-6789"}
        ]
    }
    print("Original dict:\n", json.dumps(original_dict, indent=2))
    print("\nAnonymized dict:\n", json.dumps(anonymize_data(original_dict), indent=2))

    # TEST: as JSON string
    original_json = json.dumps(original_dict)
    anon_json = anonymize_data(original_json)
    print("\nOriginal JSON string:\n", original_json)
    print("\nAnonymized JSON string:\n", anon_json)
 