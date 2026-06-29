#!/bin/bash

SKILL_NAME="db34-data-masking-assistant"
SKILL_DIR="$(dirname "$(dirname "$(realpath "$0")")")"

# Function to install the skill to a specific platform
install_to_platform() {
    PLATFORM_DIR="$1"
    echo "Installing $SKILL_NAME to $PLATFORM_DIR..."
    mkdir -p "$PLATFORM_DIR"
    ln -sf "$SKILL_DIR" "$PLATFORM_DIR/$SKILL_NAME"
    echo "$SKILL_NAME installed to $PLATFORM_DIR/$SKILL_NAME"
}

# Detect common agent skill directories and install
if [ -d "$HOME/.claude/skills" ]; then
    install_to_platform "$HOME/.claude/skills"
fi

if [ -d "$HOME/.agents/skills" ]; then
    install_to_platform "$HOME/.agents/skills"
fi

# Add more platform detections as needed

echo "Installation complete. You can now use /$SKILL_NAME in your agent."
