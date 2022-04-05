import copy
import numpy as np
import matplotlib.pyplot as plt
# don't add any other packages


# data simulator and testing function (Don't change them)
def polynomial_data_simulator(n_train: int = 50,
                              n_test: int = 10,
                              order: int = 5,
                              v_noise: float = 1,
                              r_seed: int = 42) -> dict:
    """
    Simulate the training and testing data generated by a polynomial model
    :param n_train: the number of training data
    :param n_test: the number of testing data
    :param order: the order of the polynomial function
    :param v_noise: the variance of noise
    :param r_seed: the random seed
    :return:
        a dictionary containing training set, testing set, and the ground truth parameters
    """
    x_train = 4 * (np.random.RandomState(r_seed).rand(n_train) - 0.5)
    X_train = np.array([x_train ** d for d in range(order)]).T
    x_test = 5 * (np.random.RandomState(r_seed).rand(n_test) - 0.5)
    X_test = np.array([x_test ** d for d in range(order)]).T
    weights = np.random.RandomState(r_seed).randn(order, 1)
    y_train = X_train @ weights + v_noise * np.random.RandomState(r_seed).randn(n_train, 1)
    y_test = X_test @ weights + v_noise * np.random.RandomState(r_seed).randn(n_test, 1)
    data = {'train': [np.expand_dims(x_train, axis=1), y_train],
            'test': [np.expand_dims(x_test, axis=1), y_test],
            'real': weights}
    return data


def visualization_curves(weights: np.ndarray, label: str, curve_type: str):
    landmarks = 5 * (np.arange(0, 100) / 100 - 0.5)
    order = weights.shape[0]
    curve = np.array([landmarks ** d for d in range(order)]).T @ weights
    plt.plot(landmarks, curve, curve_type, label=label)


def visualization_points(x: np.ndarray, y: np.ndarray, label: str, point_type: str):
    plt.plot(x, y, point_type, label=label)


def visualization_kernel_curves(alpha: np.ndarray, x_train: np.ndarray,
                                k_type: str, h: float, label: str, curve_type: str, normalize: bool = False):
    landmarks = 5 * (np.arange(0, 100) / 100 - 0.5)
    kappa = kernel(x=x_train, y=np.expand_dims(landmarks, axis=1), k_type=k_type, bandwidth=h)
    if normalize:
        curve = (kappa / np.sum(kappa + 1e-10, axis=1, keepdims=True)) @ alpha
    else:
        curve = kappa @ alpha
    plt.plot(landmarks, curve, curve_type, label=label)


def mse(x: np.ndarray, x_est: np.ndarray) -> float:
    return np.sum((x - x_est) ** 2) / x.shape[0]


# Task 1: Implement typical valid kernel functions and the Nadaraya–Watson estimator
def kernel(x: np.ndarray, y: np.ndarray = None, k_type: str = 'rbf', bandwidth: float = 'h') -> np.ndarray:
    """
    Implement four kinds of typical kernel functions
    1) RBF kernel: k(x, y) = exp(-||x - y||_2^2 / bandwidth)
    2) 'Gate' kernel: k(x, y) = 1/bandwidth if ||x - y||_1 <= bandwidth, = 0 otherwise
    3) 'Triangle' kernel: k(x, y) = (bandwidth - ||x - y||_1) if ||x - y||_1 <= bandwidth, = 0 otherwise
    4) Linear kernel: k(x, y) = <x, y>
    :param x: a set of samples with size (N, D), where N is the number of samples, D is the dimension of features
    :param y: a set of samples with size (M, D), where M is the number of samples. this input can be None
    :param k_type: the type of kernels, including 'rbf', 'gate', 'triangle', 'linear'
    :param bandwidth: the hyperparameter controlling the width of rbf/gate/triangle kernels
    :return:
        if y = None, return a matrix with size (N, N)
        otherwise, return a matrix with size (M, N)
    """
    if y is None:
        y = copy.deepcopy(x)
    # TODO: Change the code below and implement the four kinds of kernel functions mentioned in the above comments.
    K = np.zeros((y.shape[0], x.shape[0]))
    if k_type == 'rbf':
        for i in range(y.shape[0]):
            for j in range(x.shape[0]):
                K[i, j] = np.e**(-(np.linalg.norm(y[i] - x[j], 2)**2 / bandwidth))
    elif k_type == 'gate':
        for i in range(y.shape[0]):
            for j in range(x.shape[0]):
                if np.linalg.norm(y[i] - x[j], 1) <= bandwidth:
                    K[i, j] = 1/bandwidth
                else:
                    K[i, j] = 0
    elif k_type == 'triangle':
        for i in range(y.shape[0]):
            for j in range(x.shape[0]):
                if np.linalg.norm(y[i] - x[j], 1) <= bandwidth:
                    K[i, j] = 1 - np.e**(-(np.linalg.norm(y[i] - x[j], 2)**2 / bandwidth))
                    K[i, j] = 2*K[i, j] / bandwidth
                else:
                    K[i, j] = 0
    elif k_type == 'linear':
        for i in range(y.shape[0]):
            for j in range(x.shape[0]):
                K[i, j] = x[j].T @ y[i]
    return K

