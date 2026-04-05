import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_chat(message):
    print(f"\n> User: {message}")
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"message": message, "session_id": "test-session-context-fix"},
        headers={"X-API-Key": "mi-api-key-segura-123"}
    )
    if response.status_code == 200:
        data = response.json()
        reply = data.get('reply')
        print(f"< Assistant: {reply}")
        if data.get('sources'):
            print(f"Sources: {data.get('sources')}")
        return data
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

if __name__ == "__main__":
    print("Reproduction Test: Context and Tool Stability")
    
    # 1. Simple greeting to establish session
    test_chat("hola")
    
    time.sleep(2)
    
    # 2. Complex question that requires RAG
    print("\nAsking about mortgage debt negotiation...")
    result = test_chat("hola, quisiera saber como puedo negociar una deuda de credito hipotecario.")
    
    # Validation logic
    if result and result.get('reply') and "Bancolombia" in result.get('reply') and len(result.get('reply')) > 200:
        print("\nSUCCESS: Assistant returned a detailed, context-aware answer.")
    elif result and result.get('reply') and "¡Hola!" in result.get('reply') and len(result.get('reply')) < 100:
        print("\nFAILURE: Assistant returned a generic greeting instead of searching.")
    else:
        print("\nUNSURE: Please check the content manually.")
