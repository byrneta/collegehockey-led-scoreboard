import ncaa_api.game
import ncaa_api.info
import calendar


def day(year, month, day):
    """
        Return a list of games for a certain day.
    """

    # get the days per month
    daysinmonth = calendar.monthrange(year, month)[1]
    # do not even try to get data if day is too high
    if daysinmonth < day:
        return []
    # get data
    data = ncaa_api.game.scoreboard(year, month, day)
    return [ncaa_api.game.GameScoreboard(data[x]) for x in data]


def teams():
    """Return list of Info objects for each team"""
    return [ncaa_api.info.Info(x) for x in ncaa_api.info.team_info()]


def overview(game_id):
    """Return Overview object that contains game information."""
    return ncaa_api.game.Overview(ncaa_api.game.overview(game_id))


def game_status_info():
    return ncaa_api.info.status()


def current_season_info():
    return ncaa_api.info.current_season()
