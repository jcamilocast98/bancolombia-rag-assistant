import os
import asyncio
from anthropic import AsyncAnthropic
from dotenv import load_dotenv

load_dotenv()

async def test_direct():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    print(f"API Key length: {len(api_key) if api_key else 'None'}")
    if api_key:
        print(f"API Key starts with: {api_key[:7]}...")
    
    client = AsyncAnthropic(api_key=api_key)
    
    models_to_try = [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-haiku-20240307"
    ]
    
    for model in models_to_try:
        print(f"\n--- Probando modelo: {model} ---")
        try:
            message = await client.messages.create(
                model=model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hola"}]
            )
            print(f"Exito con {model}!")
            print(f"Respuesta: {message.content[0].text}")
            break
        except Exception as e:
            print(f"Error con {model}: {e}")

if __name__ == "__main__":
    asyncio.run(test_direct())
