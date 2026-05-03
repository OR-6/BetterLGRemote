# LGWebOSRemote
Command line webOS remote for LGTVs. This tool uses a connection via websockets to port 3000 on newer LG TVs, there are other tools which use a restful connection to port 8080 however that port is closed on newer firmware versions.

## A note from the developer

My LG TV is now so out of date that largely what is developed here is tested, improved and debugged by the community. As it goes my TV works fine and I'm not the kind of person to create more unnecessary electrical waste than I need to so as long as my current TV works, it's largely down to you guys.

A big thanks for the contributions over the years too, lots of people have made lots of changes to this project over time, and it would only be as useful as it is with their help.


## Supported models

### Tested with

  * 43LM6300PSB
  * 24TL520S
  * 43UN73003LC
  * 43UJ630V-ZA
  * 43UR78006LK
  * 60UJ6300-UA
  * HU80KG.AEU (CineBeam 4K)
  * OLED48A2
  * OLED55B7
  * OLED55C9
  * OLED55CX5LB
  * OLED55CXAUA
  * OLED55G29LA
  * OLED65B9PUA
  * OLED77CX9LA
  * OLED77GX
  * OLED48C1 (ssl)
  * OLED42C2 (ssl)
  * OLED48C2 (ssl)
  * OLED83C4 (ssl)
  * SK8500PLA
  * SM9010PLA
  * UF776V
  * UF830V
  * UH650V
  * UU668V
  * UJ6309
  * UJ635V
  * UJ6570
  * UJ701V
  * [please add more!]

Tested with python 3.9 on Debian Unstable.
Tested with python 3.10 on Windows 10/11
Tested with 3.10 on WSL (Ubuntu 20.04)
Tested with python 3.12 on macOS

### Likely supports

All devices with firmware major version 4, product name "webOSTV 2.0"

## Available Commands
	lgtv scan
	lgtv auth <host> MyTV
	lgtv setDefault MyTV
	lgtv --name MyTV audioStatus
	lgtv --name MyTV audioVolume
	lgtv --name MyTV closeAlert <alertId>
	lgtv --name MyTV closeApp <appid>
	lgtv --name MyTV createAlert <message> <button>
	lgtv --name MyTV execute <command>
	lgtv --name MyTV getCursorSocket
	lgtv --name MyTV getForegroundAppInfo
	lgtv --name MyTV getPictureSettings
	lgtv --name MyTV getPowerState
	lgtv --name MyTV getSoundOutput
	lgtv --name MyTV getSystemInfo
	lgtv --name MyTV getTVChannel
	lgtv --name MyTV input3DOff
	lgtv --name MyTV input3DOn
	lgtv --name MyTV inputChannelDown
	lgtv --name MyTV inputChannelUp
	lgtv --name MyTV inputMediaFastForward
	lgtv --name MyTV inputMediaPause
	lgtv --name MyTV inputMediaPlay
	lgtv --name MyTV inputMediaRewind
	lgtv --name MyTV inputMediaStop
	lgtv --name MyTV listApps
	lgtv --name MyTV listLaunchPoints
	lgtv --name MyTV listChannels
	lgtv --name MyTV listInputs
	lgtv --name MyTV listServices
	lgtv --name MyTV mute <true|false>
	lgtv --name MyTV notification <message>
	lgtv --name MyTV notificationWithIcon <message> <url>
	lgtv --name MyTV off
	lgtv --name MyTV on
	lgtv --name MyTV openAppWithPayload <payload>
	lgtv --name MyTV openBrowserAt <url>
	lgtv --name MyTV openYoutubeId <videoid>
	lgtv --name MyTV openYoutubeURL <url>
	lgtv --name MyTV openYoutubeLegacyId <videoid>
	lgtv --name MyTV openYoutubeLegacyURL <url>
	lgtv --name MyTV sendButton <button>
	lgtv --name MyTV serialise
	lgtv --name MyTV setDeviceInfo <id> <icon> <label>
            # Example: lgtv --name MyTV setDeviceInfo HDMI_2 hdmi.png "My Input".
            # Purpose: force TV to disable so-called "PC mode" for inputs where the attached device incorrectly or undesiredly signals itself as "PC", eg. Raspberry Pi with LibreELEC.
	lgtv --name MyTV setInput <input_id>
	lgtv --name MyTV setSoundOutput <tv_speaker|external_optical|external_arc|external_speaker|lineout|headphone|tv_external_speaker|tv_speaker_headphone|bt_soundbar>
	lgtv --name MyTV screenOff
	lgtv --name MyTV screenOn
	lgtv --name MyTV setTVChannel <channelId>
	lgtv --name MyTV setVolume <level>
	lgtv --name MyTV startApp <appid>
	lgtv --name MyTV swInfo
	lgtv --name MyTV volumeDown
	lgtv --name MyTV volumeUp

