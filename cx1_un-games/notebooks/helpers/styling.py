"""Shared styling for GDP Spurious Regression notebooks."""

import ipywidgets as widgets

# Dark theme colors
DARK_BG = '#0a0e27'
AXES_BG = '#1a1a2e'
TEXT_COLOR = '#e0e7ff'
ACCENT_BLUE = '#3b82f6'
GREEN = '#22c55e'
RED = '#ef4444'
GRAY = '#94a3b8'
MUTED_TEXT = '#a5b4fc'

# Role colors
ROLE_COLORS = {
    'causal': '#22c55e',
    'bizarre': '#ef4444',
    'incidental': '#94a3b8',
    'target': '#3b82f6',
}


def apply_dark_theme(fig, ax):
    """Apply dark theme to a matplotlib figure and axes."""
    fig.patch.set_facecolor(DARK_BG)
    if isinstance(ax, list):
        axes = ax
    else:
        axes = [ax] if not hasattr(ax, '__iter__') else list(ax.flat)
    for a in axes:
        a.set_facecolor(AXES_BG)
        a.tick_params(colors=MUTED_TEXT, which='both')
        a.xaxis.label.set_color(MUTED_TEXT)
        a.yaxis.label.set_color(MUTED_TEXT)
        a.title.set_color(TEXT_COLOR)
        a.grid(True, alpha=0.15, linestyle='--', color='#4a5568')
        for spine in a.spines.values():
            spine.set_edgecolor('#4a4a6a')
            spine.set_linewidth(1.5)


def takeaway_box(text):
    """Return a styled HTML widget with a takeaway message."""
    return widgets.HTML(f"""
    <div style='background: linear-gradient(135deg, #1e3a5f, #1a1a2e);
                padding: 20px 25px; border-radius: 12px;
                border-left: 4px solid {ACCENT_BLUE};
                margin: 15px 0; max-width: 900px;'>
        <p style='color: {TEXT_COLOR}; font-size: 15px; line-height: 1.6; margin: 0;'>
            {text}
        </p>
    </div>
    """)


def metric_card(label, value, color=ACCENT_BLUE, width='180px'):
    """Return a styled HTML card showing a single metric."""
    return widgets.HTML(f"""
    <div style='background: #1e293b; padding: 14px 18px; border-radius: 10px;
                border: 1px solid #475569; text-align: center;
                display: inline-block; width: {width}; margin: 5px;'>
        <div style='color: #94a3b8; font-size: 12px; text-transform: uppercase;
                    letter-spacing: 1px; margin-bottom: 6px;'>{label}</div>
        <div style='color: {color}; font-size: 24px; font-weight: bold;'>{value}</div>
    </div>
    """)


def role_bar_colors(features, role_map):
    """Return list of colors for bar chart based on feature roles."""
    return [ROLE_COLORS.get(role_map.get(f, 'incidental'), GRAY) for f in features]


def role_legend_html():
    """Return HTML for a role color legend."""
    return widgets.HTML("""
    <div style='display: flex; gap: 20px; margin: 10px 0; align-items: center;'>
        <span style='color: #22c55e; font-weight: bold;'>&#9679; Causal</span>
        <span style='color: #ef4444; font-weight: bold;'>&#9679; Bizarre</span>
        <span style='color: #94a3b8; font-weight: bold;'>&#9679; Incidental</span>
    </div>
    """)


def styled_button(description, color=ACCENT_BLUE, width='140px'):
    """Create a styled button matching the dark theme."""
    btn = widgets.Button(
        description=description,
        layout=widgets.Layout(width=width, height='40px')
    )
    btn.style.button_color = color
    btn.style.text_color = 'white'
    btn.style.font_weight = 'bold'
    return btn
