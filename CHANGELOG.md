# Changelog


## v1.9.4 (2018-04-12)

### Fix

* Fixed crash when "Update Twitch" and "Update Nightbot" was pressed.


## v1.9.3 (2018-04-11)

### New

* Added predefined Custom Match formats for Koprulu, WardiTV, and PSISTOM Gaming Team League.

* Added Shortcuts to Favorites and Alias Settings.


## v1.9.2 (2018-04-10)

### New

* Added option to specify player and team aliases. These aliases are replaced by the actual name when encountered by the match grabber. Additionally, SC2 player names listed as aliases are replaced in the intros by the actual name and used to identify players by the automatic background tasks *Score Update* and *Set Ingame Score*.


## v1.9.1 (2018-04-08)

### New

* Dialog in the Map Manager to add a map from Liquipedia.

### Fix

* Fixed a few minor bug in the Map Manager.


## v1.9.0 (2018-04-07)

### New

* *Set Ingame Score* task will work even if one player is not entered in SCCT.

* Added option to automatically press Ctrl+X to enforce the SCCT's player order in the Observer UI.

* Added completer for Liquipedia logo search.

* All logos can be dragged and dropped in the logo manager.

* Favorites or Last Used icons can be dragged and dropped to the team icon.

* Added `CTRL+S` shortcut for *Update OBS Data*.

* Double click on a logo in the logo manager will set it as a team logo.

* *Auto Score Update* task will now detect the score even if one player name is missing and update the missing name accordingly.

* *Auto Score Update* task will now set the races when a score is automatically updated.

### Changes

* Improved OCR reliability (e.g., with Gawliq UI).


## v1.8.10 (2018-04-05)

### Fix

* Fixed Bug in Score Icon.


## v1.8.9 (2018-04-05)

### New

* Last 100 team name are saved for auto completion.


## v1.8.8 (2018-04-05)

### New

* Option to overwrite the font of the icon has been added to Settings: Styles.

### Fix

* Fixed bug that prevented intros from working.


## v1.8.7 (2018-04-04)

### Fix

* Font is now correctly displayed in landscape map icons.


## v1.8.6 (2018-04-04)

### New

* "Apply Format" and "Update OBS Data" buttons now indicated when they need to be pressed.

* The winner highlight color is selectable in Settings: Styles.

### Changes

* A map is only labled as "Ace" when appropriate.

* "Reset Match Data" now resets logos as well as the score.


## v1.8.5 (2018-04-03)

### New

* The race of the last 100 players is now saved and will be selected automatically.

### Changes

* When selecting the map a popup window with all available maps is now displayed.

### Fix

* Improved new intro animation with respect to the race logo and the default skin.


## v1.8.4 (2018-04-02)

### Changes

* Russian localization has been updated.


## v1.8.3 (2018-04-02)

### New

* Added two alternative Intro animations (Slide & Fanfare) including new sounds that can be selected at Settings: Connections: Intro & Hotkeys.


## v1.8.2 (2018-04-02)

### Fix

* Winning player should now be properly transfered to the next map when using All-Kill-Format/Mode.


## v1.8.1 (2018-04-02)

### New

* Player names are used or have been used in the current session are available for auto completion.

* Match Grabber can now be used by pressing enter.

* Removed FTP-Upload. If you were using this feature, please contact me and I will provide an alternative via websockets.

* Added Logo Manager featuring last used logos, favorites, adding from URL, and searching Liquipedia for logos.

### Changes

* All-Kill Format no longer needs to be applied via "Apply Format".

* Migrated to Python 3.6.5.

* Returning to the official python keyboard package since v0.13 has been published.

* Changelog is now displayed on restart after an update.

### Fix

* Testing the Twitch title template works again.

* RSTL Matchgrabber should be working properly for all matches now.


## v1.7.2 (2018-03-26)

### Changes

* Updated map images of Abiogenesis, Backwater, and Odyssey. Removed old maps (Blood Boil, Defenders Landing, Honorgrounds, Paladino Terminal, Proxima Station).

### Fix

* Fixed incorrect labeling of maps names when using the match grabber.


## v1.7.1 (2018-03-19)

### New

* Changelog added.

### Changes

* Nighbot commands that are deleted in SCCT get now deleted in Nightbot as well.


