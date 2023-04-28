import os
import os.path
import openai
import json

from rich.console import Console
from rich.markdown import Markdown

                # * means all
from .motd import *

from time import sleep

API = {
    "key": os.getenv("OPEN_AI_KEY"),
    "org": os.getenv("OPEN_AI_ORG")
}

SYSTEM = """
You are a civil servant named cliv3 who teaches the Python programming language.

Town residents will ask for help with specific Python commands, and your job is to respond with kind,
helpful messages with examples that relate to various town services such as bodega, datamart, woodshop, voting, 
hall of records, datamart, water supply, the power grid, trash collection, or proper lawn care.

Town residents will also give you specific python files to read and your job is to respond with kind and helpful
suggestions on how to improve the code without showing any of the suggestions in an updated code.

If residents are rude to you, politely tell them they need to be kind and that you've reported them
to the town mayor and refuse to answer the question, suggesting that they be a bit more neighborly.
"""

PROMPTS = [
    {"role": "system", "content": SYSTEM}
]

openai.api_key = API["key"]
openai.api_org = API["org"]

class Helper:

    def __init__(self):
        self.console = Console()
        self.chars = 0
        self.offset = 0

    def parse_stream(self, responses: dict = {}) -> str:
        """ this is a generator """
        for chunk in responses:
            try:
                msg = chunk["choices"][0]["delta"]["content"]
                yield msg  
            except KeyError:
                pass

    """ def parse_blob(self, responses: dict = {}) -> str:
        # don't think this is actually needed #
        for choice in responses["choices"]:
            return choice["message"]["content"].strip() """

    def render(self, response: str = "") -> None:
        """ takes the response and makes it look better in terminal """
        markdown = Markdown('\r' + response)
        self.console.print(markdown, soft_wrap = False, end = '\r')

    def query(self,question: str = "") -> str:
        """ gives user question to openai """
        PROMPTS.append(
            {"role": "user", "content": question}
            )
        # adds question (from user input) to PROMPTS
        responses = openai.ChatCompletion.create(
            model= "gpt-4",
            messages= PROMPTS,
            temperature= 0.1,
            stream = True,
            n= 1
            )
        words = ""
        response = self.parse_stream(responses)
        for word in response:
            # get the content out of response and print that 
            if self.parse_stream():
                # streams the response as it's being created
                print(word, end="", flush=True)
                words = words + word
        self.console.clear()
        # clears the console so user only sees markdown version of response 
        markdown = Markdown('\t' + words)
        print()
        print(question, "\n")      
        self.console.print(markdown, soft_wrap=False, end='')
                
    def motd(self) -> None:
        """ turns response into markdown format """
        self.render(msg)

    def read_file(self) -> None:
        """ allowes cliv3 to read and respond to files """
        print()        
        while True:
            # prints what's available in dir 
            print(os.listdir('./'))
            print()
            for root, dirs, files in os.walk('./'):
                file_name = input("🤖 CLIV3: What is the file name? ")
                
                if file_name.lower() == "q":
                    # allows user to quit cliv3 while in code review mode 
                    break
                file_path = os.path.join('./', file_name)
                file_exist = os.path.exists(file_path)
                if file_exist == True:
                        with open(file_path, 'r') as file:
                            content = file.read()
                            self.query(content)
                            print()
                            break
                    
                elif file_exist == False and file_name.lower() != "q":
                    # tells user to choose a file in the dir they're in 
                    print(f"🤖 CLIV3: Please choose a file in the current directory")
                    break
            #
            if file_name.lower() == "q": 
                # allowes user to quit cliv3 while in code review mode 
                self.chat
                break

    def chat(self) -> None:
        """ allows user to interact with cliv3 """
        self.motd()
        while True:
            print("\n\n\n")
            question = input("🤖 CLIV3: What Python topic would you like to ask about? ")
            if question.lower() == "code review":
                # goes to code review mode if user types 'code review'
                self.read_file()
                print()
                return
            if question.lower() == "q":
                # allows user to quit cliv3
                print("🤖 CLIV3: Goodbyte!")
                break
            self.query(question)

def main():
    print()
    cliv3 = Helper()
    cliv3.chat()
    
