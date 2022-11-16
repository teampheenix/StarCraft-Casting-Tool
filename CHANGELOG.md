# Changelog


## v2.14.0 (2022-11-16)

### New

* Add Chinese translation. Thanks to ciwomuli!


## v2.13.3 (2022-11-16)

### Fix

* Fixed a bug where jpeg maps would no show in mapstats browser source.


## v2.13.2 (2022-07-24)

### Changes

* New ladder maps added.

### Fix

* Fix download of mapstats from liquipedia.

* Enable liquipedia map download again.


## v2.13.1 (2022-03-03)

### Changes

* Increase delays for requests to Liquipedia.


## v2.13.0 (2022-03-03)

### Changes

* Remove Spire.gg, AlphaTL, RSL, RSTL.


## v2.12.0 (2022-02-13)

### Changes

* Use new Twitch-API to set stream title.


## v2.11.0 (2021-10-30)

### Fix

* Fix download of maps from Liquipedia.


## v2.10.2 (2021-07-18)

### New

* Add option for prefix text to the ticker.

### Fix

* Increase time between liquipedia API stats queries.


## v2.10.1 (2021-07-04)

### Fix

* Remove console.


## v2.10.0 (2021-07-04)

### Changes

* Dependencies updated.

### Fix

* Fixed a bug where the map stats would not update.

* Prompt about new ladder maps is appearing again!

* Break "2000 Atmospheres" in mapstats.


## v2.9.2 (2021-01-19)

### New

* You can now define aliases for league names  that will be used by the match grabber.

* Match grabber can now retrieve ace players from spire.gg.

* Spire.gg match grabber will now also fetch the match score and reset the score if needed.

### Changes

* Locales updated.

* Dependencies upgraded.

### Fix

* Missing meta data of maps will now be updated.

* Map creator, size and spawn position is now correctly fetched from Liquipedia.


## v2.9.0 (2020-10-25)

### New

* Added new map images.

* Added match grabber for spire.gg solo matches.

* Added match grabber for spire.gg team matches.

* In 1vs1 mode the intro player names and order can now be directly read from from SCCT instead of SC2.

* Add upcoming spire.gg matches to search bar.

* All CSS items of intro gain the class attribute defaultLogo if the default SC2 logo is used. This allows to hide the logo or change intro layout.

* Added assets to intro browser source that can be used to display items outside of the intro box.

### Changes

* Python 3.7 support removed.

* Improved support for the new WCS overlay.

* Removed Python 3.6 compatibility.

### Fix

* Fixed a bug where Lightshade would be correct to Nightshade when fetch with the match grabber.

* File ending of logos are automatically added when missing.

* MatchGrabber for RSL will correctly read maps in All-Kill format.


## v2.8.6 (2020-07-14)

### New

* Added one-click button to download all current ladder maps to map manager.

* Currently entered maps can be displayed in the playing order for the map stats.

* Prompt to download missing current ladder maps.

### Fix

* Fixed and issue with high DPI displays.

* Countdown should no longer occasionally skip a second.


## v2.8.5 (2020-05-28)

### Changes

* Maps updated - Acropolis, Cobalt, Disco Bloodbath, Thunderbird, and Winter's Gate removed; Deathaura, Ice and Chrom, Pillars of Gold, and Submarine added.


## v2.8.4 (2020-05-12)

### Fix

* Twitch Title Updater patched to reflect recent OAuth requirement.

* Prevent crash when running from source without TTS API key.


## v2.8.3 (2020-04-24)

### New

* Separate style can be assigned to each instance of the mapicons.


## v2.8.2 (2020-04-05)

### New

* Added clan1.txt and clan2.txt files that will always contain the name of the team even in 1vs1 mode.

* HTTP server now servers otf font files.

### Fix

* Fixed error when a non-css file would be placed in the css folder.

* Landscape map icons are now properly centered horizontally for the StarCraft2 skin.

* Nightbot OAuth fixed.


## v2.8.1 (2020-03-15)

### Changes

* Map Images fo Ever Dream, Golden Wall, Purity and Industry, and Zen updated.

### Fix

* Fixed bug when adding Nightbot commands.


## v2.8.0 (2020-03-06)

### New

* Update broken - due to a hard drive crash, v2.8.0 needs to be updated manually.

