#! /usr/bin/env python3

from subprocess import run, PIPE
from os import chdir, getcwd, getenv, listdir, mkdir, path, rmdir
from sys import exit, stdout, stderr, argv 
from typing import Any, NoReturn, TextIO
from requests import get, post
from urllib3 import request, PoolManager

API_UPDATE = "api/documents.update"
TARGET_FILE = "https://raw.githubusercontent.com/emudev-org/discord-resources/refs/heads/main/emudev_resources_general.md"



class Main:
    def __init__(self, url: str) -> None:
        self._api_key: str | None = getenv("OUTLINE_API_KEY") # get api key

        if self._api_key == None:
            print("[ERROR]: Make sure to add your outline API key as a env var.")
            print(f"OUTLINE_API_KEY=\"account_token\"")
            exit(-1)

        self._uid: str = url.split("/")[-1] # strip uuid from url

        parsed_url: list(str) = url.split("/")[:-2] # get base domain 
        parsed_url += "/" + API_UPDATE # append api domain

        self._outline_url = ''.join(str(word) for word in parsed_url) # conver to string
        self._outline_url = self._outline_url.replace("https:", "https://") # fix url

        self._target_file = TARGET_FILE
        self._markdown: str = "" 

        # if we are able to get content
        if self.getContent():
            ### do the thing ###
            docName: str = self.request()

            print(f"Succesfully sent message: {self._markdown}")
            print(f"to document: {docName}")
        else:
            print(f"[ERROR] Failed to retreive target content from url.")
            exit(-1)

    # gets markdown content from raw url and stores in it self._markdown
    def getContent(self) -> bool:
        status: bool = False;
        http = PoolManager()
        print(f"Started getting markdown content...")
        response = http.request("GET", self._target_file)

        if response.status == 200:
            self._markdown = response.data.decode('utf-8')
            print(f"Markdown content downloaded succesfully.")
            print(f"{self._markdown}")
            status = True
        return status

    # assumes every variable is set correctly
    # returns String with the document title
    def request(self) -> str:
        payload: dict[Any, Any] = {
            "id": self._uid,
            "text": self._markdown,
            "append": False,
            "publish": True
        }

        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}"
        }

        # make api request
        print(f"Making send request to outline API")
        response = post(
            self._outline_url, json=payload, headers=headers
        ).json()

        # handle error response
        if response["status"] != 200:
            output: TextIO = stderr
            output.write(f"[ERROR]: {response["message"]} \n")
            output.write(f"Returned with status code {response["status"]}\n")
            output.flush()
            exit(-1)
        
        # return doc name if success
        return response["data"]["title"]
            
        

if __name__ == "__main__":
    # some vars may be pass as arguments to main
    
    url: str | None = None # app domain
    argc: int = len(argv)  

    # only accepts 1 param for now
    if argc == 2:
        url = argv[1]
      
        # Run
        Main(url = url)
    else:
        #print("Repo is up to date...")
        print(f"Usage: \n$ {path.basename(__file__)} https://docs.chiren.xyz/doc/UUID ")
        exit(-1)
        
