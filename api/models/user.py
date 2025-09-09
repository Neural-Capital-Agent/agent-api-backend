from typing import Optional

class User:
    def __init__(
        self,
        email: Optional[str],
        phone: str,
        street_address: str,
        city: str,
        state: str,
        postal_code: str,
        given_name: str,
        family_name: str,
        date_of_birth: str,
        country_of_citizenship: str,
        country_of_birth: str,
        tax_id: str,
        contact_given: str,
        contact_family: str,
        contact_email: str,
        password: str,
        id: Optional[str] = None
    ):
        self.id = id
        self.email = email
        self.phone = phone
        self.street_address = street_address
        self.city = city
        self.state = state
        self.postal_code = postal_code
        self.given_name = given_name
        self.family_name = family_name
        self.date_of_birth = date_of_birth
        self.country_of_citizenship = country_of_citizenship
        self.country_of_birth = country_of_birth
        self.tax_id = tax_id
        self.contact_given = contact_given
        self.contact_family = contact_family
        self.contact_email = contact_email
        self.password = password
