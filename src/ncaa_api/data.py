import json

import requests
import debug

BASE_URL = "http://site.api.espn.com/apis/site/v2/sports/hockey/mens-college-hockey/"
STATUS_URL = BASE_URL + 'scoreboard'

#SCHEDULE_URL = BASE_URL + 'undefined'
#TEAM_URL = 'undefined'.format(BASE_URL)
#OVERVIEW_URL = BASE_URL + 'undefined'
#CURRENT_SEASON_URL = BASE_URL + 'undefined'
#STANDINGS_URL = BASE_URL + 'undefined'
REQUEST_TIMEOUT = 5


#def get_schedule(year, month, day):
#    try:
#        data = requests.get(SCHEDULE_URL.format(year, month, day), timeout=REQUEST_TIMEOUT)
#        return data
#    except requests.exceptions.RequestException as e:
#        raise ValueError(e)

#def get_teams():
#    try:
#        data = requests.get(TEAM_URL, timeout=REQUEST_TIMEOUT)
#        return data
#    except requests.exceptions.RequestException as e:
#        raise ValueError(e)


#def get_overview(game_id):
#    try:
#        data = requests.get(OVERVIEW_URL.format(game_id), timeout=REQUEST_TIMEOUT)
#        # data = dummie_overview()
#        return data
#    except requests.exceptions.RequestException as e:
#        raise ValueError(e)

def get_game_status():
    try:
        data = requests.get(STATUS_URL, timeout=REQUEST_TIMEOUT)
        return data
    except requests.exceptions.RequestException as e:
        raise ValueError(e)


#def get_current_season():
#    try:
#        data = requests.get(CURRENT_SEASON_URL, timeout=REQUEST_TIMEOUT)
#        return data
#    except requests.exceptions.RequestException as e:
#        raise ValueError(e)
#
#
#def get_standings():
#    try:
#        data = requests.get(STANDINGS_URL, timeout=REQUEST_TIMEOUT)
#        return data
#    except requests.exceptions.RequestException as e:
#        raise ValueError(e)
#
### DEBUGGING DATA (TO DELETE)
#def dummie_overview():
#    with open('dummie_nhl_data/overview_reg_final.json') as json_file:
#        data = json.load(json_file)
#        return data
