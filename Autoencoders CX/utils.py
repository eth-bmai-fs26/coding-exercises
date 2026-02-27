import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, accuracy_score
from sklearn.decomposition import PCA

# ── Device & reproducibility ──────────────────────────────────────────────────
torch.manual_seed(42)
np.random.seed(42)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def setup():
    """Call once at the top of the notebook to confirm everything is ready."""
    print(f"✅ Setup complete. Running on: {DEVICE}")


def train_classifier(model_cls, X_np, y_np, epochs=10, batch_size=256):
    """
    Train the MNISTClassifier on the provided images and labels.

    Parameters
    ----------
    model_cls : the classifier class (e.g. MNISTClassifier)
    X_np      : images, shape (N, 28, 28)
    y_np      : integer labels, shape (N,)
    """
    model = model_cls().to(DEVICE)
    X_t = torch.tensor(X_np[:, None, :, :]).to(DEVICE)
    y_t = torch.tensor(y_np, dtype=torch.long).to(DEVICE)
    loader = DataLoader(TensorDataset(X_t, y_t), batch_size=batch_size, shuffle=True)
    opt = optim.Adam(model.parameters())
    model.train()
    for _ in range(epochs):
        for xb, yb in loader:
            opt.zero_grad()
            nn.CrossEntropyLoss()(model(xb), yb).backward()
            opt.step()
    return model


# ── Evaluation ────────────────────────────────────────────────────────────────

def evaluate_and_plot_confusion(classifier, X_np, y_true, title="Confusion Matrix"):
    """
    Run the classifier on X_np, print accuracy, and display a confusion matrix.

    Returns
    -------
    acc : float — classification accuracy
    """
    classifier.eval()
    with torch.no_grad():
        preds = classifier(
            torch.tensor(X_np[:, None, :, :]).to(DEVICE)
        ).argmax(1).cpu().numpy()

    acc = accuracy_score(y_true, preds)
    print(f"  Accuracy: {acc:.2%}")

    fig, ax = plt.subplots(figsize=(8, 7))
    ConfusionMatrixDisplay(confusion_matrix(y_true, preds)).plot(ax=ax, colorbar=False)
    ax.set_title(f"{title}  (acc = {acc:.2%})", fontsize=12)
    plt.tight_layout()
    plt.show()
    return acc


# ── Visualisation ─────────────────────────────────────────────────────────────

def plot_original_vs_reconstructed(original, reconstructed, n=8, title="Original vs. Reconstructed"):
    """
    Display two rows of images: originals on top, reconstructions below.

    Parameters
    ----------
    original      : numpy array, shape (N, 28, 28)
    reconstructed : numpy array, shape (N, 28, 28)
    n             : number of image pairs to show
    title         : figure title
    """
    fig, axes = plt.subplots(2, n, figsize=(2*n, 5))
    fig.suptitle(title, fontsize=13, fontweight='bold')
    for i in range(n):
        axes[0, i].imshow(original[i],      cmap='gray'); axes[0, i].axis('off')
        axes[1, i].imshow(reconstructed[i], cmap='gray'); axes[1, i].axis('off')
    axes[0, 0].set_ylabel("Original",      fontsize=11)
    axes[1, 0].set_ylabel("Reconstructed", fontsize=11)
    plt.tight_layout()
    plt.show()

# ── Analysis helpers ──────────────────────────────────────────────────────────

def plot_per_digit_mse(recon, X_test, y_test):
    """
    Compute and plot average reconstruction MSE for each digit class.

    Parameters
    ----------
    recon  : numpy array (N, 28, 28) — reconstructed images
    X_test : numpy array (N, 28, 28) — ground-truth clean images
    y_test : numpy array (N,)        — digit labels

    Returns
    -------
    digit_mse : dict  {digit: mse_value}
    worst_digit : int
    """
    digit_mse = {}
    for d in range(10):
        mask = (y_test == d)
        digit_mse[d] = np.mean((X_test[mask] - recon[mask]) ** 2)

    print("Average reconstruction MSE per digit:")
    for d, mse in digit_mse.items():
        print(f"  Digit {d}: {mse:.5f}")

    fig, ax = plt.subplots(figsize=(10, 4))
    colors = ['crimson' if v == max(digit_mse.values()) else 'steelblue'
              for v in digit_mse.values()]
    ax.bar(list(digit_mse.keys()), list(digit_mse.values()), color=colors, edgecolor='black')
    ax.set_xlabel("Digit", fontsize=12)
    ax.set_ylabel("Average MSE", fontsize=12)
    ax.set_title("Reconstruction Error per Digit Class (red = worst)", fontsize=13, fontweight='bold')
    ax.set_xticks(range(10))
    plt.tight_layout()
    plt.show()

    worst_digit = max(digit_mse, key=digit_mse.get)
    print(f"\nWorst reconstructed digit: {worst_digit}")

    mask_worst = (y_test == worst_digit)
    plot_original_vs_reconstructed(
        X_test[mask_worst][:5], recon[mask_worst][:5], n=5,
        title=f"Digit {worst_digit}: Original vs. Reconstructed"
    )
    return digit_mse, worst_digit


