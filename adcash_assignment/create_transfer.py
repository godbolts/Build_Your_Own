import requests

api_url = "http://localhost:5000/transfer"

amount = input("Please enter the amount you want to transfer: ")

try:
    amount_eur = round(float(amount), 2)
    data = {"amount_eur": amount_eur}
    response = requests.post(api_url, data=data)
    response.raise_for_status()
    print(response.status_code)
    print(response.json())

except ValueError:
    print("Please provide a valid amount of euros.")

except requests.exceptions.RequestException as e:
    print(f"Error making the request: {e}")
