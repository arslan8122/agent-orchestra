# ADR-0014: PR videos are hosted outside the repo: gh --attach first, bucket fallback

- Status: Accepted
- Date: 2026-11-19
- Deciders: Arslan Asghar

## Context
Videos committed to the repo (even on an orphan branch) bloat every clone. GitHub's own attachment storage keeps them out of git and inherits repo visibility, and GitHub CLI 2.99 (Sept 2026) can upload to it with `--attach`.

## Decision
`scripts/upload-proof.sh` posts the video as a PR comment with `gh pr comment --attach`, then links it in the Demo section. If that's unavailable, it uploads to the configured S3-compatible bucket (Cloudflare R2's free tier is the suggested default) with a GIF preview. If both fail, the PR stays draft and a human attaches the video.

## Consequences
- + Free, nothing in git, inline video player on GitHub.
- − Requires gh >= 2.99 for the default path.
- − Bucket links are unguessable, not access-controlled.

## Alternatives considered
- Orphan `pr-media` branch: still inside the repo.
- YouTube unlisted: OAuth, quota, public-by-link.
- S3 presigned URLs: expire within 7 days.