def nadaraya_watson_estimator(x_test: np.ndarray, x_train: np.ndarray, y_train: np.ndarray, k_type: str, h: float) -> np.ndarray:
    """
    Implement the Nadaraya-Watson estimator:

    y_test = sum_{n=1}^{N} kappa_h(x_test - x_n) / sum_{i=1}^{N} kappa_h(x)

    :param x_test: the input data of testing set, with size (M, D)
    :param x_train: the input data in the training set, with size (N, D)
    :param y_train: the label/output data in the training set, with size (N, 1)
    :param k_type: the type of kernel, default is 'rbf', and other options include 'gate', 'triangle', 'linear'
    :param h: the hyperparameter controlling the width of rbf/gate/triangle kernels
    :return:
        the estimation of y_test with size (M, 1)
    """
    # TODO: Change the code below and implement the NW-estimator based on specific kernel functions
    result = np.zeros((x_test.shape[0], 1))
    estimator = kernel(x_train, x_test, k_type=k_type, bandwidth=h)
    for i in range(x_test.shape[0]):
        sum = estimator[i].sum()
        if sum == 0:
            # result[i] = estimator[i] @ y_train
            estimator[i] = estimator[i] + 0.01
        result[i] = (estimator[i]/estimator[i].sum()) @ y_train
        # print(estimator, estimator.shape)
    return result

# Task 2: Implement the training and the testing method of Kernel Ridge Regression method.
def training_krr(x_train: np.ndarray, y_train: np.ndarray, k_type: str, h: float, tau: float = 0.1) -> np.ndarray:
    """
    The training method of kernel ridge regression (KRR)

    min_{a} ||y - Ka||_2^2 + tau * a^T K a

    :param x_train: the input data in the training set, with size (N, D)
    :param y_train: the label/output data in the training set, with size (N, 1)
    :param k_type: the type of kernel, default is 'rbf', and other options include 'gate', 'triangle', and 'linear'
    :param h: the hyperparameter controlling the width of rbf/gate/triangle kernels
    :param tau: the hyperparameter controlloing the significance of the regularizer
    :return:
        the weights associated with the training data, with size (N, 1)
    """
    # TODO: Change the code below and implement the closed form solution of kernel ridge regression
    #   Hint: Use as few computations as possible
    K = kernel(x_train, x_train, k_type=k_type, bandwidth=h)
    a = np.linalg.pinv(tau*K + K@K)@K@y_train
    # a = np.linalg.pinv(tau + K) @ y_train
    return a

def testing_krr(x_test: np.ndarray, x_train: np.ndarray, alpha: np.ndarray, k_type: str, h: float) -> np.ndarray:
    """
    Testing a learned kernel ridge regression model
    :param x_test: the input data of testing set, with size (M, D)
    :param x_train: the input data in the training set, with size (N, D)
    :param alpha: the learned KRR model, with size (N, 1)
    :param k_type: the type of kernel, default is 'rbf', and other options include 'gate', 'triangle', and 'linear'
    :param h: the hyperparameter controlling the width of rbf/gate/triangle kernels
    :return:
        y_test, the estimated output with size (M, 1)
    """
    # TODO: Change the code below and implement the prediction method of kernel ridge regression
    K = kernel(x_train, x_test, bandwidth=h, k_type=k_type)
    result = np.zeros((x_test.shape[0], 1))
    for i in range(x_test.shape[0]):
        result[i] = K[i] @ alpha
    return result




