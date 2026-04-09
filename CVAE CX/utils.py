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
        z = torch.randn(n, latent_dim).to(DEVICE) * 0.75
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
            z = torch.randn(n_per_digit, latent_dim).to(DEVICE) * 0.75
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
            z = torch.randn(n_per_digit, latent_dim).to(DEVICE) * 0.75
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


# =============================================================================
# CelebA-specific utilities
# =============================================================================

def train_cvae_celeba(model, loss_fn, X_train_np, attrs_train_np,
                      epochs=25, batch_size=32, lr=1e-3, beta=1.0):
    """
    Train a CelebA Conditional VAE.

    Parameters
    ----------
    model           : CelebAConvCVAE instance
    loss_fn         : callable(recon_x, x, mu, log_var, beta) -> (total, recon, kl)
    X_train_np      : images, shape (N, 3, 64, 64), float32 in [0, 1]
    attrs_train_np  : binary attributes, shape (N, 40), float32
    """
    X_t = torch.tensor(X_train_np).to(DEVICE)
    a_t = torch.tensor(attrs_train_np).to(DEVICE)
    loader = DataLoader(TensorDataset(X_t, a_t), batch_size=batch_size, shuffle=True)

    opt = optim.Adam(model.parameters(), lr=lr)
    model.train()

    history = {'total': [], 'recon': [], 'kl': []}

    for epoch in range(1, epochs + 1):
        sum_total, sum_recon, sum_kl, n = 0.0, 0.0, 0.0, 0
        for xb, ab in loader:
            opt.zero_grad()
            recon_x, mu, log_var = model(xb, ab)
            total, recon, kl = loss_fn(recon_x, xb, mu, log_var, beta)
            total.backward()
            opt.step()
            bs = xb.size(0)
            sum_total += total.item() * bs
            sum_recon += recon.item() * bs
            sum_kl    += kl.item() * bs
            n += bs

        history['total'].append(sum_total / n)
        history['recon'].append(sum_recon / n)
        history['kl'].append(sum_kl / n)

        if epoch % 5 == 0 or epoch == 1:
            print(f"  Epoch {epoch:3d}/{epochs} -- Total: {history['total'][-1]:.2f}  "
                  f"Recon: {history['recon'][-1]:.2f}  KL: {history['kl'][-1]:.2f}")

    print("Training complete!")
    return model, history


def reconstruct_cvae_celeba(model, X_np, attrs_np):
    """
    Pass CelebA images + attributes through the CVAE, return reconstructions.

    Returns
    -------
    recon : numpy array, shape (N, 3, 64, 64)
    """
    model.eval()
    with torch.no_grad():
        X_t = torch.tensor(X_np).to(DEVICE)
        a_t = torch.tensor(attrs_np).to(DEVICE)
        recon, _, _ = model(X_t, a_t)
    return recon.cpu().numpy()


def plot_original_vs_reconstructed_celeba(original, reconstructed, n=8,
                                          title="Original vs. Reconstructed"):
    """
    Display two rows of CelebA faces: originals on top, reconstructions below.

    Parameters
    ----------
    original, reconstructed : numpy arrays, shape (N, 3, 64, 64)
    """
    fig, axes = plt.subplots(2, n, figsize=(2.5 * n, 5.5))
    fig.suptitle(title, fontsize=13, fontweight='bold')
    for i in range(n):
        img_o = np.clip(original[i].transpose(1, 2, 0), 0, 1)
        img_r = np.clip(reconstructed[i].transpose(1, 2, 0), 0, 1)
        axes[0, i].imshow(img_o); axes[0, i].axis('off')
        axes[1, i].imshow(img_r); axes[1, i].axis('off')
    axes[0, 0].set_ylabel("Original",      fontsize=11)
    axes[1, 0].set_ylabel("Reconstructed", fontsize=11)
    plt.tight_layout()
    plt.show()


