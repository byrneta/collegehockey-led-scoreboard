from PIL import Image, ImageDraw, ImageFont
try:
    # Real hardware driver (built from submodules/rpi-rgb-led-matrix on a Raspberry Pi).
    from rgbmatrix import RGBMatrix, RGBMatrixOptions
    USING_EMULATOR = False
except ImportError:
    # Falls back to https://github.com/ty-porter/RGBMatrixEmulator for local development
    # on non-Pi machines (pip install RGBMatrixEmulator). Configure the display via
    # emulator_config.json (e.g. "display_adapter": "terminal") in this directory.
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions
    USING_EMULATOR = True
from datetime import datetime, date, timedelta
import requests
import json
import time
import math
import os.path
import colorsys
from functools import lru_cache

def getTeamData():
    """Create team names and abbreviations for NCAA Mens Hockey, return information as a dictionary.

    Returns:
        teams (dictionary): Contains the char6 name from NCAA API and three letter abbreviation of each NCAA team.
    """
    
    teams = {
        'AIRFOR' : "AFA" ,
        'AK ANC' : "AKA" ,
        'AK FBK' : "AKF" ,
        'AZ ST' : "ASU" ,
        'ARMY' : "ARM" ,
        'AUG SD' : "AUG" ,
        'BEMDJI' : "BMJ" ,
        'BENTLY' : "BEN" ,
        'BC' : "BC" ,
        'BU' : "BU" ,
        'BGSU' : "BGS" ,
        'BROWN': "BRN" ,
        'CANISI' : "CNS" ,
        'CLARKS' : "CLK" ,
        'COLGAT' : "CLG" ,
        'CO COL' : "CC" ,
        'UCONN' : "CON" ,
        'CORN' : "COR" ,
        'DART' : "DAR" ,
        'DENVER' : "DEN" ,
        'FERRIS' : "FSU" ,
        'HARV' : "HAR" ,
        'HOLYCR' : "HCR" ,
        'LK SUP' : "LSS" ,
        'LINWOD' : "LIN" ,
        'LIU': "LIU" ,
        'MAINE' : "MNE" ,
        'UMASS' : "UMA" ,
        'MERCYH' : "MRC" ,
        'MERMCK' : "MER" ,
        'MIA OH' : "MIA" ,
        'MICHST' : "MSU" ,
        'MITECH' : "MTU" ,
        'MICH' : "MIC" ,
        'MN DUL' : "MND" ,
        'MNSTMA' : "MNS" ,
        'MINN' : "MIN" ,
        'UNH' : "UNH" ,
        'NIAGRA' : "NIA" ,
        'NO DAK' : "NDK" ,
        'NOEAST' : "NOE" ,
        'N MICH' : "NMU" ,
        'N DAME' : "NDM" ,
        'OHIOST' : "OSU" ,
        'OMAHA' : "UNO" ,
        'PENNST' : "PSU" ,
        'PRINCE' : "PRI" ,
        'PROV' : "PRV" ,
        'QUINN' : "QUI" ,
        'RPI' : "REN" ,
        'RIT' : "RIT" ,
        'ROBMOR' : "ROB" ,
        'SACHRT' : "SAC" ,
        'SCSU' : "STC" ,
        'ST LAW' : "STL" ,
        'STTHOM' : "STT" ,
        'STONEH' : "STO" ,
        'UMASSL' : "UML" ,
        'UNION' : "UNI" ,
        'VERMNT' : "VER" ,
        'W MICH' : "WMU" ,
        'WISC' : "WIS" ,
        'YALE' : "YLE" 
    }

    return teams

def getSchoolAbbrMap():
    """Maps the rankings endpoint's "School" name strings to getTeamData()'s
    char6 abbreviations, so the rankings board can show team abbreviations
    (e.g. "MIA") instead of full school names (e.g. "Miami (OH)").

    Returns:
        dict: "School" string (as returned by getRankings()) -> char6
        abbreviation (a key of getTeamData()'s dictionary).
    """
    return {
        'Michigan': 'MICH',
        'North Dakota': 'NO DAK',
        'Michigan St.': 'MICHST',
        'Western Mich.': 'W MICH',
        'Denver': 'DENVER',
        'Dartmouth': 'DART',
        'Providence': 'PROV',
        'Minn. Duluth': 'MN DUL',
        'Penn St.': 'PENNST',
        'Quinnipiac': 'QUINN',
        'Cornell': 'CORN',
        'Wisconsin': 'WISC',
        'Minnesota St.': 'MNSTMA',
        'UConn': 'UCONN',
        'Augustana (SD)': 'AUG SD',
        'St. Thomas (MN)': 'STTHOM',
        'Massachusetts': 'UMASS',
        'Boston College': 'BC',
        'Merrimack': 'MERMCK',
        'Michigan Tech': 'MITECH',
        'Ohio St.': 'OHIOST',
        'Princeton': 'PRINCE',
        'Bentley': 'BENTLY',
        'Bowling Green': 'BGSU',
        'Maine': 'MAINE',
        'Union (NY)': 'UNION',
        'Northeastern': 'NOEAST',
        'Boston U.': 'BU',
        'Sacred Heart': 'SACHRT',
        'St. Cloud St.': 'SCSU',
        'Colorado Col.': 'CO COL',
        'Harvard': 'HARV',
        'Miami (OH)': 'MIA OH',
        'Clarkson': 'CLARKS',
        'Alas. Fairbanks': 'AK FBK',
        'Air Force': 'AIRFOR',
        'Lindenwood': 'LINWOD',
        'Holy Cross': 'HOLYCR',
        'Minnesota': 'MINN',
        'New Hampshire': 'UNH',
        'Arizona St.': 'AZ ST',
        'LIU': 'LIU',
        'Omaha': 'OMAHA',
        'RIT': 'RIT',
        'Army West Point': 'ARMY',
        'UMass Lowell': 'UMASSL',
        'Robert Morris': 'ROBMOR',
        'Canisius': 'CANISI',
        'Colgate': 'COLGAT',
        'Bemidji St.': 'BEMDJI',
        'Notre Dame': 'N DAME',
        'Vermont': 'VERMNT',
        'Lake Superior St.': 'LK SUP',
        'Rensselaer': 'RPI',
        'Niagara': 'NIAGRA',
        'Ferris St.': 'FERRIS',
        'Stonehill': 'STONEH',
        'Yale': 'YALE',
        'Brown': 'BROWN',
        'Northern Mich.': 'N MICH',
        'St. Lawrence': 'ST LAW',
        'Alas. Anchorage': 'AK ANC',
        'Mercyhurst': 'MERCYH',
    }

NCAA_API_BASE = "https://ncaa-api.henrygd.me"
REQUEST_TIMEOUT = 5
REQUEST_HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36', 'accept-language': 'en-US,en-CA;q=0.9,en;q=0.8,hi-IN;q=0.7,hi;q=0.6'}


