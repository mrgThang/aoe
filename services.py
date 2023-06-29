import os

import requests
from dotenv import load_dotenv

from services_models import GameActionsReq, GameActionsResp, GameActionsStatusResp, GameStatusResp, GameResp

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ''))
load_dotenv(os.path.join(BASE_DIR, '.env'))


class Service:

    def __init__(self, game_id: int):
        self._game_id = game_id
        self._url = os.getenv('URL', '')
        self._token = os.getenv('TOKEN', '')
        self._headers = {
            'Content-Type': 'application/json',
            'Authorization': self._token
        }

    def get_game_with_game_id(self) -> GameResp:
        response = requests.get(self._url + f"/games/{self._game_id}",
                                headers=self._headers)
        return GameResp(**response.json())

    def get_game_status_with_game_id(self) -> GameStatusResp:
        response = requests.get(self._url + f"/games/{self._game_id}/status",
                                headers=self._headers)
        return GameStatusResp(**response.json())

    def get_game_actions_with_game_id(self) -> GameActionsResp:
        response = requests.get(self._url + f"games/{self._game_id}/actions",
                                headers=self._headers)
        return GameActionsResp(**response.json())

    def post_game_actions(self, game_actions_req: GameActionsReq) -> GameActionsStatusResp:
        data = game_actions_req.dict()
        response = requests.post(self._url + f"/games/{self._game_id}/actions",
                                 json=data,
                                 headers=self._headers)
        return GameActionsStatusResp(**response.json())
