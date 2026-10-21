"""Check index.json the way D5 Mod Kit's Browse Mods page does (d5lib/modindex.py), and every mod that is new or
changed: download it, compare its size and SHA-256 with the entry, and run the package rules on the zip.

    python tools/check_index.py                 check the list's format only
    python tools/check_index.py --changed BASE  also download and check the entries that differ from BASE
                                                (a copy of index.json from the main branch)

Standard library only.  Exit code 1 when anything is wrong (the pull request check fails)."""
import hashlib
import json
import os
import re
import sys
import tempfile
import urllib.parse
import urllib.request
import zipfile

FORMAT = 1
CATEGORIES = ["Character", "Outfit", "Class", "Monster", "Stage", "Skill", "Music", "Text", "Gameplay", "Other"]
ALLOWED_HOSTS = {"github.com", "raw.githubusercontent.com", "objects.githubusercontent.com",
                 "release-assets.githubusercontent.com"}
MAX_DOWNLOAD = 2 << 30
MAX_FILE = 512 << 20
MAX_TOTAL = 4 << 30
MAX_RATIO = 400
MAX_FILES = 50000
MAX_PREVIEW = 1 << 20
ALLOWED_EXT = {".json", ".txt", ".md", ".lzs", ".anm", ".obf", ".txf", ".dat", ".chr", ".hex", ".gop", ".pac", ".bin",
               ".ogg", ".vag", ".png", ".jpg", ".jpeg", ".webp", ".bmp", ".wav", ".flac", ".mp3"}
