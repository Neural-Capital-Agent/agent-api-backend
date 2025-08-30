import httpx  

class supabase:
    def __init__(self, url: str, key: str):
        self.url = url
        self.key = key

    async def fetch_data(self, table: str):
        headers = {
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json"
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.url}/rest/v1/{table}", headers=headers)
            response.raise_for_status()
            return response.json()
            
    async def insert_data(self, table: str, data: dict):
        email = data.get('mail', '')
        password = data.get('password', '')
        return ''
        headers = {
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json"
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.url}/rest/v1/{table}", headers=headers, json=data)
            response.raise_for_status()
            return response.json()