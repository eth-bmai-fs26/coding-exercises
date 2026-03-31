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