HEX64 = re.compile(r"^[0-9a-f]{64}$")
UID = re.compile(r"^[0-9a-f]{32}$")
ROOT = os.environ.get("D5MODS_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def url_ok(url):
    u = urllib.parse.urlparse(url)
    return u.scheme == "https" and (u.hostname or "").lower() in ALLOWED_HOSTS


def entry_problems(e):
    out = []
    for k in ("uid", "name", "author", "version", "download", "sha256", "size"):
        if not e.get(k):
            out.append(f"missing '{k}'")
    if e.get("uid") and not UID.match(str(e["uid"])):
        out.append("uid must be the 32 hex digits of the mod's mod.json")
    if e.get("sha256") and not HEX64.match(str(e["sha256"]).lower()):
        out.append("sha256 is not 64 hex digits")
    try:
        if not 0 < int(e.get("size", 0)) <= MAX_DOWNLOAD:
            out.append("size out of range")
    except (TypeError, ValueError):
        out.append("size is not a number")
    if e.get("download") and not url_ok(e["download"]):
        out.append("download must be an https address on github.com (a release asset or a repository file)")
    if e.get("category") and e["category"] not in CATEGORIES:
        out.append(f"category must be one of {', '.join(CATEGORIES)}")
    p = e.get("preview")
    if p:
        if p.startswith("https://"):
            if not url_ok(p):
                out.append("preview must be in this repository (previews/...) or on github.com")
        else:
            full = os.path.join(ROOT, p)
            if ".." in p.split("/") or not p.startswith("previews/"):
                out.append("preview must be a file in previews/")
            elif not os.path.exists(full):
                out.append(f"preview {p} is not in the repository")
            elif os.path.getsize(full) > MAX_PREVIEW:
                out.append(f"preview {p} is over 1 MB")
            elif os.path.splitext(p)[1].lower() not in (".png", ".jpg", ".jpeg", ".webp"):
                out.append("preview must be PNG, JPG or WebP")
    if e.get("github") and not re.match(r"^[A-Za-z0-9-]{1,39}$", str(e["github"])):
        out.append("github must be a GitHub account name")
    for r in e.get("requires") or []:
        if not UID.match(str(r)):
            out.append(f"requires: {r!r} is not a mod uid")
    return out


def check_zip(path):
    with zipfile.ZipFile(path) as z:
        infos = [i for i in z.infolist() if not i.is_dir()]
        if not infos or len(infos) > MAX_FILES:
            raise ValueError("empty, or too many files")
        tops, total = set(), 0
        for i in infos:
            n = i.filename
            parts = n.split("/")
            if n.startswith("/") or "\\" in n or ":" in n or ".." in parts or any(p in ("", ".") for p in parts):
                raise ValueError(f"unsafe path: {n}")
            if i.flag_bits & 0x1:
                raise ValueError(f"encrypted file: {n}")
            tops.add(parts[0])
            if "/".join(parts[1:]) != "mod.json" and os.path.splitext(n)[1].lower() not in ALLOWED_EXT:
                raise ValueError(f"a file type mods don't use: {n}")
            if len(parts) > 2 and parts[1] == "files" and parts[2].upper() in ("EXE", "GAME"):
                raise ValueError(f"a program file for the game folder: {n}")
            if i.file_size > MAX_FILE:
                raise ValueError(f"a file over {MAX_FILE >> 20} MB: {n}")
            if i.compress_size and i.file_size / i.compress_size > MAX_RATIO and i.file_size > (1 << 20):
                raise ValueError(f"unpacks far too big: {n}")
            total += i.file_size
        if total > MAX_TOTAL:
            raise ValueError("more than 4 GB unpacked")
        if len(tops) != 1:
            raise ValueError("the zip must hold exactly one mod folder")
        top = tops.pop()
        return json.loads(z.read(f"{top}/mod.json").decode("utf-8"))


def check_download(e):
    req = urllib.request.Request(e["download"], headers={"User-Agent": "D5ModKit-Mods-check"})
    h, size = hashlib.sha256(), 0
    fd, tmp = tempfile.mkstemp(suffix=".zip")
    try:
        with os.fdopen(fd, "wb") as out, urllib.request.urlopen(req, timeout=120) as r:
            if not url_ok(r.geturl()):
                return [f"the download redirects off GitHub: {r.geturl()}"]
            while True:
                chunk = r.read(1 << 20)
                if not chunk:
                    break
                size += len(chunk)
                if size > MAX_DOWNLOAD:
                    return ["the download is over 2 GB"]
                h.update(chunk)
                out.write(chunk)
        out = []
        if size != int(e["size"]):
            out.append(f"size is {size}, the entry says {e['size']}")
        if h.hexdigest() != str(e["sha256"]).lower():
            out.append(f"sha256 is {h.hexdigest()}, the entry says {e['sha256']}")
        try:
            meta = check_zip(tmp)
            if meta.get("uid") != e["uid"]:
                out.append(f"the package's mod.json uid is {meta.get('uid')}, the entry says {e['uid']}")
            if str(meta.get("version", "")) != str(e["version"]):
                out.append(f"the package's version is {meta.get('version')}, the entry says {e['version']}")
        except Exception as ex:
            out.append(f"package: {ex}")
        return out
    except Exception as ex:
        return [f"download failed: {ex}"]
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass


def pr_author():
    """the pull request's author (GitHub Actions' event file), or None"""
    try:
        with open(os.environ["GITHUB_EVENT_PATH"], encoding="utf-8") as f:
            return json.load(f)["pull_request"]["user"]["login"]
    except (KeyError, OSError, ValueError, TypeError):
        return None


def main(argv):
    with open(os.path.join(ROOT, "index.json"), encoding="utf-8") as f:
        idx = json.load(f)
    bad = 0
    if idx.get("format") != FORMAT or not isinstance(idx.get("mods"), list):
        print(f"index.json: 'format' must be {FORMAT} and 'mods' a list")
        return 1
    seen = set()
    for e in idx["mods"]:
        name = e.get("name") or e.get("uid") or "?"
        probs = entry_problems(e)
        if e.get("uid") in seen:
            probs.append("the same uid twice (one entry per mod: update its version instead)")
        seen.add(e.get("uid"))
        for p in probs:
            print(f"{name}: {p}")
        bad += bool(probs)
    if "--changed" in argv:
        base_path = argv[argv.index("--changed") + 1]
        try:
            with open(base_path, encoding="utf-8") as f:
                base = {x.get("uid"): x for x in json.load(f).get("mods", [])}
        except (OSError, ValueError):
            base = {}
        author = pr_author()
        owner = (os.environ.get("GITHUB_REPOSITORY_OWNER") or "").lower()
        now = {x.get("uid") for x in idx["mods"]}
        if author and author.lower() != owner:
            for uid, was in base.items():
                if uid not in now and (was.get("github") or "").lower() != author.lower():
                    print(f"{was.get('name')}: a post can't take someone else's mod off the list")
                    bad += 1
        for e in idx["mods"]:
            if base.get(e.get("uid")) == e or entry_problems(e):
                continue
            was = base.get(e.get("uid"))
            if author and author.lower() != owner:
                who = (e.get("github") or "").lower()
                if who and who != author.lower():
                    print(f"{e['name']}: the entry says it was posted by {e['github']}, the pull request is by {author}")
                    bad += 1
                    continue
                if was and was.get("github") and was["github"].lower() != author.lower():
                    print(f"{e['name']}: only {was['github']} (who posted it) can post its updates")
                    bad += 1
                    continue
            print(f"checking {e['name']} v{e['version']} ...")
            probs = check_download(e)
            for p in probs:
                print(f"{e['name']}: {p}")
            bad += bool(probs)
    print("index.json: OK" if not bad else f"{bad} entr{'y' if bad == 1 else 'ies'} with problems")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
