from itertools import product
import numpy as np
import logging


def sub_sampling_discerete_choices(name, Xt, St, n_objects=5):
    logger = logging.getLogger(name=name)
    bucket_size = int(Xt.shape[1] / n_objects)
    logger.info("###### X instances {} objects {} bucket_size {} ######".format(Xt.shape[0], Xt.shape[1], bucket_size))
    X_train = []
    Y_train = []
    for i in range(bucket_size):
        X = np.copy(Xt)
        S = np.copy(St)
        rs = np.random.RandomState(42 + i)
        idx = rs.randint(bucket_size, size=(len(X), n_objects))
        idx += np.arange(start=0, stop=X.shape[1], step=bucket_size)[:n_objects]
        X = X[np.arange(X.shape[0])[:, None], idx]
        S = S[np.arange(X.shape[0])[:, None], idx]
        Y = S.argmax(axis=1)
        if len(X_train) == 0:
            X_train = X
            Y_train = Y
        else:
            Y_train = np.concatenate([Y_train, Y], axis=0)
            X_train = np.concatenate([X_train, X], axis=0)
    logger.info("Sampled instances {} objects {}".format(X_train.shape[0], X_train.shape[1]))
    return X_train, Y_train


def generate_pairwise_instances(x, choice):
    pairs = np.array(list(product(x, choice[None, :])))
    n_pairs = len(pairs)
    neg_indices = np.arange(0, n_pairs, 2)
    a, b = np.copy(pairs[neg_indices, 0]), np.copy(pairs[neg_indices, 1])
    pairs[neg_indices, 1] = a
    pairs[neg_indices, 0] = b

    X1 = pairs[:, 0]
    X2 = pairs[:, 1]
    Y_double = np.ones([n_pairs, 1]) * np.array([1, 0])
    Y_single = np.repeat(1, n_pairs)

    Y_double[neg_indices] = [0, 1]
    Y_single[neg_indices] = 0
    return X1, X2, Y_double, Y_single


def generate_complete_pairwise_dataset(X, Y):
    Y_double = []
    X1 = []
    X2 = []
    Y_single = []
    choices = X[np.arange(X.shape[0]), Y]
    for x, choice in zip(X, choices):
        x1, x2, y1, y2 = generate_pairwise_instances(x, choice)
        X1.extend(x1)
        X2.extend(x2)
        Y_double.extend(y1)
        Y_single.extend(y2)
    X1 = np.array(X1)
    X2 = np.array(X2)
    Y_double = np.array(Y_double)
    Y_single = np.array(Y_single)
    return X1, X2, Y_double, Y_single
