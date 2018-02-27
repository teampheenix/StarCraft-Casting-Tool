![streaming-tool](https://user-images.githubusercontent.com/26044736/30242151-7d5fb0a8-9591-11e7-803f-6cda9bec3fe3.png)

# StarCraft Casting Tool
StarCraft Casting Tool (SCC Tool) is a small program written in Python 3 that can grab all relevant data of a Stracraft 2 Team League Match from either [Alpha SC2 Teamleague](http://alpha.tl/) (AlphaTL) or [Russian StarCraft Team League](http://hdgame.net/en/tournaments/list/tournament/rstl-13/) (RSTL) and process it such that the information can be readily included for streaming, e.g., in OBS-Studio, X-Split or any other similar streaming tool. Alternatively, the format of a *Custom Match* can be specified. The title of your Twitch stream and your Nightbot chat commands can be updated accordingly by a single click.

## Download

* **[Latest executable](https://github.com/teampheenix/StarCraft-Casting-Tool/releases/latest)** for Windows
* **[Source code](https://github.com/teampheenix/StarCraft-Casting-Tool/archive/master.zip)**

## Feature List

* **Match Grabber** for [AlphaTL](http://alpha.tl/) and [RSTL](http://hdgame.net/en/tournaments/list/tournament/rstl-12/)
* **Custom Match Format**: Bo1-Bo9, allkill format
* Two sets of **Map Icons**: Box and Landscape in `OBS_mapicons/icons_box` and `OBS_mapicons/icons_landscape`
* **Scoreboard** including team icons in `OBS_html`
* **Animated Player Intros** in `OBS_html` including playername & race via SC2-Client, team with logo via SCC Tool
* **TXT-files** with match infos in `OBS_data`
* **Twitch & Nightbot Integration**: Update your stream title or bot commands via a single click or automatically
* **Automatic Score Detection** via SC2-Client
* **Automatic FTP-Upload** of all resources to provide resources to a co-caster
* **Interaction with SC2-Observer-UI**: Automatically toggle Production Tab and set Score at the start of a Map
* Nearly **unlimited Customization** via Skins and CSS
* German and Russian language support.

## Discord Server

If you need support, have questions, want to be up-to-date on, or like to contribute to this project, join our [Discord server](https://discord.gg/G9hFEfh).

## Icon Preview

**[https://teampheenix.github.io/SCCT-archive/](https://teampheenix.github.io/SCCT-archive/)**

## General Information
The tool generates various browser sources (and text-files): Amongst others, two complete sets of corresponding *Map Icons* (including map, players, races, and score), a Score Icon (including the score, team names, and logos) and GSL-like *Intros* (including player, race and team). All of these files can be included via local files and optionally uploaded to a specified FTP server to provide these files remotely to others, for example, to your co-caster.

StarCraft Casting Tool can monitor your SC2-Client to detect the score, update it automatically, and provide corresponding player Intros. On Windows, the tool can additionally and automatically set and toggle the score in your SC2-Observer UI and toggle the production tab at the start of a game.

This tool should run on any operating system that supports Python 3, e.g., Windows, MacOS, and Linux (the interaction with the SC2-Observer-UI is currently only supported on Windows).  

## Installation

### Executable with Updater

**Only Windows: [Download the latest executable](https://github.com/teampheenix/StarCraft-Casting-Tool/releases/latest)** `StarCraft-Casting-Tool.exe`, place it in an preferable empty folder folder with *sufficient write-privileges* and execute it. After the first start a subfolder structure is generated and all additional data is downloaded - do not move or alter this data structure relative to the executable.

### Alternativ: Python Script

**Windows, MacOS, Linux: [Download the Source Code as Archive](https://github.com/teampheenix/StarCraft-Casting-Tool/archive/master.zip)** and exctract StarCraft Casting Tool, download the latest version of Python 3 at [https://www.python.org/downloads](https://www.python.org/downloads). This tool requires the additional Python Packages *PyQt5*, *requests*, *configparser*, *flask*, *obs-ws-rc*, *humanize*, *markdown2*, *pyupdater*, and on Windows additionally *pypiwin32*, *Pillow*, *pytesseract*. To install these packages execute the script `installPackages.py` once or do it manually (e.g., via *pip*). Execute `StarCraftCastingTool.pyw` or execute the command `python3 StarCraftCastingTool.pyw` to start the SCC Tool.

## Instructions for Use

Run StarCraft Casting Tool via `StarCraft-Casting-Tool.exe` (or `StarCraftCastingTool.pyw`). Enter the Match-URL of an AlphaTL or RSTL match in the *Match Grabber* tab, e.g., "http://alpha.tl/match/3000", and press *Load Data from URL*. Alternatively one can create a match in the *Custom Match* tab.  Edit the data if necessary. The sliders control the score of each map. Press *Update OBS Data* or alter the score to update the data for streaming. The top slider is to select *your* team. Once selected the border of the Map Icons turn (by default) green or red depending on the result. To select your team automatically you can add it to *Favorite Teams* list under *Settings: Misc*. Similarly you can enter your players' nicknames into *Favorite Players* for auto completion.

### Data for Streaming
can be found in the directory `OBS_data` and be included into OBS (or any similar streaming tool) via *Text read from local file*. If you want to include the team logos and the matchbanner, it is recommended to include them as *browser source from local file* via the HTML files given in the directory `OBS_html` *(Score Icon size: 1280x100px, Logo sizes: 300x300px, Intro sizes: Your screen resolution)*. The Map Icons can be found in the directory `OBS_mapicons` and have to be included via *browser source from local file* as well. There are two type of icons: box icons in `OBS_mapicons/icons_box` and landscape icons in `OBS_mapicons/icons_landscape`. One can either include each Map Icon separately *(box size: 280x270px, landscape size: 1010x110px)* and arrange them freely or one can include them via the single html file `all_maps.html` *(the chosen dimension of the browser source determines the arrangement of the icons)*. Note that you can scale the browser source(s) down/up if you want to make the icons smaller/larger. Except of the intros all browser sources refresh automatically - you should have to refresh the cache of this browser sources only if you select a different skin/style or a new update has been applied.

If the tool is missing a map, you can add them in the *Map Manager* in *Settings: Misc*.

### Twitch & Nightbot
To update your [Twitch](https://www.twitch.tv/) title (and set your game to *StarCraft 2*) or [Nightbot](https://nightbot.tv/) command via click on *Update Twitch Title* or *Update Nightbot* you have to set your Twitch *Channel* and/or generate an corresponding access token. This can be done via *Settings: Connections*. Note that you can also change the title of Twitch channels that do not belong to the user you have generated the access token with as long as this user is registered as an editor of corresponding channel. The format of your new title can be customized via the *Title Template* with the use of placeholders (hover over the input field to get a list of all available placeholders) and specified under *Settings: Connections*.

### Background Tasks

#### Automatic Score Detection
To active the automatic detection of the score via the SC2-Client-API check the box *Auto Score Update* of the *Background Tasks*. This score detection does only work if you either play or observe a decided game (game length > 60 seconds) with a pair of players that were specified on one of sets. If there are multiple sets eligible, the score is entered for the first undecided set.

#### Set Ingame Score
Some Observer Interfaces like [GameHeart](https://sites.google.com/site/ahlismods/gameheart-obs-ui/changelog-1vs1) have a toogle-able score, that can be toogled by pressing `Ctrl+Shift+S`. When using other Oberserver-UI like WCS that have no toggle-able score and don't have assigned this hot-key combination SC2 will be interpret it as `Ctrl+S` and typically disable your sound. Therefore, SCC-Tool does not press `Ctrl+Shift+S` to toggle the score in the Observer-UI by default at start of a game. To enable this feature, you have to set the checkbox under *Settings: Misc - AlphaTL & Ingame Score*.

Sometimes the order of players given by the SC2-Client-API differs from the order in the Observer-UI resulting in a swapped match score when using *Set Ingame Score*. To correct this you can activate Optical Character Recognition once you have to downloaded and installed [Tesseract-OCR](https://github.com/UB-Mannheim/tesseract/wiki#tesseract-at-ub-mannheim).

#### Player Intros
[![intro-demo](https://user-images.githubusercontent.com/26044736/30003831-4fe09b14-90c4-11e7-9593-439454d4e324.gif)](https://youtu.be/JNuAr63L0wM)

Include the Player Intros as browser sources (using the full height and width of your display), activate the option *Shutdown source when not visible* and assign hot-keys to make the sources visible. The content of the intros refresh accordingly if the task *Provide Player Intros* is activated and a game or replay is started in the StarCraft 2 client. To automatically hide the browser sources of the Player Intros afterwards (only OBS studio) you have to install the [OBS websocket plugin](https://github.com/Palakis/obs-websocket/releases/latest), activate it in OBS studio, specify the corresponding SCC-Tool settings under *Settings: Connections*, and name the Intro sources accordingly (default names are "Intro1" and "Intro2"). The first intro, `intro1.html`, is always corresponding to the player your observer camera is centered on at start of a game.

## Customization

Some basic options for customization can be found under *Settings: Styles*, for example, alternative styles/skins for the Map Icons, Score Icon, Intros and option to specify border colors. For additional **nearly unlimited customization** of the Icons you can make your own custom skins via [CSS](https://www.w3schools.com/css/) by creating new alternative *css*-files and placing them into `OBS_mapicons/src/css/box_styles`, `OBS_mapicons/src/css/landscape_styles`, `OBS_html/src/css/score_styles`, or `OBS_html/src/css/intro_styles` respectively. If you do so, please share your custom skins with this project. If you want help implementing your own icon skin with CSS or just want to share an idea for a skin join the [Discord server](https://discord.gg/G9hFEfh).

## Help, Bug-Report, Suggestions & Contribution

If you need help, have bugs to report, have suggestions to make, or want to contribute to this project in any way message me (*pres.sure#5247*) on [Discord](https://discordapp.com/) or join the Discord Server of this project via https://discord.gg/G9hFEfh.

In the case of a bug report please provide the log-file `scctool.log` (and `installpackages.log` if applicable).

## Support

If you want to support this project join our [Discord Server](https://discord.gg/G9hFEfh) and consider subscribing to [twitch.tv/teampheenix](https://www.twitch.tv/teampheenix) or [donate directly](https://streamlabs.com/scpressure). Alternatively and free of cost - just follow the team pheeniX and my personal [twitch.tv/scpressure](https://www.twitch.tv/scpressure) Twitch channel!
