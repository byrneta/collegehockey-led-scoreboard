# CollegeHockey-LED-scoreboard

Major work in progress fork of the awesome [nhl-led-scoreboard](https://github.com/riffnshred/nhl-led-scoreboard) to get it working with college hockey. Since the API is limited in the amount of information available, I am focusing on getting the bare bones functional before building it out further.

## Priorities

- Research information available on API 
- Upcoming Games 
- In Game Updates
- Scrolling Schedule (if API allows)

## Configuration
~~First thing first, Open the config.json file from the config directory to configure your scoreboard.~~
FIRST, you will need to make a copy of the config.json.sample and rename it config.json. Then open it and modify the options. 

### Modes
These are options to set the scoreboard to run in a certain mode. This is where you enable the live game mode
while will show the scoreboard of your favorite game when it's live.
| Settings    | Type | Parameters  | Description                                                           |
|-------------|------|-------------|-----------------------------------------------------------------------|
| `debug`     | Bool | true, false | Enable the debug mode which shows the console on your scoreboard      |
| `live_mode` | Bool | true, false | Enable the live mode which show live game data of your favorite team. |

### Preferences
All the data related options. 
| Settings                 | Type   | Parameters                                       | Description                                                                                                                                                                          |
|--------------------------|--------|--------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `live_game_refresh_rate` | INT    | `15`                                             | The rate at which a live game will call the API to catch the new data. It is NOT advised to reduce this. (Default 15 sec) |
| `time_format`            | String | `"12h"` or `"24h"`                               | The format in which the game start time will be displayed.                                                                                                                           |
| `end_of_day`             | String | `"12:00"`                                        | A 24-hour time you wish to consider the end of the previous day before starting to display the current day's games.                                                                  |
| `teams`                  | Array  | `["Canadiens", Blackhawks", "Avalanche"]`        | List of preferred teams. First one in the list is considered the favorite. If left empty, the scoreboard will be in "offday" mode                                                    |                                                                                                                                                      |                                                                                                                                                          |

### Goal Animations
The goal animations can be set for both teams of just the preferred teams.

| Settings         | Type | Parameters      | Description      |
|------------------|------|-----------------|------------------|
| `pref_team_only` | Bool | `true`, `false` | self explanatory |

### Teams
For the `teams` parameters, only put the team's ID. You can copy and paste your team's name from this table.

| Team Name            | ID     |
|----------------------|--------|
| Air Force          | `2005` |
| Alabama Huntsville | `2008` |
| Alaska Anchorage   | `1`    |
| Alaska             | `298`  |
| American Intl      | `2022` |
| Arizona St.        | `9`    |
| Army               | `349`  |
| Bemidji St.        | `132`  |
| Bentley            | `2060` |
| Boston College     | `103`  |
| Boston University  | `104`  |
| Bowling Green      | `189`  |
| Brown              | `225`  |
| Canisius           | `2099` |
| Clarkson           | `2137` |
| Colgate            | `2142` |
| Colorado College   | `2144` |
| Connecticut        | `41`   |
| Cornell            | `172`  |
| Dartmouth          | `159`  |
| Denver             | `2172` |
| Ferris St.         | `2222` |
| Harvard            | `108`  |
| Holy Cross         | `107`  |
| Lake Superior      | `285`  |
| Maine              | `311`  |
| Massachusetts      | `113`  |
| Mercyhurst         | `2385` |
| Merrimack          | `2771` |
| Miami              | `193`  |
| Michigan St.       | `127`  |
| Michigan Tech      | `2392` |
| Michigan           | `130`  |
| Minnesota Duluth   | `134`  |
| Minnesota St.      | `2364` |
| Minnesota          | `135`  |
| Nebraska Omaha     | `2437` |
| New Hampshire      | `160`  |
| Niagara            | `315`  |
| North Dakota       | `155`  |
| Northeastern       | `111`  |
| Northern Michigan  | `128`  |
| Notre Dame         | `87`   |
| Ohio St.           | `194`  |
| Penn State         | `213`  |
| Princeton          | `163`  |
| Providence         | `2507` |
| Quinnipiac         | `2514` |
| RIT                | `178`  |
| Robert Morris      | `2523` |
| RPI                | `2528` |
| Sacred Heart       | `2529` |
| St. Cloud St.      | `2594` |
| St. Lawrence       | `2779` |
| UMass Lowell       | `2349` |
| Union NY           | `2785` |
| Vermont            | `261`  |
| Western Michigan   | `2711` |
| Wisconsin          | `275`  |
| Yale               | `43`   |

## Shout-out

This project was inspired by the [nhl-led-scoreboard](https://github.com/riffnshred/nhl-led-scoreboard) which was based on [mlb-led-scoreboard](https://github.com/MLB-LED-Scoreboard/mlb-led-scoreboard). I based some of the API calls off the [nfl-led-scoreboard](https://github.com/mikemountain/nfl-led-scoreboard) as well.

## Licensing
This project uses the GNU Public License. If you intend to sell these, the code must remain open source.
