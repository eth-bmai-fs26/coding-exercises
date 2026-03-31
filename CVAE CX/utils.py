import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, accuracy_score
from sklearn.decomposition import PCA

# -- Device & reproducibility -------------------------------------------------
torch.manual_seed(42)
np.random.seed(42)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def setup():
    """Call once at the top of the notebook to confirm everything is ready."""
    print(f"Setup complete. Running on: {DEVICE}")


# -- Classifier training (reused from Autoencoders CX) -----------------------

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


# -- CVAE training ------------------------------------------------------------

def train_cvae(model, loss_fn, X_train_np, y_train_oh_np,
               epochs=20, batch_size=128, lr=1e-3, beta=1.0):
    """
    Train a Conditional VAE.

    Parameters
    ----------
    model         : ConvCVAE instance
    loss_fn       : callable(recon_x, x, mu, log_var, beta) -> (total, recon, kl)
    X_train_np    : images, shape (N, 28, 28), float32 in [0, 1]
    y_train_oh_np : one-hot labels, shape (N, 10), float32
    epochs        : number of training epochs
    batch_size    : mini-batch size
    lr            : learning rate
    beta          : KL weighting factor

    Returns
    -------
    model        : trained model
    loss_history : dict with keys 'total', 'recon', 'kl' (lists of per-epoch averages)
    """
    X_t = torch.tensor(X_train_np[:, None, :, :]).to(DEVICE)
    y_t = torch.tensor(y_train_oh_np).to(DEVICE)
    loader = DataLoader(TensorDataset(X_t, y_t), batch_size=batch_size, shuffle=True)

    opt   = optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    sched = optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs)
    model.train()

    history = {'total': [], 'recon': [], 'kl': []}

    for epoch in range(1, epochs + 1):
        sum_total, sum_recon, sum_kl, n = 0.0, 0.0, 0.0, 0
        for xb, yb in loader:
            opt.zero_grad()
            recon_x, mu, log_var = model(xb, yb)
            total, recon, kl = loss_fn(recon_x, xb, mu, log_var, beta)
            total.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            opt.step()
            bs = xb.size(0)
            sum_total += total.item() * bs
            sum_recon += recon.item() * bs
            sum_kl    += kl.item() * bs
            n += bs
        sched.step()

        history['total'].append(sum_total / n)
        history['recon'].append(sum_recon / n)
        history['kl'].append(sum_kl / n)

        if epoch % 5 == 0 or epoch == 1:
            print(f"  Epoch {epoch:3d}/{epochs} -- Total: {history['total'][-1]:.2f}  "
                  f"Recon: {history['recon'][-1]:.2f}  KL: {history['kl'][-1]:.2f}  "
                  f"(lr={sched.get_last_lr()[0]:.5f})")

    print("Training complete!")
    return model, history


# -- Loss plot ----------------------------------------------------------------

def plot_losses(history):
    """Plot total, reconstruction, and KL losses over epochs."""
    fig, axes = plt.subplots(1, 3, figsize=(16, 4))
    titles = ['Total Loss', 'Reconstruction Loss (BCE)', 'KL Divergence']
    keys   = ['total', 'recon', 'kl']
    colors = ['crimson', 'seagreen', 'steelblue']

    for ax, key, title, color in zip(axes, keys, titles, colors):
        ax.plot(history[key], color=color, linewidth=2)
        ax.set_xlabel('Epoch')
        ax.set_ylabel('Loss')
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.show()


# -- Reconstruction -----------------------------------------------------------

def reconstruct_cvae(model, X_np, y_oh_np):
    """
    Pass images + labels through the CVAE, return reconstructions as numpy.

    Parameters
    ----------
    model   : trained ConvCVAE
    X_np    : images, shape (N, 28, 28)
    y_oh_np : one-hot labels, shape (N, 10)

    Returns
    -------
    recon : numpy array, shape (N, 28, 28)
    """
    model.eval()
    with torch.no_grad():
        X_t = torch.tensor(X_np[:, None, :, :]).to(DEVICE)
        y_t = torch.tensor(y_oh_np).to(DEVICE)
        recon, _, _ = model(X_t, y_t)
    return recon.cpu().numpy()[:, 0, :, :]


# -- Visualisation (reused / adapted from Autoencoders CX) -------------------

