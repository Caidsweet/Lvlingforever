# Forever — Party Quest Log

Open **index.html** directly in your browser. The page is self-contained and needs no installation. For local development: `python -m http.server 8080 --directory /workspace/Lvlingforever`.

## Classic Interface

The local redesign uses original Classic interface textures for the stone panels, silver frame corners, quest-book emblem, red buttons, selection highlights, parchment and scroll arrows. The quest view places its list in the left panel and its text/rewards on the right page. Dungeon preparation is an expandable section. The window has working close/reopen controls, independent desktop scrolling and a responsive mobile layout. Progress, quest maps and cached item tooltips remain functional.

Edit `assets/ui/classic.css` to change the theme. The builder embeds its `asset://` references, including the open fonts, into `index.html`, so review copies work offline. Asset sources and font licences are recorded in `data/ui-assets.json` and `THIRD-PARTY-NOTICES.md`. `forever-guide-classic-v6.html` is the local review copy. It starts in a selected quest to demonstrate the two-panel layout; the published page starts at the normal 1–10 route.

Alliance, 1 tank, 1 healer and 3 DPS. Follow RestedXP for levels 1–10, then a general levelling route to **30**. Twelve dungeon views, 67 quest entries and 108 reward cards remain available, including class quests and follow-ups. Three additional Void Pearl entries are retained as unresolved references because their Forever item records are unavailable. The same quest may appear in multiple dungeons. Ragefire Chasm is excluded. Dalaran and Razorfen Kraul are optional late-20s plans with no verified full-run recommendation before 30. Gnomeregan and Scarlet Monastery notes are saved separately for later planning; quests with a minimum level above 30 are explicitly labelled.

The main route is based on the user's research compiled October 10, 2026, prioritising [ForeverDB](https://foreverdb.net/guide/leveling) and [WoW Forever Guides](https://wowforeverguides.com/leveling). Research & Sources includes all six guide references, their assessed uses and limitations, class-guide links and the supplied October 8 Blizzard patch summary. The linked articles and official post could not be accessed from this runtime (proxy HTTP 403), so these summaries are attributed to the supplied research, rather than claimed as independently verified. The assessment is editable in `data/leveling-research.json` and embedded by the builder.

Zone bands are overlapping alternatives: racial starters, Westfall/Loch Modan/Darkshore around 10–20, then Ashenvale/Wetlands/Duskwood around 20–30, with Redridge to fill gaps. The page does not ask the party to finish every zone. Preparation details are drawn separately from the quest snapshots. No XP-per-hour or fixed completion-time claims are used. The reported approximately 20% dungeon-enemy XP increase is not presented as 20% more total run XP or proof that dungeon farming is faster.

The northern route combines Ruins of Lordaeron at around level 22 with Shadowfang Keep during the same 22–24 trip. Blackfathom Deeps follows at 24–26. Prepare paladin and warlock quests before travelling north, and group the turn-ins after both northern dungeons.

Quest completion and checked prerequisites are saved locally in your browser. In-game quest and item names retain their English names. Item tooltips support mouse hover, keyboard focus and touch. All 108 reward cards use cached Wowhead Forever tooltip markup and original icons, covering 106 distinct items fetched on October 10, 2026. The classic dark tooltip frame preserves rarity colours, item level, equipment slots, class requirements, Equip/Use effects, cooldowns and sell-price coins. It follows the cursor and stays within the viewport. Tooltip HTML is filtered before display. Internal stat names and duplicated school-damage totals are excluded from fallback formatting.

Use **Refresh Wowhead Tooltips** in Research & Sources to request live updates from `nether.wowhead.com/forever/tooltip/item/{id}`. A failed request retains the embedded successful tooltip and icon. `python scripts/fetch_items.py` downloads missing tooltips and icons; add `--refresh` to update successful cached records. Failed refreshes preserve prior data. Run `python scripts/build_data.py` afterwards to embed the cache. The three unavailable Void Pearl IDs are documented in `data/item-data-gaps.json`; their old names are not displayed as confirmed reward cards.

## Data Sources and Limitations

