import requests

url = "http://localhost:8000/api/metrics/overview"

if __name__ == "__main__":
    response = requests.get(url)
    print(f"Status code: {response.status_code}")
    print("JSON response:")
    print(response.json())
