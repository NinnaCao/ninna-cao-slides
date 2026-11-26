#!/bin/sh
# Build dist/Ninna_Cao_Slides_v<version>.zip containing the single ninna-cao-slides/ folder,
# ready for Claude (Customize > Skills > Upload) or ~/.claude/skills/.
set -e
cd "$(dirname "$0")/.."
version=$(cat ninna-cao-slides/VERSION)
mkdir -p dist
out="dist/Ninna_Cao_Slides_v${version}.zip"
rm -f "$out"
zip -qr "$out" ninna-cao-slides -x '*.DS_Store' -x '*__pycache__*' -x '*.pyc'
unzip -tq "$out"
echo "$out"
