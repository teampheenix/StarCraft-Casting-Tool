# Changelog


## v1.12.3 (2018-07-20)

### Changes

* Changed Koprulu League format to Pro League. [2press]


## v1.12.2 (2018-06-01)

### Fix

* Fixed a bug that prevented using a non-default skin for the intros. [2press]


## v1.12.1 (2018-05-26)

### Fix

* Fixed a bug that prevented StarCraft Casting Tool from terminating. [2press]


## v1.12.0 (2018-05-26)

### Fix

* Text-to-Speech is now disabled by default. [2press]

* Fixed the authentification flow with Twitch and Nightbot. [2press]


## v1.11.0 (2018-05-22)

### New

* Added option to use Text-to-Speech for the Intros reading the team and player name. [2press]

### Fix

* Fixed a bug where Tesseract-OCR would not work when installed on a different drive. [2press]


## v1.10.3 (2018-05-19)

### Fix

* Liquipedia Image Search fixed by switching to https. [2press]


## v1.10.2 (2018-05-15)

### Fix

* Intro is no longer visible shortly when browser source is started/refreshed. [2press]


## v1.10.1 (2018-05-10)

### New

* Added option to auto swap a favorite team to the left at Misc Settings: Favorites. [2press]

* Added button to swap the teams. [2press]


## v1.10.0 (2018-05-09)

### New

* Added upcoming Season 2 Ladder Maps. [2press]

### Changes

* Improved centering of mapname and label of landscape map icons. [2press]


## v2.0.0 (2018-04-29)

### New

* Added a Profile Manager. [2press]

* Added LEDs to status bar indicating when browser sources are connected to StarCraft Casting Tool. [2press]


## v1.9.12 (2018-04-29)

### Fix

* Race Icons are visible again. [2press]


## v1.9.11 (2018-04-29)

### New

* Added a dialog for recording hotkeys. [2press]

### Changes

* `README.md`, `CHANGELOG.md` as well as the folder `src` and `locales` are now included in the executable - you are inclined to delete these files and folders. [2press]


## v1.9.9 (2018-04-25)

### Fix

* Misc Settings are available again. [2press]


## v1.9.8 (2018-04-24)

### Fix

* Fixed a bug where the Tesseract-OCR links wasn't properly displayed in the OCR Tab (Misc Settings). [2press]

* Russian Localization was revised by Vexxorian. [2press]


## v1.9.7 (2018-04-22)

### New

* Added predefined Custom Match formats for All-In TheNydus, Chobo Team League,  and Validity Star League. [2press]

### Fix

* Fixed a bug in the RSTL match grabber where it failed to grab the start map in the All-Kill format. [2press]


## v1.9.6 (2018-04-17)

### Fix

* Custom Mode '1vs1' should work again. [2press]


## v1.9.5 (2018-04-15)

### Fix

* Fixed a bug in the Intros that would associate both players always with Team 1. [2press]


## v1.9.4 (2018-04-12)

### Fix

* Fixed crash when "Update Twitch" and "Update Nightbot" was pressed. [2press]


## v1.9.3 (2018-04-11)

### New

* Added predefined Custom Match formats for Koprulu, WardiTV, and PSISTOM Gaming Team League. [2press]

* Added Shortcuts to Favorites and Alias Settings. [2press]


## v1.9.2 (2018-04-10)

### New

* Added option to specify player and team aliases. These aliases are replaced by the actual name when encountered by the match grabber. Additionally, SC2 player names listed as aliases are replaced in the intros by the actual name and used to identify players by the automatic background tasks *Score Update* and *Set Ingame Score*. [2press]


## v1.9.1 (2018-04-08)

### New

* Dialog in the Map Manager to add a map from Liquipedia. [2press]

### Fix

* Fixed a few minor bug in the Map Manager. [2press]


## v1.9.0 (2018-04-07)

### New

* *Set Ingame Score* task will work even if one player is not entered in SCCT. [2press]

* Added option to automatically press Ctrl+X to enforce the SCCT's player order in the Observer UI. [2press]

* Added completer for Liquipedia logo search. [2press]

* All logos can be dragged and dropped in the logo manager. [2press]

* Favorites or Last Used icons can be dragged and dropped to the team icon. [2press]

* Added `CTRL+S` shortcut for *Update OBS Data*. [2press]

* Double click on a logo in the logo manager will set it as a team logo. [2press]

* *Auto Score Update* task will now detect the score even if one player name is missing and update the missing name accordingly. [2press]

* *Auto Score Update* task will now set the races when a score is automatically updated. [2press]

### Changes

* Improved OCR reliability (e.g., with Gawliq UI). [2press]


## v1.8.10 (2018-04-05)

### Fix

* Fixed Bug in Score Icon. [2press]


## v1.8.9 (2018-04-05)

### New

* Last 100 team name are saved for auto completion. [2press]


## v1.8.8 (2018-04-05)

### New

* Option to overwrite the font of the icon has been added to Settings: Styles. [2press]

### Fix

* Fixed bug that prevented intros from working. [2press]


## v1.8.7 (2018-04-04)

### Fix

* Font is now correctly displayed in landscape map icons. [2press]


## v1.8.6 (2018-04-04)

### New

* "Apply Format" and "Update OBS Data" buttons now indicated when they need to be pressed. [2press]

* The winner highlight color is selectable in Settings: Styles. [2press]

### Changes

* A map is only labled as "Ace" when appropriate. [2press]

* "Reset Match Data" now resets logos as well as the score. [2press]


## v1.8.5 (2018-04-03)

### New

* The race of the last 100 players is now saved and will be selected automatically. [2press]

### Changes

* When selecting the map a popup window with all available maps is now displayed. [2press]

### Fix

* Improved new intro animation with respect to the race logo and the default skin. [2press]


## v1.8.4 (2018-04-02)

### Changes

* Russian localization has been updated. [2press]


## v1.8.3 (2018-04-02)

### New

* Added two alternative Intro animations (Slide & Fanfare) including new sounds that can be selected at Settings: Connections: Intro & Hotkeys. [2press]


## v1.8.2 (2018-04-02)

### Fix

* Winning player should now be properly transfered to the next map when using All-Kill-Format/Mode. [2press]


## v1.8.1 (2018-04-02)

### New

* Player names are used or have been used in the current session are available for auto completion. [2press]

* Match Grabber can now be used by pressing enter. [2press]

* Removed FTP-Upload. If you were using this feature, please contact me and I will provide an alternative via websockets. [2press]

* Added Logo Manager featuring last used logos, favorites, adding from URL, and searching Liquipedia for logos. [2press]

### Changes

* All-Kill Format no longer needs to be applied via "Apply Format". [2press]

* Migrated to Python 3.6.5. [2press]

* Returning to the official python keyboard package since v0.13 has been published. [2press]

* Changelog is now displayed on restart after an update. [2press]

### Fix

* Testing the Twitch title template works again. [2press]

* RSTL Matchgrabber should be working properly for all matches now. [2press]


## v1.7.2 (2018-03-26)

### Changes

* Updated map images of Abiogenesis, Backwater, and Odyssey. Removed old maps (Blood Boil, Defenders Landing, Honorgrounds, Paladino Terminal, Proxima Station). [2press]

### Fix

* Fixed incorrect labeling of maps names when using the match grabber. [2press]


## v1.7.1 (2018-03-19)

### New

* Changelog added. [2press]

### Changes

* Nighbot commands that are deleted in SCCT get now deleted in Nightbot as well. [2press]