def getGamesForDate(teams, year, month, day):
    """Get game data for every D1 men's hockey game on a specific date.

    Args:
        teams (dictionary): Team names and three letter abbreviations. Needed as the game API doesn't return short team abbreviations.
        year (str): Four digit year, e.g. "2026".
        month (str): Two digit month, e.g. "01".
        day (str): Two digit day, e.g. "05".

    Returns:
        games (list of dictionaries): All game info needed to display on scoreboard. Teams, scores, start times, game clock, etc.
    """
    # Call the NCAA API for the date's game info. Save the result as a JSON object.
    gamesResponse = requests.get(url=NCAA_API_BASE+"/scoreboard/icehockey-men/d1/"+year+"/"+month+"/"+day, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
    gamesJson = gamesResponse.json()

    # Declare an empty list to hold the games dicts.
    games = []

    # For each game, build a dict recording it's information. Append this to the end of the teams list.
    if gamesJson['games']: # If games today.
        for game in gamesJson['games']:

            # Prep the period data for consistency. This data doesn't exist in the API response until game begins.
            if game['game']['gameState'] != "pre":
                perName = game['game']['currentPeriod']
                perTimeRem = game['game']['contestClock']
            else:
                perName = "Not Started"
                perTimeRem = "Not Started"

            if game['game']['home']['names']['char6'] in teams:
                shortHome = teams[game['game']['home']['names']['char6']]
            elif len(game['game']['home']['names']['char6']) > 0:
                shortHome = game['game']['home']['names']['char6'][0:3]
            else:
                shortHome = game['game']['home']['names']['short'][0:3].upper()

            if game['game']['away']['names']['char6'] in teams:
                shortAway = teams[game['game']['away']['names']['char6']]
            elif len(game['game']['away']['names']['char6']) > 0:
                shortAway = game['game']['away']['names']['char6'][0:3]
            else:
                shortAway = game['game']['away']['names']['short'][0:3].upper()
            if game['game']['gameID'] == "":
                gameIdent = "0"
            else:
                gameIdent = game['game']['gameID']

            # Absolute scheduled start time, used to know when to start polling
            # for a game that hasn't begun yet (see computeNextFetchTime()).
            try:
                startTimeEpoch = int(game['game']['startTimeEpoch'])
            except (KeyError, TypeError, ValueError):
                startTimeEpoch = None

            # The new API reports times like "7:00 PM ET" / "10:00 PM ET" (no
            # leading zero on single-digit hours). Normalize to zero-padded
            # "HH:MM" here so the rest of the file (which slices this string by
            # fixed character position) doesn't need to change.
            rawStartTime = game['game']['startTime']
            if rawStartTime and rawStartTime.upper() != "TBA":
                try:
                    hourStr, minuteStr = rawStartTime.split(" ")[0].split(":")
                    startTimeLocal = "{:02d}:{}".format(int(hourStr), minuteStr)
                except (ValueError, IndexError):
                    startTimeLocal = rawStartTime
            else:
                startTimeLocal = rawStartTime

            # Prep the dict data.
            gameDict = {
                'Game ID': int(gameIdent),
                'Home Team': game['game']['home']['names']['short'],
                'Home Abbreviation': game['game']['home']['names']['char6'],
                'Away Team': game['game']['away']['names']['short'],
                'Away Abbreviation': game['game']['away']['names']['char6'],
                'Home Score': game['game']['home']['score'],
                'Away Score': game['game']['away']['score'],
                'Start Time Local': startTimeLocal,
                'Status': game['game']['gameState'],
                'Detailed Status': game['game']['finalMessage'],
                'Period Name': perName,
                'Period Time Remaining': perTimeRem,
                'Home Winner': json.dumps(game['game']['home']['winner']),
                'Away Winner': json.dumps(game['game']['away']['winner']),
                'Home Short': shortHome,
                'Away Short': shortAway,
                'Start Time Epoch': startTimeEpoch
            }

            # Append the dict to the games list.
            games.append(gameDict)

        # Sort list by Game ID. Ensures order doesn't change as games end.
        games.sort(key=lambda x:x['Game ID'])
    return games


def getGameData(teams):
    """Get game data for all of today's (or, before noon, last night's) games.

    Args:
        teams (dictionary): Team names and three letter abbreviations, passed through to getGamesForDate().

    Returns:
        games (list of dictionaries): See getGamesForDate().
    """
    todays_date = date.today()

    # If earlier than 12PM local time, pull games from the previous night
    if int(datetime.now().strftime("%H")) < 12:
        yesterdays_date = todays_date - timedelta(days = 1)
        YEAR = '{:04d}'.format(yesterdays_date.year)
        MONTH = '{:02d}'.format(yesterdays_date.month)
        DAY = '{:02d}'.format(yesterdays_date.day)
    else:
        YEAR = '{:04d}'.format(todays_date.year)
        MONTH = '{:02d}'.format(todays_date.month)
        DAY = '{:02d}'.format(todays_date.day)

    return getGamesForDate(teams, YEAR, MONTH, DAY)


def getRankings(teams):
    """Get the current NCAA Division I men's hockey rankings.

    Uses the "pairwise" rankings route, which currently serves NPI (Net Passing
    Index) data -- NPI replaced the old PairWise ranking as the tournament
    selection metric a few years back, but the API route/slug never got renamed.

    Args:
        teams (dictionary): The char6 -> three-letter-abbreviation dictionary
            from getTeamData(), used (via getSchoolAbbrMap()) to attach a
            'Short' abbreviation to each ranking entry.

    Returns:
        rankings (list of dictionaries): Each entry has 'Rank' (int), 'School'
        (str, e.g. "Miami (OH)"), 'Short' (str, e.g. "MIA" -- the team's
        three-letter abbreviation, or the first few characters of 'School' if
        no abbreviation mapping was found for it), 'Abbr' (str or None -- the
        char6 abbreviation, i.e. a key of getTeamData(), or None if
        unmapped -- used to look up the team's logo/color), 'Record' (str,
        e.g. "18-16-2"), and 'Conference' (str). Sorted by rank, ascending.
    """
    schoolAbbrMap = getSchoolAbbrMap()

    rankingsResponse = requests.get(url=NCAA_API_BASE+"/rankings/icehockey-men/d1/pairwise", headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
    rankingsJson = rankingsResponse.json()

    rankings = []
    for entry in rankingsJson.get('data', []):
        try:
            rank = int(entry['Rank'])
        except (KeyError, TypeError, ValueError):
            continue
        school = entry.get('School', '')
        # Fall back to a truncated school name if there's no abbreviation
        # mapping for it (a new/unmapped program), rather than dropping the
        # row or leaving it unrenderable.
        short = teams.get(schoolAbbrMap.get(school), school[:3].upper())
        rankings.append({
            'Rank': rank,
            'School': school,
            'Short': short,
            'Abbr': schoolAbbrMap.get(school),
            'Record': entry.get('Record', ''),
            'Conference': entry.get('Conf', '')
        })

    rankings.sort(key=lambda x: x['Rank'])
    return rankings


def getFavoriteTeamNextGame(teams, favoriteAbbr, maxDatesToCheck=25):
    """Find the favorite team's next scheduled (non-final) game.

    The NCAA API has no "team schedule" endpoint, so this works in two steps:
    first pull the season's calendar of game-dates (a lightweight list of dates
    that have any D1 games at all -- no team info), then check each of those
    dates' full scoreboards, starting from today, for a game involving the
    favorite team, stopping at the first one found.

    Args:
        teams (dictionary): Team names and three letter abbreviations, passed through to getGamesForDate().
        favoriteAbbr (str): The favorite team's char6 NCAA abbreviation (e.g. "MIA OH").
        maxDatesToCheck (int): Safety cap on how many game-dates to scan forward,
        so a bug or unusual gap in the schedule can't turn into an unbounded
        run of API calls.

    Returns:
        nextGame (dictionary or None): The favorite team's next non-final game
        (same shape as a getGamesForDate() entry), or None if nothing is found
        (e.g. off-season, or the rest of the season's schedule isn't posted yet).
    """
    today = date.today()

    # The schedule calendar is keyed by championship year (the later calendar
    # year of the Oct-Apr season), not the season's starting year.
    championshipYear = today.year + 1 if today.month >= 8 else today.year

    try:
        calendarResponse = requests.get(url=NCAA_API_BASE+"/schedule-alt/icehockey-men/d1/"+str(championshipYear), headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
        candidateDates = calendarResponse.json()['data']['schedules']['games']
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None

    # Parse "MM/DD/YYYY" strings into real dates, keep only today-or-later, and
    # sort chronologically so the nearest ones are checked first.
    parsedDates = []
    for entry in candidateDates:
        try:
            gameDate = datetime.strptime(entry['contestDate'], "%m/%d/%Y").date()
        except (KeyError, ValueError):
            continue
        if gameDate >= today:
            parsedDates.append(gameDate)
    parsedDates.sort()

    for gameDate in parsedDates[:maxDatesToCheck]:
        YEAR = '{:04d}'.format(gameDate.year)
        MONTH = '{:02d}'.format(gameDate.month)
        DAY = '{:02d}'.format(gameDate.day)
        try:
            gamesOnDate = getGamesForDate(teams, YEAR, MONTH, DAY)
        except Exception:
            continue
        for game in gamesOnDate:
            if game['Status'] != "final" and favoriteAbbr in (game['Home Abbreviation'], game['Away Abbreviation']):
                return game

    return None

def getMaxBrightness(time):
    """ Calculates the maximum brightness and fade step increments based on the time of day.

    Args:
        time (int): Hour of the day. Can be 0-23.

    Returns:
        maxBrightness (int): The maximum brightness for the LED display.
        fadeStep (int): The increments that the display should fade up and down by.
    """
    
    # If the time is midnight, set the time to 1am to avoid the display fulling turning off.
    if time == 0:
        time = 1

    # Max brightness is the time divided by 12 and multiplied by the global maxMatrixBrightness. For pm times, the difference between 24 and the time is used.
    # This means that max brightness is at noon, with the lowest from 11pm through 1am (because of the above edge case).
    maxBrightness = math.ceil(maxMatrixBrightness * time / 12 if time <= 12 else maxMatrixBrightness * (24-time)/12)
    
    # If the previous calculation results in a brightness less than 15, set brightness to 15.
    maxBrightness = maxBrightness if maxBrightness >= 15 else 15

    # Fade step divides the maxBrightness into 15 segments. Floor since you can't have fractional brightness.
    fadeStep = math.ceil(maxBrightness/15)

    return maxBrightness, fadeStep

def checkGoalScorer(game, gameOld):
    """Checks if a team has scored.

    Args:
        game (dict): All information for a specific game.
        gameOld (dict): Same information from one update cycle ago.

    Returns:
        scoringTeam (string): If either team has scored. both/home/away/none.
    """

    # The API returns scores as strings (e.g. "4"), so compare numerically
    # rather than lexicographically -- a plain string ">" would (incorrectly)
    # say "9" > "10".
    def toInt(score):
        try:
            return int(score)
        except (TypeError, ValueError):
            return 0

    awayScore = toInt(game['Away Score'])
    awayScoreOld = toInt(gameOld['Away Score'])
    homeScore = toInt(game['Home Score'])
    homeScoreOld = toInt(gameOld['Home Score'])

    # Check if either team has scored by comparing the score of the last cycle. Set scoringTeam accordingly.
    if awayScore > awayScoreOld and homeScore == homeScoreOld:
        scoringTeam = "away"
    elif awayScore == awayScoreOld and homeScore > homeScoreOld:
        scoringTeam = "home"
    elif awayScore > awayScoreOld and homeScore > homeScoreOld:
        scoringTeam = "both"
    else:
        scoringTeam = "none"

    return scoringTeam

def checkGameWinner(game):
    """Checks which team has won.

    Args:
        game (dict): All information for a specific game.

    Returns:
        winningTeam (string): If the home team, away team, or neither won.
    """

    # Check if either team has score by compare the score of the last cycle. Set scoringTeam accordingly.
    if game['Home Winner'] == 'true' and game['Away Winner'] == 'false':
        winningTeam = "home"
    elif game['Home Winner'] == 'false' and game['Away Winner'] == 'true':
        winningTeam = "away"
    else:
        winningTeam = "none"

    return winningTeam


def computeNextFetchTime(games, now):
    """Decides when runScoreboard() should next call the NCAA API, so it doesn't
    poll pointlessly when nothing is going to change.

    Args:
        games (list of dictionaries): The most recently fetched games (may be empty).
        now (float): The current time (time.time()) to measure from.

    Returns:
        nextFetchTime (float): A time.time()-style timestamp of the next allowed fetch.
    """

    # No games today: the schedule for today won't change once it's come back
    # empty, so don't check again until tomorrow.
    if not games:
        tomorrow = date.today() + timedelta(days = 1)
        midnight = datetime.combine(tomorrow, datetime.min.time())
        return midnight.timestamp()

    # If every game today is still "pre" (hasn't started), there's nothing to
    # refresh until the earliest one is about to start.
    upcomingStarts = [g['Start Time Epoch'] for g in games if g['Status'] == "pre" and g['Start Time Epoch'] is not None]
    if len(upcomingStarts) == len(games):
        return min(upcomingStarts) - PREGAME_BUFFER

    # Otherwise at least one game is live, finished, or postponed: resume the
    # normal refresh cadence.
    return now + REFRESH_INTERVAL


def buildGameNotStarted(game):
    """Adds all aspects of the game not started screen to the image object.

    Args:
        game (dict): All information for a specific game.
    """

    # Add the logos of the teams involved to the image.
    displayLogos(game['Away Abbreviation'],game['Home Abbreviation'],game['Away Short'],game['Home Short'])

    # Add "Today" to the image.
    draw.text((firstMiddleCol+1,0), "T", font=fontMedReg, fill=fillWhite)
    draw.text((firstMiddleCol+5,2), "o", font=fontSmallReg, fill=fillWhite)
    draw.text((firstMiddleCol+9,2), "d", font=fontSmallReg, fill=fillWhite)
    draw.text((firstMiddleCol+13,2), "a", font=fontSmallReg, fill=fillWhite)
    draw.text((firstMiddleCol+17,2), "y", font=fontSmallReg, fill=fillWhite)

    startTime = game['Start Time Local']

    # Add the start time to the image. Adjust placement for times before/after 10pm local time.

    if len(startTime) == 0 or startTime== "TBA": # If the time isn't listed or listed as TBA
        draw.text((firstMiddleCol+3,22), "TBA", font=fontSmallReg, fill=fillWhite)

    elif startTime[0] == "1": # 10pm or later.
        # Add "@" to the image.
        draw.text((firstMiddleCol+6,8), "@", font=fontLargeReg, fill=fillWhite)

        # Hour.
        draw.text((firstMiddleCol,22), startTime[0], font=fontSmallReg, fill=fillWhite)
        draw.text((firstMiddleCol+5,22), startTime[1], font=fontSmallReg, fill=fillWhite)
        # Colon (manual dots since the font's colon looks funny).
        draw.rectangle(((firstMiddleCol+10,25),(firstMiddleCol+10,25)), fill=fillWhite)
        draw.rectangle(((firstMiddleCol+10,27),(firstMiddleCol+10,27)), fill=fillWhite)
        # Minutes.
        draw.text((firstMiddleCol+12,22), startTime[3], font=fontSmallReg, fill=fillWhite) # Skipping startTime[2] as that would be the colon.
        draw.text((firstMiddleCol+17,22), startTime[4], font=fontSmallReg, fill=fillWhite)

    else: # 9pm or earlier.
        # Add "@" to the image.
        draw.text((firstMiddleCol+6,8), "@", font=fontLargeReg, fill=fillWhite)

        # Hour.
        draw.text((firstMiddleCol+3,22), startTime[1], font=fontSmallReg, fill=fillWhite)
        # Colon (manual dots since the font's colon looks funny).
        draw.rectangle(((firstMiddleCol+8,25),(firstMiddleCol+8,25)), fill=fillWhite)
        draw.rectangle(((firstMiddleCol+8,27),(firstMiddleCol+8,27)), fill=fillWhite)
        # Minutes.
        draw.text((firstMiddleCol+10,22), startTime[3], font=fontSmallReg, fill=fillWhite)
        draw.text((firstMiddleCol+15,22), startTime[4], font=fontSmallReg, fill=fillWhite)

def buildGameInProgress(game, gameOld, scoringTeam):
    """Adds all aspects of the game in progress screen to the image object.

    Args:
        game (dict): All information for a specific game.
        gameOld (dict): The same information, but from one cycle ago.
        scoringTeam (string): If the home team, away team, or both, or neither scored.
    """

    # Add the logos of the teams involved to the image.
    displayLogos(game['Away Abbreviation'],game['Home Abbreviation'],game['Away Short'],game['Home Short'])

    # Add the period to the image.
    displayPeriod(game['Period Name'], game['Period Time Remaining'])

    # Add the current score to the image. Note if either team scored.
    displayScore(game['Away Score'], game['Home Score'], scoringTeam)

def buildGameOver(game, winningTeam):
    """Adds all aspects of the game over screen to the image object.

    Args:
        game (dict): All information for a specific game.
        winningTeam (string): If the home team, away team, or neither won.
    """

    # Add the logos of the teams involved to the image.
    displayLogos(game['Away Abbreviation'],game['Home Abbreviation'],game['Away Short'],game['Home Short'])

    # Add "Final" to the image.
    draw.text((firstMiddleCol+1,0), "F", font=fontMedReg, fill=fillWhite)
    draw.text((firstMiddleCol+5,2), "i", font=fontSmallReg, fill=fillWhite)
    draw.text((firstMiddleCol+9,2), "n", font=fontSmallReg, fill=fillWhite)
    draw.text((firstMiddleCol+14,2), "a", font=fontSmallReg, fill=fillWhite)
    draw.text((firstMiddleCol+17,2), "l", font=fontSmallReg, fill=fillWhite)

    # Check if the game ended in overtime or a shootout.
    # If so, add that to the image.
    if game['Period Name'] == "FINAL (OT)":
        draw.text((firstMiddleCol+6,9), "OT", font=fontMedReg, fill=fillWhite)
    if game['Period Name'] == "FINAL (2OT)":
        draw.text((firstMiddleCol+2,9), "2OT", font=fontMedReg, fill=fillWhite)
    if game['Period Name'] == "FINAL (3OT)":
        draw.text((firstMiddleCol+2,9), "3OT", font=fontMedReg, fill=fillWhite)
    if game['Period Name'] == "FINAL (4OT)":
        draw.text((firstMiddleCol+2,9), "4OT", font=fontMedReg, fill=fillWhite)
    if game['Period Name'] == "FINAL (5OT)":
        draw.text((firstMiddleCol+2,9), "5OT", font=fontMedReg, fill=fillWhite)
    elif game['Period Name'] == "FINAL/SO":
        draw.text((firstMiddleCol+6,9), "SO", font=fontMedReg, fill=fillWhite)

    # Add the current score to the image.
    displayScore(game['Away Score'],game['Home Score'], winningTeam)

def buildGamePostponed(game):
    """Adds all aspects of the postponed screen to the image object.

    Args:
        game (dict): All information for a specific game.
    """
    
    # Add the logos of the teams involved to the image.
    displayLogos(game['Away Abbreviation'],game['Home Abbreviation'],game['Away Short'],game['Home Short'])

    # Add "PPD" to the image.
    draw.text((firstMiddleCol+2,0), "PPD", font=fontMedReg, fill=fillWhite)

def buildNoGamesToday():
    """Adds all aspects of the no games today screen to the image object."""

    # Add the NCAA logo to the image.
    ncaaLogo = Image.open("assets/images/NCAA_Logo_Simplified.png")
    ncaaLogo.thumbnail((30,30))
    image.paste(ncaaLogo, (1, 1))

    # Add "No Games Today" to the image.
    draw.text((32,0), "No", font=fontMedReg, fill=fillWhite)
    draw.text((32,10), "Games", font=fontMedReg, fill=fillWhite)
    draw.text((32,20), "Today", font=fontMedReg, fill=fillWhite)

def buildFavoriteTeamBoard(favoriteAbbr, favoriteShort, record, nextGame):
    """Adds the favorite-team board (logo, W-L-T record, and next game) to the image object.

    Args:
        favoriteAbbr (string): The favorite team's char6 NCAA abbreviation (used to find its logo file).
        favoriteShort (string): The favorite team's three letter abbreviation.
        record (string or None): The team's "W-L-T" record (e.g. "18-16-2"), or None if it
            couldn't be found (e.g. too early in the season, or an unexpected API response).
        nextGame (dictionary or None): The team's next scheduled game (see getGamesForDate()),
            or None if nothing could be found (e.g. off-season, or the rest of the season's
            schedule isn't posted yet).
    """

    # Add the favorite team's logo to the image, same size/fallback rule as displayLogos().
    logoSize = (20,20)
    if os.path.exists("assets/images/team logos/png/" + favoriteAbbr + ".png"):
        favoriteLogo = Image.open("assets/images/team logos/png/" + favoriteAbbr + ".png")
    else:
        favoriteLogo = Image.open("assets/images/team logos/png/NCAA.png")
    favoriteLogo.thumbnail(logoSize)
    image.paste(favoriteLogo, (0, 0))

    # Record, to the right of the logo. (No text label under the logo itself --
    # this whole board is the favorite team's, so the logo + record + opponent
    # already make that clear, and the space is needed below for the date/time
    # row, which is too wide to share a row with anything else.)
    draw.text((22,0), record if record else "N/A", font=fontSmallReg, fill=fillWhite)

    if nextGame is None:
        draw.text((22,11), "NO GAME", font=fontSmallReg, fill=fillWhite)
        draw.text((2,22), "SCHEDULED", font=fontSmallReg, fill=fillWhite)
        return

    # Figure out the opponent and whether the favorite team is home or away.
    if nextGame['Home Abbreviation'] == favoriteAbbr:
        opponentShort = nextGame['Away Short']
        symbol = "vs "
    else:
        opponentShort = nextGame['Home Short']
        symbol = "@ "

    draw.text((22,11), symbol + opponentShort, font=fontSmallReg, fill=fillWhite)

    # Date (from the epoch, in the format month/day) and start time. This can run
    # up to ~55px wide (e.g. "12/25 07:00"), too wide for the 42px-tall column to
    # the right of the logo, so it gets its own full-width row instead.
    if nextGame['Start Time Epoch']:
        gameDatetime = datetime.fromtimestamp(nextGame['Start Time Epoch'])
        dateTimeStr = "{}/{} {}".format(gameDatetime.month, gameDatetime.day, nextGame['Start Time Local'])
    else:
        dateTimeStr = nextGame['Start Time Local']
    draw.text((2,22), dateTimeStr, font=fontSmallReg, fill=fillWhite)

def buildLoading():
    """Adds all aspects of the loading screen to the image object."""

    # Add the NCAA logo to the image.
    ncaaLogo = Image.open("assets/images/NCAA_Logo_Simplified.png")
    ncaaLogo.thumbnail((30,30))
    image.paste(ncaaLogo, (1, 1))

    # Add "Now Loading" to the image.
    draw.text((29,8), "Now", font=fontSmallReg, fill=fillWhite)
    draw.text((29,15), "Loading", font=fontSmallReg, fill=fillWhite)

def displayLogos(awayTeam, homeTeam, shortAway, shortHome):
    """Adds the logos of the home and away teams to the image object, making sure to not overlap text and center logos.

    Args:
        awayTeam (string): Abbreviation of the away team.
        homeTeam (string): Abbreviation of the home team.
        awayShort (string): Three letter abbreviation of the away team.
        homeShort (string): Three letter abbreviation of the home team.
    """

    # Define the max width and height that a logo can be.
    logoSize = (20,20)

    if os.path.exists("assets/images/team logos/png/" + awayTeam + ".png"):
        # Load and resize the away team logo.
        awayLogo = Image.open("assets/images/team logos/png/" + awayTeam + ".png")
        awayLogo.thumbnail(logoSize)
    else:
        # Load and resize the away team logo.
        awayLogo = Image.open("assets/images/team logos/png/NCAA.png")
        awayLogo.thumbnail(logoSize)

    if os.path.exists("assets/images/team logos/png/" + homeTeam + ".png"):
        # Load and resize the home team logo.
        homeLogo = Image.open("assets/images/team logos/png/" + homeTeam + ".png")
        homeLogo.thumbnail(logoSize)
    else:
        # Load and resize the home team logo.
        homeLogo = Image.open("assets/images/team logos/png/NCAA.png")
        homeLogo.thumbnail(logoSize)

    # Record the width and heights of the logos.
    awayLogoWidth, awayLogoHeight = awayLogo.size
    homeLogoWidth, homeLogoHeight = homeLogo.size

    image.paste(awayLogo, (0, 0))
    image.paste(homeLogo, (44, 0))

    if len(shortAway) == 2:
        draw.text((4,20), shortAway, font=fontMedReg, fill=fillWhite)
    else:
        draw.text((1,20), shortAway, font=fontMedReg, fill=fillWhite)

    if len(shortHome) == 2:
        draw.text((49,20), shortHome, font=fontMedReg, fill=fillWhite)
    else:
        draw.text((46,20), shortHome, font=fontMedReg, fill=fillWhite)
    

def displayPeriod(periodName, timeRemaining):
    """Adds the current period to the image object.

    Args:
        periodName (string): [description]
        timeRemaining (string): [description]
    """

    # If the first period, add "1st" to the image.
    if periodName == "1ST":
        draw.text((firstMiddleCol+5,0), "1", font=fontMedReg, fill=fillWhite)
        draw.text((firstMiddleCol+9,0), "s", font=fontSmallReg, fill=fillWhite)
        draw.text((firstMiddleCol+13,0), "t", font=fontSmallReg, fill=fillWhite)

    # If the second period, add "2nd" to the image.
    elif periodName == "2ND":
        draw.text((firstMiddleCol+4,0), "2", font=fontMedReg, fill=fillWhite)
        draw.text((firstMiddleCol+10,0), "n", font=fontSmallReg, fill=fillWhite)
        draw.text((firstMiddleCol+14,0), "d", font=fontSmallReg, fill=fillWhite)

    # If the third period, add "3rd" to the image.
    elif periodName == "3RD":
        draw.text((firstMiddleCol+4,0), "3", font=fontMedReg, fill=fillWhite)
        draw.text((firstMiddleCol+10,0), "r", font=fontSmallReg, fill=fillWhite)
        draw.text((firstMiddleCol+14,0), "d", font=fontSmallReg, fill=fillWhite)

    # If in overtime/shootout, add that to the image.
    elif periodName == "OT" or periodName == "SO":
        draw.text((firstMiddleCol+5,0), periodName, font=fontMedReg, fill=fillWhite)

    # Otherwise, we're in 2OT or later. Add that to the image.
    else:
        draw.text((firstMiddleCol+3,0), periodName, font=fontMedReg, fill=fillWhite)

    # If not in the SO, and the period not over, add the time remaining in the period to the image.
    if periodName != "SO":
        if timeRemaining != "0:00":
            displayTimeRemaining(timeRemaining) # Adds the time remaining in the period to the image.

        # If not in the SO and the time remaining is "END", then we know that we're in intermission. Don't add time remaining to the image.
        else:
            draw.text((firstMiddleCol+2,8), "INT", font=fontMedReg, fill=fillWhite)

def displayTimeRemaining(timeRemaining):
    """Adds the remaining time in the period to the image. Takes into account different widths of time remaining.

    Args:
        timeRemaining (string): The time remaining in the period in "MM:SS" format. For times less than 10 minutes, the minutes should have a leading zero (e.g 09:59).
    """

    # If time left is 20:00 (period about to start), add the time to the image with specific spacing.
    if timeRemaining[0] == "2" and len(timeRemaining) == 5: # If the first digit of the time is 2.
        # Minutes.
        draw.text((firstMiddleCol+1,9), timeRemaining[0], font=fontSmallReg, fill=fillWhite)
        draw.text((firstMiddleCol+5,9), timeRemaining[1], font=fontSmallReg, fill=fillWhite)
        # Colon.
        draw.rectangle(((firstMiddleCol+10,12),(firstMiddleCol+10,12)), fill=fillWhite)
        draw.rectangle(((firstMiddleCol+10,14),(firstMiddleCol+10,14)), fill=fillWhite)
        # Seconds.
        draw.text((firstMiddleCol+12,9), timeRemaining[3], font=fontSmallReg, fill=fillWhite) # Skipping "2" as it's the colon.
        draw.text((firstMiddleCol+16,9), timeRemaining[4], font=fontSmallReg, fill=fillWhite)
    
    # If time left is between 10 and 20 minutes, add the time to the image with different spacing.
    elif timeRemaining[0] == "1" and len(timeRemaining) == 5: # If the first digit of the time is 1.
        # Minutes.
        draw.text((firstMiddleCol,9), timeRemaining[0], font=fontSmallReg, fill=fillWhite)
        draw.text((firstMiddleCol+5,9), timeRemaining[1], font=fontSmallReg, fill=fillWhite)
        # Colon.
        draw.rectangle(((firstMiddleCol+10,12),(firstMiddleCol+10,12)), fill=fillWhite)
        draw.rectangle(((firstMiddleCol+10,14),(firstMiddleCol+10,14)), fill=fillWhite)
        # Seconds.
        draw.text((firstMiddleCol+12,9), timeRemaining[3], font=fontSmallReg, fill=fillWhite)
        draw.text((firstMiddleCol+17,9), timeRemaining[4], font=fontSmallReg, fill=fillWhite)

    # Otherwise, time is less than 10 minutes. Add the time to the image with spacing for a single digit minute.
    elif timeRemaining[0] == "0" and len(timeRemaining) == 5:
        # Minutes.
        draw.text((firstMiddleCol+3,9), timeRemaining[1], font=fontSmallReg, fill=fillWhite)
        # Colon.
        draw.rectangle(((firstMiddleCol+8,12),(firstMiddleCol+8,12)), fill=fillWhite)
        draw.rectangle(((firstMiddleCol+8,14),(firstMiddleCol+8,14)), fill=fillWhite)
        # Seconds.
        draw.text((firstMiddleCol+10,9), timeRemaining[3], font=fontSmallReg, fill=fillWhite)
        draw.text((firstMiddleCol+15,9), timeRemaining[4], font=fontSmallReg, fill=fillWhite)

    else :
        # Minutes.
        draw.text((firstMiddleCol+3,9), timeRemaining[0], font=fontSmallReg, fill=fillWhite)
        # Colon.
        draw.rectangle(((firstMiddleCol+8,12),(firstMiddleCol+8,12)), fill=fillWhite)
        draw.rectangle(((firstMiddleCol+8,14),(firstMiddleCol+8,14)), fill=fillWhite)
        # Seconds.
        draw.text((firstMiddleCol+10,9), timeRemaining[2], font=fontSmallReg, fill=fillWhite)
        draw.text((firstMiddleCol+15,9), timeRemaining[3], font=fontSmallReg, fill=fillWhite)

def displayScore(awayScore, homeScore, scoringTeam = "none"):
    """Add the score for both teams to the image object.

    Args:
        awayScore (int): Score of the away team.
        homeScore (int): Score of the home team.
        scoringTeam (str, optional): The team that scored if applicable. Options: "away", "home", "both", "none". Defaults to "none".
    """

    # Add the hyphen to the image.
    draw.text((firstMiddleCol+9,20), "-", font=fontSmallBold, fill=fillWhite)

    # If no team scored, add both scores to the image.
    if scoringTeam == "none":
        draw.text((firstMiddleCol+1,17), str(awayScore), font=fontLargeBold, fill=fillWhite)
        draw.text((firstMiddleCol+13,17), str(homeScore), font=fontLargeBold, fill=(fillWhite))
    
    # If either or both of the teams scored, add that number to the image in red.
    elif scoringTeam == "away":
        draw.text((firstMiddleCol+1,17), str(awayScore), font=fontLargeBold, fill=fillRed)
        draw.text((firstMiddleCol+13,17), str(homeScore), font=fontLargeBold, fill=fillWhite)
    elif scoringTeam == "home":
        draw.text((firstMiddleCol+1,17), str(awayScore), font=fontLargeBold, fill=fillWhite)
        draw.text((firstMiddleCol+13,17), str(homeScore), font=fontLargeBold, fill=fillRed)
    elif scoringTeam == "both":
        draw.text((firstMiddleCol+1,17), str(awayScore), font=fontLargeBold, fill=fillRed)
        draw.text((firstMiddleCol+13,17), str(homeScore), font=fontLargeBold, fill=fillRed)

def displayGoalFade(score, location, secondScore = "", secondLocation = (0,0), both=False):
    """Adds a red number to the image and fades it to white.
       Note that this is the only time that the matrix is updated in a build or display function.

    Args:
        score (int): The score that needs to be printed.
        location (tuple): Where to add that score to the image.
        secondScore (str, optional): If a second score also needs to be printed, that number. Defaults to "".
        secondLocation (tuple, optional): Location for that second score. Defaults to (0,0).
        both (bool, optional): If both teams have scored. Defaults to False.
    """

    # Print that a team score. This is only for testing.
    print("***\n\nGoal!\n\n***")

    time.sleep(1.5)

    # If both teams have scored.
    if both == True:  
        # Fade both numbers to white.
        for n in range(50, 256):
            draw.text(location, score, font=fontLargeBold, fill=(255, n, n, 255))
            draw.text(secondLocation, secondScore, font=fontLargeBold, fill=(255, n, n, 255))
            matrix.SetImage(image)
            time.sleep(.015)
    
    # If one team has scored.
    else:
        # Fade number to white.
        for n in range(50, 256):
            draw.text(location, score, font=fontLargeBold, fill=(255, n, n, 255))
            matrix.SetImage(image)
            time.sleep(.015)

def recordTextWidth(drawObj, record, font, hyphenWidth=3):
    """Computes the pixel width drawRecordText() would use for this record,
    without drawing anything -- needed to right-align it before its start
    position is known. See drawRecordText() for why this isn't just
    drawObj.textbbox() on the whole string.
    """
    parts = record.split('-')
    width = sum(drawObj.textbbox((0,0), part, font=font)[2] for part in parts)
    width += hyphenWidth * (len(parts) - 1)
    return width

def drawRecordText(drawObj, xy, record, font, color, hyphenWidth=3):
    """Draws a "W-L-T" record string using a slim hand-drawn hyphen instead of
    the bitmap font's '-' glyph.

    fontSmallReg/fontSmallBold are fixed-width bitmap fonts, so the font's own
    '-' takes the same full character cell (5px) as any digit -- more than a
    separator mark needs. Drawing a 2px dash by hand instead reclaims a couple
    of pixels per hyphen, which is what lets the record fit next to the
    rank+abbreviation on the rankings board (see displayScrollingRankings()).
    """
    x, y = xy
    parts = record.split('-')
    for i, part in enumerate(parts):
        if i > 0:
            hyphenY = y + 4  # matches where the font's own '-' sits in a 9px-tall cell
            drawObj.line((x, hyphenY, x + 1, hyphenY), fill=color)
            x += hyphenWidth
        drawObj.text((x, y), part, font=font, fill=color)
        x += drawObj.textbbox((0,0), part, font=font)[2]

@lru_cache(maxsize=None)
def getTeamColor(charAbbr):
    """Derives a team's row color for the rankings board from its own logo,
    instead of a hand-maintained color list -- the logo files under
    assets/images/team logos/png/ already exist for every team (see
    displayLogos()/buildFavoriteTeamBoard()), so this reads the actual brand
    color out of the image instead of looking it up separately.

    The approach: find the most common pixel color in the logo that isn't
    close to white, black, or gray (those are almost always background fill
    or outline, not the team's real color), then, if that color is too dark
    to read clearly against the display's black background, brighten it
    (keeping its hue) until it is. Results are cached -- each logo is only
    ever decoded once per run, however many times this gets called.

    Args:
        charAbbr (string or None): The team's char6 NCAA abbreviation (see
            getTeamData()/getRankings()'s 'Abbr' field), or None.

    Returns:
        tuple: An (R,G,B,255) color. Falls back to fillWhite if charAbbr is
        None, the logo file is missing/unreadable, or the logo simply has no
        strong color in it (e.g. a purely black-and-white crest).
    """
    if not charAbbr:
        return fillWhite

    path = "assets/images/team logos/png/" + charAbbr + ".png"
    if not os.path.exists(path):
        return fillWhite

    try:
        logo = Image.open(path).convert("RGBA")
        logo.thumbnail((100, 100))  # full-size logos are overkill for this
        pixels = logo.getdata()
    except Exception as e:
        print(f"getTeamColor: couldn't read logo for {charAbbr}: {e}")
        return fillWhite

    # Bucket similar shades together (rounding to the nearest 8) so that
    # anti-aliased edges don't split one real color into dozens of
    # near-identical entries that each lose to a cleaner background color.
    counts = {}
    for r, g, b, a in pixels:
        if a < 128:
            continue
        mx, mn = max(r, g, b), min(r, g, b)
        brightness = (r + g + b) / 3
        saturation = 0 if mx == 0 else (mx - mn) / mx
        if brightness > 235 or brightness < 25 or saturation < 0.15:
            continue
        key = (r // 8 * 8, g // 8 * 8, b // 8 * 8)
        counts[key] = counts.get(key, 0) + 1

    if not counts:
        return fillWhite

    r, g, b = max(counts, key=counts.get)

    # Brighten (in HSV, so the hue doesn't shift) if the extracted color is
    # too dark or too washed-out to read clearly on the matrix.
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    v = max(v, 0.55)
    if s > 0:
        s = max(s, 0.4)
    r, g, b = colorsys.hsv_to_rgb(h, s, v)

    return (round(r * 255), round(g * 255), round(b * 255), 255)

def displayScrollingRankings(rankings, favoriteSchool=None, maxTeams=20, topHoldSeconds=0.6, bottomHoldSeconds=0.6, scrollDelay=0.08):
    """Scrolls the current NPI rankings vertically through the display.

    Like displayGoalFade(), this is a display function that updates the matrix
    directly rather than just drawing to the shared image -- a scroll needs many
    intermediate frames, which doesn't fit the single build-then-fade pattern the
    static boards use. Callers should fade up before calling this and fade back
    down after; this function assumes the matrix is already at max brightness
    when it starts, and leaves the display showing the last frame of the list
    (the bottom of the scroll) when it returns.

    If the favorite team's real rank falls outside maxTeams, its row is
    appended after a short dashed separator marking the skipped ranks, rather
    than just tacking it on with no indication of the jump.

    Args:
        rankings (list of dictionaries): See getRankings().
        favoriteSchool (string or None): Exact "School" name (see getRankings())
            to highlight in bold as the list scrolls past it (see getTeamColor()
            for its color), or None to highlight nothing.
        maxTeams (int): Cap on how many ranked teams to scroll through, so one
            full cycle doesn't take too long.
        topHoldSeconds (float): How long to pause on the first screen (the top
            of the list) before scrolling starts, so it's actually readable
            and not just flashed past.
        bottomHoldSeconds (float): Same, but for the last screen (the bottom
            of the list) once scrolling finishes.
        scrollDelay (float): Seconds to sleep between each 1px scroll step;
            lower is faster.
    """

    if not rankings:
        return

    teamsToShow = rankings[:maxTeams]

    # The favorite team should always show up somewhere in the scroll -- that's
    # the whole point of highlighting it -- even if its rank didn't make the
    # top maxTeams cutoff. If it's missing, tack its real entry (real rank and
    # all) onto the end, with a dashed separator row marking the skipped ranks,
    # rather than leaving it out entirely.
    favoriteAppended = False
    if favoriteSchool is not None and not any(entry['School'] == favoriteSchool for entry in teamsToShow):
        favoriteEntry = next((entry for entry in rankings if entry['School'] == favoriteSchool), None)
        if favoriteEntry is not None:
            teamsToShow = teamsToShow + [favoriteEntry]
            favoriteAppended = True

    # Build one 64-wide image tall enough to hold every row, then draw each
    # team's row into it. Scrolling is just cropping a moving 64x32 window out
    # of this tall image and pushing each crop to the matrix.
    rowHeight = 11
    gapHeight = 5  # height of the dashed separator row before an appended favorite
    numRows = len(teamsToShow)
    tallHeight = max(rowHeight * numRows + (gapHeight if favoriteAppended else 0), 32)
    tallImage = Image.new("RGB", (64, tallHeight))
    tallDraw = ImageDraw.Draw(tallImage)

    for i, entry in enumerate(teamsToShow):
        isFavorite = favoriteSchool is not None and entry['School'] == favoriteSchool
        # Every row is colored by that team's own primary color (see
        # getTeamColor()); the favorite team isn't recolored specially -- it's
        # already set apart by the bold font.
        rowFont = fontSmallBold if isFavorite else fontSmallReg
        rowColor = getTeamColor(entry.get('Abbr'))

        # The appended favorite (always the last row when favoriteAppended is
        # set) is pushed down past a short dashed line marking the gap between
        # the cutoff rank and its real, worse rank.
        rowY = i * rowHeight
        if favoriteAppended and i == numRows - 1:
            gapColor = (90, 90, 90)
            dashY = rowY + gapHeight // 2
            for x in range(0, 64, 4):
                tallDraw.line((x, dashY, x + 2, dashY), fill=gapColor)
            rowY += gapHeight

        # Rank + abbreviation (see getRankings()/getSchoolAbbrMap()), left-aligned.
        prefix = "{:>2} {}".format(entry['Rank'], entry.get('Short', entry['School']))
        # Safety net: if 'Short' is missing (older/pre-fetched data) or an
        # unmapped school's fallback still doesn't fit, trim from the end.
        while prefix and tallDraw.textbbox((0,0), prefix, font=rowFont)[2] > 63:
            prefix = prefix[:-1]
        tallDraw.text((0, rowY), prefix, font=rowFont, fill=rowColor)

        # W-L-T record, right-aligned, in whatever room is left after the
        # rank+abbreviation. Only actually draw it if it fits without
        # overlapping the prefix -- an edge case (e.g. a long unmapped-school
        # fallback, or a well-into-a-long-season double-digit-everything
        # record) just goes without a record on that one row rather than
        # overlapping text.
        record = entry.get('Record', '')
        if record:
            prefixWidth = tallDraw.textbbox((0,0), prefix, font=rowFont)[2]
            recordWidth = recordTextWidth(tallDraw, record, font=rowFont)
            recordX = 64 - recordWidth
            if recordX >= prefixWidth + 2:
                drawRecordText(tallDraw, (recordX, rowY), record, font=rowFont, color=rowColor)

    maxOffset = tallHeight - 32

    # Show the top of the list and hold.
    image.paste(tallImage.crop((0, 0, 64, 32)), (0, 0))
    matrix.SetImage(image)
    time.sleep(topHoldSeconds)

    # Scroll upward through the list, one pixel at a time.
    for offset in range(1, maxOffset + 1):
        image.paste(tallImage.crop((0, offset, 64, offset + 32)), (0, 0))
        matrix.SetImage(image)
        time.sleep(scrollDelay)

    # Hold on the bottom of the list before returning.
    time.sleep(bottomHoldSeconds)

def runScoreboard():
    """Runs the scoreboard getting scores and other game data and cycles through them in an infinite loop."""

    # Initial calculation and setting of the max brightness.
    maxBrightness, fadeStep = getMaxBrightness(int(datetime.now().strftime("%H")))
    matrix.brightness = maxBrightness

    # Build the loading screen.
    buildLoading()
    matrix.SetImage(image) # Set the matrix to the image.

    networkError = False

    # Try to get team and game data. Max of 100 attempts before it gives up.
    for i in range(100):
        try:
            teams = getTeamData()
            games = getGameData(teams)
            gamesOld = games # Needed for checking logic on initial loop.
            networkError = False
            break

        # In the event that the NCAA API cannot be reached, assume No Games Today.
        # TODO: Make this more robust for specific fail cases.
        except Exception as e:
            print(f"Network Error: {e}")
            networkError = True
            draw.rectangle(((0,0),(63,31)), fill=fillBlack)
            matrix.SetImage(image)
            buildNoGamesToday()
            matrix.brightness = maxBrightness
            matrix.SetImage(image)
            time.sleep(3600)
            #    if i >= 10:
            #        draw.rectangle(((63,31),(63,31)), fill=fillRed)
            #        matrix.SetImage(image)
            #    time.sleep(1)
    else:
        # All 100 attempts failed. Fall back to empty game lists instead of
        # crashing on the undefined 'games'/'gamesOld' referenced below.
        games = []
        gamesOld = []

    # Initial fetch of the favorite-team/rankings data shown on the idle boards
    # (see below). These are supplementary, so a failure here just leaves them
    # empty/None for now rather than holding up the scoreboard the way a failed
    # games fetch does above -- they'll be retried on the normal refresh cadence.
    try:
        rankings = getRankings(teams)
    except Exception as e:
        print(f"Network Error (rankings): {e}")
        rankings = []

    try:
        favoriteNextGame = getFavoriteTeamNextGame(teams, FAVORITE_TEAM_ABBR)
    except Exception as e:
        print(f"Network Error (favorite next game): {e}")
        favoriteNextGame = None

    favoriteRecord = next((r['Record'] for r in rankings if r['School'] == FAVORITE_TEAM_SCHOOL), None)

    # lastFetchTime/nextFetchTime track the NCAA API refresh schedule; see
    # computeNextFetchTime() for the "no games" / "not started yet" / "live" logic.
    lastFetchTime = time.time()
    nextFetchTime = computeNextFetchTime(games, lastFetchTime)

    # Wait one extra second on the loading screen. Users thought it was too quick.
    time.sleep(1)

    # Fade out.
    for brightness in range(maxBrightness,0,-fadeStep):
        matrix.brightness = brightness
        matrix.SetImage(image)
        time.sleep(.025)

    # "Wipe" the image by writing over the entirety with a black rectangle.
    draw.rectangle(((0,0),(63,31)), fill=fillBlack)
    matrix.SetImage(image)

    while True:
        
        # Update the maxBrightness and fadeSteps.
        maxBrightness, fadeStep = getMaxBrightness(int(datetime.now().strftime("%H")))

        # Adjusting cycle time for single game situation.
        if len(games) == 1:
            cycleTime = 10
        else:
            cycleTime = 7

        # True if there are games today but none of them have started yet --
        # this is also an "idle" period as far as the display is concerned.
        allGamesPre = bool(games) and all(game['Status'] == "pre" for game in games)

        # If there's games today.
        if games:

            # Loop through both the games and gamesOld arrays.
            for game, gameOld in zip(games, gamesOld):

                # Check if either team has scored.
                scoringTeam = checkGoalScorer(game, gameOld)

                # Check if either team has won.
                winningTeam = checkGameWinner(game)

                # If the game is postponed, build the postponed screen.
                if game['Status'] == "postponed":
                    buildGamePostponed(game)

                # If the game has yet to begin, build the game not started screen.
                elif game['Status'] == "pre":
                    buildGameNotStarted(game)

                # If the game is over, build the final score screen.
                elif game['Status'] == "final":
                    buildGameOver(game, winningTeam)
                
                # Otherwise, the game is in progress. Build the game in progress screen.
                # If the home or away team has scored, take note of that.
                else:
                    buildGameInProgress(game, gameOld, scoringTeam)

                # Set bottom right LED to red if there's a network error.
                if networkError:
                    draw.rectangle(((63,31),(63,31)), fill=fillRed)

                # Fade up to the image.
                for brightness in range(0,maxBrightness,fadeStep):
                    matrix.brightness = brightness
                    matrix.SetImage(image)
                    time.sleep(.025)
                
                # If a team has scored, fade the red number to white.
                if scoringTeam == "away":
                    displayGoalFade(str(game['Away Score']), (22,17))
                elif scoringTeam == "home":
                    displayGoalFade(str(game['Home Score']), (34,17))
                elif scoringTeam == "both":
                    displayGoalFade(str(game['Away Score']), (22,17), str(game['Home Score']), (34,17), True) # True indicates that both teams have scored.

                # Hold the screen before fading.
                time.sleep(cycleTime)

                # Fade down to black.
                for brightness in range(maxBrightness,0,-fadeStep):
                    matrix.brightness = brightness
                    matrix.SetImage(image)
                    time.sleep(.025)

                # Make the screen totally blank between fades.
                draw.rectangle(((0,0),(63,31)), fill=fillBlack) 
                matrix.SetImage(image)

        # If there's no games today, or today's games all haven't started yet,
        # this lap has room to spare -- fill it with the favorite-team board and
        # the rankings board (in addition to the "no games today" screen, if
        # there really are no games) instead of sitting on one static screen,
        # possibly for hours, until the next scheduled check (see
        # computeNextFetchTime: tomorrow, if there's still no games; the
        # earliest start time, if some have since appeared).
        if not games or allGamesPre:

            if not games:
                buildNoGamesToday()
                if networkError:
                    draw.rectangle(((63,31),(63,31)), fill=fillRed)
                matrix.brightness = maxBrightness
                matrix.SetImage(image)
                time.sleep(idleBoardHoldSeconds)
                draw.rectangle(((0,0),(63,31)), fill=fillBlack)
                matrix.SetImage(image)

            # On a day with no games at all, the rankings board still lingers
            # and scrolls a bit slower than it does on a day where games just
            # haven't started yet -- there, you're probably watching for the
            # first puck drop, not settling in. (The no-games-today screen and
            # favorite-team board hold for the same idleBoardHoldSeconds either
            # way -- see below.)
            noGamesToday = not games

            buildFavoriteTeamBoard(FAVORITE_TEAM_ABBR, FAVORITE_TEAM_SHORT, favoriteRecord, favoriteNextGame)
            if networkError:
                draw.rectangle(((63,31),(63,31)), fill=fillRed)
            matrix.brightness = maxBrightness
            matrix.SetImage(image)
            time.sleep(idleBoardHoldSeconds)
            draw.rectangle(((0,0),(63,31)), fill=fillBlack)
            matrix.SetImage(image)

            # Only scroll the rankings board once there's actually data to show --
            # e.g. it may still be empty on a fresh start if the initial fetch
            # above failed.
            if rankings:
                matrix.brightness = maxBrightness
                if noGamesToday:
                    displayScrollingRankings(rankings, favoriteSchool=FAVORITE_TEAM_SCHOOL,
                                              scrollDelay=noGamesRankingsScrollDelay, bottomHoldSeconds=1)
                else:
                    displayScrollingRankings(rankings, favoriteSchool=FAVORITE_TEAM_SCHOOL)
                draw.rectangle(((0,0),(63,31)), fill=fillBlack)
                matrix.SetImage(image)

        # Refresh the game data, but not before nextFetchTime. Record the data of
        # the last cycle in gamesOld to check for goals.
        if time.time() >= nextFetchTime:
            try:
                gamesOld = games
                games = getGameData(teams)
                networkError = False
            except Exception as e:
                print(f"Network Error: {e}")
                networkError = True
            finally:
                lastFetchTime = time.time()
                nextFetchTime = computeNextFetchTime(games, lastFetchTime)

            # Refresh the slower-moving favorite-team/rankings data on the same
            # cadence as the game data above, rather than giving it its own
            # separate polling schedule -- this data only changes a few times a
            # week at most, so piggybacking here is already more than fresh
            # enough. Failures here are non-fatal; the boards just keep showing
            # the last data they had.
            try:
                rankings = getRankings(teams)
            except Exception as e:
                print(f"Network Error (rankings): {e}")

            try:
                favoriteNextGame = getFavoriteTeamNextGame(teams, FAVORITE_TEAM_ABBR)
            except Exception as e:
                print(f"Network Error (favorite next game): {e}")

            favoriteRecord = next((r['Record'] for r in rankings if r['School'] == FAVORITE_TEAM_SCHOOL), favoriteRecord)

if __name__ == "__main__":

    # This creates the options, matrix, and image objects, as well as some globals that will be needed throughout the code.
    # Note a huge fan of the amount of globals, but they work fine in a small scope project like this.

    # Configure options for the matrix
    options = RGBMatrixOptions()
    options.rows = 32
    options.cols = 64
    options.chain_length = 1
    options.parallel = 1
    options.gpio_slowdown= 2
    options.hardware_mapping = 'adafruit-hat-pwm'
    options.pwm_bits = 10
    options.pwm_dither_bits = 1
    options.limit_refresh_rate_hz = 120

    # Define a matrix object from the options.
    matrix = RGBMatrix(options = options)

    if USING_EMULATOR:
        # RGBMatrixEmulator needs an initial frame canvas allocated before SetImage()
        # is called directly; the real hardware driver doesn't need this.
        matrix.CreateFrameCanvas()

    # Define an image object that will be printed to the matrix.
    image = Image.new("RGB", (64, 32))

    # Define a draw object. This will be used to draw shapes and text to the image.
    draw = ImageDraw.Draw(image)

    # Declare fonts that are used throughout.
    fontSmallReg = ImageFont.load("assets/fonts/PIL/Tamzen5x9r.pil")
    fontSmallBold = ImageFont.load("assets/fonts/PIL/Tamzen5x9b.pil")
    fontMedReg = ImageFont.load("assets/fonts/PIL/Tamzen6x12r.pil")
    fontMedBold = ImageFont.load("assets/fonts/PIL/Tamzen6x12b.pil")
    fontLargeReg = ImageFont.load("assets/fonts/PIL/Tamzen8x15r.pil")
    fontLargeBold = ImageFont.load("assets/fonts/PIL/Tamzen8x15b.pil")

    # Declare text colors that are needed.
    fillWhite = 255,255,255,255
    fillBlack = 0,0,0,255
    fillRed = 255,50,50,255

    # Define the max brightness of the RGB matrix display
    maxMatrixBrightness = 60

    # Define the first col that can be used for center text.
    # i.e. the first col you can use without worry of logo overlap.
    firstMiddleCol = 21

    # Define the number of seconds to sit on each game. (Immediately
    # overwritten at the top of runScoreboard()'s loop based on how many games
    # there are that day -- this default is never actually used, but is kept
    # in sync so it isn't misleading.)
    cycleTime = 7

    # How long to hold each idle-rotation board (the "no games today" screen
    # and the favorite-team board) on screen before moving to the next one.
    # The rankings board doesn't use this -- it scrolls through its own list
    # of teams instead of holding a single static frame.
    idleBoardHoldSeconds = 10

    # The rankings board's normal scroll speed (see displayScrollingRankings())
    # is tuned for days where games are about to start soon. On a day with no
    # games at all, it scrolls a bit slower instead, in keeping with
    # idleBoardHoldSeconds above.
    noGamesRankingsScrollDelay = 0.1

    # Minimum seconds between NCAA API refreshes once games are live (see
    # computeNextFetchTime()). Kept low enough to catch goals promptly without
    # cutting a full slate of games short just to poll.
    REFRESH_INTERVAL = 30

    # How many seconds before a game's scheduled start to begin polling the API,
    # instead of waiting for the exact second it's due to start.
    PREGAME_BUFFER = 120

    # The favorite team to feature on the favorite-team board. FAVORITE_TEAM_ABBR
    # is the char6 NCAA abbreviation (used to find the team's logo file and to
    # match it against game data's Home/Away Abbreviation fields -- see
    # getTeamData()). FAVORITE_TEAM_SHORT is its three-letter abbreviation (see
    # getTeamData()). FAVORITE_TEAM_SCHOOL is the exact "School" name the
    # rankings endpoint uses for this team (see getRankings()) -- this is a
    # separate constant, rather than derived from the other two, because the
    # rankings feed and the team-abbreviation feed use different naming
    # conventions (e.g. "MIA OH" / "MIA" vs. "Miami (OH)") that don't reliably
    # map to each other, so fuzzy-matching them was judged too fragile.
    FAVORITE_TEAM_ABBR = "MIA OH"
    FAVORITE_TEAM_SHORT = "MIA"
    FAVORITE_TEAM_SCHOOL = "Miami (OH)"

    # Run the scoreboard.
    runScoreboard()