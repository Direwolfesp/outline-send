#! /usr/bin/env python3

import json
import argparse
from subprocess import run, PIPE
from os import chdir, getcwd, getenv, listdir, mkdir, path, rmdir
from sys import exit, stdout, stderr, argv 
from typing import Any, NoReturn, TextIO
from requests import get, post
from urllib3 import request, PoolManager

RED = '\033[31m'
BLUE = '\033[38;5;31m'
YELLOW = '\033[33m'

RESET = '\033[0m'
FINISH = '   ' + BLUE + '\u2714' + RESET
PROMPT: str = YELLOW + "::" + RESET
ERROR: str = "[" + RED + "ERROR" + RESET + "]:"

API_UPDATE = "api/documents.update"

class Main:
    def __init__(self, arg_list: list[str]) -> None:

        # the whole json dump
        self.config_data: dict[str, Any] = self.load_config(arg_list[0])
        if not self.config_data:
            print(f"{ERROR} Failed to load configuration.")
            exit(-1)

        # get append parameter from arg list
        self.append = arg_list[1]

        # get unique outline api token
        self.api_key: str = self.config_data["outline_api"]
        if not self.api_key:
            print(f"{ERROR} No outline API key provided")
            exit(-1)
        

        # get the array of connections
        entry_list: list[dict[str, str]] = self.config_data["data"]
        
        # process each connection
        for entry in entry_list:
            self.process_entry(entry)

    def load_config(self, config_file: str) -> dict[Any, Any]:
        try:
            with open(config_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"{ERROR} Configuration file {config_file} not found.")
        except json.JSONDecodeError:
            print(f"{ERROR} Invalid JSON format in {config_file}.")
        return None

    # manages the full process of retreiving and sending the content
    # uses the same api key
    def process_entry(self, entry: dict[str, str]) -> None:
        # get url and folder uid
        self.source_url: str = entry["source"]
        self.folder_uid: str = entry["destination"].split("/")[-1]

        if not self.source_url or not self.folder_uid:
            print(f"{ERROR} Missing source or destination in entry: {entry}")
            return

        # we need to get the domain outline api url
        temp: list(str) = entry["destination"].split("/")[:-2] # sanitize domain
        temp += "/" + API_UPDATE  # add the desire api path

        self.api_url: str = ''.join(str(word) for word in temp)
        self.api_url = self.api_url.replace("https:", "https://") 

        # now we got everything, source, uuid and api_url

        # - get content from source_url
        if self.getContent():
            print(f"{PROMPT} Sending content to {entry["destination"]}")

            ## pushing content to outline
            title: str = self.request()
            print(f"{FINISH} Content sent succesfully to {title}")
        else:
            print(f"{ERROR} Couldn't retrieve content from {self.source_url}. Omiting request.")

    # asumes every other variable is correct
    # returns a string with the document title if success
    def request(self) -> str:
        payload: dict[Any, Any] = {
            "id": self.folder_uid,
            "text": self.content,
            "append": self.append,
            "publish": True
        }

        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            response = post(
                self.api_url, json=payload, headers=headers 
            ).json()

            # handle error response
            if response["status"] != 200:
                output: TextIO = stderr
                output.write(f"{ERROR} {response["message"]}\n")
                output.write(f"Returned with status code {response["status"]}")
                output.flush()
                exit(-1)
            
            # return document name 
            return response["data"]["title"] if "data" in response and "title" in response["data"] else None
            
        except Exception as e:
            print(f"{ERROR} Exception ocurred while making request: {e}")
            exit(-1)

    # download markdown from the source url
    # url MUST contain raw text content 
    def getContent(self) -> bool:
        status: bool = False
        http = PoolManager()
        print(f"{PROMPT} Started getting content from {self.source_url}...")
        response = http.request("GET", self.source_url)

        if response.status == 200:
            self.content = response.data.decode("utf-8")
            print(f"{FINISH} Markdown content downloaded successfully.")
            status = True
        return status


if __name__ == "__main__":
    # Initialize arg parse object
    parser = argparse.ArgumentParser(
        prog='outline_send.py', 
        description="Send multiple files to Outline documents. Each file is stored in a raw url link."
    )

    # add file flag
    parser.add_argument(
        '-f', '--file', type=str, required=True,
        help='Path to the config JSON file.'
    )

    # add append flag
    parser.add_argument(
        '-a', '--append', action='store_true',
        help='If enabled, appends content to the end of the document instead of replacing it.'
    )
    args = parser.parse_args()
    
    Main(arg_list=[args.file, args.append])
