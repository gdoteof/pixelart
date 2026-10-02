"""Upload a project's video to YouTube with the YouTube Data API.

    python -m pixelart.youtube PROJECT --dry-run              parse and check the upload kit
    python -m pixelart.youtube PROJECT                        upload (private) once you say yes, set the thumbnail
    python -m pixelart.youtube PROJECT --set-privacy public   change the uploaded video's privacy
    python -m pixelart.youtube PROJECT --set-thumbnail        (re)set the uploaded video's thumbnail
    python -m pixelart.youtube --sign-out                     revoke the tool's access, delete the token

The title, description, tags and main thumbnail come from the upload kit,
PROJECT/thumbs/youtube_upload.txt (the same text that would be pasted into
YouTube Studio), and are checked against YouTube's limits before anything is
sent. The video goes up in the Music category, not made for kids, flagged as
altered content when the kit has an ALTERED CONTENT section. Nothing is sent
until the user answers yes to a prompt naming the channel (--yes answers it
in advance). The only thing kept from YouTube is the new video's id, in
PROJECT/build/youtube.json with the title the kit gave it: a second upload
needs --again, and --set-privacy and --set-thumbnail act on that video.

The tool uses YouTube API Services, and using it means agreeing to the YouTube
Terms of Service. PRIVACY.md at the repo root is its privacy policy.

Credentials stay outside the repo, in ~/.config/pixelart (PIXELART_CONFIG):
youtube_client_secret.json is the Google Cloud project's OAuth client (type
Desktop), and youtube_token.json is written after the first browser consent.
Until the Cloud project passes YouTube's API audit, YouTube keeps every video
it uploads private; make it public by hand in YouTube Studio. Custom
thumbnails need a phone-verified channel (youtube.com/verify). Needs the
youtube extra (uv sync --extra youtube).
"""
import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

CONFIG = Path(os.environ.get("PIXELART_CONFIG", Path.home() / ".config" / "pixelart"))
SCOPES = ["https://www.googleapis.com/auth/youtube"]   # upload, thumbnails, and privacy changes
MUSIC = "10"
PRIVACY = ("private", "unlisted", "public")
WRITABLE_STATUS = ("privacyStatus", "publishAt", "license", "embeddable", "publicStatsViewable",
                   "selfDeclaredMadeForKids", "containsSyntheticMedia")
THUMB_MAX = 2 * 1024 * 1024
REVOKE = "https://oauth2.googleapis.com/revoke"
TERMS = ("This tool uses YouTube API Services. By using it you agree to the YouTube Terms of Service "
         "(https://www.youtube.com/t/terms). See the Google Privacy Policy (https://policies.google.com/privacy) "
         "and this tool's privacy policy (https://github.com/gdoteof/pixelart/blob/main/PRIVACY.md).")

SECTIONS = ("TITLE", "TITLE ALTERNATES", "THUMBNAILS", "ALTERED CONTENT", "DESCRIPTION", "TAGS", "PINNED COMMENT")
HEADER = re.compile(rf"^({'|'.join(SECTIONS)})(?: \(.*\))?$")
RULE = re.compile(r"^-{20,}$", re.M)


@dataclass(frozen=True)
class Kit:
    title: str
    description: str
    tags: tuple
    thumbnail: str | None   # file name in thumbs/
    altered: bool


def parse_kit(text):
    """The kit's sections are headed by known capitalised names; the description sits between dashed rules."""
    parts = RULE.split(text)
    if len(parts) != 3:
        raise ValueError("the description must sit between two lines of dashes")
    before, description, after = parts
    sections, name = {}, None
    for line in (before + after).splitlines():
        line = line.strip()
        if m := HEADER.match(line):
            name = m.group(1)
            sections[name] = []
        elif name and line:
            sections[name].append(line)
    if not sections.get("TITLE"):
        raise ValueError("no TITLE section")
    thumbs = sections.get("THUMBNAILS", [])
    main = next((line for line in thumbs if "<- upload this" in line), thumbs[0] if thumbs else None)
    tags = ",".join(sections.get("TAGS", [])).split(",")
    return Kit(title=sections["TITLE"][0], description=description.strip(),
               tags=tuple(t.strip() for t in tags if t.strip()),
               thumbnail=main.split()[0] if main else None, altered="ALTERED CONTENT" in sections)


def tags_length(tags):
    """YouTube's count: the commas between tags and the quotes around tags with spaces count too."""
    return sum(len(t) + 2 * (" " in t) for t in tags) + max(len(tags) - 1, 0)


