"""Simplified Claude Code SDK wrapper for standalone usage.

Provides a minimal async wrapper around the claude-agent-sdk package,
handling plugin loading, message collection, and cost tracking.

Requires:
    pip install claude-agent-sdk
    npm install -g @anthropic-ai/claude-code
    ANTHROPIC_API_KEY environment variable
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class ClaudeCodeResult:
    """Result from a Claude Code SDK query."""

    result: str = ""
    session_id: Optional[str] = None
    total_cost_usd: Optional[float] = None
    duration_ms: Optional[int] = None
    num_turns: Optional[int] = None
    is_error: bool = False


def _get_plugin_config(cc_settings_dir: Path) -> dict:
    """Convert cc-settings directory to SDK plugin configuration.

    The SDK discovers skills via the plugins mechanism. This converts
    a local cc-settings directory path into the required plugin dict format.
    """
    resolved = cc_settings_dir.resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"cc-settings directory not found: {resolved}")
    return {"type": "local", "path": str(resolved)}


async def run_claude_code(
    prompt: str,
    *,
    cc_settings_dir: Path,
    working_dir: Path,
    allowed_tools: list[str],
    max_turns: int = 150,
    model: str = "claude-sonnet-4-5",
) -> ClaudeCodeResult:
    """Execute a Claude Code SDK query with the given configuration.

    Args:
        prompt: The task prompt for the agent.
        cc_settings_dir: Path to cc-settings/ directory containing skills and CLAUDE.md.
        working_dir: Working directory for the agent (file operations resolve here).
        allowed_tools: List of tools the agent can use (e.g., ["Skill", "Read", "Write", "Bash"]).
        max_turns: Maximum agent turns before stopping.
        model: Claude model to use.

    Returns:
        ClaudeCodeResult with the agent's output, cost, and metadata.
    """
    try:
        from claude_agent_sdk import (
            ClaudeAgentOptions,
            query,
            ResultMessage,
        )
    except ImportError as e:
        raise ImportError(
            "claude-agent-sdk not installed. Run: pip install claude-agent-sdk\n"
            "Also requires Claude Code CLI: npm install -g @anthropic-ai/claude-code"
        ) from e

    # Build plugin config for cc-settings directory
    plugin_config = _get_plugin_config(cc_settings_dir)

    options = ClaudeAgentOptions(
        allowed_tools=allowed_tools,
        permission_mode="acceptEdits",
        cwd=str(working_dir.resolve()),
        max_turns=max_turns,
        model=model,
        plugins=[plugin_config],
    )

    result_text = ""
    session_id = None
    total_cost = None
    duration_ms = None
    num_turns = None
    is_error = False
    result_captured = False

    try:
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, ResultMessage):
                msg_is_error = getattr(message, "is_error", False)
                msg_cost = getattr(message, "total_cost_usd", None)
                msg_result = message.result or ""

                # Skip subsequent error messages if we already have a successful result
                if result_captured and msg_is_error and (msg_cost is None or msg_cost == 0):
                    continue

                result_text = msg_result
                session_id = getattr(message, "session_id", None)
                total_cost = msg_cost
                duration_ms = getattr(message, "duration_ms", None)
                num_turns = getattr(message, "num_turns", None)
                is_error = msg_is_error

                if not is_error and (total_cost or result_text):
                    result_captured = True

    except Exception as e:
        logger.exception("Claude Code SDK query failed")
        return ClaudeCodeResult(
            result=f"Error: {str(e)}",
            is_error=True,
        )

    return ClaudeCodeResult(
        result=result_text,
        session_id=session_id,
        total_cost_usd=total_cost,
        duration_ms=duration_ms,
        num_turns=num_turns,
        is_error=is_error,
    )
