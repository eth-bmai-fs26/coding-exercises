import numpy as np
import torch
from torchvision import datasets, transforms


def load_mnist():
    """
    Downloads and returns MNIST as numpy float32 arrays normalised to [0, 1].

    Returns
    -------
    X_train, y_train, X_test, y_test
        Images are shape (N, 28, 28); labels are shape (N,).
    """
    transform = transforms.ToTensor()
    train_data = datasets.MNIST(root='./data', train=True,  download=True, transform=transform)
    test_data  = datasets.MNIST(root='./data', train=False, download=True, transform=transform)

    X_train = train_data.data.numpy().astype("float32") / 255.0
    y_train = train_data.targets.numpy()
    X_test  = test_data.data.numpy().astype("float32") / 255.0
    y_test  = test_data.targets.numpy()

    print(f"Training images : {X_train.shape}  -> {len(X_train):,} images of 28x28 pixels")
    print(f"Test images     : {X_test.shape}   -> {len(X_test):,} images of 28x28 pixels")
    print(f"Digit classes   : {np.unique(y_train)}")

    return X_train, y_train, X_test, y_test


def to_one_hot(y, num_classes=10):
    """
    Converts integer labels to one-hot encoded float32 numpy arrays.

    Parameters
    ----------
    y           : numpy array of shape (N,) with integer labels
    num_classes : number of classes (default 10 for MNIST)

    Returns
    -------
    one_hot : numpy array of shape (N, num_classes), dtype float32
    """
    one_hot = np.zeros((len(y), num_classes), dtype="float32")
    one_hot[np.arange(len(y)), y] = 1.0
    return one_hot


# -- CelebA -------------------------------------------------------------------

CELEBA_ATTR_NAMES = [
    "5_o_Clock_Shadow", "Arched_Eyebrows", "Attractive", "Bags_Under_Eyes",
    "Bald", "Bangs", "Big_Lips", "Big_Nose", "Black_Hair", "Blond_Hair",
    "Blurry", "Brown_Hair", "Bushy_Eyebrows", "Chubby", "Double_Chin",
    "Eyeglasses", "Goatee", "Gray_Hair", "Heavy_Makeup", "High_Cheekbones",
    "Male", "Mouth_Slightly_Open", "Mustache", "Narrow_Eyes", "No_Beard",
    "Oval_Face", "Pale_Skin", "Pointy_Nose", "Receding_Hairline",
    "Rosy_Cheeks", "Sideburns", "Smiling", "Straight_Hair", "Wavy_Hair",
    "Wearing_Earrings", "Wearing_Hat", "Wearing_Lipstick", "Wearing_Necklace",
    "Wearing_Necktie", "Young",
]


def load_celeba(max_samples=30000):
    """
    Downloads CelebA via HuggingFace datasets and returns numpy arrays in [0, 1].

    Uses HuggingFace (tpremoli/CelebA-attrs) instead of torchvision to avoid
    Google Drive quota limits. This dataset includes images + 40 binary
    attributes with proper train/test splits.

    Parameters
    ----------
    max_samples : cap on training images to fit in Colab RAM (~1.5 GB at 30 k)

    Returns
    -------
    X_train, attrs_train, X_test, attrs_test
        Images  : (N, 3, 64, 64) float32 in [0, 1]
        Attrs   : (N, 40)        float32 with values 0.0 / 1.0
    """
    try:
        from datasets import load_dataset
    except ImportError:
        import subprocess, sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "datasets"])
        from datasets import load_dataset

    from PIL import Image

    transform = transforms.Compose([
        transforms.CenterCrop(178),
        transforms.Resize(64),
        transforms.ToTensor(),
    ])

    print("Downloading CelebA from HuggingFace (this may take a few minutes)...")
    ds_train = load_dataset("tpremoli/CelebA-attrs", split="train")
    ds_test = load_dataset("tpremoli/CelebA-attrs", split="test")

    def _extract(dataset, n):
        n = min(n, len(dataset))
        imgs, attrs_list = [], []
        for i in range(n):
            row = dataset[i]
            img = row["image"]
            if not isinstance(img, Image.Image):
                continue
            img_t = transform(img.convert("RGB"))
            imgs.append(img_t.numpy())

            # Extract the 40 attributes in order; convert -1/1 to 0/1
            attr_vec = []
            for attr_name in CELEBA_ATTR_NAMES:
                val = row.get(attr_name, -1)
                attr_vec.append(1.0 if val == 1 else 0.0)
            attrs_list.append(attr_vec)

            if (i + 1) % 5000 == 0:
                print(f"  processed {i + 1:,}/{n:,} images...")

        imgs = np.array(imgs, dtype="float32")
        attrs = np.array(attrs_list, dtype="float32")
        return imgs, attrs

    n_train = min(max_samples, len(ds_train))
    n_test = min(max_samples // 3, len(ds_test))

    print(f"Processing {n_train:,} training images...")
    X_train, attrs_train = _extract(ds_train, n_train)
    print(f"Processing {n_test:,} test images...")
    X_test, attrs_test = _extract(ds_test, n_test)

    print(f"Training images : {X_train.shape}  -> {len(X_train):,} images of 64x64x3")
    print(f"Test images     : {X_test.shape}   -> {len(X_test):,} images of 64x64x3")
    print(f"Attributes      : {attrs_train.shape[1]} binary attributes per image")

    return X_train, attrs_train, X_test, attrs_test
