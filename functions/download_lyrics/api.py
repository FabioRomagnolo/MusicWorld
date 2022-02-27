import os
import jwt
import json
from json import JSONDecodeError
import requests


class Api(object):
    def __init__(self, verbose=True):
        # ATTENTION! In order to access backend resources a valid Json Web Token must be setted first
        self.token = jwt.encode({'user': 'Music World - Cloud Functions - download_lyrics'},
                                os.environ['FLASK_SECRET_KEY'], algorithm="HS256")
        self.verbose = verbose
        if self.verbose is True:
            print("--- JWT token setted for authorized requests: ", self.token)
        self.baseURL = os.environ.get('BACKEND_BASEURL', "http://127.0.0.1:5000/api/v1")

    def get(self, url, params=None, headers=None):
        if headers is not None:
            headers['Authorization'] = 'Bearer '+self.token
        else:
            headers = {'Authorization': 'Bearer '+self.token}
        r = requests.get(url=url, params=params, headers=headers)
        try:
            data = r.json()
        except (JSONDecodeError, ValueError):
            data = None
        if self.verbose:
            # print("--- GET STATUS CODE: ", r.status_code, r.text)
            print("--- GET STATUS CODE: ", r.status_code)
        return data

    def post(self, url, params=None, headers=None, data=None):
        if headers is not None:
            headers['Authorization'] = 'Bearer '+self.token
        else:
            headers = {'Authorization': 'Bearer '+self.token}
        r = requests.post(url=url, params=params, headers=headers, data=data)
        if self.verbose:
            print("--- POST STATUS CODE: ", r.status_code)
        return r.status_code

    def delete(self, url, params=None, headers=None):
        if headers is not None:
            headers['Authorization'] = 'Bearer ' + self.token
        else:
            headers = {'Authorization': 'Bearer ' + self.token}
        r = requests.delete(url=url, params=params, headers=headers)
        if self.verbose:
            print("--- DELETE STATUS CODE: ", r.status_code)
        return r.status_code

    def get_track(self, track_id):
        try:
            # GET request
            URL = self.baseURL + "/tracks/" + track_id
            return self.get(URL)
        except Exception as e:
            print(e)
            return None

    def get_track_genius(self, track_id):
        try:
            # GET request
            URL = self.baseURL + "/tracks/" + track_id + "/genius"
            return self.get(URL)
        except Exception as e:
            print(e)
            return None

    def post_track(self, track_id, name, lyrics):
        try:
            # GET request
            URL = self.baseURL + "/tracks/" + track_id
            headers = {'Content-type': 'application/json'}
            data = {
                'name': name,
                'lyrics': lyrics
            }
            json_data = json.dumps(data)
            return self.post(url=URL, headers=headers, data=json_data)
        except Exception as e:
            print(e)
            return None
