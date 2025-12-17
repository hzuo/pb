run *args:
  cd cli && pnpm run tsx {{args}}

alias r := run

marimo:
  cd platform && uv run marimo edit --watch

alias mo := marimo

bot:
  #!/usr/bin/env bash
  uv run --env-file=.env personalbot.py -m gpt52

bot-gpt51:
  #!/usr/bin/env bash
  uv run --env-file=.env personalbot.py -m gpt51

bot-gpt52:
  #!/usr/bin/env bash
  uv run --env-file=.env personalbot.py -m gpt52

bot-sonnet:
  #!/usr/bin/env bash
  uv run --env-file=.env personalbot.py -m sonnet

bot-haiku:
  #!/usr/bin/env bash
  uv run --env-file=.env personalbot.py -m haiku

bot-opus:
  #!/usr/bin/env bash
  uv run --env-file=.env personalbot.py -m opus

bot-gemini:
  #!/usr/bin/env bash
  uv run --env-file=.env personalbot.py -m gemini

bot-gemini-pro:
  #!/usr/bin/env bash
  uv run --env-file=.env personalbot.py -m gemini-3-pro-preview

bot-gemini-flash:
  #!/usr/bin/env bash
  uv run --env-file=.env personalbot.py -m gemini-3-flash-preview

alias b := bot
alias b51 := bot-gpt51
alias b52 := bot-gpt52
alias bs := bot-sonnet
alias bh := bot-haiku
alias bo := bot-opus
alias bg := bot-gemini
alias bgp := bot-gemini-pro
alias bgf := bot-gemini-flash

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

healthfit-download:
  uv run --env-file=.env "scripts/25-11-16-sun-healthfit-download.py"

mf1:
  uv run --env-file=.env "scripts/25-12-02-tue-stonybrook-notes-01-download.py"

mf11:
  uv run --env-file=.env "scripts/25-12-10-wed-stonybrook-radiology-01-download.py"

mf2:
  uv run --env-file=.env "scripts/25-12-02-tue-stonybrook-notes-02-convert.py"

mf3:
  uv run --env-file=.env "scripts/25-12-02-tue-stonybrook-notes-03-upload.py"
