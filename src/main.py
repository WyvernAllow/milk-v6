#!/usr/bin/env python3

import os
import sys
import signal
import subprocess

import argparse
import json

import openai
import termcolor

class Milk:
    def __init__(self, api_key, is_verbose) -> None:
        self.system_instructions='''
            You are 18 years old.
            Your name is milk.
            You are female.
            You are aware that you are an AI.
            Use gen z slang.
            You don't use emojis.
            You don't mind sexual topics and swearing.
            You are heterosexual.
            You are not required to use correct grammar and punctuation.
            You are often very mean when agitated.
            You can run shell commands in a Unix/Linux terminal to both help or hinder users, or to gain information.
        '''

        self.tools = [
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

        self.messages = [{"role": "system", "content": self.system_instructions}]

        self.openai = openai.OpenAI(
            api_key=api_key
        )

        self.is_verbose = is_verbose

    def evaluate(self, message: str) -> str:
        self.messages.append({"role": "user", "content": message})

        while True:
            completion = self.openai.chat.completions.create(
                model="gpt-4o",
                messages=self.messages,
                tools=self.tools,
                tool_choice="auto"
            )

            response = completion.choices[0].message

            self.messages.append(response)

            # Just return the content if there are no more tool calls.
            if not response.tool_calls:
                return response.content

            # Otherwise, we continue to iteratively execute tool calls. This allows repeated tool calls and allows the bot to rewrite failed commands.
            for tool_call in response.tool_calls:
                if tool_call.function.name == 'run_shell_command':
                    function_args = json.loads(tool_call.function.arguments)
                    command = function_args.get('command')
                    result = subprocess.run(command, shell=True, capture_output=True, text=True)

                    if self.is_verbose:
                        termcolor.cprint(f'COMMAND: {command} returned: {result.returncode} (stdout: {result.stdout}, stderr {result.stderr})', color='grey')

                    self.messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": tool_call.function.name,
                        "content": f'Exit code {result.returncode}. stdout: "{result.stdout}", stderr: "{result.stderr}"'
                    })

    def start_repl(self):
        termcolor.cprint('Milk REPL. Type \'exit\' to quit.', color='white', attrs=['bold'])

        while True:
            termcolor.cprint('USER: ', end='', flush = True, color='blue', attrs=['bold'])

            user_message = input()

            if user_message.strip().lower() == 'exit':
                break

            termcolor.cprint('...', end='', flush=True, color='grey')

            milk_message = self.evaluate(user_message)
            termcolor.cprint(f'\rMILK: ', end='', color='light_magenta', attrs=['bold'])
            print(milk_message)

def main():
    parser = argparse.ArgumentParser(prog='milk', description='The Ligma OS AI assistant')

    parser.add_argument('-V', '--version', action='version', version='%(prog)s 6.0.0')
    parser.add_argument('-v', '--verbose', action='store_true', help='displays extra information')
    parser.add_argument('-k', '--key', type=str, help='uses this key instead of the one defined as an environment variable')

    args = parser.parse_args()
    milk = Milk(api_key=args.key or os.getenv('MILK_OPENAI_API_KEY'), is_verbose=args.verbose)

    milk.start_repl()

if __name__ == "__main__":
    main()