def visualise_latent_space(model, X_test, y_test, n_viz=2000, grid=14):
    """
    Project the latent space to 2D with PCA and display:
      - Left:  encoder map (digit labels coloured by class)
      - Right: decoder grid (what each region of latent space decodes to)

    Parameters
    ----------
    model  : trained ConvAutoencoder
    X_test : numpy array (N, 28, 28)
    y_test : numpy array (N,)
    n_viz  : number of test images to use
    grid   : side length of the decoder grid (grid × grid images)

    Returns
    -------
    lat_2d     : (n_viz, 2) PCA-projected latent vectors
    labels_viz : (n_viz,)   corresponding labels
    pca_viz    : fitted PCA object (useful for Exercise 2)
    """
    model.eval()
    with torch.no_grad():
        latent_all = model.encode(
            torch.tensor(X_test[:n_viz, None, :, :]).to(DEVICE)
        ).cpu().numpy()

    labels_viz = y_test[:n_viz]

    pca_viz = PCA(n_components=2)
    lat_2d  = pca_viz.fit_transform(latent_all)
    var_exp = pca_viz.explained_variance_ratio_.sum()
    print(f"2D PCA explains {var_exp:.1%} of latent variance")

    # Build decoder grid
    x_range = np.linspace(lat_2d[:, 0].min() * 0.9, lat_2d[:, 0].max() * 0.9, grid)
    y_range = np.linspace(lat_2d[:, 1].max() * 0.9, lat_2d[:, 1].min() * 0.9, grid)

    grid_points_2d = np.array([[x, y] for y in y_range for x in x_range], dtype="float32")
    grid_latent    = pca_viz.inverse_transform(grid_points_2d)

    model.eval()
    with torch.no_grad():
        grid_images = model.decode(
            torch.tensor(grid_latent).to(DEVICE)
        ).cpu().numpy()[:, 0, :, :]

    decoder_canvas = np.zeros((grid * 28, grid * 28))
    for idx, img in enumerate(grid_images):
        r, c = divmod(idx, grid)
        decoder_canvas[r*28:(r+1)*28, c*28:(c+1)*28] = img

    # Plot
    COLORS = plt.cm.tab10(np.linspace(0, 1, 10))
    fig, (ax_enc, ax_dec) = plt.subplots(1, 2, figsize=(16, 7))
    fig.patch.set_facecolor('white')

    for d in range(10):
        mask = labels_viz == d
        ax_enc.scatter(lat_2d[mask, 0], lat_2d[mask, 1], color=COLORS[d], s=0, alpha=0)
        for x, y in zip(lat_2d[mask, 0][:40], lat_2d[mask, 1][:40]):
            ax_enc.text(x, y, str(d), fontsize=7, color=COLORS[d],
                        ha='center', va='center', fontweight='bold', alpha=0.8)

    ax_enc.set_xlabel("PCA₁  (Z₁)", fontsize=11)
    ax_enc.set_ylabel("PCA₂  (Z₂)", fontsize=11)
    ax_enc.set_title("ENCODER MAP (each point = one test image)", fontsize=12, fontweight='bold')
    ax_enc.spines[['top', 'right']].set_visible(False)

    ax_dec.imshow(decoder_canvas, cmap='gray', origin='upper',
                  extent=[x_range[0], x_range[-1], y_range[-1], y_range[0]], aspect='auto')
    ax_dec.set_xlabel("PCA₁  (Z₁)", fontsize=11)
    ax_dec.set_ylabel("PCA₂  (Z₂)", fontsize=11)
    ax_dec.set_title("DECODER GRID (what does each region of latent space decode to?)",
                     fontsize=12, fontweight='bold')

    plt.suptitle("Latent Space Visualisation", fontsize=14, fontweight='bold', y=1.01)
    plt.tight_layout()
    plt.show()

    return lat_2d, labels_viz, pca_viz


