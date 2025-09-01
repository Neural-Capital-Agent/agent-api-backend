import os
import json
import http.client
import base64
from dotenv import load_dotenv

load_dotenv()

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
API_KEY_ALPACA = os.getenv("API_KEY_ALPACA")
API_SECRET_ALPACA = os.getenv("API_SECRET_ALPACA")
URL_ALPACA = os.getenv("URL_ALPACA")

class Alpaca:
    @staticmethod
    def requestAlpaca(method, endpoint, data=None):
        conn = http.client.HTTPSConnection(URL_ALPACA)
        credentials = f"{API_KEY_ALPACA}:{API_SECRET_ALPACA}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json"
        }
        body = json.dumps(data) if data is not None else None
        conn.request(method, endpoint, body=body, headers=headers)
        response = conn.getresponse()
        result = response.read().decode()
        conn.close()
        return result,response

    
    @staticmethod
    def create_user(user):
        data = {
            "contact": {
                "email_address": user.get('mail', ''),
                "phone_number": user.get('phone', ''),
                "street_address": [user.get('street_address', '')],
                "city": user.get('city', ''),
                "state": user.get('state', ''),
                "postal_code": user.get('postal_code', '')
            },
            "identity": {
                "given_name": user.get('given_name', ''),
                "family_name": user.get('family_name', ''),
                "date_of_birth": user.get('date_of_birth', ''),
                "country_of_citizenship": user.get('country_of_citizenship', ''),
                "country_of_birth": user.get('country_of_birth', ''),
                "party_type": "",
                "tax_id": user.get('tax_id', ''),
                "tax_id_type": "USA_SSN",
                "country_of_tax_residence": "USA",
                "funding_source": ["employment_income"]
            },
            "disclosures": {
                "is_control_person": False,
                "is_affiliated_exchange_or_finra": False,
                "is_affiliated_exchange_or_iiroc": False,
                "is_politically_exposed": False,
                "immediate_family_exposed": False,
                "is_discretionary": None
            },
            "agreements": [
                {
                    "agreement": "customer_agreement",
                    "signed_at": "2025-08-25T16:13:50.12796722Z",
                    "ip_address": "127.0.0.1"
                }
            ],
            "documents": [
                {
                    "document_type": "identity_verification",
                    "document_sub_type": "passport",
                    "content": "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD3+iiigD//2Q==",
                    "content_data": None,
                    "mime_type": "image/jpeg"
                }
            ],
            "trusted_contact": {
                "given_name": user.get('contact_given', ''),
                "family_name": user.get('contact_family', ''),
                "email_address": user.get('contact_email', '')
            },
            "minor_identity": None,
            "entity_id": None,
            "additional_information": "",
            "account_type": "",
            "account_sub_type": None,
            "trading_type": None,
            "auto_approve": None,
            "beneficiaries": None,
            "trading_configurations": None,
            "currency": None,
            "enabled_assets": None,
            "instant": None,
            "authorized_individuals": None,
            "ultimate_beneficial_owners": None,
            "sub_correspondent": None,
            "primary_account_holder_id": None
        }
        return Alpaca.requestAlpaca("POST", "/v1/accounts", data)

    @staticmethod
    def connect_ach(id):
        data = {
            "account_owner_name": "Condescending Gagarin",
            "bank_account_type": "CHECKING",
            "bank_account_number": "32131231abc",
            "bank_routing_number": "123103716",
            "nickname": "Bank of America Checking"
        }
        return Alpaca.requestAlpaca("POST", f"/v1/accounts/{id}/ach_relationships", data)

    @staticmethod
    def transfer(id, relation_id):
        data = {
            "transfer_type": "ach",
            "relationship_id": relation_id,
            "amount": "1234.56",
            "direction": "INCOMING"
        }
        return Alpaca.requestAlpaca("POST", f"/v1/accounts/{id}/transfers", data)

    @staticmethod
    def makeOrder(id):
        data = {
            "symbol": "AAPL",
            "qty": 1,
            "side": "buy",
            "type": "market",
            "time_in_force": "day"
        }
        return Alpaca.requestAlpaca("POST", f"/v1/accounts/{id}/orders", data)


