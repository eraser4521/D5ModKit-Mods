# D5 Mod Kit — community mods

The list of mods that players share for **Disgaea 5 Complete (PC)**, made with
[D5 Mod Kit](https://github.com/eraser4521/D5ModKit). D5 Mod Kit reads this list on its **🛍 Browse Mods** page:
every mod here, with a picture and a description, can be installed in one click.

You don't need a GitHub account to browse or install. Open D5 Mod Kit (1.5.7 or newer) and pick **Browse Mods**.

## How safe is it?

* A mod is **data**: sprites, maps, text, music and the kit's patch files. D5 Mod Kit refuses any package that
  carries programs (`.exe`, `.dll`, scripts …) or files for the game folder. The kit writes every change to the game
  program itself.
* Every entry has the download's exact size and **SHA-256** checksum. The kit throws away a download that doesn't
  match, so a file that was swapped or damaged after review is never imported.
* Downloads come from GitHub only (release assets or repository files).
* New entries and updates are **reviewed** before they are merged, and an automatic check downloads every new or
  changed mod and runs the same package rules the kit uses. Only the account that posted a mod can post its updates
  or take it off the list.
* Installing a new version keeps the old one as a backup (`D5ModKit/state/mod_backups`).

## Post a mod

Everything happens in D5 Mod Kit (1.5.7 or newer):

1. **Browse Mods › 📤 Post my mod…**
2. The first time, sign in with GitHub: the kit shows a short code, **Open GitHub** opens the page where you paste it
   and press **Authorize**. You need a free GitHub account; that page lets you make one. Only once per PC.
3. Pick your mod, give it a version, your name, its kind, a one-line summary, a description and a picture, tick
   that it's your work, and press **📤 Post**.

The kit uploads the mod, adds it to the list and sends it for review. **📬 My posts** shows whether it's waiting,
published or declined (with the reviewer's reason). An **update** is the same mod posted again with a higher
version: players who have it see **⬆ Update**. Only the account that posted a mod can post its updates.

<details><summary>Without the kit (for people who know GitHub)</summary>

Make the entry yourself (format below), upload the zip to a release of a repository of yours, add the entry to
`index.json` and a picture as `previews/<uid>.png` in a fork, and open a pull request.
</details>

### What gets listed

* Your own work, or work you have permission to share. Credit what it builds on; the kit records it in the mod's
  `based_on` when you use **Make my own version**.
* Mods that work: tested in the game with the D5 Mod Kit version given in the entry's `kit` field.
* No content that is illegal or hateful, and no sexual content involving minors.

Mods belong to their authors. The list itself (index.json and the tools) is MIT licensed.

## The entry format

```json
{
  "uid": "32 hex digits: the mod's identity (from its mod.json)",
  "name": "Thunderlady",
  "author": "you",
  "version": "1.2",
  "category": "Character",
  "summary": "One line: what it adds",
  "description": "A few lines: what's in it, how to get it in game",
  "tags": ["character", "Disgaea RPG"],
  "requires": ["uid of a mod it needs", "..."],
  "kit": "1.5.7",
  "preview": "previews/<uid>.png",
  "page": "https://github.com/you/your-repo (optional)",
  "download": "https://github.com/you/your-repo/releases/download/v1.2/Thunderlady_v1.2.zip",
  "size": 1234567,
  "sha256": "64 hex digits",
  "updated": "2026-10-21"
}
```

Categories: Character, Outfit, Class, Monster, Stage, Skill, Music, Text, Gameplay, Other.

`python tools/check_index.py` checks the list. `python tools/check_index.py --changed <old index.json>` also
downloads and checks the entries that changed.
