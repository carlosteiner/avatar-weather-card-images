#!/usr/bin/env python3
"""Add (or remove) a set in index.json from a release zip. Used by the GitHub Action; also runnable by hand:

  python3 tools/update_index.py --zip amanda-1.0.0.zip --tag amanda-v1.0.0 --repo OWNER/REPO [--index index.json]
  python3 tools/update_index.py --remove --tag amanda-v1.0.0

The release tag must be <id>-v<version>; both must match series.json inside the zip. Nothing is written when the zip is not valid.
"""
import argparse, hashlib, json, re, sys, zipfile

TAG = re.compile(r"^([a-z0-9][a-z0-9_-]{0,39})-v(\d+\.\d+\.\d+)$")
MAX_ZIP, MAX_FILES, MAX_UNPACKED = 150 * 1024 * 1024, 700, 400 * 1024 * 1024
SLOT = re.compile(r"^[a-z0-9_]+\.webp$")


def fail(msg):
    print(f"ERROR: {msg}")
    sys.exit(1)


def check_zip(path, sid, version):
    data = open(path, "rb").read()
    if len(data) > MAX_ZIP:
        fail("the zip is larger than 150 MB")
    try:
        z = zipfile.ZipFile(path)
        infos = z.infolist()
        meta = json.loads(z.read("series.json"))
    except (zipfile.BadZipFile, KeyError, ValueError) as err:
        fail(f"not a valid set zip (needs a series.json): {err}")
    if len(infos) > MAX_FILES or sum(i.file_size for i in infos) > MAX_UNPACKED:
        fail("too many files or too large when unpacked")
    pics = [i.filename for i in infos if i.filename.endswith(".webp")]
    bad = [n for n in pics if not SLOT.match(n)]
    if bad:
        fail(f"picture names not allowed: {bad[:3]}")
    if not pics:
        fail("the zip has no pictures")
    for k, label in (("id", sid), ("version", version)):
        if meta.get(k) != label:
            fail(f"series.json {k} is {meta.get(k)!r} but the release tag says {label!r}")
    for k in ("name", "author", "license"):
        if not str(meta.get(k, "")).strip():
            fail(f"series.json has no {k}: fill it in (Rename / details) and export again")
    return data, meta, len(pics)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--zip", default="")
    ap.add_argument("--repo", default="")
    ap.add_argument("--index", default="index.json")
    ap.add_argument("--remove", action="store_true")
    a = ap.parse_args()
    m = TAG.match(a.tag)
    if not m:
        fail(f"the release tag {a.tag!r} must look like <id>-v<version>, e.g. amanda-v1.0.0")
    sid, version = m.groups()
    try:
        idx = json.load(open(a.index))
    except FileNotFoundError:
        idx = {"series": []}
    series = [e for e in idx.get("series", []) if e.get("id") != sid]
    if a.remove:
        old = [e for e in idx.get("series", []) if e.get("id") == sid and f"/{a.tag}/" in e.get("zip_url", "")]
        if not old:
            print("nothing to remove (that version is not the one in the catalog)")
            return
    else:
        if not a.zip or not a.repo:
            fail("--zip and --repo are needed")
        data, meta, count = check_zip(a.zip, sid, version)
        name = a.zip.replace("\\", "/").rsplit("/", 1)[-1]
        series.append({"id": sid, "name": meta["name"], "version": version, "description": meta.get("description", ""),
                       "author": meta["author"], "license": meta["license"], "attribution": meta.get("attribution", ""),
                       "count": count, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                       "zip_url": f"https://github.com/{a.repo}/releases/download/{a.tag}/{name}"})
    series.sort(key=lambda e: e["id"])
    json.dump({"series": series}, open(a.index, "w"), indent=2, ensure_ascii=False)
    open(a.index, "a").write("\n")
    print(("removed " if a.remove else "catalog updated: ") + a.tag)


if __name__ == "__main__":
    main()
