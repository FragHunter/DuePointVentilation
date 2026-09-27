#!/usr/bin/env bash
set -euo pipefail

EXPECTED_WLED_SHA=961961fdde8c22150a0212243621ee71bc9a7639
ROOT=$(cd "$(dirname "$0")" && pwd)
WLED_DIR=${1:?usage: validate_against_wled.sh WLED_DIR PIO_BIN}
PIO_BIN=${2:?usage: validate_against_wled.sh WLED_DIR PIO_BIN}

actual=$(git -C "$WLED_DIR" rev-parse HEAD)
if [[ "$actual" != "$EXPECTED_WLED_SHA" ]]; then
  echo "WLED commit mismatch: expected $EXPECTED_WLED_SHA got $actual" >&2
  exit 2
fi

git -C "$WLED_DIR" diff --quiet || { echo "WLED checkout must start clean" >&2; exit 3; }
git -C "$WLED_DIR" apply "$ROOT/patches/wled-main-961961f-duepoint-pinowner.patch"

rm -rf "$WLED_DIR/usermods/DuePointActuator"
ln -s "$ROOT" "$WLED_DIR/usermods/DuePointActuator"

cat > "$WLED_DIR/platformio_override.ini" <<'PIO'
[platformio]
default_envs = duepoint_esp32

[env:duepoint_esp32]
extends = env:esp32dev
custom_usermods = ${env:esp32dev.custom_usermods} DuePointActuator
PIO

"$PIO_BIN" run -d "$WLED_DIR" -e duepoint_esp32
test -f "$WLED_DIR/.pio/build/duepoint_esp32/firmware.bin"