- [Wowhead Forever](https://www.wowhead.com/forever): primary source for current item tooltips. Direct access succeeded during map research on October 10, 2026. Map positions were extracted from Forever quest pages and cached; later requests returned HTTP 403, so successful research records are preserved rather than replaced by failed refreshes. The browser map workflow was tested using embedded images and cached coordinates.
- [Dungeon Questie](https://github.com/coffeelover1010/dungeon-questie): beta catalogue and recursive prerequisites. Exact snapshot commits are recorded in `data/research-snapshot.json`.
- [GearQuest Forever](https://github.com/Henrik8210/gear-quest-forever): older item stats retained only as a fallback for new imported/missing records. Current reward tooltips use the cached Forever data instead; matching names in older Classic/TBC data do not establish current Forever stats.
- The user’s screenshots confirm quest lists for the seven dungeons shown.

Known gaps are flagged on the page: the Abominable Creatures pickup, some Ruins of Lordaeron quest-starting items, certain Excavation chains, Past Due and the prerequisite for Researching the Corruption. The Treaty of Understanding: the screenshot shows minimum level 9, while the catalogue lists 16. The Fury Runs Deep: the screenshot shows 25, while the catalogue lists 22; the guide plans pickup at 25. City of Dalaran was open in beta according to the catalogue; launch availability and the recommended group level have not been verified live.

All rewards are listed when present in the catalogue. An empty reward list means item rewards are not documented, rather than proving that the quest has none. Choice and guaranteed rewards are not always distinguished in the source. No missing stats or locations have been invented.

## Update the Data

`python scripts/build_data.py` builds `data/guide.json` and the HTML file’s embedded quest, item, map and levelling-research data from the included editable snapshots. No packages or external checkouts are needed. Generated text and interface copy are in English. Versioned `forever-guide-*.html` review copies are local and ignored by Git; regenerate and copy `index.html` to a new versioned filename when sharing a new attachment preview.

## GitHub Pages

The site entry point is `index.html`. The `.nojekyll` file enables plain static-file publication. In the repository's **Settings → Pages**, use **Deploy from a branch**, select **main** and **/ (root)**, then save. GitHub will build and publish the page at `https://caidsweet.github.io/Lvlingforever/`. Subsequent pushes to main update the site automatically. No Node build, backend or custom domain is required. Cached item icons, tooltips and maps work without external requests; live refreshes depend on Wowhead availability.

To deliberately update from new research checkouts: `python scripts/build_data.py /path/to/dungeon-questie /path/to/gear-quest-forever`. Review data gaps and changes before using new values for a launch run. Research & Sources on the page also supports JSON imports for temporary additions; an import lasts for the session and replaces the entire dungeon list.

## Quest Map

Use **Quest Map** for the full map view, or **Show Quest on Map** inside a quest. Filter by dungeon, quest and zone. Gold `!` markers show quest pickups; gold `?` markers show turn-ins. Hover, focus or tap a marker to see the NPC, quest name, coordinates and prerequisite step. Multiple quests at the same NPC are grouped. Pickups and turn-ins at the same location have separate markers. Prerequisite and follow-up quests are included by default; completed steps can be hidden.

Twenty original WoW Forever / Classic+ in-game zone maps are embedded in the HTML. Their source is `wow.zamimg.com/images/wow/classicplus/maps/enus/original/{zoneId}.jpg`. The Classic+ path is required: the general Retail path uses different layouts and cannot be used with these coordinates. Coordinates come from the corresponding Wowhead Forever quest mapper data, not guessed positions or converted Retail pins. Horde class trainers in shared quest records are omitted for this Alliance route.

Where Wowhead publishes no world-map position, the location instructions are listed below the map without a marker. Item-started quests and interior pickups are not assigned invented outdoor coordinates. Published coordinates are database evidence, not live-client verification of launch availability.

`python scripts/fetch_maps.py` reads cached successful quest records, downloads map assets, and writes `data/map-snapshot.json`. Add `--refresh` to explicitly refresh quest pages. Failed quest refreshes retain the previous successful record. Run `python scripts/build_data.py` afterwards to embed updated coordinates and maps into `index.html`. The cached research records and original downloaded maps are included in `data/wowhead/` and `assets/maps/`.

[Mobalytics — Zone Map Level Ranges](https://mobalytics.gg/wow-forever/guides/zone-map-level-ranges) is a user-recommended planning reference. Its domain was added to the saved network configuration draft, preserving the existing Wowhead domains. Access remains blocked in the current runtime; the article has not been reviewed or used as verified route data. Review and save the network settings and publish the environment to enable the saved configuration.

## Reusable Cloud Setup

The saved environment draft includes `start_skill` instructions for serving and checking this static page, preserving cached research and using the existing checkout. It also retains the Wowhead and Mobalytics domains and adds the six linked research hosts: `foreverdb.net`, `wowforeverguides.com`, `overgear.com`, `wowforeversite.wiki`, `www.wowforever.games` and `us.forums.blizzard.com`. Saving the draft does not apply these changes to the running instance or publish the environment. Review/save the settings and publish to make them reusable. No installation script or secret is needed for the offline HTML workflow.

## Licences

Adapted Classic reference data is covered by GPLv3. The licence, copyright notices and original authors are included in `licenses/`. Corresponding editable snapshot data and the conversion script are included. Dungeon Questie’s original code is MIT-licensed; no addon functions were copied here. See `THIRD-PARTY-NOTICES.md`. Game names, content and online artwork belong to Blizzard or its licensors.
