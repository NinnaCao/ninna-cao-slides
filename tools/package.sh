#!/bin/sh
# Build dist/Visual_Slides_v<version>.zip containing the single visual-slides/ folder,
# ready for Claude (Customize > Skills > Upload) or ~/.claude/skills/.
set -e
cd "$(dirname "$0")/.."
version=$(cat visual-slides/VERSION)
mkdir -p dist
out="dist/Visual_Slides_v${version}.zip"
rm -f "$out"
zip -qr "$out" visual-slides -x '*.DS_Store' -x '*__pycache__*' -x '*.pyc'
unzip -tq "$out"
echo "$out"
