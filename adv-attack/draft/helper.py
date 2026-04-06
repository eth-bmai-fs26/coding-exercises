"""helper.py — Utility functions for the Adversarial Attacks coding exercise.

Intentionally kept separate so that notebooks stay focused on concepts,
not boilerplate.  Students should not need to modify this file.
"""

import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf

_C = {
    "clean":       "#4C72B0",
    "adversarial": "#C44E52",
    "robust":      "#55A868",
}
plt.rcParams.update({
    "figure.facecolor": "#fafafa",
    "axes.facecolor":   "#fafafa",
    "axes.spines.top":  False,
    "axes.spines.right": False,
})


def build_model():
    """Build and compile a small MLP for MNIST (28×28×1 → 10 classes)."""
    model = tf.keras.Sequential([
        tf.keras.layers.Flatten(input_shape=(28, 28, 1)),
        tf.keras.layers.Dense(256, activation="relu"),
        tf.keras.layers.Dense(128, activation="relu"),
        tf.keras.layers.Dense(10,  activation="softmax"),
    ])
    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def compute_gradient(image, label, model):
    """Return ∇_image L(model(image), label) via automatic differentiation.

    Uses tf.GradientTape to record the forward pass and differentiate the
    categorical cross-entropy loss with respect to the input image tensor.
    """
    image = tf.cast(image, tf.float32)
    with tf.GradientTape() as tape:
        tape.watch(image)
        pred = model(image, training=False)
        loss = tf.keras.losses.categorical_crossentropy(label, pred)
    return tape.gradient(loss, image)


def print_epoch_stats(epoch, total, model, images, labels, fgsm_fn, epsilon):
    """Print clean and adversarial accuracy on the evaluation set after each epoch."""
    true = np.argmax(labels.numpy(), axis=1)

    clean_preds = np.argmax(model(images, training=False).numpy(), axis=1)
    clean_acc   = (clean_preds == true).mean()

    adv_imgs  = fgsm_fn(images, labels, model, epsilon)
    adv_preds = np.argmax(model(adv_imgs, training=False).numpy(), axis=1)
    adv_acc   = (adv_preds == true).mean()

    print(f"  \u21b3 clean: {clean_acc:.1%}  |  adv (\u03b5={epsilon}): {adv_acc:.1%}\n")


def plot_adversarial_examples(model, images, labels, fgsm_fn, epsilon, n=6):
    """Display n original vs adversarial image pairs with model predictions.

    Each column shows one image: original on top, adversarial on bottom.
    A red prediction title means the attack succeeded (model was fooled).
    """
    imgs  = images[:n]
    lbls  = labels[:n]
    adv   = fgsm_fn(imgs, lbls, model, epsilon)

    true   = np.argmax(lbls.numpy(), axis=1)
    o_pred = np.argmax(model(imgs, training=False).numpy(), axis=1)
    a_pred = np.argmax(model(adv,  training=False).numpy(), axis=1)

    fig, axes = plt.subplots(2, n, figsize=(2.4 * n, 5), facecolor="#fafafa")
    for i in range(n):
        axes[0, i].imshow(imgs[i].numpy().squeeze(), cmap="gray_r", vmin=0, vmax=1)
        axes[0, i].set_title(f"label: {true[i]}", fontsize=9, color=_C["clean"])
        axes[0, i].axis("off")

        axes[1, i].imshow(adv[i].numpy().squeeze(), cmap="gray_r", vmin=0, vmax=1)
        fooled = a_pred[i] != true[i]
        color  = _C["adversarial"] if fooled else _C["clean"]
        axes[1, i].set_title(f"pred: {a_pred[i]}", fontsize=9, color=color)
        axes[1, i].axis("off")

    axes[0, 0].set_ylabel("Original", fontsize=11)
    axes[1, 0].set_ylabel(f"Adversarial\n(\u03b5={epsilon})", fontsize=11)
    n_fooled = (a_pred != true).sum()
    plt.suptitle(
        f"FGSM (\u03b5={epsilon}) \u2014 {n_fooled}/{n} predictions changed  (red\u00a0=\u00a0attack succeeded)",
        fontsize=12, y=1.02, color=_C["adversarial"],
    )
    plt.tight_layout()
    plt.show()


def plot_accuracy_vs_epsilon(model, images, labels, fgsm_fn, epsilons):
    """Plot how accuracy degrades as the perturbation strength \u03b5 increases."""
    true = np.argmax(labels.numpy(), axis=1)
    accs = []
    for eps in epsilons:
        adv   = fgsm_fn(images, labels, model, eps)
        preds = np.argmax(model(adv, training=False).numpy(), axis=1)
        accs.append((preds == true).mean())

    plt.figure(figsize=(7, 4), facecolor="#fafafa")
    plt.plot(epsilons, accs, "o-", color=_C["adversarial"], lw=2, ms=7,
             label="Adversarial accuracy")
    plt.axhline(accs[0], color=_C["clean"], ls="--", lw=1.5,
                label=f"Clean (\u03b5\u00a0=\u00a00): {accs[0]:.1%}")
    plt.xlabel("\u03b5  (perturbation strength)")
    plt.ylabel("Accuracy")
    plt.title("FGSM: accuracy vs. perturbation strength")
    plt.ylim(0, 1.05)
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_robustness_comparison(std_model, rob_model, images, labels, fgsm_fn, epsilons):
    """Compare standard vs adversarially trained model across \u03b5 values."""
    true = np.argmax(labels.numpy(), axis=1)
    std_accs, rob_accs = [], []
    for eps in epsilons:
        for accs, m in [(std_accs, std_model), (rob_accs, rob_model)]:
            adv = fgsm_fn(images, labels, m, eps)
            p   = np.argmax(m(adv, training=False).numpy(), axis=1)
            accs.append((p == true).mean())

    plt.figure(figsize=(8, 4.5), facecolor="#fafafa")
    plt.plot(epsilons, std_accs, "o--", color=_C["adversarial"], lw=2,
             label="Standard model (no defence)")
    plt.plot(epsilons, rob_accs, "o-",  color=_C["robust"],      lw=2,
             label="Robust model (adversarially trained)")
    plt.xlabel("\u03b5  (perturbation strength)")
    plt.ylabel("Adversarial accuracy")
    plt.title("Standard vs. Robust Model: Adversarial Accuracy")
    plt.ylim(0, 1.05)
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()