def plot_original_vs_reconstructed(original, reconstructed, n=8,
                                   title="Original vs. Reconstructed"):
    """Display two rows: originals on top, reconstructions below."""
    fig, axes = plt.subplots(2, n, figsize=(2*n, 5))
    fig.suptitle(title, fontsize=13, fontweight='bold')
    for i in range(n):
        axes[0, i].imshow(original[i],      cmap='gray'); axes[0, i].axis('off')
        axes[1, i].imshow(reconstructed[i], cmap='gray'); axes[1, i].axis('off')
    axes[0, 0].set_ylabel("Original",      fontsize=11)
    axes[1, 0].set_ylabel("Reconstructed", fontsize=11)
    plt.tight_layout()
    plt.show()


def plot_per_digit_mse(recon, X_test, y_test):
    """
    Compute and plot average reconstruction MSE for each digit class.

    Returns
    -------
    digit_mse   : dict {digit: mse_value}
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
    ax.bar(list(digit_mse.keys()), list(digit_mse.values()),
           color=colors, edgecolor='black')
    ax.set_xlabel("Digit", fontsize=12)
    ax.set_ylabel("Average MSE", fontsize=12)
    ax.set_title("Reconstruction Error per Digit Class (red = worst)",
                 fontsize=13, fontweight='bold')
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


# -- Conditional generation ---------------------------------------------------

def generate_conditional(model, digit, n=8, latent_dim=32):
    """
    Generate n images of a specific digit by sampling z ~ N(0, I).

    Parameters
    ----------
    model      : trained ConvCVAE
    digit      : integer digit to generate (0-9)
    n          : number of images to generate
    latent_dim : latent space dimensionality

    Returns
    -------
    images : numpy array (n, 28, 28)
    """
    model.eval()
    with torch.no_grad():
        z = torch.randn(n, latent_dim).to(DEVICE)
        label = torch.zeros(n, 10).to(DEVICE)
        label[:, digit] = 1.0
        images = model.decode(z, label).cpu().numpy()[:, 0, :, :]

    fig, axes = plt.subplots(1, n, figsize=(2*n, 2.5))
    fig.suptitle(f"Generated digit: {digit}", fontsize=13, fontweight='bold')
    for i in range(n):
        axes[i].imshow(images[i], cmap='gray')
        axes[i].axis('off')
    plt.tight_layout()
    plt.show()
    return images


def generate_digit_grid(model, latent_dim=32, n_per_digit=10):
    """
    Generate a grid of images: one row per digit (0-9), n_per_digit columns.
    """
    model.eval()
    fig, axes = plt.subplots(10, n_per_digit, figsize=(2*n_per_digit, 20))
    fig.suptitle("Conditional Generation: All Digits", fontsize=15, fontweight='bold')

    with torch.no_grad():
        for digit in range(10):
            z = torch.randn(n_per_digit, latent_dim).to(DEVICE)
            label = torch.zeros(n_per_digit, 10).to(DEVICE)
            label[:, digit] = 1.0
            images = model.decode(z, label).cpu().numpy()[:, 0, :, :]
            for j in range(n_per_digit):
                axes[digit, j].imshow(images[j], cmap='gray')
                axes[digit, j].axis('off')
            axes[digit, 0].set_ylabel(str(digit), fontsize=14, fontweight='bold',
                                      rotation=0, labelpad=20)

    plt.tight_layout()
    plt.show()


# -- Latent interpolation -----------------------------------------------------

def interpolate_latent(model, X_test_np, y_test_oh_np, idx1, idx2,
                       n_steps=10, switch_label=False):
    """
    Interpolate in latent space between two test images and display the result.

    Parameters
    ----------
    model          : trained ConvCVAE
    X_test_np      : test images (N, 28, 28)
    y_test_oh_np   : one-hot test labels (N, 10)
    idx1, idx2     : indices of the two images to interpolate between
    n_steps        : number of interpolation steps
    switch_label   : if True, switch the label halfway through
    """
    model.eval()
    with torch.no_grad():
        x1 = torch.tensor(X_test_np[idx1:idx1+1, None, :, :]).to(DEVICE)
        x2 = torch.tensor(X_test_np[idx2:idx2+1, None, :, :]).to(DEVICE)
        l1 = torch.tensor(y_test_oh_np[idx1:idx1+1]).to(DEVICE)
        l2 = torch.tensor(y_test_oh_np[idx2:idx2+1]).to(DEVICE)

        mu1, _ = model.encode(x1, l1)
        mu2, _ = model.encode(x2, l2)

        ratios = np.linspace(0, 1, n_steps)
        images = []
        for i, r in enumerate(ratios):
            z = (1 - r) * mu1 + r * mu2
            if switch_label:
                label = l1 if r < 0.5 else l2
            else:
                label = l1
            img = model.decode(z, label).cpu().numpy()[0, 0, :, :]
            images.append(img)

    d1 = int(y_test_oh_np[idx1].argmax())
    d2 = int(y_test_oh_np[idx2].argmax())
    mode = "label switch at midpoint" if switch_label else "fixed label"

    fig, axes = plt.subplots(1, n_steps, figsize=(2*n_steps, 2.5))
    fig.suptitle(f"Interpolation: {d1} -> {d2} ({mode})",
                 fontsize=13, fontweight='bold')
    for i in range(n_steps):
        axes[i].imshow(images[i], cmap='gray')
        axes[i].axis('off')
        axes[i].set_title(f"{ratios[i]:.1f}", fontsize=9)
    plt.tight_layout()
    plt.show()


# -- Latent space visualization -----------------------------------------------

def visualise_latent_space_cvae(model, X_test, y_test, y_test_oh, n_viz=3000):
    """
    Encode test images, project to 2D with PCA, and display scatter plot
    coloured by digit class.

    Parameters
    ----------
    model     : trained ConvCVAE
    X_test    : numpy array (N, 28, 28)
    y_test    : numpy array (N,) integer labels
    y_test_oh : numpy array (N, 10) one-hot labels
    n_viz     : number of images to visualise
    """
    model.eval()
    with torch.no_grad():
        X_t = torch.tensor(X_test[:n_viz, None, :, :]).to(DEVICE)
        y_t = torch.tensor(y_test_oh[:n_viz]).to(DEVICE)
        mu, _ = model.encode(X_t, y_t)
        latent = mu.cpu().numpy()

    labels_viz = y_test[:n_viz]

    pca = PCA(n_components=2)
    lat_2d = pca.fit_transform(latent)
    var_exp = pca.explained_variance_ratio_.sum()
    print(f"2D PCA explains {var_exp:.1%} of latent variance")

    COLORS = plt.cm.tab10(np.linspace(0, 1, 10))

    fig, ax = plt.subplots(figsize=(10, 8))
    for d in range(10):
        mask = labels_viz == d
        ax.scatter(lat_2d[mask, 0], lat_2d[mask, 1],
                   color=COLORS[d], s=5, alpha=0.5, label=str(d))

    ax.legend(title="Digit", fontsize=10, markerscale=3)
    ax.set_xlabel("PCA 1", fontsize=11)
    ax.set_ylabel("PCA 2", fontsize=11)
    ax.set_title("CVAE Latent Space (z_mean, PCA to 2D)", fontsize=13, fontweight='bold')
    ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    plt.show()

    return lat_2d, labels_viz


# -- Classifier evaluation of generated images --------------------------------

def evaluate_and_plot_confusion(classifier, X_np, y_true,
                                title="Confusion Matrix"):
    """
    Run the classifier on X_np, print accuracy, and display a confusion matrix.

    Returns
    -------
    acc : float
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


def evaluate_generated_images(model, classifier, latent_dim=32,
                              n_per_digit=200):
    """
    Generate images for each digit using the CVAE, then classify them
    with a pre-trained MNISTClassifier to measure generation quality.

    Returns
    -------
    acc : float -- classification accuracy on generated images
    """
    model.eval()
    all_images = []
    all_labels = []

    with torch.no_grad():
        for digit in range(10):
            z = torch.randn(n_per_digit, latent_dim).to(DEVICE)
            label = torch.zeros(n_per_digit, 10).to(DEVICE)
            label[:, digit] = 1.0
            imgs = model.decode(z, label).cpu().numpy()[:, 0, :, :]
            all_images.append(imgs)
            all_labels.append(np.full(n_per_digit, digit))

    all_images = np.concatenate(all_images, axis=0)
    all_labels = np.concatenate(all_labels, axis=0)

    print(f"Evaluating {len(all_images)} generated images...")
    acc = evaluate_and_plot_confusion(
        classifier, all_images, all_labels,
        title="Classifier on CVAE-Generated Images"
    )
    return acc
