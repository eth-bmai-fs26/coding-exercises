# Autoencoders In-Class Exercise

A hands-on notebook introducing autoencoders, denoising autoencoders, and latent space visualisation using MNIST.

## Getting Started (Google Colab)

1. Open `Autoencoders_student.ipynb` in Google Colab
2. Run the first two setup cells — they clone this repo and import all helpers
3. Work through the notebook top to bottom

> **Tip:** Enable GPU in Colab → Runtime → Change runtime type → T4 GPU. Training will be ~5× faster.

## Repository Structure

```
autoencoders-lab/
├── Autoencoders_student.ipynb   ← start here
├── models.py                    ← ConvAutoencoder, MNISTClassifier (complete encode/decode/forward)
├── utils.py                     ← training loop, reconstruct(), plotting helpers (complete TODOs)
├── data.py                      ← MNIST loading, add_noise() (complete the TODO)
└── README.md
```

## TODO Summary

There are **5 TODOs** to complete — all in the `.py` helper files, guided by the notebook:

| # | File | What to implement |
|---|------|-------------------|
| 1a | `models.py` | `encode()` — encoder forward pass |
| 1b | `models.py` | `decode()` — decoder forward pass |
| 1c | `models.py` | `forward()` — chain encode + decode |
| 2  | `utils.py`  | Training step: loss, backward, optimizer step |
| 3  | `utils.py`  | `reconstruct()` — inference with `no_grad` |
| 4  | `data.py`   | `add_noise()` — Gaussian noise + clip |
| 5  | Notebook    | Configure denoising AE training call |

Plus **3 open-ended exercises** in the notebook itself (per-digit MSE, latent space centroids, head-to-head comparison).
