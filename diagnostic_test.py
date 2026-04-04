import requests
import json
import time

def test_chat():
    url = "http://localhost:8000/api/v1/chat"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "mi-api-key-segura-123"
    }
    payload = {
        "session_id": "test-session-diag",
        "message": "¿Qué tipos de cuentas de ahorro ofrece Bancolombia?"
    }

    print(f"Enviando petición a {url}...")
    try:
        start_time = time.time()
        response = requests.post(url, headers=headers, json=payload)
        end_time = time.time()
        
        print(f"Status Code: {response.status_code}")
        print(f"Tiempo: {end_time - start_time:.2f}s")
        print("Respuesta:")
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print(response.text)
            
    except Exception as e:
        print(f"Error de conexión: {e}")

if __name__ == "__main__":
    test_chat()
