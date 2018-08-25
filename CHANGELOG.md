# Changelog


## v2.2.0 (2018-08-25)

### New

* Added Match Tabs that allow you to manage multiple matches at the same time and jump between them.

* Added a generic Proleague Format to Custom Formats.

### Changes

* Koprulu custom format changed back to Bo7 All-Kill.

### Fix

* Fixed a crash that would occur when adding a map to the mapstats custom map pool.


## v2.1.4 (2018-08-20)

### Fix

* Fixed a crash that would occure when adding a map to the mapstats custom map pool.


## v2.1.3 (2018-08-19)

### Fix

* Fixed a bug where the new AlphaTL Match Banner would not be downloaded.


## v2.1.2 (2018-08-14)

### New

* Added link to Tutorial Video.

### Fix

* Fixed a bug where "0 - 0" would always be written into score.txt.

* Fixed a bug where dragging and dropping a logo onto team 2 would not work.


## v2.1.0 (2018-08-11)

### New

* Implemented Google-Cloud Text-to-Speech Voices for the Intros.


## v2.0.1 (2018-08-07)

### New

* Map Icons are now connected via websocket to the tool and fully animated.

* Added a new Mapstats Browser Source.

* Added a blacklist for the ingame score task to deactivate it when you are playing yourself.

* Already played maps can be marked in the mapstats browser source.

* Added a 'Blue' skin/style for the score icon, the landscape map icons, and the player intro.

* Added scope and volume to Text-to-Speech settings.

* The Score Icon is now connect via websocket to SCCT and fully animated.

* Logos and Matchbanner are no longer download if they are identical to the current logos or banner.

* Restructured the settings.

### Changes

* Added upcoming ladder maps.

* Updated to Twitch-API v5 and included the option to set game to 'StarCraft 2' and community to 'StarCraft Casting Tool'.

* Changed Koprulu League format to Pro League.

* Added option to import and overwrite current profile.

* Added the GIF format to the list of supported file types for the team logo.

* One can now use a single combined hotkey for both player intros. This option is the new default.

### Fix

* Fixed a bug where the hotkeys for intros would not be reactivated.

* Fixed various typos in the localization.

* Fixed a bug in the AlphaTL match grabber that occured if a team has no logo.

* Custom css-files with whitespaces are automatically renamed.

* Fixed a bug to save nightbot commands.

* Fixed a bug the would prevent the Nightbot token from being saved.

* Fixed a bug that would prevent the Nightbot token from being saved.

* Fixed a bug in connection with tesseract OCR.

* Text-to-Speech is now disabled by default.


## v1.13.0 (2018-07-29)

### New

* Prepared tool for upcoming upgrade to v2.0; This is the last update prior to v2.0.

### Changes

* Upgrade to Twitch-API v5.


## v1.12.3 (2018-07-20)

### Changes

* Changed Koprulu League format to Pro League.


## v1.12.2 (2018-06-01)

### Fix

* Fixed a bug that prevented using a non-default skin for the intros.


## v1.12.1 (2018-05-26)

### Fix

* Fixed a bug that prevented StarCraft Casting Tool from terminating.


## v1.12.0 (2018-05-26)

### Fix

* Text-to-Speech is now disabled by default.

* Fixed the authentification flow with Twitch and Nightbot.


## v1.11.0 (2018-05-22)

### New

* Added option to use Text-to-Speech for the Intros reading the team and player name.

### Fix

* Fixed a bug where Tesseract-OCR would not work when installed on a different drive.


## v1.10.3 (2018-05-19)

### Fix

* Liquipedia Image Search fixed by switching to https.


## v1.10.2 (2018-05-15)

### Fix

* Intro is no longer visible shortly when browser source is started/refreshed.


## v1.10.1 (2018-05-10)

### New

* Added option to auto swap a favorite team to the left at Misc Settings: Favorites.

* Added button to swap the teams.


## v1.10.0 (2018-05-09)

### New

* Added upcoming Season 2 Ladder Maps.

### Changes

* Improved centering of mapname and label of landscape map icons.


## v2.0.0 (2018-04-29)

### New

* Added a Profile Manager.

* Added LEDs to status bar indicating when browser sources are connected to StarCraft Casting Tool.


## v1.9.12 (2018-04-29)

### Fix

* Race Icons are visible again.


## v1.9.11 (2018-04-29)

### New

* Added a dialog for recording hotkeys.

### Changes

* `README.md`, `CHANGELOG.md` as well as the folder `src` and `locales` are now included in the executable - you are inclined to delete these files and folders.


## v1.9.9 (2018-04-25)

### Fix

* Misc Settings are available again.


## v1.9.8 (2018-04-24)

### Fix

* Fixed a bug where the Tesseract-OCR links wasn't properly displayed in the OCR Tab (Misc Settings).

* Russian Localization was revised by Vexxorian.


## v1.9.7 (2018-04-22)

### New

* Added predefined Custom Match formats for All-In TheNydus, Chobo Team League,  and Validity Star League.

### Fix

* Fixed a bug in the RSTL match grabber where it failed to grab the start map in the All-Kill format.


## v1.9.6 (2018-04-17)

### Fix

* Custom Mode '1vs1' should work again.


## v1.9.5 (2018-04-15)

### Fix

* Fixed a bug in the Intros that would associate both players always with Team 1.


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


