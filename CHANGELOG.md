# Changelog

## 1.1.0
- Bigger kill goals, each stage twice the last or more: Horde 1 150 of each kind (210 of each out), Horde 2 300 of each (420 out), the Climb 500 of each (700 out).
- The Climb's beasts are scattered through every hall of 1@mjo2 instead of crowding a few corridors, and everyone lands at 320, 79.
- Nightwing points the way: whenever there's someone to find (Nightwing after a horde, James on the crag, the summit, James in Niflheim, the chest), everyone gets a word from him with a link that opens the navigation.
- The Alpha Werewolves face off with Nightwing before they attack, in a dialogue everyone on the crag clicks through: the Druid's blue werewolf portrait on the left (mirrored to face him) and Nightwing's wereraptor on the right. The alphas wait until the leader closes it, or 30 seconds.
- The finale: 3 Werewolves come halfway between the Black Sun's calls, and the Black Sun's werewolf face flashes up every time it calls its 35 beasts.
- Nightwing's orders match the stages again (150 of each kind for Horde 1, 300 of each for Horde 2, 500 of each on the Climb).
- James comes back to himself only once the chest has been opened (by everyone on the field, or a minute after the leader), so nobody is sent home before taking their share.
- The Black Sun's werewolf portrait is as big as Nightwing's, in the corner, with his whole face and claw in view.
- Cleaner portraits: no pale rim or specks left over from the backgrounds they were cut from, and John's fur cuff is whole again (tools/clean_cutin.py).
- The beasts' skills are in effect again next to eden-rework-2021: the app can't combine two mods' db/mob_skill_db.txt, so Black Sun now loads after it ("after" in mod.json) and its copy wins. eden-rework-2021's own monster skills are left out while both are on (README).

## 1.0.0
- Black Sun is a full instance on Mt. Mjolnir (1@mjo1, the Crag, and 1@mjo2, the Climb), built on rAthena's instance system: every party (or solo player) gets its own copy, so any number of groups can run it at once.
- John Wolf (Prontera 113, 190) opens it: he tells James's story every time before anything else, then starts the climb (the party leader; members follow through him and can come back after dying), and keeps both exchanges (500 Premium Black Coins for 150 Cash Points, 1 Premium Black Ticket for 10,000,000 Zeny).
- The story: James is John's younger brother, and Nightwing (Royal Nightmare's) is their cousin and turns into a wereraptor; Horde 1 (the Pack), the three Alpha Werewolves, Horde 2 (the Black Sun rising), James on the crag, the Climb (1,500 frozen beasts on the switchbacks), and Niflheim (nif_fild03, the map the Black Werewolf always stood on), where James surrenders to the Black Sun. The instance has its own copy of nif_fild03, with the field's warps and NPCs switched off.
- The MVP is James, the Black Sun (26710): 2,000,000,000 HP, takes 1% damage (a red aura shows it), and while anyone is near him the Black Sun calls 35 beasts every 15 seconds. Every other beast takes 10% of the damage it's dealt.
- Every stage's beasts spawn all at once when it starts, and every stage holds more than the last: Horde 1 150 of each kind (100 of each to kill), Horde 2 300 of each (200), the Climb 500 of each (350). Each Alpha Werewolf brings a pack.
- The reward is a chest where James falls (the 4_STAR_BOX_POW2 look), opened by everyone in the run for their own share: base and job EXP (10% of their level each), a Grey Wolf Cub in Mouth, a Wolf Orb (Above All) Lv 3, 5 King Wolf Scrolls, 500 Premium Black Coins and a Premium Black Ticket. Whoever leaves without opening it gets their share by mail. 8 hour cooldown per character.
- Base level 200 to enter.
- New monsters: the Werewolf (1022, 100M HP, Blue Moon Loli Ruri's damage a fifth higher), Alpha Werewolf, Moonfang Wolf, Black Sun Shade, Frostbite Hound, Feral Wereraptor and Skoll the Sun-Chaser, with their own skills (db/mob_skill_db.txt). The werewolf and wereraptor looks are the Druid's own forms.
- Every beast spawns large.
- The Alpha Werewolves, Feral Wereraptors and James have monster sprites of their own, made from the Druid's werewolf and wereraptor forms (System/jobname.lub, data/sprite/monster/, tools/druid_to_monster.py), so they can be clicked and targeted like any monster. James is the biggest of them, black as the eclipse.
- The sky darkens and the Black Sun rises as the night goes on (client/index.js): a black disc in a burning corona that travels across the sky faster at every stage.
- Portraits: Nightwing's (Royal Nightmare's), and John and James Wolf's own at the same size. James has three: himself, the wolf breaking through, and the Black Sun's werewolf. Nightwing's wereraptor form is the Druid's own art.
- Nightwing's wereraptor form uses a status nothing else on the server starts (db/status.yml): the Druid's own carries a player-only script and can't be put on an NPC.
