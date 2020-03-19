[![Release](https://img.shields.io/github/release/teampheenix/StarCraft-Casting-Tool.svg)](https://github.com/teampheenix/StarCraft-Casting-Tool/releases/latest)
[![Build status](https://ci.appveyor.com/api/projects/status/5g765ntfwpyv4xq4/branch/master?svg=true)](https://ci.appveyor.com/project/2press/starcraft-casting-tool/branch/master)
[![Downloads](https://img.shields.io/github/downloads/teampheenix/StarCraft-Casting-Tool/total.svg)](https://github.com/teampheenix/StarCraft-Casting-Tool/releases/latest)
[![GitHub license](https://img.shields.io/github/license/teampheenix/StarCraft-Casting-Tool.svg)](https://github.com/teampheenix/StarCraft-Casting-Tool/blob/master/LICENSE)
[![Requirements Status](https://requires.io/github/teampheenix/StarCraft-Casting-Tool/requirements.svg?branch=master)](https://requires.io/github/teampheenix/StarCraft-Casting-Tool/requirements/?branch=master)
[![Discord](https://img.shields.io/discord/408901724355559435.svg)](https://discord.gg/G9hFEfh)
[![Patreon](https://img.shields.io/badge/Become%20a-Patron-orange.svg)](https://www.patreon.com/StarCraftCastingTool)

# StarCraft Casting Tool

**StarCraft Casting Tool** (SCC Tool) is a free to use open source program that makes casting StarCraft 2 simple while increasing the production value substantially by providing a match grabber, predefined custom formats, and various sets of animated icons and browser sources to be presented to the viewer.

![scct-v2](https://user-images.githubusercontent.com/26044736/43646667-c915c8e2-9735-11e8-883c-4e9d6b94061b.jpg)

## Important Note (2020-03-06)

Due to a crash of my hard drive, I lost the keypack to sign the updates. Therefore, I had to rebuild the update channel of the application. Thus, in order to update your version of StarCraft Casting Tool you have to download the **[latest Setup](https://github.com/teampheenix/StarCraft-Casting-Tool/releases/latest)** and install the latest version manually

## Downloads

-   **[Latest Setup](https://github.com/teampheenix/StarCraft-Casting-Tool/releases/latest)** for Windows (64-bit only)
-   **[Source code](https://github.com/teampheenix/StarCraft-Casting-Tool/archive/master.zip)**

## Feature List

-   **Match Grabber** for [Alpha Team League](https://alpha.tl/), [Russian StarCraft 2 League](https://rfcs.ru/en/tournaments/list/tournament/rsl-1/) and [Chobo Team League](https://www.choboteamleague.com/home/)
-   **Custom Match Format**: Bo1-Bo15, All-Kill format, 1vs1 - including predefined formats for Koprulu, WardiTV, and PSISTORM Gaming Team League.
-   Two sets of **Map Icons**: Box and Landscape in `casting_html`
-   **Scoreboard** including team icons in `casting_html`
-   **Animated Player Intros** in `casting_html` including Text-to-Speech, player name & race via SC2-Client, team with logo via SCC Tool
-   **Map Preview with Statistics** from Liquipedia in `casting_html`
-   **Aligulac Browser Source** that predicts the outcome of a 1vs1 match in `casting_html`
-   **Map Vetoes Browser Source** in `vetoes.html`
-   **Countdown Browser Source** in `countdown.html`
-   **TXT-files** with match infos in `casting_data`
-   **Twitch & Nightbot Integration**: Update your stream title or bot commands via a single click or automatically
-   **Automatic Score Detection** via SC2-Client
-   **Interaction with SC2-Observer-UI**: Automatically toggle Production Tab and set Score at the start of a Game
-   Nearly **unlimited Customization** via Skins and CSS
-   French, German, and Russian language support

## Discord Server

If you need support, have questions, want to be up-to-date on, or like to contribute to this project in any way, join our [Discord Server](https://discord.gg/G9hFEfh).

## Links

[Video Tutorial](https://youtu.be/j5iWa4JB8bM) \| [Changelog](https://github.com/teampheenix/StarCraft-Casting-Tool/blob/master/CHANGELOG.md) \| [Discord Server](https://discord.gg/G9hFEfh)

## General Information

The tool generates various browser sources (and text-files): Amongst others, two complete sets of corresponding _Map Icons_ (including map, players, races, and score), a _Score Icon_ (including the score, team names, and logos), GSL-like _Intros_ (including player, race and team), and _Map Statistics_.

StarCraft Casting Tool can monitor your SC2-Client to detect the score, update it automatically, and provide corresponding player Intros. On Windows, the tool can additionally and automatically set and toggle the score in your SC2-Observer UI and toggle the production tab at the start of a game.

This tool should run on any operating system that supports Python 3, e.g., Windows, MacOS, and Linux, _but the interaction with the SC2-Observer-UI is currently only supported on Windows_.  

## Installation

### Executable with Updater

**Only Windows (64-bit): [Download the latest executable](https://github.com/teampheenix/StarCraft-Casting-Tool/releases/latest)** `StarCraft-Casting-Tool.exe`, place it in a preferable empty folder folder with _sufficient write-privileges_ and execute it. After the first start a subfolder structure is generated and all additional data is downloaded - do not move or alter this data structure relative to the executable. Do not rename the executable.

### Alternativ: Python Script

**Windows, MacOS, Linux: [Download the Source Code as Archive](https://github.com/teampheenix/StarCraft-Casting-Tool/archive/master.zip)** and exctract StarCraft Casting Tool, download the latest version of Python 3.6 at <https://www.python.org/downloads>. This tool requires the additional Python Packages, to install these packages execute `pip install -r requirements.txt`.

## Instructions for Use

### Video Tutorial

[![Video Tutorial](https://img.youtube.com/vi/j5iWa4JB8bM/mqdefault.jpg)](https://youtu.be/j5iWa4JB8bM)

### Basics

Run StarCraft Casting Tool via `StarCraft-Casting-Tool.exe` (or `StarCraftCastingTool.pyw`). Search for an Alpha-TL match or enter the Match-URL of an AlphaTL or RSL match in the _Match Grabber_ tab, e.g., `https://alpha.tl/match/3000`, and press _Load Data from URL_ (For Chobo Team League one has to enter a link to an article with the match ups -- for the most recent matches `https://www.choboteamleague.com/home` is sufficient). Alternatively one can create a match in the _Custom Match_ tab.  Edit the data if necessary. The sliders control the score of each map. The top slider is to select _your_ team. Once selected the border of the Map Icons turn (by default) green or red depending on the result. To select your team automatically you can add it to _Favorite Teams_ list under _Settings: Misc_. Similarly you can enter your players' nicknames into _Favorite Players_ for auto completion.

### Data for Streaming

All data (placed in `casting_data` or `casting_html`) can be found in the respective _profile folder_ at `C:\Users\<User>\AppData\Local\team pheeniX\StarCraft-Casting-Tool\profiles\<Profile>\` that can be accessed conveniently by via SCCT's menu _Profile: Open current folder_.

Raw data for streaming can be found in the directory `casting_data` and be included into OBS (or any similar streaming tool) via _Text read from local file_. If you want to include the team logos and the match banner (of AlphaTL), it is recommended to include them as _browser source from local file_ via the HTML files given in the directory `casting_html` _(Score Icon size: 1280x100px, Logo sizes: 300x300px, Intro size: Your screen resolution, Map Stats: 1700x800px)_. The Map Icons can be found in the directory `casting_html` and have to be included via _browser source from local file_ as well. There are two type of icons: box icons in `casting_html/mapicons_box_x.html` and landscape icons in `casting_html/mapicons_landscape_x.html`. A single icons has the following dimensions - _box size: 275x275px, landscape size: 1005x105px_, but _the chosen dimension of the browser source determines the arrangement of the icons_. Note that you can scale the browser source(s) down/up if you want to make the icons smaller/larger. All browser sources refresh automatically - you should have to refresh the cache of this browser sources only if a new update has been applied. A simple method to add the browser source in OBS studio is drop drag and drop the files into your desired scene.

If the tool is missing a map, you can add them in the _Map Manager_ that can be found in _Settings: Misc_.

#### Local network URL

Instead of including browser sources _from local file_, one can include them via a local network URL `http://localhost:{port}/{browser_source}`, e.g., `http://localhost:{port}/score`. The `{port}` is a unique number for each profile (displayed when hovering over the LEDs in the status bar at the bottom). Adding `.html` to `{browser_source}` is optional. You can open or copy these URL's by navigating the Browser Sources menu. Moreover the txt-files in `casting_data` can be accessed via `http://localhost:{port}/{file}.txt` as well (`.txt` optional).

The disadvantage is that the browser source that are included via a local network URL are only available when StarCraft Casting Tool is running, whereas the browser sources from local file will display the last data even if the tool is not running.

You can use this to serve browser sources to another PC in the network (`http://{your_local_network_ip}:{port}/{browser_source}`) or to a different person via the internet (`http://{your_internet_ip}:{port}/{browser_source}`) given that you enable port forwarding on your PC (and router) for the specific port (TCP) that StarCraft Casting Tool is using.

### Twitch & Nightbot

To update your [Twitch](https://www.twitch.tv/) title (and set your game to _StarCraft 2_) or [Nightbot](https://nightbot.tv/) command via click on _Update Twitch Title_ or _Update Nightbot_ you have to set your Twitch _Channel_ and/or generate an corresponding access token. This can be done via _Settings: Connections_. Note that you can also change the title of Twitch channels that do not belong to the user you have generated the access token with as long as this user is registered as an editor of corresponding channel. The format of your new title can be customized via the _Title Template_ with the use of placeholders (hover over the input field to get a list of all available placeholders) and specified under _Settings: Connections_.

### Background Tasks

#### Automatic Score Detection

To active the automatic detection of the score via the SC2-Client-API check the box _Auto Score Update_ of the _Background Tasks_. This score detection does only work if you either play or observe a decided game (game length > 60 seconds) with a pair of players that were specified on one of sets. If there are multiple sets eligible, the score is entered for the first undecided set.

#### Set Ingame Score

Some Observer Interfaces like [GameHeart](https://sites.google.com/site/ahlismods/gameheart-obs-ui/changelog-1vs1) have a toogle-able score, that can be toogled by pressing `Ctrl+Shift+S`. When using other Oberserver-UI like WCS that have no toggle-able score and don't have assigned this hot-key combination SC2 will be interpret it as `Ctrl+S` and typically disable your sound. Therefore, SCC-Tool does not press `Ctrl+Shift+S` to toggle the score in the Observer-UI by default at start of a game. To enable this feature, you have to set the checkbox under _Settings: Misc: AlphaTL & Ingame Score_ - similiar additional options can be found there as well.

Frequently the order of players given by the SC2-Client-API differs from the order in the Observer-UI resulting in a swapped match score when using _Set Ingame Score_. To correct this you can activate Optical Character Recognition (OCR) once you have to downloaded and installed [Tesseract-OCR](https://github.com/UB-Mannheim/tesseract/wiki#tesseract-at-ub-mannheim) - it's recommended to use an [older](https://digi.bib.uni-mannheim.de/tesseract/) v3 version of Tesseract-OCR. On a dual monitor setup OCR will currently only work if SC2 is displayed on the primary monitor.

#### Player Intros

[![intro-demo](https://user-images.githubusercontent.com/26044736/30003831-4fe09b14-90c4-11e7-9593-439454d4e324.gif)](https://youtu.be/JNuAr63L0wM)

Include the Player Intro `casting_html/intro.html` as browser sources (using the full height and width of your display). The data will be updated when a game or replay is started in the StarCraft 2 client. You have to assign hotkeys to trigger the intros in _Settings: Browser Sources: Intros_. The first player is always corresponding to the player your observer camera is centered on at start of a game. The sound volume of the intros as well as the duration of the intros can be adjusted in _Settings: Browser Sources: Intros_. Additionally you can activate Text-to-Speech to include an automatic annoucements of the player's team and name. There are currently three different animations with an unique sound, e.g., _Fanfare_ - see <https://youtu.be/kEcxS4K9vJ4?t=25m45s> for an review of _Fanfare_.

You have the option to have the player announced with Google-Cloud Text-to-Speech featuring high quality voices that you can test at <https://cloud.google.com/text-to-speech/>.

## Customization

Some basic options for customization can be found under _Settings: Styles_, for example, alternative styles/skins for the Map Icons, Score Icon, Intro and option to specify colors. For additional **nearly unlimited customization** of the Icons you can make your own custom skins via [CSS](https://www.w3schools.com/css/) by creating new alternative _CSS_-files and placing them into `casting_html/src/css/{browser-source}`. If you do so, please share your custom skins with this project. If you want help implementing your own icon skin with CSS or just want to share an idea for a skin join the [Discord Server](https://discord.gg/G9hFEfh).

## Help, Bug-Report, Suggestions & Contribution

If you need help, have bugs to report, have suggestions to make, or want to contribute to this project in any way join the Discord Server of this project via <https://discord.gg/G9hFEfh> and/or message me (_pres.sure#5247_) on [Discord](https://discordapp.com/).

In the case of a bug report please provide the log-file (after closing StarCraft Casting Tool) that can be found in the directory `C:\Users\<User>\AppData\Local\team pheeniX\StarCraft-Casting-Tool\Log` or navigated to via the menu.

You can support StarCraft Casting Tool via [Patreon](https://www.patreon.com/StarCraftCastingTool) or [Paypal](https://www.paypal.me/StarCraftCastingTool).