## Install

Requires wakeonlan, websocket for python (python3-websocket for python3), and getmac.
python-pip (python3-pip for python3) and git are required for the installation process.

    python -m venv lgtv-venv
    source lgtv-venv/bin/activate
    pip install git+https://github.com/OR-6/BetterLGRemote

To install it system wide:

	sudo mkdir -p /opt
	sudo python -m venv /opt/lgtv-venv
	source /opt/lgtv-venv/bin/activate
	sudo pip install git+https://github.com/OR-6/BetterLGRemote

or with [pipx](https://pipx.pypa.io/stable/):

	pipx install git+https://github.com/OR-6/BetterLGRemote.git

## Example usage
    # Scan/Authenticate
    $ lgtv scan
    {
        "count": 1,
        "list": [
            {
                "address": "192.168.1.31",
                "model": "UF830V",
                "uuid": "10f34f86-0664-f223-4b8f-d16a772d9baf"
            }
        ],
        "result": "ok"
    }
    $ lgtv auth 192.168.1.31 MyTV
    # At this point the TV will request pairing, follow the instructions on screen

    $lgtv --no-ssl auth 192.168.1.100 OldTV
    # Authenticate without SSL (if needed)

    # Commands are basically
    $ lgtv --name TVNAME COMMAND COMMAND_ARGS

    $ lgtv --name MyTV on
    $ lgtv --name MyTV off

    $lgtv --no-ssl --name OldTV volumeDown
    # Using --no-ssl (for older TVs)

    # If you have the youtube plugin
    $ lgtv --name MyTV openYoutubeURL https://www.youtube.com/watch?v=dQw4w9WgXcQ

    # Otherwise, this works reasonably well
    $ lgtv --name MyTV openBrowserAt https://www.youtube.com/tv#/watch?v=dQw4w9WgXcQ

    # You can set the default TV so the `--name` argument can be skipped
    $ lgtv setDefault MyTV

## SSL

Starting 25th of January 2023 LG has deprecated insecure ws connections, ssl is now required. Because of this, should you wish to not use it on older firmware devices you can append the argument "no-ssl" at the back. It connects to 3001 with wss, But it wont connect if no-ssl is provided 

### Example
```
$ lgtv auth 192.168.1.31 MyTV
$ lgtv --name MyTV off
$ lgtv --name MyTV screenOff
```

sendButton args:
['asterisk', 'back', 'blue', 'channel_down', 'channel_up', 'click', 'down', 'enter', 'exit', 'fast_forward', 'green', 'home', 'left', 'pause', 'play', 'red', 'rewind', 'right', 'stop', 'up', 'volume_down', 'volume_up', 'yellow']

## Logging Output
 
With `--debug` flag, you'll see detailed information:
 
```
INFO:root:Scanning network for TV: LivingRoomTV
INFO:root:Found TV 'LivingRoomTV' at new IP: 192.168.1.105
INFO:root:Updated IP for 'LivingRoomTV' from 192.168.1.100 to 192.168.1.105 in /home/user/.config/lgtv/config.json
INFO:root:Retrying with new IP: 192.168.1.105
```

## Caveats

You need to auth with the TV before being able to use the on command as it requires the mac address.

## TODO

Implement the following features:

	closeToast
	getSystemSettings

## Bugs

I couldn't test youtube because it seems the app isn't installed and not available to download right now
maybe they're updating it?
