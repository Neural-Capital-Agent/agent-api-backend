import httpx  

class Supabase:
    def __init__(self, url: str, key: str):
        self.url = url
        self.key = key

    async def fetch_data(self, table: str):
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json"
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.url}/rest/v1/{table}", headers=headers)
            response.raise_for_status()
            return response.json()
            
    async def insert_data(self, table: str, data: dict):
    
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.url}/rest/v1/{table}", headers=headers, json=data)
                response.raise_for_status()
                return response
        except httpx.HTTPError as e:
            print(f"Error inserting data into {table}: {e}")
            return {"error": str(e), "details": e.response.text if e.response else "No response"}

    async def add_user(self, user_data: dict):
        return await self.insert_data("users", user_data)