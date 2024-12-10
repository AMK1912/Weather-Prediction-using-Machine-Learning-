import requests
import os
from dotenv import load_dotenv


load_dotenv()

def test_Api_key():
    api_key = os.getenv("OPENWEATHER_API_KEY")
    city = "London"

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print("API key is valid! Current Weather in London:")
            print(f"Temperature: {data['main']['temp']}°C")
            print(f"Humidity: {data['main']['humidity']}%")
            print(f"Description: {data['weather'][0]['description']}")

        else:
            print(f"API key is invalid. Status code: {response.status_code}")
            print(response.json())
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    test_Api_key()