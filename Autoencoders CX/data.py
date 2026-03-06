import numpy as np
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

    print(f"Training images : {X_train.shape}  → {len(X_train):,} images of 28×28 pixels")
    print(f"Test images     : {X_test.shape}   → {len(X_test):,} images of 28×28 pixels")
    print(f"Digit classes   : {np.unique(y_train)}")

    return X_train, y_train, X_test, y_test