### Changes

* Adjusted Liquipedia format to gather map info.

* Added upcoming Ladder Maps.

* Map images of Ephemeron, Eternal Empire, Nightshade, Simulacrum, Triton, World of Sleepers, and Zen updated.


## v2.7.14 (2019-11-16)

### New

* Switched to Python 3.8.

### Changes

* Removed 'Winner Highlight Color' as this color can only be controlled via the css-styles.

* Added upcoming 1vs1 ladder maps Eternal Empire, Nightshade, Simulacrum, and Zen.

### Fix

* Increased compatibility with Python 3.8.


## v2.7.13 (2019-09-24)

### Changes

* Updated Koprulu Team League Format.

### Fix

* 'Thunderbird' is now wrapped correctly in the Mapstats browser source.


## v2.7.12 (2019-08-20)

### Changes

* Added new upcoming ladder maps.

* Reverted Broodwar map support.

### Fix

* Fixed a bug, where you could get blocked from Liquipedia.


## v2.7.11 (2019-08-06)

### New

* Added (limited) support for Broodwar maps. You can now add Broodwar maps via the Map Manager, and the map statistics are automatically refreshed.

### Fix

* Fixed a bug that would cause the tool to crash at the startup.


## v2.7.9 (2019-05-13)

### Changes

* Added upcoming ladder maps: Acropolis, Thunderbird, Turbo Cruise '84.

### Fix

* Fixed a crash that would occure when moving a match tab.


## v2.7.8 (2019-05-05)

### New

* Added new GSL map Cobalt.

### Changes

* Updated locales and mapstats.

### Fix

* Fixed a bug that would prevent the dynamic countdown from working.

* Adding map via Liquipedia fixed.

* Fixed a bug where tts would not work for intros when serving via http.


## v2.7.7 (2019-04-27)

### New

* Added `ticker.txt` to `casting_data`. This file contains all non-zero score matches defined by your open tabs in the form `Team A 1-2 TeamB | TeamC 1-0 TeamD | ` to be readily included as a ticker for all latest results.

### Changes

* Added the China Team Championship Format (3xBo2, Bo1 Ace) to the Custom Formats. Updated the ESL Team League Format.

### Fix

* Fixed a bug where the map name in the vetos browser source would not be fully visible.


## v2.7.6 (2019-04-06)

### New

* Added Countdown Settings Tab in Misc Settings Menu.

* Added casting_data/countdown.txt containing a custom text depending on wheter the countdown is running or finished.

* Added option to update static countdown via the match grabber (AlphaTL only).

### Changes

* Updated to Python 3.7.3.


## v2.7.5 (2019-03-15)

### Fix

* Fixed another instance where the Chobo Team League match grabber would not worker properly.

* Fixed a bug where match grabber would not overwrite old data.

* Fixed a bug where the Chobo Team League match grabber would not work.


## v2.7.4 (2019-02-22)

### Fix

* Fixed a bug that would prevent the map statistics from being updated.

* Fixed a bug that could occure when deleting match tabs.

* Fixed a bug that would hinder text-to-speech.

* Fixed a bug, where the logo in the browser logo source would not be centered.


## v2.7.3 (2019-02-13)

### Fix

* Fixed a crash caused by closing match tabs.

* Fixed a bug where import & overwrite profile would fail if only one profile exists.


## v2.7.2 (2019-02-11)

### New

* Added a MatchGrabber for Chobo Team League.


## v2.7.1 (2019-02-10)

### Fix

* Fixed a bug that would prevent the misc setttings to show.


## v2.7.0 (2019-02-10)

### New

* Added a new Veto Browser Source.

