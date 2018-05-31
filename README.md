[![Release](https://img.shields.io/github/release/teampheenix/StarCraft-Casting-Tool.svg)](https://github.com/teampheenix/StarCraft-Casting-Tool/releases/latest)
[![GitHub (Pre-)Release Date](https://img.shields.io/github/release-date-pre/teampheenix/StarCraft-Casting-Tool.svg)](https://github.com/teampheenix/StarCraft-Casting-Tool/releases)
[![Downloads](https://img.shields.io/github/downloads/teampheenix/StarCraft-Casting-Tool/total.svg)](https://github.com/teampheenix/StarCraft-Casting-Tool/releases/latest)
[![GitHub license](https://img.shields.io/github/license/teampheenix/StarCraft-Casting-Tool.svg)](https://github.com/teampheenix/StarCraft-Casting-Tool/blob/master/LICENSE)
[![Discord](https://img.shields.io/discord/408901724355559435.svg)](https://discord.gg/G9hFEfh)
[![Patreon](https://img.shields.io/badge/Become%20a-Patron-orange.svg)](https://www.patreon.com/StarCraftCastingTool)
[![Paypal](https://img.shields.io/badge/Donate-PayPal-blue.svg)](https://www.paypal.me/StarCraftCastingTool)

# StarCraft Casting Tool

**StarCraft Casting Tool** (SCC Tool) is a free to use open source program that makes casting StarCraft 2 simple while increasing the production value substantially by providing a match grabber, predefined custom formats, and various sets of animated icons and browser sources to be presented to the viewer. 

![streaming-tool](https://user-images.githubusercontent.com/26044736/38167067-7b78fd10-352f-11e8-8676-50a7b0bf9e98.png)

## Download

* **[Latest executable](https://github.com/teampheenix/StarCraft-Casting-Tool/releases/latest)** for Windows
* **[Source code](https://github.com/teampheenix/StarCraft-Casting-Tool/archive/master.zip)**

## Feature List

* **Match Grabber** for [AlphaTL](http://alpha.tl/) and [RSTL](http://hdgame.net/en/tournaments/list/tournament/rstl-12/)
* **Custom Match Format**: Bo1-Bo9, all-kill format, 1vs1 - including predefined formats for Chobo, Koprulu, WardiTV, and PSISTOM Gaming Team League, ...
* Two sets of **Map Icons**: Box and Landscape in `OBS_mapicons/icons_box` and `OBS_mapicons/icons_landscape`
* **Scoreboard** including team icons in `OBS_html`
* **Animated Player Intros** in `OBS_html` including playername & race via SC2-Client, team with logo via SCC Tool
* **TXT-files** with match infos in `OBS_data`
* **Twitch & Nightbot Integration**: Update your stream title or bot commands via a single click or automatically
* **Automatic Score Detection** via SC2-Client
* **Interaction with SC2-Observer-UI**: Automatically toggle Production Tab and set Score at the start of a Map
* Nearly **unlimited Customization** via Skins and CSS
* German and Russian language support.

## Discord Server

If you need support, have questions, want to be up-to-date on, or like to contribute to this project, join our [Discord Server](https://discord.gg/G9hFEfh).

## Twitch Community

Join the [StarCraft Casting Tool Twitch Community](https://www.twitch.tv/communities/starcraftcastingtool) to find other streams that are using the StarCraft Casting Tool and promote your own stream when using it.

## Links

[Changelog](https://github.com/teampheenix/StarCraft-Casting-Tool/blob/master/CHANGELOG.md) | [Icon Preview](https://teampheenix.github.io/SCCT-archive/) | [Discord Server](https://discord.gg/G9hFEfh)


## General Information
The tool generates various browser sources (and text-files): Amongst others, two complete sets of corresponding *Map Icons* (including map, players, races, and score), a Score Icon (including the score, team names, and logos) and GSL-like *Intros* (including player, race and team).

StarCraft Casting Tool can monitor your SC2-Client to detect the score, update it automatically, and provide corresponding player Intros. On Windows, the tool can additionally and automatically set and toggle the score in your SC2-Observer UI and toggle the production tab at the start of a game.

This tool should run on any operating system that supports Python 3, e.g., Windows, MacOS, and Linux (the interaction with the SC2-Observer-UI is currently only supported on Windows).  

## Installation

### Executable with Updater

**Only Windows: [Download the latest executable](https://github.com/teampheenix/StarCraft-Casting-Tool/releases/latest)** `StarCraft-Casting-Tool.exe`, place it in a preferable empty folder folder with *sufficient write-privileges* and execute it. After the first start a subfolder structure is generated and all additional data is downloaded - do not move or alter this data structure relative to the executable.

### Alternativ: Python Script

**Windows, MacOS, Linux: [Download the Source Code as Archive](https://github.com/teampheenix/StarCraft-Casting-Tool/archive/master.zip)** and exctract StarCraft Casting Tool, download the latest version of Python 3 at [https://www.python.org/downloads](https://www.python.org/downloads). This tool requires the additional Python Packages *PyQt5*, *requests*, *configparser*, *humanize*, *markdown2*, *pyupdater*, *keyboard*, *websockets*, *beautifulsoup4*, *appdirs*, *gTTS* and on Windows additionally *pypiwin32*, *Pillow*, *pytesseract*. To install these packages execute the script `installPackages.py` once or do it manually (e.g., via *pip*). Execute `StarCraftCastingTool.pyw` or execute the command `python3 StarCraftCastingTool.pyw` to start the SCC Tool.

## Instructions for Use

Run StarCraft Casting Tool via `StarCraft-Casting-Tool.exe` (or `StarCraftCastingTool.pyw`). Enter the Match-URL of an AlphaTL or RSTL match in the *Match Grabber* tab, e.g., "http://alpha.tl/match/3000", and press *Load Data from URL*. Alternatively one can create a match in the *Custom Match* tab.  Edit the data if necessary. The sliders control the score of each map. Press *Update OBS Data* or alter the score to update the data for streaming. The top slider is to select *your* team. Once selected the border of the Map Icons turn (by default) green or red depending on the result. To select your team automatically you can add it to *Favorite Teams* list under *Settings: Misc*. Similarly you can enter your players' nicknames into *Favorite Players* for auto completion.

### Data for Streaming
can be found in the directory `OBS_data` and be included into OBS (or any similar streaming tool) via *Text read from local file*. If you want to include the team logos and the matchbanner, it is recommended to include them as *browser source from local file* via the HTML files given in the directory `OBS_html` *(Score Icon size: 1280x100px, Logo sizes: 300x300px, Intro size: Your screen resolution)*. The Map Icons can be found in the directory `OBS_mapicons` and have to be included via *browser source from local file* as well. There are two type of icons: box icons in `OBS_mapicons/icons_box` and landscape icons in `OBS_mapicons/icons_landscape`. One can either include each Map Icon separately *(box size: 280x270px, landscape size: 1010x110px)* and arrange them freely or one can include them via the single html file `all_maps.html` *(the chosen dimension of the browser source determines the arrangement of the icons)*. Note that you can scale the browser source(s) down/up if you want to make the icons smaller/larger. All browser sources refresh automatically - you should have to refresh the cache of this browser sources only if you select a different skin/style (not needed for intros) or a new update has been applied.

If the tool is missing a map, you can add them in the *Map Manager* that can be found in *Settings: Misc*.

### Twitch & Nightbot
To update your [Twitch](https://www.twitch.tv/) title (and set your game to *StarCraft 2*) or [Nightbot](https://nightbot.tv/) command via click on *Update Twitch Title* or *Update Nightbot* you have to set your Twitch *Channel* and/or generate an corresponding access token. This can be done via *Settings: Connections*. Note that you can also change the title of Twitch channels that do not belong to the user you have generated the access token with as long as this user is registered as an editor of corresponding channel. The format of your new title can be customized via the *Title Template* with the use of placeholders (hover over the input field to get a list of all available placeholders) and specified under *Settings: Connections*.

### Background Tasks

#### Automatic Score Detection
To active the automatic detection of the score via the SC2-Client-API check the box *Auto Score Update* of the *Background Tasks*. This score detection does only work if you either play or observe a decided game (game length > 60 seconds) with a pair of players that were specified on one of sets. If there are multiple sets eligible, the score is entered for the first undecided set.

#### Set Ingame Score
Some Observer Interfaces like [GameHeart](https://sites.google.com/site/ahlismods/gameheart-obs-ui/changelog-1vs1) have a toogle-able score, that can be toogled by pressing `Ctrl+Shift+S`. When using other Oberserver-UI like WCS that have no toggle-able score and don't have assigned this hot-key combination SC2 will be interpret it as `Ctrl+S` and typically disable your sound. Therefore, SCC-Tool does not press `Ctrl+Shift+S` to toggle the score in the Observer-UI by default at start of a game. To enable this feature, you have to set the checkbox under *Settings: Misc: AlphaTL & Ingame Score* - similiar additional options can be found there as well.

Frequently the order of players given by the SC2-Client-API differs from the order in the Observer-UI resulting in a swapped match score when using *Set Ingame Score*. To correct this you can activate Optical Character Recognition (OCR) once you have to downloaded and installed [Tesseract-OCR](https://github.com/UB-Mannheim/tesseract/wiki#tesseract-at-ub-mannheim). On a dual monitor setup OCR will currently only work if SC2 is displayed on the primary monitor.

#### Player Intros
[![intro-demo](https://user-images.githubusercontent.com/26044736/30003831-4fe09b14-90c4-11e7-9593-439454d4e324.gif)](https://youtu.be/JNuAr63L0wM)

Include the Player Intro `OBS_html/intro.html` as browser sources (using the full height and width of your display). The intros will only work if the task *Provide Player Intros* is activated in SCC-Tool. The data will be updated when a game or replay is started in the StarCraft 2 client. You have to assign hotkeys to trigger the intros in *Settings: Connections: Intros & Hotkeys*. The first player is always corresponding to the player your observer camera is centered on at start of a game. The sound volume of the intros as well as the duration of the intros can be adjusted in *Settings: Connections: Intros & Hotkeys*. There are currently three different animations with an unique sound, e.g., *Fanfare* - see https://youtu.be/kEcxS4K9vJ4?t=25m38s for an review of *Fanfare*.

## Customization

Some basic options for customization can be found under *Settings: Styles*, for example, alternative styles/skins for the Map Icons, Score Icon, Intros and option to specify border colors. For additional **nearly unlimited customization** of the Icons you can make your own custom skins via [CSS](https://www.w3schools.com/css/) by creating new alternative *css*-files and placing them into `OBS_mapicons/src/css/box_styles`, `OBS_mapicons/src/css/landscape_styles`, `OBS_html/src/css/score_styles`, or `OBS_html/src/css/intro` respectively. If you do so, please share your custom skins with this project. If you want help implementing your own icon skin with CSS or just want to share an idea for a skin join the [Discord Server](https://discord.gg/G9hFEfh).

## Help, Bug-Report, Suggestions & Contribution

If you need help, have bugs to report, have suggestions to make, or want to contribute to this project in any way join the Discord Server of this project via https://discord.gg/G9hFEfh and/or message me (*pres.sure#5247*) on [Discord](https://discordapp.com/).

In the case of a bug report please provide the log-file that can be found in the directory `C:\Users\username\AppData\Local\team pheeniX\StarCraft-Casting-Tool\Log`.

You can support StarCraft Casting Tool via [Patreon](https://www.patreon.com/StarCraftCastingTool) or [Paypal](https://www.paypal.me/StarCraftCastingTool).
