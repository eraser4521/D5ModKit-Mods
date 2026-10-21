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
  changed mod and runs the same package rules the kit uses.
* Installing a new version keeps the old one as a backup (`D5ModKit/state/mod_backups`).

## Submit a mod

1. In D5 Mod Kit: **Browse Mods › 📤 Share my mod…**. Pick the mod, fill in the version, your name, the kind of mod,
   a one-line summary and a description, and press **Export package + entry**. You get the mod's `.zip` and its
   list entry.
2. Upload the `.zip` to GitHub:
   * a release of a repository of yours (**Releases › Draft a new release**, attach the zip): the best place, and
     the only one for zips over 25 MB, or
   * a comment on your pull request (drag the zip into it; GitHub gives it a `github.com/user-attachments/...`
     address).

   Upload the file exactly as exported (the entry's checksum is that file's; a new export is a different file).
   Paste its download address into **Share my mod…** and press **Set address**.
3. Fork this repository. Add your entry to the `mods` list in `index.json`, and a picture as `previews/<uid>.png`
   (the `uid` is in the entry; 16:9, about 640 × 360, under 1 MB).
4. Open a pull request. The check runs on its own. A reviewer installs the mod and looks at it, then merges.

**An update** changes your existing entry (same `uid`): new `version`, `download`, `size`, `sha256` and `updated`.
Players who have the mod see **⬆ Update** on the Browse Mods page.

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