* Added '(Race1)' and '(Race2)' placeholders for Twitch and Nightbot (in a team match these refer to player's races of the next set).

* Added 'bestof.txt' file to 'casting_data'.

* "BoX" can now be displayed in the score browser source as demonstrated by the "Blue" skin.

* Vetoed maps can now be marked in the MapStats Browser Source.

* Added option to enter map vetos.

### Changes

* Executable can now be placed in folders that require admin priviliges.

* Reworked the Custom Match-Format Tab.

* Updated map images of Acid Plant, Automaton, Cyber Forest, Dreamcatcher, Kairos Junction, King's Cove, New Repuganancy, Para Site, Stasis, and Year Zero.

### Fix

* Fixed a bug that would prevent interaction with the mapstats browser source in OBS when using the 'StarCraft 2' skin.

* Fixed bug where the maps would not be order alphabetically in mapstats browser source.


## v2.6.2 (2019-01-19)

### Changes

* Added two misc div containers in score.html to allow for more freedom in designing a score skin/style.

* Added span-tags to race logos in html templates of both mapicons as well as the intro to allow for an easier custom coloring.

* Added upcoming ladder maps (Cyper Forest, King's Cove, New Repugnancy, Year Zero) and removed old maps (16-Bit, Catalyst, Darkness Sanctuary, Redshift). Note: If you want old maps removed from you profile, you have to remove them by yourself using the Map Manager in Misc Settings.


## v2.6.1 (2019-01-16)

### New

* Added the options to open/copy the external URL of a browser source to the menus.

### Fix

* Fixed a bug where a new profile would only work after a restart.


## v2.6.0 (2019-01-12)

### New

* StarCraft Casting Tool now serves all browser sources via http. This allows for easier access and access via local network or internet.

* Added txt-files `score1.txt` and `score2.txt` with individual scores to casting_data.

### Changes

* Executable is now 64-bit based on Python 3.7.2 (32-bit is no longer supported)

### Fix

* Fixed a bug where the number of connected browser sources would not be displayed correctly.

* Fixed an issue where the top border of the StarCraft 2 score icon would be cut off with standard Custom CSS settings in OBS.


## v2.5.4 (2018-12-15)

### Fix

* Updated RSL format in match grabber to Proleague format.


## v2.5.3 (2018-12-14)

### New

* Added Matchgrabber for RSTL successor RSL (https://rfcs.ru/en/tournaments/list/tournament/rsl-1/).


## v2.5.2 (2018-12-09)

### New

* Added context menu with predefined durations to countdown.

* Added "Add Alias" context menu entry for player names.

* Added "Set Today" context menu and popup calender to countdown date selection.

* A (partial) translation to French is now available thanks to chemsed alias Seireitei.

### Changes

* Countdown will now display 'soon™' or a custom text once the countdown is finished - it can be changed in config.ini.

### Fix

* Fixed a bug where the txt-files would not be updated in 1vs1 mode when a player name was changed.


## v2.5.0 (2018-11-18)

### New

* Added StarCraft2 skin/style for Countdown.

* New Countdown Browser Source!


## v2.4.3 (2018-11-11)

### New

* Playernames can now be assigned to Aligulac IDs in the Misc Settings to improve reliability of the Aligulac Prediction.

### Changes

* Improved automatic player selection of Aligulac Prediction.


## v2.4.2 (2018-11-04)

### Fix

* Fixed an issue where the top border of the StarCraft 2 score skin would be could off when using standard Custom CSS settings in OBS.


## v2.4.1 (2018-10-21)

### New

* Added Custom Format for upcoming ESL SC2 Open Team League Autumn 2018, see https://play.eslgaming.com/starcraft/global/sc2/open/league/all-kill-autumn-2018/


## v2.4.0 (2018-10-14)

### New

* MatchGrabber is now suggesting upcoming AlphaTL matches.

* Added score and landscape mapicon style 'Continuous Red' created by Seireitei.

### Changes

* Removed 'Twitch Communites' as they are deprecated.


## v2.3.2 (2018-10-07)

### Fix

* Longer map names such as 'Dreamcatcher' are now completly visible in the mapstats 'StarCraft2' skin.

* Fixed mapstats animation when changing the map pool.


## v2.3.1 (2018-09-25)

### Changes

* Added handling of critical errors.

### Fix

* Fixed a bug where race icons in the maps stats browser source would not be displayed in StreamlabsOBS.


## v2.3.0 (2018-09-16)

### New

* Added a new 'StarCraft 2' style/skin for all browser sources.

### Fix

* Fixed a bug where the logo would not be swapped when the option to auto swap is active.

* Fixed a bug where the Match Format was not updated when using the Match Grabber.

* Fixed a bug where a incomplete signal was sent to the mapicons when using auto completion for maps.


## v2.2.2 (2018-09-10)

### Fix

* Fixed a bug where the match format would not update when changing the match tabs.

* Fixed entanglement issue of match tabs.


## v2.2.0 (2018-09-09)

### New

* Added a basic Aligulac Browser Source that predicts the outcome of a 1vs1 match.

* Added option to specify the SC2 client API address in the misc menu to enable a two pc streaming setup.

* Added Match Tabs that allow you to manage multiple matches at the same time and jump between them.

* Added a generic Proleague Format to Custom Formats.

### Changes

* Last open tab is now saved and automatically selected in settings dialogs.

* Koprulu custom format changed back to Bo7 All-Kill.

### Fix

* Fixed a bug where placeholders used by Twitch and Nighbot would use the selected match tab instead of the active tab.

* Fixed a bug where copying a match tab would entangle both tabs.

* Fixed a bug where TTS would announce team 'TBD'.

* Fixed a bug that impaired tts.


## v2.1.4 (2018-08-20)

### Fix

* Fixed a crash that would occure when adding a map to the mapstats custom map pool.

* Fixed a crash that would occur when adding a map to the mapstats custom map pool.


## v2.1.3 (2018-08-19)

### New

* Added link to Tutorial Video.

### Fix

* Fixed a bug where the new AlphaTL Match Banner would not be downloaded.

* Fixed a bug where "0 - 0" would always be written into score.txt.

* Fixed a bug where dragging and dropping a logo onto team 2 would not work.


## v2.1.0 (2018-08-11)

### New

* Implemented Google-Cloud Text-to-Speech Voices for the Intros.

### Fix

* Fixed a bug where the hotkeys for intros would not be reactivated.

* Fixed various typos in the localization.


## v2.0.1 (2018-08-03)

### New

* Map Icons are now connected via websocket to the tool and fully animated.

* Added a new Mapstats Browser Source.

* Added a blacklist for the ingame score task to deactivate it when you are playing yourself.

* Prepared tool for upcoming upgrade to v2.0; This is the last update prior to v2.0.

* Already played maps can be marked in the mapstats browser source.

* Added a 'Blue' skin/style for the score icon, the landscape map icons, and the player intro.

* Added scope and volume to Text-to-Speech settings.

* The Score Icon is now connect via websocket to SCCT and fully animated.

* Logos and Matchbanner are no longer download if they are identical to the current logos or banner.

* Restructured the settings.

* Added a Profile Manager.

* Added LEDs to status bar indicating when browser sources are connected to StarCraft Casting Tool.

### Changes

* Added upcoming ladder maps.

* Upgrade to Twitch-API v5.

* Updated to Twitch-API v5 and included the option to set game to 'StarCraft 2' and community to 'StarCraft Casting Tool'.

* Changed Koprulu League format to Pro League.

* Added option to import and overwrite current profile.

* Added the GIF format to the list of supported file types for the team logo.

* One can now use a single combined hotkey for both player intros. This option is the new default.

### Fix

* Fixed a bug in the AlphaTL match grabber that occured if a team has no logo.

* Custom css-files with whitespaces are automatically renamed.

* Fixed a bug to save nightbot commands.

* Fixed a bug the would prevent the Nightbot token from being saved.

* Fixed a bug that would prevent the Nightbot token from being saved.

* Fixed a bug in connection with tesseract OCR.

* Text-to-Speech is now disabled by default.


## v1.12.3 (2018-07-20)

### Changes

* Changed Koprulu League format to Pro League.


## v1.12.2 (2018-06-01)

### Fix

* Fixed a bug that prevented using a non-default skin for the intros.


## v1.12.1 (2018-05-26)

### Fix

* Fixed a bug that prevented StarCraft Casting Tool from terminating.

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

### New

* Player names are used or have been used in the current session are available for auto completion.

### Changes

* All-Kill Format no longer needs to be applied via "Apply Format".

### Fix

* Winning player should now be properly transfered to the next map when using All-Kill-Format/Mode.


## v1.8.0 (2018-03-31)

### New

* Match Grabber can now be used by pressing enter.

* Removed FTP-Upload. If you were using this feature, please contact me and I will provide an alternative via websockets.

* Added Logo Manager featuring last used logos, favorites, adding from URL, and searching Liquipedia for logos.

### Changes

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


