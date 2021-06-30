import requests
import json

class Dad_Jokes():
    def __init__(self):
        self.headers = {"Accept": "application/json"}
        self.baseurl = "https://icanhazdadjoke.com/"

    def get_joke(self):
        return requests.get(self.baseurl, headers=self.headers).json().get("joke")
        

def main():
    print(Dad_Jokes().get_joke())
    
    
if __name__ == '__main__':
    main()