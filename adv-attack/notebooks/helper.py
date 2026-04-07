"""helper.py — Shared visualization utilities for the Adversarial Attacks exercises.

Kept separate so that notebooks stay focused on concepts, not plotting boilerplate.
Students should not need to modify this file.

Framework: PyTorch + Matplotlib.
"""

import numpy as np
import matplotlib.pyplot as plt
import torch

# ── Colour palette (consistent across all plots) ──────────────────────────────
_C = {
    "clean":       "#4C72B0",   # blue  — clean / benign
    "adversarial": "#C44E52",   # red   — adversarial / attack
    "robust":      "#55A868",   # green — robust / defence
    "neutral":     "#8172B3",   # purple — neutral series
}

plt.rcParams.update({
    "figure.facecolor":  "#fafafa",
    "axes.facecolor":    "#fafafa",
    "axes.spines.top":   False,
    "axes.spines.right": False,
})

_CIFAR10_MEAN = [0.4914, 0.4822, 0.4465]
_CIFAR10_STD  = [0.2470, 0.2435, 0.2616]


# ── Image utilities ────────────────────────────────────────────────────────────

def denormalize_cifar10(tensor):
    """Reverse CIFAR-10 normalization and clamp to [0, 1] for display.

    Args:
        tensor: (C, H, W) or (N, C, H, W) float tensor, normalized.

    Returns:
        Tensor of the same shape with values in [0, 1].
    """
    t = tensor.clone().float()
    is_batch = t.dim() == 4
    if not is_batch:
        t = t.unsqueeze(0)
    for i in range(3):
        t[:, i] = t[:, i] * _CIFAR10_STD[i] + _CIFAR10_MEAN[i]
    t = torch.clamp(t, 0.0, 1.0)
    return t if is_batch else t.squeeze(0)


# ── Plotting functions ─────────────────────────────────────────────────────────

def plot_accuracy_curves(x_values, y_dict, xlabel, title, hlines=None, figsize=(7, 4)):
    """Plot one or more accuracy curves against a shared x-axis.

    Args:
        x_values:  List of x-axis values (e.g. epsilon values, poison rates).
        y_dict:    Dict mapping curve label → list of y values (same length as x_values).
                   Example: {"FGSM": [0.9, 0.7, 0.3], "PGD": [0.85, 0.5, 0.1]}
        xlabel:    Label for the x-axis.
        title:     Plot title.
        hlines:    Optional dict mapping label → y value for horizontal reference lines.
                   Example: {"Clean accuracy": 0.93}
        figsize:   Figure size tuple.
    """
    palette = [_C["adversarial"], _C["clean"], _C["robust"], _C["neutral"]]
    markers = ["o", "s", "^", "D"]
    linestyles = ["-", "--", "-.", ":"]

    plt.figure(figsize=figsize)
    for idx, (label, y_values) in enumerate(y_dict.items()):
        plt.plot(
            x_values, y_values,
            marker=markers[idx % len(markers)],
            linestyle=linestyles[idx % len(linestyles)],
            color=palette[idx % len(palette)],
            linewidth=2, markersize=7,
            label=label,
        )
    if hlines:
        hline_colors = [_C["clean"], _C["robust"], _C["neutral"]]
        for i, (label, y) in enumerate(hlines.items()):
            plt.axhline(y, color=hline_colors[i % len(hline_colors)],
                        linestyle="--", linewidth=1.5, label=label)
    plt.xlabel(xlabel)
    plt.ylabel("Accuracy")
    plt.title(title)
    plt.ylim(0, 1.05)
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_image_grid(rows, suptitle=None, figsize=None):
    """Display a grid of images, one row per entry in `rows`.

    Args:
        rows: List of dicts, one per visual row. Each dict has:
            - "images":  list of N image tensors (C,H,W) or (H,W)
            - "titles":  list of N title strings (shown above each image)
            - "colors":  list of N title colour strings, or None for default
            - "ylabel":  optional string for the row y-axis label
        suptitle: Optional super-title for the entire figure.
        figsize:  Optional (width, height) tuple. Auto-sized if None.

    Each image tensor is handled automatically:
        - 3-channel (C=3): treated as CIFAR-10, denormalized.
        - 1-channel or 2D: displayed as grayscale without denormalization.
    """
    n_rows = len(rows)
    n_cols = len(rows[0]["images"])
    if figsize is None:
        figsize = (max(2.4 * n_cols, 8), 2.6 * n_rows)

    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
    if n_rows == 1:
        axes = axes[np.newaxis, :]
    if n_cols == 1:
        axes = axes[:, np.newaxis]

    for r, row in enumerate(rows):
        images = row["images"]
        titles = row.get("titles", [""] * n_cols)
        colors = row.get("colors", [None] * n_cols)
        ylabel = row.get("ylabel", None)

        denorm = row.get("denorm", True)   # set False for rows already in [0, 1]

        for c in range(n_cols):
            ax = axes[r, c]
            img = images[c]
            if isinstance(img, torch.Tensor):
                img = img.detach().cpu()
                if img.dim() == 3 and img.shape[0] == 3:
                    if denorm:
                        img = denormalize_cifar10(img).permute(1, 2, 0).numpy()
                    else:
                        img = torch.clamp(img, 0, 1).permute(1, 2, 0).numpy()
                    ax.imshow(img)
                elif img.dim() == 3 and img.shape[0] == 1:
                    ax.imshow(img.squeeze().numpy(), cmap="gray", vmin=0, vmax=1)
                else:
                    ax.imshow(img.squeeze().numpy(), cmap="gray", vmin=0, vmax=1)
            else:
                ax.imshow(img)
            ax.axis("off")
            title_color = colors[c] if colors[c] is not None else "black"
            ax.set_title(titles[c], fontsize=9, color=title_color)

        if ylabel and n_cols > 0:
            axes[r, 0].set_ylabel(ylabel, fontsize=11)

    if suptitle:
        plt.suptitle(suptitle, fontsize=12, y=1.02)
    plt.tight_layout()
    plt.show()


