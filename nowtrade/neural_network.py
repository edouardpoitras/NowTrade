"""
Module that enables the use of neural networks with NowTrade.
"""
import cPickle
import numpy as np
from pybrain.tools.shortcuts import buildNetwork
from pybrain.datasets.supervised import SupervisedDataSet
from pybrain.supervised.trainers.backprop import BackpropTrainer
from nowtrade import logger

# Networks
FEED_FORWARD_NETWORK = 0
RECURRENT_NETWORK = 1

# Datasets
SUPERVISED_DATASET = 0
SEQUENTIAL_DATASET = 1
CLASSIFICATION_DATASET = 2
SEQUENTIAL_CLASSIFICATION_DATASET = 3
IMPORTANCE_DATASET = 4

# Trainers
BACKPROP_TRAINER = 0
RPROP_TRAINER = 1

def load(network, dataset=None):
    """
    Load a previously pickled neural network.
    """
    network = cPickle.loads(network)
    if dataset:
        network.build_network(dataset, new=False)
    return network

def load_from_file(filename, dataset=None):
    """
    Load a neural network from a previous one saved to file.
    """
    file_handler = open(filename, 'rb')
    network = cPickle.load(file_handler)
    file_handler.close()
    if dataset:
        network.build_network(dataset, new=False)
    return network

class InvalidNetworkType(Exception):
    """
    Exception raised when an invalid network type is specified.
    """
    pass
class InvalidTrainerType(Exception):
    """
    Exception raised when an invalid trainer type is specified.
    """
    pass
class InvalidNetworkDatasetType(Exception):
    """
    Exception raised when an invalid network dataset type is specified.
    """
    pass
class InvalidDataset(Exception):
    """
    Exception raised when a invalid dataset is specified.
    """
    pass

class NeuralNetwork(object):
    """
    The neural network class does all the heavy lifting to incorporate pybrain
    neural networks into the NowTrade ecosystem.
    """
    def __init__(self, train_data, prediction_data, network_type=FEED_FORWARD_NETWORK,
                 network_dataset_type=SUPERVISED_DATASET,
                 trainer_type=BACKPROP_TRAINER):
        self.train_data = train_data
        self.prediction_data = prediction_data
        self.network_type = network_type
        self.network_dataset_type = network_dataset_type
        self.trainer_type = trainer_type
        self.network = None
        self.network_dataset = None
        self.dataset = None
        self.trainer = None
        self.trained_iterations = 0
        self.momentum = None
        self.learning_rate = None
        self.hidden_layers = None
        self.prediction_window = None
        self.logger = logger.Logger(self.__class__.__name__)
        self.logger.info('train_data: %s  prediction_data: %s, network_type: %s, \
                          network_dataset_type: %s, trainer_type: %s'
                         %(train_data, prediction_data, network_type, \
                           network_dataset_type, trainer_type))

    def save(self):
        """
        Returns the pickled trained/tested neural network as a string.
        """
        return cPickle.dumps(self)

    def save_to_file(self, filename):
        """
        Saves a neural network to file for later use.

        Look into pybrain.datasets.supervised.SupervisedDataSet.saveToFile()
        http://pybrain.org/docs/api/datasets/superviseddataset.html
        """
        file_handler = open(filename, 'wb')
        cPickle.dump(self, file_handler)
        file_handler.close()

    def build_network(self, dataset, new=True, **kwargs):
        """
        Builds a neural network using the dataset provided.
        Expected keyword args:
            - 'hidden_layers'
            - 'prediction_window'
            - 'learning_rate'
            - 'momentum'
        """
        self.hidden_layers = kwargs.get('hidden_layers', None)
        self.prediction_window = kwargs.get('prediction_window', None)
        self.learning_rate = kwargs.get('learning_rate', None)
        self.momentum = kwargs.get('momentum', None)
        if not new:
            self.network.sorted = False
            self.network.sortModules()
            if self.network_dataset_type == SUPERVISED_DATASET:
                self.ready_supervised_dataset(dataset)
            else: raise InvalidNetworkDatasetType()
        else:
            if self.network_type == FEED_FORWARD_NETWORK:
                self.network = buildNetwork(len(self.train_data), self.hidden_layers, 1)
            else: raise InvalidNetworkType()
            if self.network_dataset_type == SUPERVISED_DATASET:
                self.ready_supervised_dataset(dataset)
            else: raise InvalidNetworkDatasetType()
            if self.trainer_type == BACKPROP_TRAINER:
                self.trainer = BackpropTrainer(self.network,
                                               learningrate=self.learning_rate,
                                               momentum=self.momentum,
                                               verbose=True)
                self.trainer.setData(self.network_dataset)
            else: raise InvalidTrainerType()

    def ready_supervised_dataset(self, dataset):
        """
        Ready the supervised dataset for training.

        @TODO: Need to randomize the data being fed to the network.
        See randomBatches() here: http://pybrain.org/docs/api/datasets/superviseddataset.html
        """
        self.network_dataset = SupervisedDataSet(len(self.train_data), 1)
        # Currently only supports log function for normalizing data
        training_values = np.log(dataset.data_frame[self.train_data])
        results = np.log(dataset.data_frame[self.prediction_data].shift(-self.prediction_window))
        training_values['PREDICTION_%s' %self.prediction_data[0]] = results
        training_values = training_values.dropna()
        for _, row_data in enumerate(training_values.iterrows()):
            _, data = row_data
            sample = list(data[:-1])
            result = [data[-1]]
            self.network_dataset.addSample(sample, result)

    def train(self, cycles=1):
        """
        Trains the network the number of iteration specified in the cycles parameter.
        """
        for _ in range(cycles):
            res = self.trainer.train()
            self.trained_iterations += 1
        return res

    def train_until_convergence(self, max_cycles=1000, continue_cycles=10,
                                validation_proportion=0.25):
        """
        Wrapper around the pybrain BackpropTrainer trainUntilConvergence method.

        @see: http://pybrain.org/docs/api/supervised/trainers.html
        """
        self.trainer = \
            self.trainer.trainUntilConvergence(maxEpochs=max_cycles,
                                               continueEpochs=continue_cycles,
                                               validationProportion=validation_proportion)

    def _activate(self, data):
        """
        Activates the network using the data specified.
        Returns the network's prediction.
        """
        return self.network.activate(data)[0]

    def activate_all(self, data_frame):
        """
        Activates the network for all values in the dataframe specified.
        """
        dataframe = np.log(data_frame[self.train_data])
        res = []
        for _, row_data in enumerate(dataframe.iterrows()):
            _, data = row_data
            sample = list(data)
            res.append(self._activate(sample))
        return np.exp(res)
