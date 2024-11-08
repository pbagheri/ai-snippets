#Hi everyone!
#Below is an example of calling multiple functions using the function call capability of GPT. I hope you find it useful.


from dotenv import load_dotenv
import openai
import math
import os
import requests
import json

os.chdir('path-to-your-folder-containing-your-.env-file')


load_dotenv()


# Define the base URL for the weather API
base_url = "http://api.weatherapi.com/v1"
api_method = "/current.json"
weather_api_key = os.environ.get('WEATHER_API_KEY')


def get_temp(location):
    parameters = {
        "key": weather_api_key,
        "q": location
    }
    response = requests.get(base_url + api_method, params=parameters)
    data = response.json()
    temp = data['current']['temp_c']
    print('This temp function is called')
    return temp


def calc_sine(angle):
    print('This sine function is called')
    return math.sin(angle)


def max_of(*a):
    print('This max function is called')
    return max(*a)


# Map function names to actual functions
function_map = {
    "get_temp": get_temp,
    "calc_sine": calc_sine,
    "max_of": max_of
}

# Define the tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "calc_sine",
            "description": "Calculate the sine of an angle. Do this whenever an angle is provided by the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "angle": {
                        "type": "number",
                        "description": "An angle in radians.",
                    },
                },
                "required": ["angle"],
                "additionalProperties": False,
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_temp",
            "description": "Get the temperature of a location. Do this whenever a location is provided by the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "A location, e.g. 'San Francisco'.",
                    },
                },
                "required": ["location"],
                "additionalProperties": False,
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "max_of",
            "description": "Find the maximum of a list of numbers. Do this whenever a list of numbers is provided by the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "array",
                        "items": {
                            "type": "number",
                        },
                        "description": "A list of numbers.",
                    },
                },
                "required": ["a"],
                "additionalProperties": False,
            },
        }
    }
]

# Main function to run a function via GPT
def run_func_via_gpt(text):
    messages = [
        {"role": "system", "content": "You are a knowledgeable assistant. You can retrieve information from the \
        messages and provide it to the appropriate function. When the info is not there, you do not need to call \
        the function. However, if there is a request that you can answer without using the functions, you can do so.\
        Bear in mind that if there is a function for the request, you should definitely use the function."},
        {"role": "user", "content": text}
    ]

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
        tool_choice='auto'
    )

    # Access all tool calls in the response
    tool_calls = response.choices[0].message.tool_calls
    if tool_calls is None:
        print(response.choices[0].message.content)
        return response.choices[0].message.content
    else:
        # List to store individual function results
        tool_result_messages = []
        for tool_call in tool_calls:
            arguments = json.loads(tool_call.function.arguments)
            func_name = tool_call.function.name
            args = list(arguments.values())

            # Execute the function based on its name
            result = function_map[func_name](*args)

            # Create a message with the result of each function call, with its tool_call_id
            tool_result_message = {
                "role": "tool",
                "content": json.dumps({"result": result}),
                "tool_call_id": tool_call.id  # Reference each tool_call_id separately
            }
            tool_result_messages.append(tool_result_message)

        # Prepare final message payload with function results
        final_payload = [
                            {"role": "system",
                             "content": "You are an assistant. You generate responses based on the provided info in the results"},
                            {"role": "user", "content": text},
                            response.choices[0].message
                        ] + tool_result_messages

        final_response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=final_payload,
        )
        final_result = final_response.choices[0].message.content
        return final_result

# Example calls
run_func_via_gpt('What is the temperature in Rio de Janeiro?')
run_func_via_gpt('What is the cosine of 3.14?')run_func_via_gpt('What is the maximum of 34, 7, 56.8, 1.2, 8?')

print(run_func_via_gpt("What is the sine of 6.28 and the temperature in Rio de Janeiro?"))
print(run_func_via_gpt("What is the maximum of 34, 7, 56.8, 1.2, 8 and the temperature in Rio de Janeiro?"))
