import cPickle
import numpy as np
from pybrain.tools.shortcuts import buildNetwork
from pybrain.datasets.supervised import SupervisedDataSet
from pybrain.supervised.trainers.backprop import BackpropTrainer
#from pybrain.supervised.trainers import BackpropTrainer, RPropMinusTrainer
from pybrain.structure.networks import FeedForwardNetwork
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
    network = cPickle.loads(network)
    if dataset: network.build_network(dataset, new=False)
    return network

def load_from_file(filename, dataset=None):
    f = open(filename, 'rb')
    network = cPickle.load(f)
    f.close()
    if dataset: network.build_network(dataset, new=False)
    return network

class InvalidNetworkType(Exception): pass
class InvalidTrainerType(Exception): pass
class InvalidNetworkDatasetType(Exception): pass
class InvalidDataset(Exception): pass

class NeuralNetwork:
    def __init__(self, train_data, prediction_data, network_type=FEED_FORWARD_NETWORK,
                       network_dataset_type=SUPERVISED_DATASET,
                       trainer_type=BACKPROP_TRAINER):
        self.train_data = train_data
        self.prediction_data = prediction_data
        self.network_type = network_type
        self.network_dataset_type = network_dataset_type
        self.trainer_type = trainer_type
        self.network = None
        self.dataset = None
        self.trainer = None
        self.trained_iterations = 0
        self.momentum = None
        self.learning_rate = None
        self.hidden_layers = None
        self.prediction_window = None
        self.logger = logger.Logger(self.__class__.__name__)
        self.logger.info('train_data: %s  prediction_data: %s, network_type: %s, network_dataset_type: %s, trainer_type: %s'
                %(train_data, prediction_data, network_type, network_dataset_type, trainer_type))

    def save(self):
        return cPickle.dumps(self)

    def save_to_file(self, filename):
        """
        Look into pybrain.datasets.supervised.SupervisedDataSet.saveToFile()
        http://pybrain.org/docs/api/datasets/superviseddataset.html
        """
        f = open(filename, 'wb')
        cPickle.dump(self, f)
        f.close()

    def build_network(self, dataset, new=True, **kwargs):
        if 'hidden_layers' in kwargs: self.hidden_layers = kwargs['hidden_layers']
        else: assert self.hidden_layers != None
        if 'prediction_window' in kwargs: self.prediction_window = kwargs['prediction_window']
        else: assert self.prediction_window != None
        if 'learning_rate' in kwargs: self.learning_rate = kwargs['learning_rate']
        else: assert self.learning_rate != None
        if 'momentum' in kwargs: self.momentum = kwargs['momentum']
        else: assert self.momentum != None
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
        #TODO: Need to randomize the data being fed to the network.
        See randomBatches() here: http://pybrain.org/docs/api/datasets/superviseddataset.html
        """
        self.network_dataset = SupervisedDataSet(len(self.train_data), 1)
        # Currently only supports log function for normalizing data
        training_values = np.log(dataset.data_frame[self.train_data])
        results = np.log(dataset.data_frame[self.prediction_data].shift(-self.prediction_window))
        training_values['PREDICTION_%s' %self.prediction_data[0]] = results
        training_values = training_values.dropna()
        for i, row_data in enumerate(training_values.iterrows()):
            datetime, data = row_data
            sample = list(data[:-1])
            result = [data[-1]]
            self.network_dataset.addSample(sample, result)

    def train(self, cycles=1):
        """
        Trains the network the number of iteration specified in the cycles parameter.
        """
        for i in range(cycles):
            res = self.trainer.train()
            self.trained_iterations += 1
        return res

    def train_until_convergence(self, max_cycles=None,
                                      continue_cycles=10,
                                      validation_proportion=0.25):
        self.trainer.trainUntilConvergence(100)

    def _activate(self, data):
        return self.network.activate(data)[0]

    def activate_all(self, data_frame):
        df = np.log(data_frame[self.train_data])
        res = []
        for i, row_data in enumerate(df.iterrows()):
            datetime, data = row_data
            sample = list(data)
            res.append(self._activate(sample))
        return np.exp(res)
