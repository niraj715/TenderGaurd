#!/usr/bin/env bash
# Open ProcureShield AI in Antigravity IDE
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
if [ -f "/Applications/Antigravity IDE.app/Contents/Resources/app/bin/antigravity-ide" ]; then
    "/Applications/Antigravity IDE.app/Contents/Resources/app/bin/antigravity-ide" "$DIR"
    echo "✓ Opened ProcureShield AI in Antigravity IDE!"
else
    open -a "Antigravity IDE" "$DIR" 2>/dev/null || open -a "Antigravity" "$DIR" 2>/dev/null || echo "Please open Antigravity IDE and choose File -> Open Folder -> $DIR"
fi
