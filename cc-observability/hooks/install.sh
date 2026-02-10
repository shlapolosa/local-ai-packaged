#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# install.sh -- Installs cc-observability hooks into a target project
#
# Usage:
#   ./install.sh [target-project-dir]
#
# If no target directory is specified, installs into the current directory.
# ─────────────────────────────────────────────────────────────────────────────

set -e

TARGET_DIR="${1:-.}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HOOKS_DIR="$TARGET_DIR/.claude/hooks"

echo "==========================================="
echo "  CC Observability -- Hook Installer"
echo "==========================================="
echo ""
echo "Source:  $SCRIPT_DIR"
echo "Target:  $TARGET_DIR"
echo ""

# ── Validate target ──────────────────────────────────────────────────────────

if [ ! -d "$TARGET_DIR" ]; then
  echo "Error: Target directory '$TARGET_DIR' does not exist."
  exit 1
fi

# ── Create hooks directory ───────────────────────────────────────────────────

echo "Creating hooks directory: $HOOKS_DIR"
mkdir -p "$HOOKS_DIR"

# ── Copy hook files ──────────────────────────────────────────────────────────

HOOK_FILES=(
  lib.ts
  send-event.ts
  pre-tool-use.ts
  post-tool-use.ts
  post-tool-use-failure.ts
  stop.ts
  session-start.ts
  session-end.ts
  user-prompt-submit.ts
  subagent-start.ts
  subagent-stop.ts
  pre-compact.ts
  notification.ts
  permission-request.ts
  story-tracker.ts
)

echo "Copying hook scripts..."
for file in "${HOOK_FILES[@]}"; do
  if [ -f "$SCRIPT_DIR/$file" ]; then
    cp "$SCRIPT_DIR/$file" "$HOOKS_DIR/$file"
    echo "  + $file"
  else
    echo "  ! WARNING: $file not found in source directory"
  fi
done

# ── Merge or create settings.json ────────────────────────────────────────────

SETTINGS_FILE="$TARGET_DIR/.claude/settings.json"
TEMPLATE_FILE="$SCRIPT_DIR/settings.json.template"

if [ ! -f "$TEMPLATE_FILE" ]; then
  echo ""
  echo "WARNING: settings.json.template not found. Skipping settings merge."
  echo "You will need to manually configure hooks in .claude/settings.json"
else
  if [ -f "$SETTINGS_FILE" ]; then
    echo ""
    echo "Merging hook configuration into existing $SETTINGS_FILE..."
    # Use node to merge JSON (guaranteed available since Claude Code requires Node.js)
    node -e "
      const fs = require('fs');
      const existingPath = '$SETTINGS_FILE';
      const templatePath = '$TEMPLATE_FILE';

      let existing;
      try {
        existing = JSON.parse(fs.readFileSync(existingPath, 'utf8'));
      } catch (e) {
        console.error('  ! Could not parse existing settings.json:', e.message);
        console.error('  ! Creating backup and overwriting...');
        fs.copyFileSync(existingPath, existingPath + '.backup');
        existing = {};
      }

      const template = JSON.parse(fs.readFileSync(templatePath, 'utf8'));

      // Merge hooks: for each event type, append new hooks if they don't already exist
      if (!existing.hooks) {
        existing.hooks = {};
      }

      for (const [eventType, templateEntries] of Object.entries(template.hooks)) {
        if (!existing.hooks[eventType]) {
          existing.hooks[eventType] = templateEntries;
        } else {
          // Check if cc-observability hooks are already present
          const existingCommands = new Set();
          for (const entry of existing.hooks[eventType]) {
            if (entry.hooks) {
              for (const h of entry.hooks) {
                if (h.command) existingCommands.add(h.command);
              }
            }
          }

          for (const templateEntry of templateEntries) {
            if (templateEntry.hooks) {
              const newHooks = templateEntry.hooks.filter(
                h => !existingCommands.has(h.command)
              );
              if (newHooks.length > 0) {
                // Append to the first matcher entry, or create a new one
                if (existing.hooks[eventType].length > 0) {
                  if (!existing.hooks[eventType][0].hooks) {
                    existing.hooks[eventType][0].hooks = [];
                  }
                  existing.hooks[eventType][0].hooks.push(...newHooks);
                } else {
                  existing.hooks[eventType].push({ matcher: '', hooks: newHooks });
                }
              }
            }
          }
        }
      }

      fs.writeFileSync(existingPath, JSON.stringify(existing, null, 2) + '\n');
      console.log('  Settings merged successfully.');
    "
  else
    echo ""
    echo "Creating $SETTINGS_FILE from template..."
    mkdir -p "$(dirname "$SETTINGS_FILE")"
    cp "$TEMPLATE_FILE" "$SETTINGS_FILE"
    echo "  Settings file created."
  fi
fi

# ── Print summary ────────────────────────────────────────────────────────────

# Try to detect project name from git
PROJECT_NAME="my-project"
if command -v git &> /dev/null; then
  TOPLEVEL=$(git -C "$TARGET_DIR" rev-parse --show-toplevel 2>/dev/null || echo "")
  if [ -n "$TOPLEVEL" ]; then
    PROJECT_NAME=$(basename "$TOPLEVEL")
  fi
fi

echo ""
echo "==========================================="
echo "  Installation complete!"
echo "==========================================="
echo ""
echo "Set these environment variables (add to your shell profile):"
echo ""
echo "  export CC_OBSERVABILITY_URL=http://localhost:4000  # or your server URL"
echo "  export CC_PROJECT_ID=$PROJECT_NAME"
echo "  export CC_CONTRIBUTOR_ID=\$(echo -n \"\$(whoami)\$(hostname)\" | shasum -a 256 | cut -c1-12)"
echo ""
echo "Or set them in your project's .env file."
echo ""
echo "The hooks will silently do nothing if CC_OBSERVABILITY_URL is not set."
echo ""
echo "To test, run:"
echo "  echo '{\"test\":true}' | CC_OBSERVABILITY_URL=http://localhost:4000 npx tsx $HOOKS_DIR/send-event.ts --event-type Test"
echo ""
