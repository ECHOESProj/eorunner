from app.init import get_env, get_path
import requests
import json
import pprint
import logging

baseUrl = get_env('EOService_RestUrl')
username = get_env('EOService_Username')
password = get_env('EOService_Password')

def login():
    url = f'{baseUrl}/api/TokenAuth/Authenticate'
    body = {'userNameOrEmailAddress': username, 'password': password}
    headers = {'content-type': 'application/json'}
    response = requests.post(url, data=json.dumps(body), headers=headers)
    token = response.json()["result"]["accessToken"]
    return token


def get_jobs():
    token = login()
    r = requests.get(f'{baseUrl}/api/services/app/Job/GetAll?Active=true', headers={'Authorization': f'Bearer {token}'})
    return r.json()["result"]["items"]


def main():
    jobs = get_jobs()

    for job in jobs:
        logging.info("============== Job ==============")
        pprint.plogging.info(job)

if __name__ == "__main__":
    main()
