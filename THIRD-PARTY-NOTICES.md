# Data Sources and Copyright

Quest facts and adapted Classic reference relationships come from Dungeon Questie, Copyright (c) 2026 Videocat, via https://github.com/coffeelover1010/dungeon-questie. The exact catalogue revision is recorded in data/research-snapshot.json. No addon implementation was copied.

Its Classic reference data is adapted from CMaNGOS Classic-DB under GPL version 3: https://github.com/cmangos/classic-db. The relevant licence, authors and copyright notice are included in licenses/. Here, entries were filtered for Alliance and the selected dungeons, prerequisites were traversed recursively, and item facts were merged with GearQuest. Corresponding editable source data and the conversion script are included in data/research-snapshot.json and scripts/build_data.py. Changes were made on October 10, 2026.

Item names and numerical item facts: GearQuest Forever, https://github.com/Henrik8210/gear-quest-forever. The revision is recorded in the snapshot. This is an independent web page, not an official version of either addon.

Item information: Wowhead Forever, https://www.wowhead.com/forever. Current tooltip markup is cached in data/item-tooltip-snapshot.json; original item icons served by the Wowhead CDN are cached in assets/icons/. Tooltips and icons are embedded in the standalone HTML and can be refreshed online. Original Classic+ game map images served by the Wowhead CDN are cached in assets/maps/ and embedded in the standalone HTML; map coordinates are extracted from the corresponding Forever quest mapper data. Artwork belongs to Blizzard or its licensors and is not relicensed as original software. Item and map sources and research dates are retained in the snapshots. World of Warcraft names, game content and artwork belong to Blizzard Entertainment or its licensors.

Classic interface artwork: Blizzard interface textures made available through https://github.com/Gethe/wow-ui-textures/tree/classic. Source paths are recorded in data/ui-assets.json. Original PNGs are retained in assets/ui/ and used as backgrounds and sprite pieces in the CSS. The artwork remains Blizzard's property and is not relicensed as original software. The editable theme is assets/ui/classic.css; the build script embeds the used textures into the standalone page.

Fonts: Marcellus and IM FELL English SC from https://github.com/google/fonts, used under their SIL Open Font Licences. Font files are retained in assets/fonts/ and their corresponding OFL notices are included in licenses/marcellus-OFL.txt and licenses/imfellenglishsc-OFL.txt.
