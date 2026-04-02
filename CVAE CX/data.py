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


def load_celeba(root="./data", max_samples=30000):
    """
    Downloads CelebA and returns numpy arrays normalised to [0, 1].

    Parameters
    ----------
    root        : download directory
    max_samples : cap on training images to fit in Colab RAM (~1.5 GB at 30 k)

    Returns
    -------
    X_train, attrs_train, X_test, attrs_test
        Images  : (N, 3, 64, 64) float32 in [0, 1]
        Attrs   : (N, 40)        float32 with values 0.0 / 1.0
    """
    transform = transforms.Compose([
        transforms.CenterCrop(178),
        transforms.Resize(64),
        transforms.ToTensor(),
    ])

    train_set = datasets.CelebA(root=root, split="train",
                                target_type="attr", download=True,
                                transform=transform)
    test_set = datasets.CelebA(root=root, split="test",
                               target_type="attr", download=True,
                               transform=transform)

    def _extract(dataset, n):
        n = min(n, len(dataset))
        imgs, attrs = [], []
        loader = torch.utils.data.DataLoader(dataset, batch_size=256,
                                             shuffle=False, num_workers=2)
        count = 0
        for x_batch, a_batch in loader:
            take = min(x_batch.size(0), n - count)
            imgs.append(x_batch[:take].numpy())
            attrs.append(a_batch[:take].numpy())
            count += take
            if count >= n:
                break
        imgs = np.concatenate(imgs, axis=0).astype("float32")
        attrs = np.concatenate(attrs, axis=0).astype("float32")
        # torchvision CelebA attrs are 0/1 already (older versions used -1/1)
        attrs = np.clip(attrs, 0, 1)
        return imgs, attrs

    X_train, attrs_train = _extract(train_set, max_samples)
    X_test, attrs_test = _extract(test_set, min(max_samples // 3, len(test_set)))

    print(f"Training images : {X_train.shape}  -> {len(X_train):,} images of 64x64x3")
    print(f"Test images     : {X_test.shape}   -> {len(X_test):,} images of 64x64x3")
    print(f"Attributes      : {attrs_train.shape[1]} binary attributes per image")

    return X_train, attrs_train, X_test, attrs_test
