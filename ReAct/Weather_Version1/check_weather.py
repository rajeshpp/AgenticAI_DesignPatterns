from random import choice

def get_weather(city):
    weather_data = {"Delhi": "Sunny, 31°C", "Bangalore": "Rainy, 25°C", "Mumbai": "Cloudy, 29°C"}
    return weather_data.get(city, "Unknown")

def react_agent(user_input):
    print(f"User: {user_input}")

    # Reason
    if "weather" in user_input:
        reasoning = "I should check the weather data."
        print("Reasoning:", reasoning)

        # Act
        observation = get_weather("Delhi")
        print("Action: Fetch weather → Observation:", observation)

        # Reason again
        final_response = f"The weather in Delhi is {observation}. Based on that, no umbrella needed today."
        print("Response:", final_response)

react_agent("What’s the weather in Delhi?")
