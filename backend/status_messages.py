"""Styled status card HTML builder."""

import html


def render_status(message, tone="ready", title=None):
    """Render a styled status card for the UI."""
    titles = {
        "ready": "Ready",
        "success": "Completed",
        "error": "Something went wrong",
        "warning": "Check result",
    }
    safe_message = html.escape(message)
    safe_title = html.escape(title or titles.get(tone, "Status"))
    return f"""
    <div class="status-shell">
      <div class="status-card status-{tone}">
        <div class="status-label">Status</div>
        <div class="status-title">{safe_title}</div>
        <div class="status-message">{safe_message}</div>
      </div>
    </div>
    """
