import httpx
import asyncio

async def test_chat():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/api/v1/chat",
                json={
                    "message": "tengo dudas sobre como pagar mi credito de libre inversion",
                    "session_id": "test-session-user-report"
                },
                headers={"X-API-Key": "mi-api-key-segura-123"},
                timeout=60.0
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_chat())