# Task 3: Try to learn the KRR model via the stochastic gradient descent (sgd) algorithm,
# and CHECK WHETHER it works or not:) and try to make it work as much as possible
def training_krr_sgd(x_train: np.ndarray,
                     y_train: np.ndarray,
                     k_type: str,
                     h: float,
                     tau: float = 0.1,
                     epoch: int = 11,
                     batch_size: int = 10,
                     lr: float = 5e-4,
                     r_seed: int = 1) -> np.ndarray:
    """
    The stochastic gradient descent method of kernel ridge regression.

    :param x_train: the input data in the training set, with size (N, D)
    :param y_train: the label/output data in the training set, with size (N, 1)
    :param k_type: the type of kernel, default is 'rbf', and other options include 'gate', 'triangle', and 'linear'
    :param h: the hyperparameter controlling the width of rbf/gate/triangle kernels
    :param tau: the hyperparameter controlling the significance of the regularizer
    :param epoch: the number of epochs
    :param batch_size: the batch size for sgd
    :param lr: the learning rate
    :param r_seed: random seed to initialize model parameters
    :return:
        the weights associated with the training data, with size (N, 1)
    """
    # TODO: Change the code below and try to implement a SGD algorithm for kernel ridge regression
    #  Hint 1: Think about the rationality of this SGD method based on your implementation and the corresponding results
    #  Hint 2: If your result is not good, try to adjust the hyperparameters (lr, tau, epoch) by yourself.
    alpha = np.random.RandomState(r_seed).randn(y_train.shape[0], 1)
    K = kernel(x_train, x_train, bandwidth=h, k_type=k_type)
    for i in range(epoch):
        index = [k for k in range(x_train.shape[0])]
        np.random.RandomState(r_seed).shuffle(index)
        K = K[index]
        y = y_train[index]
        for j in range(int(x_train.shape[0] / batch_size)):
            if j == int(x_train.shape[0] / batch_size) - 1 and (j+1) * batch_size < x_train.shape[0]:
                K_batch = K[j:x_train.shape[0]]
                y_batch = y[j:x_train.shape[0]]
            else:
                K_batch = K[j:j+batch_size]
                y_batch = y[j:j+batch_size]
            diff_a = 2 * K_batch.T @ (K_batch @ alpha - y_batch) + 2*tau*(K @ alpha)
            # dont forget to devide the batch_size
            alpha -= lr * diff_a / batch_size
            
    return alpha

# Testing script
if __name__ == '__main__':
    data = polynomial_data_simulator()
    kernel_types = ['linear','rbf', 'gate', 'triangle']
    bandwidths = [0.1, 1, 2, 5]
    for k in range(len(kernel_types)):
        for i in range(len(bandwidths)):
            ker_type = kernel_types[k]
            bw = bandwidths[i]
            y_est0 = nadaraya_watson_estimator(x_test=data['test'][0],
                                               x_train=data['train'][0],
                                               y_train=data['train'][1],
                                               k_type=ker_type, h=bw)
            alpha1 = training_krr(x_train=data['train'][0], y_train=data['train'][1], k_type=ker_type, h=bw)
            y_est1 = testing_krr(x_test=data['test'][0], x_train=data['train'][0], alpha=alpha1, k_type=ker_type, h=bw)
            alpha2 = training_krr_sgd(x_train=data['train'][0], y_train=data['train'][1], k_type=ker_type, h=bw)
            y_est2 = testing_krr(x_test=data['test'][0], x_train=data['train'][0], alpha=alpha2, k_type=ker_type, h=bw)

            mse0 = mse(data['test'][1], y_est0)
            mse1 = mse(data['test'][1], y_est1)
            mse2 = mse(data['test'][1], y_est2)

            setting = 'Kernel={}, Bandwidth={:.2f}'.format(
                ker_type, bw)
            result = 'NWKR: MSE={:.4f}, KRR: MSE={:.4f}, KRR-sgd: MSE={:.4f}'.format(
                mse0, mse1, mse2)
            print(setting + ' ' + result)

            plt.figure()
            visualization_points(x=data['train'][0], y=data['train'][1][:, 0], point_type='bx', label='training data')
            visualization_points(x=data['test'][0], y=data['test'][1][:, 0], point_type='kx', label='testing data')
            visualization_curves(weights=data['real'], label='ground truth', curve_type='r-')
            visualization_kernel_curves(alpha=data['train'][1], x_train=data['train'][0],
                                        k_type=ker_type, h=bw, label='nwk', curve_type='g-', normalize=True)
            visualization_kernel_curves(alpha=alpha1, x_train=data['train'][0],
                                        k_type=ker_type, h=bw, label='krr', curve_type='b-')
            visualization_kernel_curves(alpha=alpha2, x_train=data['train'][0],
                                        k_type=ker_type, h=bw, label='krr-sgd', curve_type='k:')
            plt.title(result)
            plt.xlabel(setting)
            plt.legend()
            plt.savefig('result_{}_{}.png'.format(k, i))
            plt.close('all')