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

class alpaca:
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
            "email_address": user.get('email') or user.get('mail', ''),
            "phone_number": "633-333-2323",
            "street_address":"33-33 34ST",
            "city": user.get('city', ''),
            "state":"NY",##TODO THIS FOR TEST
            "postal_code":"11111"
            },
            "identity": {
            "given_name": user.get('given_name', ''),
            "family_name": user.get('family_name', ''),
            "date_of_birth": "2000-01-01",
            "country_of_citizenship": "USA",
            "country_of_birth": "USA",
            "party_type": "",
            "tax_id": "121212121",#TODO JUST FOR TEST
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
                "document_sub_type": "passport",#TODO JUST FOR TEST
                    "content": "iVBORw0KGgoAAAANSUhEUgAAAQAAAAEACAMAAABrrFhUAAAABGdBTUEAALGPC/xhBQAAAAFzUkdCAK7OHOkAAAMAUExURUdwTOWkAGBnqDd87rnA1ZScx6q/lvD1/+Xl9f/9ALzEyvz///n5+ubo83aIu//+AP//AP/5AP//AIiayoCRwf/3AIeZyf7//6q31v/6AP/8AP3/AP/7AP///5SmzZ2szdjAV8fP47XN6v/yAJelx//tAP/pAP/1ALrE2fT0/v7+//7/+7bC3KeszMLJ3//xAP/4AKi00v7/+//lAL3H2+jq9Y6fyoGXxaCt0Pz8/uTn8tDX6MjR5f/gAJGhyK240P/mAP/wAP/2AP/nAP/oAP3//v/iAP7+/fv9//v9/vv+/u7x9/7//vj5/fj5+9zh7/n6/Nbe7uvu9eDl8ff4+8zU5v/cAP/fAPHz+N3i79fd7PX2+tLZ6enu9LfD3Ojr9LXC2/v7/c/X6Pn6/dXc7Pb3++Xo8vr8/vr6/fH09+Hl8M3V5unt9O/y+MnS5vz8/erA5sXO4+fs9OHm8PP1+NHY6evt9fDz97jE3OLn8vP0+cPN49vh7r/K3/b3+tjf7c7V57/J3uvu9v/qAPT2+vb4+vf3+8rT5fX2+fT1+tXb68PN4bvG3fL0+MfQ5LvF3bC92vLz+Orr9O3v9v/jALLA29Ha6ePm8dTb6uXp8+fp897j78TM4ezw9uns9evs9eDk7/r7/b7I3uTn8fz7/tLZ6fj6/Pj6+8bP4+zv9v/uAPj//tbf8ff8/9nf6/H2/9fh8d7l8NTb6P//83+YvtnEV9TBWJCu6P/QRf/5yf/88v/3t//fev/xuv/1qP/+9f/SVv/us//mif/97f/idf/IA//cYv/GE//99K3G9f/nhv/UK//45f/1rf/77v/sov/lkP/YXP/wvf/MJP/DAP/dav/76f/yxP/bZv/trP/TL//gff/XVP/zz//urf/mj//sn//54v/QNP/aYf/41v/xwP/OL//KGf/yzf/TQ//30//UOf/caP/fd//WT//QLv/OKdGGAC0AAAABdFJOUwBA5thmAAAJvElEQVR42u3dd1sURxgA8OFIuYOj9957rwmIICAgoICgonQL3bRo7L1rYsdo7DGJGjXFJMaYZjQaY0zvMZrE9PSWJ/Od3i67O7Nzu+/eHc/7+a/bnZnfPbCzOzM7MwKBDKwVXaHqlkvlTQ11BoPBptGoNZre3t6iooa4iuLLObO8BK6TlzKouiFPrdcYhR0S9Oj1DfE5QdMAroRLl+oMQo3FhmFBfFzQNIDyyyp9sCPo9VVJAV4y/wRSG/QEcRvUxwS6A3AjXKoL9qAQai/7A/+YPyhfa9CgBVFraoOAfwxwMc+ADqDGBHkD/5jgzlp0EM2t0sAfBqiNE1DDaNqqgT8MkK1GhzHoYgWuH+CGTo0OZV1cANhrkM/QoMPZG+cK9hbAU4UO6egSgZ0FOKdHh9UY68+0iF8Hl+IIARS9LgCP3nKBHSWKRccwWuYO9pEgD7HQEcSZyJvIi8gT/Z/A+iVGRCcxeIkJwKOXDdAg0Gm8MhvYRSJPgU5kMBTsIDEgOpm9zmAH0aGTaXTgZfEKnc5rDsBAJ7QugLME3qFCp7RXCH8gOl/nNBoSyTkKGugJ4zT6eQ0TdxbI5DS2BnIXQA06rXGcJQhCJzbYn6sEyeh2oXNbF8RRAjU6ubESDhLoBDq7Bj8OEnQKdH4buAsgGp3fWA4DXBXoAsYGsN9PDBfoDNbGMJ9X8BToFBoC2S8aVgp0Ck0RzAMQgk5iJPsA8tBJjGG9cFYh0FmsZP0aUCbQWSxj/RrQJtBp7PVmGUCxQOexj+2uYY1A5zGO7a5hg0AnMoHtEfkGgU6kL9sDEk0CnchqtodF+gQ6kdVsj8h0CXQimwLYBRAr0Jnsy7NfdKdAZ3Ig1P6QzDCBzuRovP2HgXKBzmRPvP06yDCBTmWY/aVTkwKdyibXSAYB1Al0Ks2e9te+9Ql0KpM87D+M7BPobLa72n8c3SbQ2Sy0/0C6TKDTafcAUiTQ6XTF2R2VbxTodFq9bc9Gjgh0QpPtLp6PCHRCXeyundUKdEZH7a0frRXojKbYWz+aKdAptXMErlagc3p5wqxZDzRv0ryd/e3a9Ro0oSxj7QLICKVfB+8XSCYnxrON3kGmF67fY/gH0LAdVdVGG5RYNfv+gWTuNfm+PVVG25RXdfdAMncOoZcNdrLpCHm/QDJ7RmDzBj58Z+8VSNqjQfQ+gZDtdQBpSXyBtDlHNZD82Wkc+gLZLwYGlpVm52VmZ+fl5aYnJSXNGt8v5s5OcZ9AwKjcwi8QrD8jPfXJE3Wc+gICuoMDWyoNdaM69UcU+tCzm3M7HdQXEAiqCQxsrdRrN6hvn3y5cRGV/UoBTtQ2BwBfS0tbVTtqcHl5uW5DZfaB5OQTnTrtBk2KrCl0aF9AEvdlBQS2lHEyJWkxVGCfQDYXDuZkSrLTUX0BSZPPpKYV83Mh1SGAZJC/EZT1cy5XVlaWnTGD/EDgDoCITZ6AE40YH8g/kPcR8hQkvIzrAJKm43pO5FyA8wF5xTMeGvWKiBdAPvOLtxE+AOQRWmtjqS7CGYHIPwVrDSQnZzgnEPlJoB2eQAbWc7I+2kmAPFMoYSiJ8HVWIOJVyP6XyN5A5AWB9nvEmAPYJ0y+gGDfTnXGAbUwQE4nGUVQGOz8QMRJsL2AxIc6PxA0UNUeQI6VOn+PpGz6SCCHJZ0fiD8gPxLIcYMTAEH9YOMjgeRmnAIIPBLVHHmNTJcuJ+gTKB9zbA98fZMzAPmNhkD9I4GkpTgFkDfgUcHYUCBdjXI8e0CqnQGI+A7wMNQfCOR0oBMAAad/1wRDgFztdQYg6PLprPFAwjudAYj3mKdCfWRAypwCCPTg8+EwICFtnP+RSp34NRwGJLrJGYBEl+yOhQE5HcH/+HBrpQvwW0hBYUAWVvL9N9Kq/fDuWOtQIF1eAn9ATpRBgMifIDwSBqQ9mP/fEJ3aBgLyZ4RQy4J6A4H45POedNuqfSJoTZASSEuWk/5RhX0OB/LkwZh+QCBfcl5DfXU7BMjVXifuF1MBeRZMDaQ9XMAdkDrpZTCQbqGWBfYEYt9JgCBrxSkLJ1wggIC7Z7gDUih6FQYE5w6kn1+2gYGsLeENCFYXVAQHMrGcOyAZoi5IWWAg7VHcASmUdoGBHI/mDQj+LigN6AfkbD5nQDZIe2BAsiI4A4Lzk7CQQB7VcwakTNYFCCQtnTMg+YDuCANyIYczIOWyLlAgE475ApIj64IGUiTwBaRa1gUNRJvAFRDJReBgQMqKuQKCmYGGBwLyRzFPQOrEXTBApHdDvIu/IAdlXXBANrfzA6RI2gUJhLdXaLW0CxLIlQJ+gJRIu2CBHC/kBkie7HfBAtlVyQuQDFkXNBDdbD6AnJd1QQNZX8AHkGJZFzyQDC6AbJB1wQMRvcLzAKRK1kUBZOI2DoDkyroogCzN5AAIfpvQAqQtgwMgG2Vd8ECaB9kHgvsUagHySQ/7QHLlXRRADtWwD6RZ1kUDJLqUeSCb5V00QHZlMA9ksaKLBsjBFNaBYJdJrUBecGcdSJqyiwbICdanRVoUXVRAVhWwDaRO0UUF5FKh85ZOyz/P5ABIn6KLCkhzO9NA9qm6qIDsMzINBL9OaAVSVc4ykDZlFx2QdaUMA9mi7KID0lrFMJAsZRcdkPI8hoEcVHbRAYm+wi6QVmUXJZBkZtcOpyu7KIEcyGEXyHxlFyUQfwZHzpLr+5kFslXZRQskjNExWsI1gMfZBJKr7KIGgvtZq0P4+HV2gTQquyiBSK9HL6MCsojNMbowVRc1EPz1MwogjQ2MAlmh6qIGIr8gZpAQSA2bqSPeU3VRA5E/+NKoXwbfMQokU9VFDwT77EQCBPvwmAPYreqiByK/IvCu/JnYwSqQJlUXAxD8KyQBkGRmgWSruhiAYDdqpJgx5XNYBYJ9e8ICZLeqiwGI/I74e9KX+W5mgaDXzLMAmajqYgIif6T8X6luLQyCWaqqiwkI9u0BBxJdzCyQGlUXExDsoRoHsrSRWSDYJwlZgGxVdTEBkU9afyOZyWUXyG5VFxsQxcSp4mw6u0AWqroYgWAPyTiQ6G52gdSoupiBKKalExexC2S1qosZCOYcnZ+xC2SZqosZiGINvTeXXSAHVF3MQBTXJPhjd5/4A4llF4hi5hYRyHNsA6lWdTEDUU7dIn/6mNk7op2qLnYgCZ3qN6j8jcwCOazqYgeinMYn3mUWCHZjChYg61VdzECUr5BX1rILZJ2qixmI8lU++jy7QLCHaXiADEWyC0Q5ZQ8PEMWkPRxA4rCbdDEAaVZ1MQNRvkJOZBfIAlUXOxDVtD3XGAaywdGrBxeBpLELBPPyCAsQ/K4lLEAWH2IXCOaFigeIctKeo+wCwbw04gGinLTnKLtAMHsXcAFRvMiPP8ywf5ABEezLIy4g8jkrREvZM9gFonxLwwdEuYQ6I4NhIJjNU/iAKB/aS9nDLpDDqi5nApKczTCQraoubiBpDAPZpOriBlJWzDCQfaou5wOSX8gwkElGZwNysJBlIIcUXdxAbk1iGYhi6V7eQG5GMAzkMUUXN5D7xzAM5FH1lJq8gDQcYxfI60+ou7iBPNDFLpA9inU13EDuH2AYyEXV6klOIA07GAYyX7F+lhvIg1EMTww1qoVN3EDuP8IukJzHnRzIjXhmgbQblT/PDeTBcYwCSY8yqn+eFcgfT7ALZICmnUJuIDeSmQUyTKOykRvI04+yC2ScSrNGbiDfPMDynXKa1lZuII+9wzCQR2k0aOcG8vnDDAOZQqGzXG4gN8YOYL1rktZmbiA3jjLMBEn7em4gjzH9P7XCyMsN5LFIxoEYi7mBPPEw80COFnID+Xt4P+aBRHMDeYV9IOUF3ECeYB9I61JuIDemsR8gRm4gN6azD+RPXWD/B6MQBB/yyITMAAAAAElFTkSuQmCC",
                    "content_data": None,
                    "mime_type": "image/png"
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
        return alpaca.requestAlpaca("POST", "/v1/accounts", data)


    @staticmethod
    def connect_ach(id):
        data = {
            "account_owner_name": "Condescending Gagarin",
            "bank_account_type": "CHECKING",
            "bank_account_number": "32131231abc",
            "bank_routing_number": "123103716",
            "nickname": "Bank of America Checking"
        }
        return alpaca.requestAlpaca("POST", f"/v1/accounts/{id}/ach_relationships", data)

    @staticmethod
    def transfer(id, relation_id):
        data = {
            "transfer_type": "ach",
            "relationship_id": relation_id,
            "amount": "1234.56",
            "direction": "INCOMING"
        }
        return alpaca.requestAlpaca("POST", f"/v1/accounts/{id}/transfers", data)

    @staticmethod
    def makeOrder(id):
        data = {
            "symbol": "AAPL",
            "qty": 1,
            "side": "buy",
            "type": "market",
            "time_in_force": "day"
        }
        return alpaca.requestAlpaca("POST", f"/v1/accounts/{id}/orders", data)

    @staticmethod
    def get_account(id):
        return alpaca.requestAlpaca("GET", f"/v1/accounts/{id}")
