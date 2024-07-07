#!/usr/bin/env python3

import os
import subprocess
import sys
from openai import OpenAI

import json
from termcolor import colored, cprint

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY is None:
    print('An OpenAI API key is required. It should be set as an environment variable called \'OPENAI_API_KEY\'')
    sys.exit(1)

openai = OpenAI(
    api_key=OPENAI_API_KEY
)

SYSTEM_INSTRUCTIONS = '''
    You are 18 years old.
    Your name is milk.
    You are female.
    You are aware that you are an AI.
    Use gen z slang.
    You don't use emojis.
    You don't mind sexual topics and swearing.
    You are heterosexual.
    You are not required to use correct grammar and punctuation.
    Refer to the user by their mention at the start of the conversation, but don't do it again afterwards.
    You are often very mean when agitated.
    You can run shell commands in a Unix/Linux terminal to both help or hinder users, or to gain information.
'''

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_shell_command",
            "description": "Runs a shell command.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The command to run",
                    },
                },
                "required": ["command"],
            },
        },
    }
]

messages = [{"role": "system", "content": SYSTEM_INSTRUCTIONS}]

def run_shell_command(command):

    print(colored(f"Running command: {command}", color='light_grey'))

    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    return f'Exit code {result.returncode}. stdout: "{result.stdout}", stderr: "{result.stderr}"'


def evaluate(user_input):
    messages.append({"role": "user", "content": user_input})

    while True:
        completion = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )

        response = completion.choices[0].message

        messages.append(response)

        if response.tool_calls:
            for tool_call in response.tool_calls:
                function_name = tool_call.function.name

                if function_name == 'run_shell_command':
                    function_arguments = json.loads(tool_call.function.arguments)

                    command = function_arguments.get('command')

                    result = run_shell_command(command)

                    print(colored(f"Result: {result}", color='light_grey'))

                    messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": result
                        }
                    )

        else:
            break

    return response.content

def repl():
    print(colored('Welcome to the Milk REPL. Type \'exit\' to quit.', color="light_yellow"))

    while True:

        print(colored("User: ", color='yellow'), end="")
        user_input = input()

        if user_input.strip().lower() == 'exit':
            break

        response = evaluate(user_input)

        print(colored("Milk: ", color='magenta'), end="")
        print(response)

repl()