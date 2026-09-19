# Raspberry Pi LED Matrix NCAA Men's Hockey Scoreboard

![License: GPL-3.0](https://img.shields.io/badge/license-GPL--3.0-blue.svg)
![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![Platform: Raspberry Pi](https://img.shields.io/badge/platform-Raspberry%20Pi-c51a4a.svg)

Live NCAA Division I men's ice hockey scores on a 64x32 RGB LED matrix driven by a Raspberry Pi. Follow every game of the night, and when the puck isn't dropping, see your favorite team's record, next game, and the current NPI rankings.

![Example](examples/scoreboard.gif)

Forked from [rpi-led-nhl-scoreboard](https://github.com/gidger/rpi-led-nhl-scoreboard), which was inspired by [nhl-led-scoreboard](https://github.com/riffnshred/nhl-led-scoreboard). All game data comes from the [NCAA API](https://ncaa-api.henrygd.me/openapi#description/introduction).

## Features

**Game boards**
- Cycles through every D1 men's hockey game of the day: pre-game, live, final, and postponed.
- Live games show the period, time remaining, and score. Intermissions show `INT`.
- Goal alert: when a team scores, its number flashes red and fades to white.
- Final scores show `OT`, `2OT`-`5OT`, or `SO` when applicable. Postponed games show `PPD`.
- Shows the previous night's results until 12:00 PM local time, then switches to the current day's games.
- Team logos for every Division I program, with the NCAA logo as a fallback (for example, Division II/III or exhibition opponents).

**Idle boards** (days with no games, or before the first puck drop)
- **Favorite team board:** logo, W-L-T record, and next scheduled game (home/away, date, time).
- **Rankings board:** scrolling top 20 of the current NPI rankings. Each row shows rank, team abbreviation, and record, colored with that team's own primary color. Your favorite team is bold and always shown, even outside the top 20.
- **No Games Today** screen.

**Built to run unattended**
- Adaptive brightness by time of day: brightest at noon, dimmest overnight.
- Smart API polling: sleeps until tomorrow on days with no games, wakes shortly before the first scheduled start, and refreshes every 30 seconds while games are live.
- Network problems never blank the display: it keeps showing the last good data and lights a single red pixel in the bottom-right corner.
- Runs under Supervisor (with a web dashboard) or a cron startup script.

**Developer friendly**
- Run the full scoreboard on any computer, without a Pi or matrix, using [RGBMatrixEmulator](https://github.com/ty-porter/RGBMatrixEmulator). The script auto-detects which driver is available.

## Hardware

- Raspberry Pi (any model with a 40-pin GPIO header)
- 64x32 RGB LED matrix panel (HUB75)
- [Adafruit RGB Matrix HAT or Bonnet](https://www.adafruit.com/product/2345) with a 5V power supply
- MicroSD card

The matrix settings in `collegehockey-led-scoreboard.py` (`hardware_mapping = 'adafruit-hat-pwm'`, `gpio_slowdown = 2`, and so on) assume the Adafruit HAT with the PWM mod described in the [rpi-rgb-led-matrix docs](https://github.com/hzeller/rpi-rgb-led-matrix). Adjust the `RGBMatrixOptions` block in the `__main__` section for other wiring.

## Installation Instructions

These instructions assume some basic knowledge of Unix and how to edit files via the command line.

1. Flash an SD card with [Raspberry Pi OS Lite](https://www.raspberrypi.org/software/operating-systems/) on your personal computer.

   > **Tip:** [Raspberry Pi Imager](https://www.raspberrypi.com/software/) can preset Wi-Fi, SSH, hostname, and timezone while flashing. If you use it, you can skip steps 3, 4, and 6. On newer OS releases, `config.txt` is at `/boot/firmware/config.txt`.

2. Unplug and replug the SD card.

3. Add an empty file named `ssh` to the boot directory on the SD card.

   ```
   touch ssh
   ```

4. Add and configure `wpa_supplicant.conf` in the same directory. Set your network information and two-digit [country code](https://www.iban.com/country-codes).

   ```
   country=US
   ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
   update_config=1

   network={
       ssid="NETWORK-NAME"
       psk="NETWORK-PASSWORD"
   }
   ```

5. Put the SD card in your Raspberry Pi. Boot up and SSH into it.

6. Set location/time zone and a new password via [raspi-config](https://www.raspberrypi.org/documentation/configuration/raspi-config.md).

   ```
   sudo raspi-config
   ```

7. Get the latest updates.

   ```
   sudo apt-get update -y
   sudo apt-get upgrade -y
   ```

8. Disable on-board sound (it conflicts with the matrix driver).

   ```
   sudo nano /boot/config.txt
   ```

   Edit the `dtparam` line to look like this:

   ```
   dtparam=audio=off
   ```

9. Disable Wi-Fi sleep.

   ```
   sudo nano /etc/rc.local
   ```

   Above the line that says `exit 0`, add the following and save:

   ```
   /sbin/iw wlan0 set power_save off
   ```

10. Install pip3 and git.

    ```
    sudo apt-get install python3-pip git -y
    ```

11. Clone this repository to your home directory (`--recursive` pulls in the LED matrix driver).

    ```
    cd ~/
    git clone --recursive https://github.com/byrneta/collegehockey-led-scoreboard.git
    ```

12. Build and install the LED matrix Python package.

    ```
    cd ~/collegehockey-led-scoreboard/submodules/rpi-rgb-led-matrix
    sudo apt-get update && sudo apt-get install python3-dev python3-pillow -y
    make build-python PYTHON=$(which python3)
    sudo make install-python PYTHON=$(which python3)
    ```

13. Install the remaining Python requirements.

    ```
    cd ~/collegehockey-led-scoreboard
    pip3 install -r requirements.txt
    ```

14. [Set your favorite team](#choosing-your-favorite-team), then test it:

    ```
    sudo python3 collegehockey-led-scoreboard.py
    ```

    (`sudo` is required for the real matrix driver.) Press `Ctrl+C` to stop.

## Configuration

### Choosing your favorite team

Near the bottom of `collegehockey-led-scoreboard.py`, in the `__main__` block, three constants control which team gets the favorite-team board and the bold highlight in the rankings scroll:

```python
FAVORITE_TEAM_ABBR = "MIA OH"        # NCAA "char6" code, a key in getTeamData()
FAVORITE_TEAM_SHORT = "MIA"          # three-letter display abbreviation
FAVORITE_TEAM_SCHOOL = "Miami (OH)"  # exact school name used by the rankings feed
```

To switch teams, find your team in `getTeamData()` for the first two values and in `getSchoolAbbrMap()` for the exact school name. The rankings feed and game feed name teams differently, so all three need to match.

### Other settings

These are all near the bottom of the `__main__` block:

| Setting | Default | What it does |
|---|---|---|
| `maxMatrixBrightness` | `60` | Peak brightness (at noon). Actual brightness scales down at night, with a floor of 15. |
| `cycleTime` | `7` (10 with one game) | Seconds each game is shown. Set automatically based on how many games there are. |
| `idleBoardHoldSeconds` | `10` | Seconds each idle board (No Games, favorite team) stays up. |
| `noGamesRankingsScrollDelay` | `0.1` | Rankings scroll speed on days with no games (seconds per pixel). |
| `REFRESH_INTERVAL` | `30` | Seconds between API refreshes while games are live. |
| `PREGAME_BUFFER` | `120` | How many seconds before the first start time to begin polling. |

## Auto Startup

### Supervisor (Recommended)

Supervisor runs the scoreboard for you, restarts it if it crashes, and gives you a web dashboard you can use from your phone.

1. Install Supervisor.

   ```
   sudo apt-get install supervisor
   ```

2. Open the Supervisor config file and add these two lines at the bottom.

   ```
   sudo nano /etc/supervisor/supervisord.conf
   ```

   ```
   [inet_http_server]
   port=*:9001
   ```

   Save with `Ctrl+X`, `y`, `Enter`.

3. Create a config for the scoreboard.

   ```
   sudo nano /etc/supervisor/conf.d/college-hockey-scoreboard.conf
   ```

   ```
   [program:college-hockey-scoreboard]
   command=sudo python3 collegehockey-led-scoreboard.py
   directory=/home/pi/collegehockey-led-scoreboard
   autostart=true
   autorestart=true
   ```

   Adjust `directory` if your username isn't `pi`.

4. Reboot the Pi. The scoreboard should start on its own. To open the dashboard, browse to your Pi's IP address followed by `:9001` (for example `192.168.2.19:9001`). If you see the dashboard but no process, reboot and refresh.

From the dashboard you can start, restart, and stop the scoreboard. Click the process name to see its latest log, which is the first place to look when something goes wrong.

### Startup Script

1. Create the script.

   ```
   nano ~/start-scoreboard.sh
   ```

   ```bash
   #!/bin/bash
   cd /home/pi/collegehockey-led-scoreboard
   n=0
   until [ $n -ge 10 ]
   do
      sudo python3 collegehockey-led-scoreboard.py && break
      n=$((n+1))
      sleep 10
   done
   ```

   **Optional:** to have the scoreboard update itself from GitHub on every reboot, use this version instead. It's handy for a gift for a non-technical person, but it won't start anything until the Pi can reach GitHub.

   ```bash
   #!/bin/bash
   cd /home/pi/collegehockey-led-scoreboard

   while ! ping -c 1 -W 1 github.com; do
       echo "Waiting for GitHub..."
       sleep 1
   done

   git pull origin main

   n=0
   until [ $n -ge 10 ]
   do
       sudo python3 collegehockey-led-scoreboard.py && break
       n=$((n+1))
       sleep 10
   done
   ```

2. Make it executable.

   ```
   chmod +x ~/start-scoreboard.sh
   ```

3. Run it at boot.

   ```
   sudo crontab -e
   ```

   Add to the bottom:

   ```
   @reboot /home/pi/start-scoreboard.sh > /home/pi/cron.log 2>&1
   ```

4. Save, exit, and test with `sudo reboot`.

## Running in the Emulator (no Pi required)

The fastest way to try or develop the scoreboard is on a regular computer (Mac, Linux, or Windows/WSL) using [RGBMatrixEmulator](https://github.com/ty-porter/RGBMatrixEmulator). The script tries to import the real `rgbmatrix` driver first and automatically falls back to the emulator if it isn't installed, so no flags or code changes are needed.

Requires Python 3.9+, `git`, and `pip`.

```
git clone https://github.com/byrneta/collegehockey-led-scoreboard.git
cd collegehockey-led-scoreboard
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install RGBMatrixEmulator
python3 collegehockey-led-scoreboard.py
```

You don't need `--recursive` for the emulator: the `submodules/rpi-rgb-led-matrix` submodule is only used to build the real hardware driver. `RGBMatrixEmulator` is deliberately not in `requirements.txt` for the same reason.

By default the 64x32 display renders as colored blocks in your terminal. Press `Ctrl+C` to stop.

**View it in a browser instead:** in `emulator_config.json`, change `"display_adapter": "terminal"` to `"browser"`, run the script again, and open `http://localhost:8888` (the port is set in the same file).

## How It Works

- **Games:** the NCAA API is queried for the day's scoreboard. Before noon local time, it shows the previous day's games so you can catch last night's results.
- **Polling:** it only calls the API when something can change. No games: it waits until midnight. All games still to start: it waits until 2 minutes before the earliest. Otherwise: every 30 seconds.
- **Idle rotation:** when there are no games (or none have started), it rotates through No Games Today (if applicable), the favorite-team board, and the scrolling rankings.
- **Favorite team's next game:** the API has no team-schedule endpoint, so the script reads the season's calendar of game dates and scans forward day by day until it finds a game involving your team.
- **Team colors:** each team's row color in the rankings comes from the most common non-neutral color in its logo file, brightened if needed to read on black.

## Notes and Known Limitations

1. Division II/III and other exhibition opponents appear as the NCAA logo.
2. Men's Division I only.
3. Start times are shown as reported by the NCAA API (Eastern Time), without AM/PM.
4. The rankings come from the API's `pairwise` route, which now serves NPI data.
5. Teams not yet in `getTeamData()` get a three-letter fallback name and the NCAA logo. New programs need an entry in `getTeamData()` and `getSchoolAbbrMap()`, plus a logo in `assets/images/team logos/png/`.
6. If the NCAA API can't be reached when the scoreboard first starts, it shows "No Games Today" and retries hourly.
7. The favorite team is set by editing the script. A red pixel in the bottom-right corner means the most recent refresh failed.
8. The NCAA API is a free, community-run service. Please don't shorten `REFRESH_INTERVAL` aggressively.

## Troubleshooting

- **The scoreboard isn't showing anything:** check the Supervisor log (or `cron.log`) for errors. Confirm you're running with `sudo`, and that on-board sound is disabled (step 8).
- **Panel flickers or shows noise:** try a higher `gpio_slowdown` in the `RGBMatrixOptions` block. See the [rpi-rgb-led-matrix troubleshooting guide](https://github.com/hzeller/rpi-rgb-led-matrix#troubleshooting).
- **"Resource deadlock avoided" when a logo loads (emulator):** if your clone lives in iCloud Drive or another cloud-synced folder, some logo PNGs under `assets/images/team logos/png/` may be undownloaded placeholders. Use "Download Now" on the folder, or copy the repo outside the synced folder.
- **Nothing shows in the terminal (emulator):** some terminals don't render the block characters well. Switch to the browser adapter (see above).
- **Updating:** `git pull`, then `pip3 install -r requirements.txt`.

## Credits

- [gidger/rpi-led-nhl-scoreboard](https://github.com/gidger/rpi-led-nhl-scoreboard) and [riffnshred/nhl-led-scoreboard](https://github.com/riffnshred/nhl-led-scoreboard) for the original projects.
- [hzeller/rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) for the LED matrix driver.
- [ty-porter/RGBMatrixEmulator](https://github.com/ty-porter/RGBMatrixEmulator) for the emulator.
- [henrygd/ncaa-api](https://ncaa-api.henrygd.me/) for the NCAA data.
- Tamzen bitmap fonts.

This is an unofficial fan project and is not affiliated with or endorsed by the NCAA or any university. Team names and logos are trademarks of their respective institutions.

## License

[GPL-3.0](LICENSE)