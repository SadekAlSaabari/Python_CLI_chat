from openai import OpenAI
import os
import dotenv
import json

#function for calculating token cost based on cost of using the OpenAI GPT-4.1 Mini model
def calc_cost(input_tokens, output_tokens):
    input_cost = (input_tokens / 1000000) * 0.4
    output_cost = (output_tokens / 1000000) * 1.6
    return input_cost + output_cost

#load the json file containing the conversation termination function
with open('tools.json', 'r', encoding='utf-8') as file:
    my_tools = json.load(file)

#load API key and base URL
dotenv.load_dotenv()
client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY"),
    base_url = os.getenv("OPENAI_BASE_URL")
)

# Will contain the Conversation ID for OpenAI to keep track of the conversation history
conv_id = ""
end_conv = False

# Conversation loop
while True:
    print("Enter a message:")
    message = input()

    if conv_id == "":
        response = client.responses.create(
            model = "gpt-4.1-mini",
            input = message,
            tools = my_tools,
            instructions = "You are an helpful assistant for a simple CLI chat. Only respond with text messages. Get creative with the answers!"
        )
    else:
        response = client.responses.create(
            model="gpt-5.1",
            input = message,
            tools = my_tools,
            instructions="You are an helpful assistant for a simple CLI chat. Only respond with text messages. Keep answers concise, but get creative!",
            previous_response_id = conv_id
        )
    conv_id = response.id

    for item in response.output:
        if item.type == "function_call":
            args = json.loads(item.arguments)
            end_conv = args["enabled"]
            if end_conv:
                print(item.call_id)

    print("You: " + message)
    print("Assistant: " + response.output_text)
    print("Cost: $" + str(calc_cost(response.usage.input_tokens, response.usage.output_tokens)))

    if end_conv == True:
        break