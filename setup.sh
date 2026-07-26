#!/bin/bash
# setup.sh — Bootstrap a fresh Raspberry Pi (Debian/Bookworm+) for the badge project.
# Run as your normal user (it will sudo when needed).
# Usage: curl the repo, or clone it first, then: ./setup.sh

set -euo pipefail

REPO_URL="https://github.com/framebuffers/badge.git"
BADGE_DIR="$HOME/badge"
PYTHON_MIN="3.13"

info() { printf '\033[1;34m[*]\033[0m %s\n' "$*"; }
ok() { printf '\033[1;32m[+]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[!]\033[0m %s\n' "$*"; }
fail() {
  printf '\033[1;31m[-]\033[0m %s\n' "$*"
  exit 1
}

info "Updating package lists..."
sudo apt-get update -qq

# prerrequisites
info "Installing system dependencies..."
sudo apt-get install -y -qq \
  git \
  python3 \
  python3-venv \
  python3-dev \
  python3-pip \
  libopenjp2-7 \
  libtiff6 \
  libfreetype6-dev \
  wireless-tools \
  libraspberrypi-bin \
  >/dev/null

ok "System packages installed."

# spi
info "Ensuring SPI is enabled..."
if ! grep -q "^dtparam=spi=on" /boot/firmware/config.txt 2>/dev/null &&
  ! grep -q "^dtparam=spi=on" /boot/config.txt 2>/dev/null; then
  CONFIG_FILE="/boot/firmware/config.txt"
  [ -f "$CONFIG_FILE" ] || CONFIG_FILE="/boot/config.txt"
  echo "dtparam=spi=on" | sudo tee -a "$CONFIG_FILE" >/dev/null
  warn "SPI was not enabled — added to $CONFIG_FILE. A reboot is needed."
  SPI_CHANGED=1
else
  ok "SPI already enabled."
  SPI_CHANGED=0
fi

# get/update repo
if [ -d "$BADGE_DIR/.git" ]; then
  info "Badge repo already exists at $BADGE_DIR, pulling latest..."
  git -C "$BADGE_DIR" pull --ff-only
else
  info "Cloning badge repo into $BADGE_DIR..."
  git clone "$REPO_URL" "$BADGE_DIR"
fi
ok "Repo ready at $BADGE_DIR."

# uv
if ! command -v uv &>/dev/null; then
  info "Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi
ok "uv $(uv --version) ready."

# get venv+dependencies
cd "$BADGE_DIR"

info "Syncing Python dependencies with uv..."
uv sync
ok "Python dependencies installed."

# 6. chmod +x scripts
chmod +x badge.sh test.sh demo.sh 2>/dev/null || true
ok "Shell scripts marked executable."

# summary
echo ""
ok "Setup complete!"
echo ""
echo "    cd $BADGE_DIR"
echo "    ./badge.sh text 'Hello world'   # quick text test"
echo "    ./demo.sh                        # run badge demo"
echo "    ./test.sh                        # pull latest + run main.py"
echo ""

if [ "$SPI_CHANGED" -eq 1 ]; then
  warn "SPI was just enabled. Please reboot before using the display:"
  echo "    sudo reboot"
fi
