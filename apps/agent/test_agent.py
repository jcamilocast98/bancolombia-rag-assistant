import httpx
import asyncio

async def test():
    async with httpx.AsyncClient() as client:
        print("Enviando request a la API...")
        response = await client.post(
            "http://127.0.0.1:8000/api/v1/chat",
            json={"session_id": "test-1", "message": "¿Cuéntame qué es un crédito hipotecario de Bancolombia?"},
            headers={"X-API-Key": "mi-api-key-segura-123"},
            timeout=30.0
        )
        print("Status Code:", response.status_code)
        try:
            print("Response:", response.json())
        except:
            print("Response Text:", response.text)

if __name__ == "__main__":
    asyncio.run(test())