def probe_latent_space(lat_2d, labels_viz):
    """
    Find the two digit classes whose latent-space centroids are closest,
    and plot the scatter with centroids and the closest pair highlighted.

    Parameters
    ----------
    lat_2d     : (N, 2) PCA-projected latent vectors
    labels_viz : (N,)   digit labels

    Returns
    -------
    centroids    : dict {digit: centroid_array}
    closest_pair : tuple (digit_a, digit_b)
    """
    centroids = {d: lat_2d[labels_viz == d].mean(axis=0) for d in range(10)}

    min_dist     = float('inf')
    closest_pair = (None, None)
    for i in range(10):
        for j in range(i + 1, 10):
            dist = np.linalg.norm(centroids[i] - centroids[j])
            if dist < min_dist:
                min_dist     = dist
                closest_pair = (i, j)

    print(f"Most confused digit pair: {closest_pair[0]} and {closest_pair[1]} "
          f"(centroid distance: {min_dist:.3f})")

    fig, ax = plt.subplots(figsize=(10, 8))
    sc = ax.scatter(lat_2d[:, 0], lat_2d[:, 1], c=labels_viz, cmap='tab10', s=2, alpha=0.4)
    plt.colorbar(sc, ax=ax, ticks=range(10)).set_label('Digit', fontsize=10)

    for d, c in centroids.items():
        ax.plot(*c, 'k^', markersize=10)
        ax.annotate(str(d), c, fontsize=13, fontweight='bold',
                    xytext=(5, 5), textcoords='offset points')

    a, b = closest_pair
    ax.plot([centroids[a][0], centroids[b][0]],
            [centroids[a][1], centroids[b][1]],
            'r--', linewidth=2, label=f"Closest pair: {a} & {b}")
    ax.legend(fontsize=11)
    ax.set_title("Latent Space with Centroids and Closest Pair", fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.show()

    return centroids, closest_pair


def compare_models_head_to_head(recon_classic, recon_denoised, X_test, X_test_noisy, y_test):
    """
    Full head-to-head comparison of classic vs. denoising autoencoder:
      1. Per-digit MSE table and grouped bar chart
      2. Summary winner table printed to console
      3. Visual comparison for the digit with the largest improvement

    Parameters
    ----------
    recon_classic  : (N, 28, 28) classic AE output on noisy input
    recon_denoised : (N, 28, 28) denoising AE output on noisy input
    X_test         : (N, 28, 28) clean ground-truth images
    X_test_noisy   : (N, 28, 28) noisy input images
    y_test         : (N,)        digit labels
    """
    mse_classic  = {d: np.mean((recon_classic[y_test == d]  - X_test[y_test == d]) ** 2) for d in range(10)}
    mse_denoised = {d: np.mean((recon_denoised[y_test == d] - X_test[y_test == d]) ** 2) for d in range(10)}

    # Grouped bar chart
    x = np.arange(10)
    width = 0.35
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(x - width/2, [mse_classic[d]  for d in range(10)], width, label='Classic AE',   color='tomato')
    ax.bar(x + width/2, [mse_denoised[d] for d in range(10)], width, label='Denoising AE', color='seagreen')
    ax.set_xlabel("Digit")
    ax.set_ylabel("Avg MSE (lower = better)")
    ax.set_title("Per-Digit Reconstruction Error: Classic vs. Denoising AE", fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.legend()
    plt.tight_layout()
    plt.show()

    # Summary table
    print(f"{'Digit':>6} | {'Classic MSE':>12} | {'Denoising MSE':>14} | Winner")
    print("-" * 52)
    for d in range(10):
        winner = 'Denoising AE' if mse_denoised[d] < mse_classic[d] else 'Classic AE'
        print(f"{d:>6} | {mse_classic[d]:>12.5f} | {mse_denoised[d]:>14.5f} | {winner}")

    # Largest gap + visual
    gaps              = {d: mse_classic[d] - mse_denoised[d] for d in range(10)}
    biggest_gap_digit = max(gaps, key=gaps.get)
    print(f"\nLargest improvement on digit: {biggest_gap_digit} (gap = {gaps[biggest_gap_digit]:.5f})")

    mask = (y_test == biggest_gap_digit)
    fig, axes = plt.subplots(4, 5, figsize=(12, 10))
    fig.suptitle(f"Digit {biggest_gap_digit}: Detailed Comparison", fontsize=13, fontweight='bold')
    for i in range(5):
        axes[0, i].imshow(X_test_noisy[mask][i],      cmap='gray'); axes[0, i].axis('off')
        axes[1, i].imshow(recon_classic[mask][i],      cmap='gray'); axes[1, i].axis('off')
        axes[2, i].imshow(recon_denoised[mask][i],     cmap='gray'); axes[2, i].axis('off')
        axes[3, i].imshow(X_test[mask][i],             cmap='gray'); axes[3, i].axis('off')
    axes[0, 0].set_ylabel("Noisy Input",  fontsize=9)
    axes[1, 0].set_ylabel("Classic AE",   fontsize=9)
    axes[2, 0].set_ylabel("Denoising AE", fontsize=9)
    axes[3, 0].set_ylabel("Ground Truth", fontsize=9)
    plt.tight_layout()
    plt.show()