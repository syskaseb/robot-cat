#!/usr/bin/env bash
# Gazebo GUI. Terminal 2.
#
# Separate from the server because macOS/Cocoa requires window creation on the
# main thread - `gz sim` cannot run both in one process here.
set -euo pipefail
cd "$(dirname "$0")/.."
exec pixi run gz sim -g
