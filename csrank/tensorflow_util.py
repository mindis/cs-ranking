import inspect
import logging
import multiprocessing
import os

import numpy as np
import tensorflow as tf
from keras import backend as K
from tensorflow.python.client import device_lib

from csrank.util import create_dir_recursively


def scores_to_rankings(n_objects, y_pred):
    # indices = orderings
    toprel, orderings = tf.nn.top_k(y_pred, n_objects)
    # indices = rankings
    troprel, rankings = tf.nn.top_k(orderings, n_objects)
    rankings = K.cast(rankings[:, ::-1], dtype='float32')
    return rankings


def get_instances_objects(y_true):
    n_objects = K.cast(K.int_shape(y_true)[1], 'int32')
    total = K.cast(K.greater_equal(y_true, 0), dtype='int32')
    n_instances = K.cast(tf.reduce_sum(total) / n_objects, dtype='int32')
    return n_instances, n_objects


def tensorify(x):
    """Converts x into a Keras tensor"""
    if not isinstance(x, (tf.Tensor, tf.Variable)):
        return K.constant(x)
    return x


def get_tensor_value(x):
    if isinstance(x, tf.Tensor):
        return K.get_value(x)
    return x


def setup_logger(log_path=None):
    """Function setup as many loggers as you want"""
    if log_path is None:
        dirname = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        dirname = os.path.dirname(dirname)
        log_path = os.path.join(dirname, "experiments", "logs", "logs.log")
        create_dir_recursively(log_path, True)
    logging.basicConfig(filename=log_path, level=logging.DEBUG,
                        format='%(asctime)s %(name)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')


def configure_logging_numpy_keras(seed=42, log_path=None):
    setup_logger(log_path=log_path)
    tf.set_random_seed(seed)
    os.environ["KERAS_BACKEND"] = "tensorflow"
    devices = [x.name for x in device_lib.list_local_devices()]
    logger = logging.getLogger("Configure Keras")
    logger.info("Devices {}".format(devices))
    n_gpus = len([x.name for x in device_lib.list_local_devices() if x.device_type == 'GPU'])
    if n_gpus == 0:
        config = tf.ConfigProto(intra_op_parallelism_threads=1, inter_op_parallelism_threads=1,
                                allow_soft_placement=True, log_device_placement=False,
                                device_count={'CPU': multiprocessing.cpu_count() - 2})
    else:
        config = tf.ConfigProto(allow_soft_placement=True,
                                log_device_placement=True, intra_op_parallelism_threads=2,
                                inter_op_parallelism_threads=2)  # , gpu_options = gpu_options)
    sess = tf.Session(config=config)
    K.set_session(sess)
    np.random.seed(seed)
    logger.info("Number of GPUS {}".format(n_gpus))
    logger.info("log file path: {}".format(log_path))