def plot_per_attribute_mse(recon, X_test, attrs_test, attr_names, top_k=10):
    """
    Compute average reconstruction MSE for images grouped by each attribute.

    Parameters
    ----------
    recon, X_test : numpy arrays (N, 3, 64, 64)
    attrs_test    : numpy array (N, 40) binary
    attr_names    : list of 40 attribute name strings
    top_k         : show only the top-k worst attributes
    """
    per_pixel_mse = np.mean((X_test - recon) ** 2, axis=(1, 2, 3))
    attr_mse = {}
    for i, name in enumerate(attr_names):
        mask = attrs_test[:, i] == 1.0
        if mask.sum() > 0:
            attr_mse[name] = float(np.mean(per_pixel_mse[mask]))

    sorted_attrs = sorted(attr_mse.items(), key=lambda x: x[1], reverse=True)[:top_k]
    names = [a[0] for a in sorted_attrs]
    vals  = [a[1] for a in sorted_attrs]

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ['crimson' if i == 0 else 'steelblue' for i in range(len(names))]
    ax.barh(names[::-1], vals[::-1], color=colors[::-1], edgecolor='black')
    ax.set_xlabel("Average MSE", fontsize=12)
    ax.set_title(f"Top-{top_k} Worst Reconstructed Attributes (red = worst)",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.show()

    print(f"\nWorst reconstructed attribute: {names[0]} (MSE = {vals[0]:.5f})")
    return attr_mse


def generate_conditional_celeba(model, attrs_dict, attr_names, n=8, latent_dim=128, seed=42):
    """
    Generate n CelebA faces with specific attributes.

    Parameters
    ----------
    model       : trained CelebAConvCVAE
    attrs_dict  : dict like {"Smiling": 1, "Male": 0, "Eyeglasses": 1}
    attr_names  : list of 40 attribute name strings
    n           : number of images
    latent_dim  : latent space dimensionality
    seed        : random seed for z sampling — change to explore different faces

    Returns
    -------
    images : numpy array (n, 3, 64, 64)
    """
    model.eval()
    with torch.no_grad():
        torch.manual_seed(seed)
        z = torch.randn(n, latent_dim).to(DEVICE) * 0.75
        attrs = torch.zeros(n, len(attr_names)).to(DEVICE)
        for name, val in attrs_dict.items():
            idx = attr_names.index(name)
            attrs[:, idx] = float(val)
        images = model.decode(z, attrs).cpu().numpy()

    active = [k for k, v in attrs_dict.items() if v == 1]
    title = "Generated: " + (", ".join(active) if active else "no attributes")

    fig, axes = plt.subplots(1, n, figsize=(2.5 * n, 3))
    fig.suptitle(title, fontsize=13, fontweight='bold')
    for i in range(n):
        axes[i].imshow(np.clip(images[i].transpose(1, 2, 0), 0, 1))
        axes[i].axis('off')
    plt.tight_layout()
    plt.show()


def generate_attribute_grid(model, attr_names, combos, latent_dim=128,
                            n_per_row=8):
    """
    Generate a grid of CelebA faces: one row per attribute combination.

    Parameters
    ----------
    model      : trained CelebAConvCVAE
    attr_names : list of 40 attribute name strings
    combos     : list of dicts, e.g. [{"Smiling": 1}, {"Male": 1, "Eyeglasses": 1}]
    latent_dim : latent space dimensionality
    n_per_row  : samples per combination
    """
    n_rows = len(combos)
    model.eval()
    fig, axes = plt.subplots(n_rows, n_per_row, figsize=(2.5 * n_per_row, 3 * n_rows))
    fig.suptitle("Conditional Generation: Attribute Combinations",
                 fontsize=15, fontweight='bold')
    if n_rows == 1:
        axes = axes[np.newaxis, :]

    with torch.no_grad():
        z_shared = torch.randn(n_per_row, latent_dim).to(DEVICE) * 0.75
        for row, combo in enumerate(combos):
            attrs = torch.zeros(n_per_row, len(attr_names)).to(DEVICE)
            for name, val in combo.items():
                idx = attr_names.index(name)
                attrs[:, idx] = float(val)
            images = model.decode(z_shared, attrs).cpu().numpy()
            active = [k for k, v in combo.items() if v == 1]
            label = ", ".join(active) if active else "none"
            for j in range(n_per_row):
                axes[row, j].imshow(np.clip(images[j].transpose(1, 2, 0), 0, 1))
                axes[row, j].axis('off')
            axes[row, 0].set_ylabel(label, fontsize=10, fontweight='bold',
                                    rotation=90, labelpad=10)

    plt.tight_layout()
    plt.show()


def interpolate_latent_celeba(model, X_test_np, attrs_test_np, idx1, idx2,
                              n_steps=10, switch_attrs=False):
    """
    Interpolate in latent space between two CelebA test images.

    Parameters
    ----------
    model           : trained CelebAConvCVAE
    X_test_np       : test images (N, 3, 64, 64)
    attrs_test_np   : test attributes (N, 40)
    idx1, idx2      : indices of the two images
    n_steps         : number of interpolation steps
    switch_attrs    : if True, switch attributes halfway
    """
    model.eval()
    with torch.no_grad():
        x1 = torch.tensor(X_test_np[idx1:idx1+1]).to(DEVICE)
        x2 = torch.tensor(X_test_np[idx2:idx2+1]).to(DEVICE)
        a1 = torch.tensor(attrs_test_np[idx1:idx1+1]).to(DEVICE)
        a2 = torch.tensor(attrs_test_np[idx2:idx2+1]).to(DEVICE)

        mu1, _ = model.encode(x1, a1)
        mu2, _ = model.encode(x2, a2)

        ratios = np.linspace(0, 1, n_steps)
        images = []
        for r in ratios:
            z = (1 - r) * mu1 + r * mu2
            attrs = a1 if (not switch_attrs or r < 0.5) else a2
            img = model.decode(z, attrs).cpu().numpy()[0]
            images.append(img)

    mode = "attribute switch at midpoint" if switch_attrs else "fixed attributes"
    fig, axes = plt.subplots(1, n_steps + 2, figsize=(2.5 * (n_steps + 2), 3))
    fig.suptitle(f"Latent Interpolation ({mode})", fontsize=13, fontweight='bold')

    # Show source images at the edges
    axes[0].imshow(np.clip(X_test_np[idx1].transpose(1, 2, 0), 0, 1))
    axes[0].set_title("Source", fontsize=9); axes[0].axis('off')
    for i in range(n_steps):
        axes[i + 1].imshow(np.clip(images[i].transpose(1, 2, 0), 0, 1))
        axes[i + 1].set_title(f"{ratios[i]:.1f}", fontsize=9); axes[i + 1].axis('off')
    axes[-1].imshow(np.clip(X_test_np[idx2].transpose(1, 2, 0), 0, 1))
    axes[-1].set_title("Target", fontsize=9); axes[-1].axis('off')
    plt.tight_layout()
    plt.show()


def visualise_latent_space_celeba(model, X_test, attrs_test, attr_names,
                                  color_by="Smiling", n_viz=3000):
    """
    Encode CelebA test images, project to 2D with PCA, color by a binary attribute.
    """
    model.eval()
    with torch.no_grad():
        X_t = torch.tensor(X_test[:n_viz]).to(DEVICE)
        a_t = torch.tensor(attrs_test[:n_viz]).to(DEVICE)
        mu, _ = model.encode(X_t, a_t)
        latent = mu.cpu().numpy()

    attr_idx = attr_names.index(color_by)
    labels = attrs_test[:n_viz, attr_idx]

    pca = PCA(n_components=2)
    lat_2d = pca.fit_transform(latent)
    var_exp = pca.explained_variance_ratio_.sum()
    print(f"2D PCA explains {var_exp:.1%} of latent variance")

    fig, ax = plt.subplots(figsize=(10, 8))
    for val, color, lbl in [(0, 'steelblue', f'No {color_by}'),
                             (1, 'crimson',  color_by)]:
        mask = labels == val
        ax.scatter(lat_2d[mask, 0], lat_2d[mask, 1],
                   color=color, s=5, alpha=0.4, label=lbl)

    ax.legend(fontsize=11, markerscale=3)
    ax.set_xlabel("PCA 1", fontsize=11)
    ax.set_ylabel("PCA 2", fontsize=11)
    ax.set_title(f"CVAE Latent Space coloured by '{color_by}'",
                 fontsize=13, fontweight='bold')
    ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    plt.show()
    return lat_2d, labels


def manipulate_attribute(model, X_test_np, attrs_test_np, attr_names,
                         idx, attr_to_change, latent_dim=128):
    """
    Encode a face, decode with a flipped attribute to show attribute manipulation.

    Parameters
    ----------
    idx             : index of test image
    attr_to_change  : attribute name to flip (e.g. "Smiling")
    """
    model.eval()
    attr_idx = attr_names.index(attr_to_change)

    with torch.no_grad():
        x = torch.tensor(X_test_np[idx:idx+1]).to(DEVICE)
        a_orig = torch.tensor(attrs_test_np[idx:idx+1]).to(DEVICE)
        mu, _ = model.encode(x, a_orig)

        # Decode with original attributes
        recon_orig = model.decode(mu, a_orig).cpu().numpy()[0]

        # Decode with flipped attribute
        a_flip = a_orig.clone()
        a_flip[:, attr_idx] = 1.0 - a_flip[:, attr_idx]
        recon_flip = model.decode(mu, a_flip).cpu().numpy()[0]

    orig_val = int(attrs_test_np[idx, attr_idx])
    new_val = 1 - orig_val

    fig, axes = plt.subplots(1, 3, figsize=(10, 3.5))
    fig.suptitle(f"Attribute Manipulation: {attr_to_change} ({orig_val} -> {new_val})",
                 fontsize=13, fontweight='bold')

    axes[0].imshow(np.clip(X_test_np[idx].transpose(1, 2, 0), 0, 1))
    axes[0].set_title("Original"); axes[0].axis('off')
    axes[1].imshow(np.clip(recon_orig.transpose(1, 2, 0), 0, 1))
    axes[1].set_title("Reconstructed"); axes[1].axis('off')
    axes[2].imshow(np.clip(recon_flip.transpose(1, 2, 0), 0, 1))
    axes[2].set_title(f"{attr_to_change} = {new_val}"); axes[2].axis('off')

    plt.tight_layout()
    plt.show()


def train_attribute_predictor(model_cls, X_np, attrs_np, epochs=10, batch_size=64):
    """
    Train a CelebAAttributePredictor on images and binary attributes.

    Parameters
    ----------
    model_cls : the predictor class (e.g. CelebAAttributePredictor)
    X_np      : images, shape (N, 3, 64, 64)
    attrs_np  : attributes, shape (N, 40), float32
    """
    model = model_cls().to(DEVICE)
    X_t = torch.tensor(X_np).to(DEVICE)
    a_t = torch.tensor(attrs_np).to(DEVICE)
    loader = DataLoader(TensorDataset(X_t, a_t), batch_size=batch_size, shuffle=True)
    opt = optim.Adam(model.parameters())
    loss_fn = nn.BCEWithLogitsLoss()
    model.train()
    for ep in range(1, epochs + 1):
        total_loss, n = 0.0, 0
        for xb, ab in loader:
            opt.zero_grad()
            loss = loss_fn(model(xb), ab)
            loss.backward()
            opt.step()
            total_loss += loss.item() * xb.size(0)
            n += xb.size(0)
        if ep % 3 == 0 or ep == 1:
            print(f"  Predictor epoch {ep}/{epochs} -- BCE: {total_loss / n:.4f}")
    print("Attribute predictor trained!")
    return model


def evaluate_generated_celeba(model, predictor, attr_names, latent_dim=128,
                              n_samples=1000):
    """
    Generate CelebA images with random attribute combos, classify them with
    the predictor, and report per-attribute accuracy.
    """
    model.eval()
    predictor.eval()

    # Use random binary attribute vectors
    attrs_np = (np.random.rand(n_samples, len(attr_names)) > 0.5).astype("float32")
    attrs_t = torch.tensor(attrs_np).to(DEVICE)

    with torch.no_grad():
        z = torch.randn(n_samples, latent_dim).to(DEVICE) * 0.75
        gen_imgs = model.decode(z, attrs_t)
        preds = torch.sigmoid(predictor(gen_imgs)).cpu().numpy()

    preds_binary = (preds > 0.5).astype("float32")
    per_attr_acc = np.mean(preds_binary == attrs_np, axis=0)
    mean_acc = np.mean(per_attr_acc)

    print(f"\nMean per-attribute accuracy: {mean_acc:.2%}")
    print(f"\nTop-5 best generated attributes:")
    sorted_idx = np.argsort(per_attr_acc)[::-1]
    for i in sorted_idx[:5]:
        print(f"  {attr_names[i]:25s} {per_attr_acc[i]:.2%}")
    print(f"\nTop-5 worst generated attributes:")
    for i in sorted_idx[-5:]:
        print(f"  {attr_names[i]:25s} {per_attr_acc[i]:.2%}")

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.bar(range(len(attr_names)), per_attr_acc[sorted_idx],
           color='steelblue', edgecolor='black')
    ax.set_xticks(range(len(attr_names)))
    ax.set_xticklabels([attr_names[i] for i in sorted_idx],
                       rotation=90, fontsize=8)
    ax.set_ylabel("Accuracy", fontsize=12)
    ax.set_title("Per-Attribute Classification Accuracy on Generated Images",
                 fontsize=13, fontweight='bold')
    ax.axhline(y=mean_acc, color='crimson', linestyle='--', label=f'Mean: {mean_acc:.2%}')
    ax.legend(fontsize=11)
    plt.tight_layout()
    plt.show()

    return per_attr_acc


def beta_sweep_grid_generate(beta_models, beta_configs, attr_names, latent_dim=128,
                             target_attrs=None, n_samples=6, seed=0):
    """
    Generation grid: compare beta values using shared random z vectors (no encoder).

    Parameters
    ----------
    beta_models   : dict mapping beta (float) -> trained CelebAConvCVAE
    beta_configs  : list of (beta, name) tuples, defines row order
    attr_names    : list of 40 attribute name strings
    latent_dim    : latent space dimensionality
    target_attrs  : dict like {"Smiling": 1, "Young": 1}; defaults to {"Smiling": 1, "Young": 1}
    n_samples     : number of columns (faces per beta)
    seed          : random seed for z sampling — change to explore different faces
    """
    if target_attrs is None:
        target_attrs = {"Smiling": 1, "Young": 1}

    torch.manual_seed(seed)
    z_shared = torch.randn(n_samples, latent_dim).to(DEVICE) * 0.75
    attrs_shared = torch.zeros(n_samples, len(attr_names)).to(DEVICE)
    for name, val in target_attrs.items():
        attrs_shared[:, attr_names.index(name)] = float(val)

    fig, axes = plt.subplots(len(beta_configs), n_samples,
                             figsize=(2.5 * n_samples, 3 * len(beta_configs)))
    fig.suptitle(f'Beta sweep (generation) — attributes: {target_attrs}',
                 fontsize=14, fontweight='bold')

    for row, (beta, _name) in enumerate(beta_configs):
        model = beta_models[beta]
        model.eval()
        with torch.no_grad():
            imgs = model.decode(z_shared, attrs_shared).cpu().numpy()
        for col in range(n_samples):
            axes[row, col].imshow(np.clip(imgs[col].transpose(1, 2, 0), 0, 1))
            axes[row, col].axis('off')
        axes[row, 0].set_ylabel(f'β={beta}', fontsize=11, fontweight='bold',
                                rotation=0, labelpad=50)

    plt.tight_layout()
    plt.show()


def beta_sweep_grid_reconstruct(beta_models, beta_configs, X_test_np, attrs_test_np,
                                attr_names, n_samples=6, seed=0):
    """
    Reconstruction grid: encode the same real images through each beta model and decode.

    Parameters
    ----------
    beta_models   : dict mapping beta (float) -> trained CelebAConvCVAE
    beta_configs  : list of (beta, name) tuples, defines row order
    X_test_np     : test images (N, 3, 64, 64) float32
    attrs_test_np : test attributes (N, 40) float32
    attr_names    : list of 40 attribute name strings
    n_samples     : number of columns (images to reconstruct)
    seed          : random seed to select which test images to use
    """
    rng = np.random.default_rng(seed)
    indices = rng.choice(len(X_test_np), size=n_samples, replace=False)

    x = torch.tensor(X_test_np[indices]).to(DEVICE)
    a = torch.tensor(attrs_test_np[indices]).to(DEVICE)

    fig, axes = plt.subplots(len(beta_configs) + 1, n_samples,
                             figsize=(2.5 * n_samples, 3 * (len(beta_configs) + 1)))
    fig.suptitle('Beta sweep (reconstruction)', fontsize=14, fontweight='bold')

    # First row: originals
    for col in range(n_samples):
        axes[0, col].imshow(np.clip(X_test_np[indices[col]].transpose(1, 2, 0), 0, 1))
        axes[0, col].axis('off')
    axes[0, 0].set_ylabel('Original', fontsize=11, fontweight='bold',
                           rotation=0, labelpad=50)

    for row, (beta, _name) in enumerate(beta_configs):
        model = beta_models[beta]
        model.eval()
        with torch.no_grad():
            mu, _ = model.encode(x, a)
            imgs = model.decode(mu, a).cpu().numpy()
        for col in range(n_samples):
            axes[row + 1, col].imshow(np.clip(imgs[col].transpose(1, 2, 0), 0, 1))
            axes[row + 1, col].axis('off')
        axes[row + 1, 0].set_ylabel(f'β={beta}', fontsize=11, fontweight='bold',
                                    rotation=0, labelpad=50)

    plt.tight_layout()
    plt.show()
