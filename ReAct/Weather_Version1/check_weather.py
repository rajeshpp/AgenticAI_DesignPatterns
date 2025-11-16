from random import choice

def get_weather(city):
    weather_data = {"Hyderabad": "Sunny, 32°C", "Delhi": "Sunny, 31°C", "Bangalore": "Rainy, 25°C", "Mumbai": "Cloudy, 29°C"}
    return weather_data.get(city, "Unknown")

def react_agent(user_input):
    print(f"User: {user_input}")

    # Reason
    if "weather" in user_input:
        reasoning = "I should check the weather data."
        print("Reasoning:", reasoning)

        # Act
        observation = get_weather("Hyderabad")
        print("Action: Fetch weather → Observation:", observation)

        # Reason again
        final_response = f"The weather in Hyderabad is {observation}. Based on that, no umbrella needed today."
        print("Response:", final_response)

react_agent("What’s the weather in Hyderabad?")
