# Privacy policy: the pixelart YouTube uploader

Last updated: 2 October 2026

The YouTube uploader in this repository (`pixelart.youtube`, in [`pixelart/youtube.py`](pixelart/youtube.py)) publishes videos made with pixelart to YouTube. Its operator, Geoff Golder, runs it to upload to their own channel, [Pixel Art Rap Battles](https://www.youtube.com/@pixelartrapbattles). It is not a service offered to anyone else. The Google Cloud project it signs in with (its API client) admits only the operator's Google account. The source code is public. Anyone who runs a copy does so with their own Google Cloud project, and this policy then describes what the code does on their own computer.

## YouTube API Services

The uploader uses YouTube API Services. By using it you agree to the [YouTube Terms of Service](https://www.youtube.com/t/terms). What Google does with your data is covered by the [Google Privacy Policy](http://www.google.com/policies/privacy).

## What it accesses

When you sign in, Google asks you to grant the uploader the `youtube` scope ("Manage your YouTube account"). The uploader uses that permission only to:

- read your channel's name, to show which channel a video is about to go to;
- upload a video you choose, after you confirm, with the title, description and tags from that project's upload kit (`thumbs/youtube_upload.txt`);
- set that video's thumbnail;
- read and change that video's privacy setting, when you ask it to (`--set-privacy`).

It does not read your other videos, comments, subscribers, analytics or any other account data. It acts only when you run a command.

## What it stores, and where

Everything stays on the computer that runs the uploader:

- the access token Google issues, in `~/.config/pixelart/youtube_token.json`, which only your user account can read. It is used only for the actions above.
- for each video it uploads, the video's YouTube ID and the title the uploader gave it, in that project's `build/youtube.json`, so later commands act on the same video.

Nothing else from YouTube is stored. The uploader has no server: it sends data only to Google's YouTube API. It uses no advertising, analytics, cookies or tracking. Nothing is sold or shared.

The operator sometimes runs the uploader through an AI coding assistant, Claude Code, on the same computer. The assistant runs the same commands, at the operator's request, and the command output (the channel's name, a video's ID and title) becomes part of that conversation with Anthropic. Uploads still need the operator's go-ahead.

## Revoking access and deleting data

- `python -m pixelart.youtube --sign-out` revokes the uploader's access at Google and deletes the saved token.
- You can also revoke access at any time in your Google Account's security settings: <https://security.google.com/settings/security/permissions>.
- Deleting `build/youtube.json` removes the stored video ID and title. Uploaded videos stay on YouTube until you delete them in YouTube Studio.

Because this data lives only on your computer, deleting those files deletes it. To ask the operator to delete any data about you, email the address below. It will be deleted within 7 days.

## Contact

Questions, complaints and deletion requests: Geoff Golder, <geoffgolder@gmail.com>, or an issue at <https://github.com/gdoteof/pixelart/issues>.

## Changes

Changes to this policy are made in this file, and the repository's history keeps every version.