def problems(kit):
    out = []
    if not 0 < len(kit.title) <= 100:
        out.append(f"title is {len(kit.title)} characters (YouTube allows 1-100)")
    if (n := len(kit.description.encode())) > 5000:
        out.append(f"description is {n} bytes (YouTube allows 5000)")
    for field, text in (("title", kit.title), ("description", kit.description)):
        if "<" in text or ">" in text:
            out.append(f"{field} contains < or >, which YouTube rejects")
    if (n := tags_length(kit.tags)) > 500:
        out.append(f"tags come to {n} characters (YouTube allows 500)")
    return out


def client():
    try:
        from google.auth.exceptions import RefreshError
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        raise SystemExit("needs the youtube extra: uv sync --extra youtube")
    token = CONFIG / "youtube_token.json"
    creds = Credentials.from_authorized_user_file(str(token), SCOPES) if token.exists() else None
    if creds and not creds.valid and creds.refresh_token:
        try:
            creds.refresh(Request())
        except RefreshError:   # revoked, or the 7-day limit on a Testing-mode consent screen
            creds = None
    if not creds or not creds.valid:
        secret = CONFIG / "youtube_client_secret.json"
        if not secret.exists():
            raise SystemExit(f"no OAuth client at {secret}: save the Cloud project's Desktop client JSON there")
        print(TERMS)
        print("sign in with the Google account that owns the channel, in the browser window that opens")
        creds = InstalledAppFlow.from_client_secrets_file(str(secret), SCOPES).run_local_server(port=0)
    token.touch(mode=0o600)
    token.write_text(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def sign_out():
    """Revoke the grant at Google, then delete the local token."""
    import urllib.error
    import urllib.parse
    import urllib.request
    token = CONFIG / "youtube_token.json"
    if not token.exists():
        raise SystemExit(f"not signed in (no {token})")
    saved = json.loads(token.read_text())
    data = urllib.parse.urlencode({"token": saved.get("refresh_token") or saved["token"]}).encode()
    try:
        urllib.request.urlopen(REVOKE, data=data, timeout=30)
        print("revoked this tool's access to your Google account")
    except urllib.error.HTTPError as e:   # 400 when the grant is already gone
        print(f"Google answered {e.code}; the access may already be revoked "
              "(check https://myaccount.google.com/connections)")
    token.unlink()
    print(f"deleted {token}")


def confirm(question):
    if not sys.stdin.isatty():
        raise SystemExit(f"{question} Answer in a terminal, or pass --yes")
    return input(f"{question} [y/N] ").strip().lower() in ("y", "yes")


def channel(yt):
    items = yt.channels().list(part="snippet", mine=True).execute().get("items", [])
    if not items:
        raise SystemExit("the signed-in Google account has no YouTube channel; delete youtube_token.json and sign in again")
    return items[0]["snippet"]["title"]


def upload(yt, video, kit, privacy):
    from googleapiclient.http import MediaFileUpload
    status = {"privacyStatus": privacy, "selfDeclaredMadeForKids": False}
    if kit.altered:
        status["containsSyntheticMedia"] = True
    body = {"snippet": {"title": kit.title, "description": kit.description, "tags": list(kit.tags),
                        "categoryId": MUSIC},
            "status": status}
    media = MediaFileUpload(str(video), mimetype="video/mp4", chunksize=16 * 1024 * 1024, resumable=True)
    request = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        progress, response = request.next_chunk()
        if progress:
            print(f"  {progress.progress():.0%}", flush=True)
    return response


def set_thumbnail(yt, video_id, thumb):
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload
    try:
        yt.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(str(thumb), mimetype="image/png")).execute()
        print(f"thumbnail: {thumb.name}")
    except HttpError as e:
        print(f"thumbnail not set ({e.status_code}: {e.reason})")
        if e.status_code == 403:
            print("custom thumbnails need a phone-verified channel: verify at https://www.youtube.com/verify, "
                  "then run again with --set-thumbnail")


def set_privacy(yt, video_id, privacy):
    """videos.update replaces the whole status part, so the settings it already has are sent back with it."""
    items = yt.videos().list(part="status", id=video_id).execute()["items"]
    if not items:
        raise SystemExit(f"video {video_id} not found on the channel")
    status = {k: v for k, v in items[0]["status"].items() if k in WRITABLE_STATUS}
    status["privacyStatus"] = privacy
    return yt.videos().update(part="status", body={"id": video_id, "status": status}).execute()