def plot_grouped_bars(group_labels, bar_data, bar_labels, ylabel, title, figsize=(7, 5)):
    """Display a grouped bar chart.

    Args:
        group_labels: List of group names shown on x-axis (e.g. ["Standard", "Robust"]).
        bar_data:     List of value lists, one per bar series (e.g. [clean_accs, adv_accs]).
        bar_labels:   List of legend labels, one per series (e.g. ["Clean", "Adversarial"]).
        ylabel:       Y-axis label.
        title:        Plot title.
        figsize:      Figure size tuple.
    """
    palette = [_C["clean"], _C["adversarial"], _C["robust"], _C["neutral"]]
    n_groups = len(group_labels)
    n_bars   = len(bar_data)
    width    = 0.8 / n_bars
    x        = np.arange(n_groups)

    fig, ax = plt.subplots(figsize=figsize)
    for i, (values, label) in enumerate(zip(bar_data, bar_labels)):
        offset = (i - (n_bars - 1) / 2) * width
        ax.bar(x + offset, values, width, label=label,
               color=palette[i % len(palette)], alpha=0.9)

    ax.set_xticks(x)
    ax.set_xticklabels(group_labels)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend()
    ax.set_ylim(0, max(max(v) for v in bar_data) * 1.15)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_distribution_histograms(data_dict, xlabel, title, log_y=False,
                                 figsize=(6, 4), bins=50, alpha=0.7):
    """Plot overlapping histograms for two or more distributions.

    Args:
        data_dict: Dict mapping label → 1-D array of values.
                   Example: {"Members": member_losses, "Non-members": nonmember_losses}
        xlabel:    X-axis label.
        title:     Plot title.
        log_y:     If True, use log scale on the y-axis.
        figsize:   Figure size tuple.
        bins:      Number of histogram bins.
        alpha:     Bar transparency.
    """
    palette = [_C["adversarial"], _C["clean"], _C["robust"], _C["neutral"]]
    plt.figure(figsize=figsize)
    for i, (label, data) in enumerate(data_dict.items()):
        plt.hist(data, bins=bins, alpha=alpha,
                 color=palette[i % len(palette)], label=label)
    if log_y:
        plt.yscale("log")
    plt.xlabel(xlabel)
    plt.ylabel("Count (log)" if log_y else "Count")
    plt.title(title)
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()
