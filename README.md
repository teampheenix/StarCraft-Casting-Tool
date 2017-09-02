# StarCraft Casting Tool
![streaming-tool](https://user-images.githubusercontent.com/26044736/29998600-a3053222-902f-11e7-99c5-5f3055f9225b.png)

## General Information

StarCraft Casting Tool (SCC-Tool) is a Python 3.6 script that can grab all relevant data of a Stracraft 2 Team League Match from either [Alpha SC2 Teamleague](http://alpha.tl/) (AlphaTL) or [Russian Starcraft Team League](http://hdgame.net/en/tournaments/list/tournament/rstl-12/) (RSTL) and process it such that the information can be readily included for streaming, e.g., in OBS-Studio, X-Split or any other similar streaming tool. Alternatively, the format of a *Custom Match* can be specified. The title of your Twitch stream and your Nightbot chat commands can be updated accordingly by a single click. 

The tool generates various browser sources (and text-files): Amongst others, two complete sets of corresponding *map icons* (including map, players, races, and score), a score icon (including the score, team names, and logos) and GSL-like *intros* (including player, race and team). All of these files can be included via local files and optionally uploaded to a specified FTP server to provide these files via remotely to others, for example, to your co-caster.

StarCraft Casting Tool can monitor your SC2-Client to dectect the score, update it automatically, and provide corresponding player intros. On Windows, the tool can additionally and automatically set and toogle the score in your SC2-Observer UI and toggle the production tab at the start of a game.

This tool should run on any operating system that supports Python 3, e.g., Windows, MacOS, and Linux (the interaction with the SC2-Observer-UI is currently only supported on Windows).  

## Installation

[Download](https://github.com/teampheenix/StarCraft-Casting-Tool/archive/master.zip) and exctract StarCraft Casting Tool, download the latest version of Python 3.6+ at https://www.python.org/downloads. This tool requires the additional Python Packages *PyQt5*, *requests*, *configparser*, *flask*, *obs-ws-rc* and on Windows additonally *pypiwin32*. To install these packages execute the script `installPackages.py` once or do it manually (e.g., via *pip*).

## Instructions for Use

Execute `StarCraftCastingTool.pyw` to start the SCC-Tool. Enter the Match-URL of an AlphaTL or RSTL match in the *Match Grabber* tab, e.g., "http://alpha.tl/match/2392", and press *Load Data from URL*. Alternatively one can create a match in the *Custom Match* tab.  Edit the data if necessary. The sliders control the score of each map. Press *Update OBS Data* or alter the score to update the data for streaming, which can be found in the directory `OBS_data` and can be included into OBS (or any similar streaming tool) via *Text read from local file*. If you want to include the team logos and the matchbanner, it is recommended to include them as *browser source from local file* via the html files given in the directory `OBS_html` *(Banner: 1200x740px, Logos: 300x300px)*. The map icons can be found in the directory `OBS_mapicons` and have to be included via *browser source from local file* as well. There are two type of icons: box icons in `OBS_mapicons/icons_box` and landscape icons in `OBS_mapicons/icons_landscape`. One can either include each map icon separatly *(box size: 280x270px, landscape size: 750x75px)* and arrange them freely or one can include them via the single html file `all_maps.html` *(the choosen dimension of the browser source determines the arrangement of the icons)*. Note that you can scale the browser source(s) down/up if you want to make the icons smaller/larger.

To update your [Twitch](https://www.twitch.tv/) title (and set your game to *Starcraft 2*) or [NightBot](https://nightbot.tv/) command via click on *Update Twitch Title* or *Update NightBot* you have to set your Twitch *Channel* and/or generate an corresponding access token. This can be done via *Settings: Connections*. Note that you can also change the title of twitch channels that do not belong to the user you have generated the access token with as long as this user is registered as an editor of corresponding channel. The format of your new title can be customized via the *Title Template* with the use of placeholders and specified under *Settings: Connections*.

The top slider is to select *your* team. Once selected the border of the map icons turn (by default) green or red depending on the result. To select your team by default you can add it in *Favorit Teams* list under *Settings: Misc*. Similiarly you can enter your players' nicknames into *Favorit Players* for autocompletion.

To active the automatic detection of the score via the SC2-Client-API check the box *Score Update* of the *Automatic Background Tasks*. This score detection does only work if you either play or observe a decided game (game length > 60 seconds) with a pair of players that were specified on one of sets. 

To automatically hide the browser sources of the player intros (only OBS studio) you have to install the OBS websocket plugin (https://obsproject.com/forum/resources/obs-websocket-remote-control-of-obs-studio-made-easy.466/), active it in OBS, specify the corresponding SCC-Tool settings under *Settings: Connections*.

## Customization

Some basic options for customization can be found under *Settings: Styles*, for example, alternative stlyes/skins for the map icons and option to specify border colors. For additional (nearly unlimited) customization of the map icons you can make your own custom skins via [CSS](https://www.w3schools.com/css/) by creating new alternative *css*-files and placing them into `OBS_mapicons/src/css/box_styles`, `OBS_mapicons/src/css/landscape_styles`, `OBS_html/src/css/intro_styles`, or `OBS_html/src/css/intro_styles`. If you do so, please share your custom skins with this project.

## Help, Bug-Report, Suggestions & Contribution

If you need help, have bugs to report, have suggestions to make, or want to contribute to this project in any way go to *#dev* channel of the [Alpha SC2 Discord Server](https://discordapp.com/invite/yRWNYr) and/or message me on [Discord](https://discordapp.com/): *pres.sure#5247*. In the case of a bug report please provide the log-files `src/scctool.log` and `src/installpackages.log`.

## Support

If you want to support this project, consider subscribing to https://www.twitch.tv/teampheenix or donate directly via https://streamlabs.com/scpressure. Alternativly, just follow the team pheeniX and my personal https://www.twitch.tv/scpressure twitch channel!

