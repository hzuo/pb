run *args:
  cd cli && pnpm run tsx {{args}}

alias r := run

marimo:
  cd platform && uv run marimo edit --watch

alias mo := marimo

bot:
  #!/usr/bin/env bash
  uv run --env-file=.env personalbot.py -m openai

bot2:
  #!/usr/bin/env bash
  uv run --env-file=.env personalbot.py -m sonnet

bot3:
  #!/usr/bin/env bash
  uv run --env-file=.env personalbot.py -m haiku

alias b := bot
alias b1 := bot
alias b2 := bot2
alias b3 := bot3
alias agent := bot

tutorial:
  just run nbc "platform/notebooks/ai-tutorial.py"

chrome:
  uv run "scripts/25-07-22-01-playwright-cdp-chrome-launch.py"

platform-upgrade-deps:
  #!/usr/bin/env bash
  set -euxo pipefail

  cd platform

  rm uv.lock
  uv lock
  uv sync

ssh:
  ssh alice@100.81.230.115

s3-ls:
  aws s3 ls --summarize --human-readable --recursive s3://personal-dataland

s3-push-agent-sessions:
  aws s3 sync ~/.dataland/sessions s3://personal-dataland/agent-sessions-25-11-07 --exclude "*" --include "personalbot01-*"

s3-pull-agent-sessions:
  aws s3 sync s3://personal-dataland/agent-sessions-25-11-07 ~/.dataland/sessions --exclude "*" --include "personalbot01-*"

sync-sessions:
  #!/usr/bin/env bash
  set -euxo pipefail

  ssh alice@100.81.230.115 "bash -c 'eval \"\$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)\" && cd ~/git/pb && just s3-push-agent-sessions'"
  just s3-pull-agent-sessions
  just s3-push-agent-sessions

cas-upload *args:
  uv run "scripts/25-07-26-01-cas-upload.py" {{args}}

hzuo-local-tunnel:
  cloudflared tunnel run --url http://localhost:8787 hzuo-local-tunnel

learn:
  uv run --env-file=.env "scripts/25-10-20-mon-01-bulk-learn.py"

track:
  uv run --env-file=.env "scripts/25-10-22-wed-tracker-update.py"

alias l := learn
alias t := track

smoke-test:
  uv run --env-file=.env "scripts/25-11-03-mon-bot-smoke-test.py"

alias st := smoke-test

front-events-download:
  uv run --env-file=.env "scripts/25-10-22-wed-front-events-download.py"

front-events-pull:
  #!/usr/bin/env bash
  set -euxo pipefail

  SOURCE_DIR="./_scratch/front-events-zst"
  TARGET_DIR="./_scratch/front-events"

  mkdir -p "$SOURCE_DIR"
  mkdir -p "$TARGET_DIR"

  aws s3 sync s3://personal-dataland/front-events "$SOURCE_DIR" \
    --exclude "*" \
    --include "front-events-*.jsonl.zst"

  for file in "$SOURCE_DIR"/*.jsonl.zst; do
      if [ -f "$file" ]; then
          filename=$(basename "$file" .zst)
          output="$TARGET_DIR/${filename}"
          if [ ! -f "$output" ] || [ "$file" -nt "$output" ]; then
              zstd -d "$file" -o "$output" --force
          fi
      fi
  done
