#!/bin/bash
# Install (or remove) the daily job search as a macOS LaunchAgent.
#
#   tools/schedule/install_daily_search.sh                      # candidates/animesh_murai at 02:00
#   tools/schedule/install_daily_search.sh candidates/<name> 7 30   # another candidate / time
#   tools/schedule/install_daily_search.sh --uninstall
#
# launchd runs it at the given local time. If the Mac is asleep then, it runs
# when the Mac next wakes; if the Mac is shut down, that day's run is skipped.
# Output goes to logs/discovery/daily_search.log, the digest to
# state/daily_jobs/latest.md.
set -euo pipefail

LABEL="com.job-apply.daily-search"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
REPO="$(cd "$(dirname "$0")/../.." && pwd)"

if [[ "${1:-}" == "--uninstall" ]]; then
  launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
  rm -f "$PLIST"
  echo "Removed the daily job search ($LABEL)."
  exit 0
fi

CANDIDATE="${1:-candidates/animesh_murai}"
HOUR="${2:-2}"
MINUTE="${3:-0}"
PYTHON="$REPO/.venv/bin/python"

[[ -x "$PYTHON" ]] || { echo "Missing $PYTHON. Create it first (see requirements.txt)." >&2; exit 1; }
[[ -f "$REPO/$CANDIDATE/job_search.json" ]] || { echo "Missing $REPO/$CANDIDATE/job_search.json" >&2; exit 1; }
mkdir -p "$REPO/logs/discovery" "$HOME/Library/LaunchAgents"

cat > "$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>$PYTHON</string>
    <string>$REPO/tools/daily_search.py</string>
    <string>--candidate</string>
    <string>$CANDIDATE</string>
  </array>
  <key>WorkingDirectory</key><string>$REPO</string>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key><integer>$HOUR</integer>
    <key>Minute</key><integer>$MINUTE</integer>
  </dict>
  <key>StandardOutPath</key><string>$REPO/logs/discovery/daily_search.log</string>
  <key>StandardErrorPath</key><string>$REPO/logs/discovery/daily_search.log</string>
</dict>
</plist>
PLIST

launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
printf 'Daily job search installed: %s at %02d:%02d every day.\n' "$CANDIDATE" "$HOUR" "$MINUTE"
echo "Run it now with:  launchctl kickstart gui/$(id -u)/$LABEL"
