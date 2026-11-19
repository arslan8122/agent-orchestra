#!/usr/bin/env bash
# Attach the QA video to a PR without storing it in the repo.   ADR-0008 / ADR-0014
#
#   scripts/upload-proof.sh <pr-number> <video-file> [--ready]
#
# 1. Re-encode to mp4 (<= 10 MB, GitHub's free-plan video limit).
# 2. Host it, in order of preference:
#      a. GitHub attachment in the PR body: the Demo placeholder becomes
#         `![Demo](./demo.mp4)` and `gh pr edit --attach` uploads the file and rewrites the
#         reference, so the video plays inline in the description. Stored on GitHub's
#         attachment CDN, never in git; inherits repo visibility. Free. (gh >= 2.99)
#      a2. Same upload as a PR comment (`gh pr comment --attach`) if editing the body fails.
#      b. proof.fallback (S3-compatible bucket, e.g. Cloudflare R2 free tier) + GIF preview.
# 3. Replace the <!-- orchestra:demo pending --> placeholder in the PR body with the link.
# 4. With --ready, take the PR out of draft.
# Exit 3 when no host worked: the PR stays draft and the manager asks a human to attach.
set -euo pipefail

pr="${1:?usage: upload-proof.sh <pr> <video> [--ready]}"
src="${2:?usage: upload-proof.sh <pr> <video> [--ready]}"
ready="${3:-}"
root="$PWD"; while [ ! -f "$root/.orchestra.json" ] && [ "$root" != "/" ]; do root="$(dirname "$root")"; done
work="$(mktemp -d)"; trap 'rm -rf "$work"' EXIT
mp4="$work/demo.mp4"

for crf in 28 32 36; do
  ffmpeg -loglevel error -y -i "$src" -an -vf "scale=-2:'min(720,ih)'" -c:v libx264 -preset veryfast \
         -crf "$crf" -pix_fmt yuv420p -movflags +faststart "$mp4"
  [ "$(wc -c < "$mp4")" -le 10000000 ] && break
done
[ "$(wc -c < "$mp4")" -le 10000000 ] || echo "warning: video still over 10 MB" >&2

url=""
body="$work/body.md"
if gh pr edit --help 2>/dev/null | grep -q -- '--attach'; then
  gh pr view "$pr" --json body -q .body > "$body"
  python3 - "$body" <<'PY2'
import sys
p = sys.argv[1]; s = open(p).read(); ref = "![Demo](./demo.mp4)"
s = s.replace("<!-- orchestra:demo pending -->", ref, 1) if "<!-- orchestra:demo pending -->" in s else s + f"\n\n## Demo\n{ref}\n"
open(p, "w").write(s)
PY2
  if gh pr edit "$pr" --body-file "$body" --attach "$mp4" >/dev/null 2>&1; then
    [ "$ready" = "--ready" ] && gh pr ready "$pr" >/dev/null
    echo "attached inline in PR #$pr description"; exit 0
  fi
fi
if gh pr comment --help 2>/dev/null | grep -q -- '--attach'; then
  out=$(gh pr comment "$pr" --body "Demo video (recorded by QA)" --attach "$mp4" 2>&1) && \
    url=$(printf '%s\n' "$out" | grep -oE 'https://github\.com/[^ ]+' | tail -1)
fi

if [ -z "$url" ] && [ -f "$root/.orchestra.json" ]; then
  read -r ftype bucket endpoint public < <(python3 - "$root/.orchestra.json" <<'PY'
import json, sys
f = (json.load(open(sys.argv[1])).get("proof") or {}).get("fallback") or {}
print(f.get("type", "none"), f.get("bucket", "-"), f.get("endpoint", "-"), f.get("public_base_url", "-"))
PY
)
  if [ "$ftype" = "s3" ] && command -v aws >/dev/null; then
    key="pr-proof/$(gh pr view "$pr" --json headRefName -q .headRefName | tr '/' '_')/$(date -u +%Y%m%dT%H%M%SZ)"
    gif="$work/preview.gif"
    ffmpeg -loglevel error -y -t 10 -i "$mp4" -vf "fps=8,scale=640:-2:flags=lanczos" "$gif" || true
    ep=(); [ "$endpoint" != "-" ] && ep=(--endpoint-url "$endpoint")
    aws s3 cp "${ep[@]}" "$mp4" "s3://$bucket/$key/demo.mp4" --content-type video/mp4 >/dev/null
    [ -f "$gif" ] && aws s3 cp "${ep[@]}" "$gif" "s3://$bucket/$key/preview.gif" --content-type image/gif >/dev/null
    url="$public/$key/demo.mp4"
    [ -f "$gif" ] && url="[![demo]($public/$key/preview.gif)]($url)"$'\n\n'"▶ [Full video]($public/$key/demo.mp4)"
  fi
fi

if [ -z "$url" ]; then
  echo "no proof host worked (gh --attach unavailable and no proof.fallback). PR #$pr stays draft." >&2
  exit 3
fi

gh pr view "$pr" --json body -q .body > "$body"
python3 - "$body" "$url" <<'PY'
import sys
p, url = sys.argv[1], sys.argv[2]
s = open(p).read()
link = url if url.startswith("[") else f"▶ [Demo video]({url})"
s = s.replace("<!-- orchestra:demo pending -->", link, 1) if "<!-- orchestra:demo pending -->" in s else s + f"\n\n## Demo\n{link}\n"
open(p, "w").write(s)
PY
gh pr edit "$pr" --body-file "$body" >/dev/null
[ "$ready" = "--ready" ] && gh pr ready "$pr" >/dev/null
echo "$url"