def report_privacy(asked, got):
    print(f"privacy: {got}")
    if got != asked:
        print("YouTube kept it private (the Cloud project hasn't passed the API audit): change it in YouTube Studio")


def main():
    ap = argparse.ArgumentParser(description="Upload a project's video to YouTube.", epilog=TERMS)
    ap.add_argument("project", nargs="?")
    ap.add_argument("--privacy", choices=PRIVACY, default="private", help="privacy for the upload")
    ap.add_argument("--set-privacy", choices=PRIVACY, help="change the uploaded video's privacy instead of uploading")
    ap.add_argument("--set-thumbnail", action="store_true", help="set the uploaded video's thumbnail instead of uploading")
    ap.add_argument("--video", type=Path, help="default: the project's OUTPUT")
    ap.add_argument("--thumb", help="thumbnail file in thumbs/ (default: the kit's main one)")
    ap.add_argument("--again", action="store_true", help="upload even though build/youtube.json records an upload")
    ap.add_argument("--dry-run", action="store_true", help="check the kit and files, upload nothing")
    ap.add_argument("--yes", action="store_true", help="upload without asking (the user has already said yes)")
    ap.add_argument("--sign-out", action="store_true",
                    help="revoke this tool's access to your Google account and delete the saved token")
    args = ap.parse_args()
    if args.sign_out:
        sign_out()
        return
    if not args.project:
        ap.error("PROJECT is required")

    root = Path(args.project).resolve()
    record_path = root / "build" / "youtube.json"
    record = json.loads(record_path.read_text()) if record_path.exists() else None

    if args.set_privacy:
        if not record:
            raise SystemExit(f"no upload recorded in {record_path}")
        video = set_privacy(client(), record["id"], args.set_privacy)
        report_privacy(args.set_privacy, video["status"]["privacyStatus"])
        return

    kit = parse_kit((root / "thumbs" / "youtube_upload.txt").read_text())
    if args.video:
        video = args.video
    else:
        from pixelart.project import load
        video = load(root).output
    thumb = root / "thumbs" / (args.thumb or kit.thumbnail) if (args.thumb or kit.thumbnail) else None

    if args.set_thumbnail:
        if not record:
            raise SystemExit(f"no upload recorded in {record_path}")
        if not thumb or not thumb.is_file():
            raise SystemExit(f"no thumbnail at {thumb}" if thumb else "the kit names no thumbnail; pass --thumb")
        set_thumbnail(client(), record["id"], thumb)
        return

    bad = problems(kit)
    if not video.is_file():
        bad.append(f"no video at {video} (render it first)")
    if thumb and not thumb.is_file():
        bad.append(f"no thumbnail at {thumb}")
    elif thumb and thumb.stat().st_size > THUMB_MAX:
        bad.append(f"{thumb.name} is over YouTube's 2 MB thumbnail limit")
    if record and not args.again:
        bad.append(f"already uploaded as {record['url']}; pass --again to upload another copy")

    print(f"title:       {kit.title}")
    print(f"description: {len(kit.description.encode())} bytes, {kit.description.count(chr(10)) + 1} lines")
    print(f"tags:        {len(kit.tags)} tags, {tags_length(kit.tags)} characters")
    print(f"thumbnail:   {thumb.name if thumb else '(none)'}")
    print(f"altered:     {'yes' if kit.altered else 'not declared'}")
    print(f"video:       {video}" + (f" ({video.stat().st_size / 1e6:.0f} MB)" if video.is_file() else ""))
    print(f"privacy:     {args.privacy}")
    for p in bad:
        print(f"PROBLEM: {p}")
    if bad:
        raise SystemExit(1)
    if args.dry_run:
        return

    yt = client()
    name = channel(yt)
    print(f"channel:     {name}")
    if not args.yes and not confirm(f"Upload {video.name} to {name} as {args.privacy}?"):
        raise SystemExit("nothing uploaded")
    response = upload(yt, video, kit, args.privacy)
    record = {"id": response["id"], "url": f"https://youtu.be/{response['id']}", "title": kit.title,
              "uploaded": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    record_path.parent.mkdir(exist_ok=True)
    record_path.write_text(json.dumps(record, indent=2) + "\n")
    print(f"uploaded:    {record['url']}")
    if thumb:
        set_thumbnail(yt, response["id"], thumb)
    report_privacy(args.privacy, response["status"]["privacyStatus"])


if __name__ == "__main__":
    main()
