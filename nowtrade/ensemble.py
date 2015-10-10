"""
Module that enables the use of ensembles in NowTrade.
"""
import cPickle
import numpy as np
from itertools import chain
from sklearn.ensemble import RandomForestRegressor #, RandomForestClassifier
from nowtrade import logger

RANDOM_FOREST_REGRESSOR = 'Random Forest Regressor'
RANDOM_FOREST_CLASSIFIER = 'Random Forest Classifier'
EXTRA_TREES_REGRESSOR = 'Extra Trees Regressor'
EXTRA_TREES_CLASSIFIER = 'Extra Trees Classifier'
ADA_BOOST_REGRESSOR = 'Ada Boost Regressor'
ADA_BOOST_CLASSIFIER = 'Ada Boost Classifier'
GRADIENT_BOOSTING_REGRESSOR = 'Gradient Boosting Regressor'
GRADIENT_BOOSTING_CLASSIFIER = 'Gradient Boosting Classifier'

class UnknownEnsembleType(Exception):
    """
    Exception used when an invalid ensemble type was specified.
    """
    pass

def load(ensemble):
    """
    Load a previously pickled ensemble.
    """
    return cPickle.loads(ensemble)

def load_from_file(filename):
    """
    Load an ensemble from a previous one saved to file.
    """
    file_handler = open(filename, 'rb')
    ensemble = cPickle.load(file_handler)
    file_handler.close()
    return ensemble

class Ensemble(object):
    """
    The ensemble class does all the heavy lifting to incorporate sklearn
    ensembles into the NowTrade ecosystem.
    """
    def __init__(self, train_data, prediction_data, ensemble_type=RANDOM_FOREST_REGRESSOR):
        self.train_data = train_data
        self.prediction_data = prediction_data
        self.ensemble_type = ensemble_type
        self.ensemble = None
        self.prediction_window = None
        self.look_back_window = None
        self.training_set = []
        self.target_set = []
        self.normalize = True
        self.number_of_estimators = 150
        self.max_depth = None
        self.random_state = 0
        self.min_samples_split = 2
        self.number_of_jobs = 2
        self.learning_rate = 1.0 # For Gradient Boosting
        self.rating = None
        self.feature_importances = None
        self.logger = logger.Logger(self.__class__.__name__)
        self.logger.info('train_data: %s  prediction_data: %s  ensemble_type: %s'
                         %(train_data, prediction_data, ensemble_type))

    def save(self):
        """
        Returns the pickled fitted ensemble as a string.

        WARNING: Can be very big in size.
        """
        return cPickle.dumps(self)

    def save_to_file(self, filename):
        """
        Saves an ensemble to file for later use.

        WARNING: Can be very big in size.
        """
        file_handler = open(filename, 'wb')
        cPickle.dump(self, file_handler)
        file_handler.close()

    def build_ensemble(self, dataset, **kwargs):
        """
        Builds an ensemble using the dataset provided.
        Expected keyword args:
            - 'normalize'
            - 'prediction_window'
            - 'look_back_window'
            - 'number_of_estimators'
        Optional keyword args:
            - 'max_depth'
            - 'random_state'
            - 'min_sample_split'
            - 'number_of_jobs'
            - 'learning_rate'
        @see: http://scikit-learn.org/0.15/modules/generated/sklearn.ensemble.\
              RandomForestRegressor.html#sklearn.ensemble.RandomForestRegressor
        """
        self.training_set = []
        self.target_set = []
        self.normalize = kwargs.get('normalize', True)
        self.prediction_window = kwargs.get('prediction_window', 1)
        self.look_back_window = kwargs.get('look_back_window', 10)
        self.number_of_estimators = kwargs.get('number_of_estimators', 100)
        self.max_depth = kwargs.get('max_depth', None)
        self.random_state = kwargs.get('random_state', 0)
        self.min_samples_split = kwargs.get('min_samples_split', 1)
        self.number_of_jobs = kwargs.get('number_of_jobs', 1)
        self.learning_rate = kwargs.get('learning_rate', 1.0)
        if self.normalize:
            training_values = np.log(dataset.data_frame[self.train_data])
            #training_values.fillna(method='backfill', inplace=True)
            results = \
                np.log(dataset.data_frame[self.prediction_data[0]].shift(-self.prediction_window))
            #results.fillna(method='backfill', inplace=True)
            # Replace all 0's that have been log'ed to -inf with -999
            # -999 is sufficient as np.exp(-999) brings it back to 0
            training_values.replace(-np.inf, -999, inplace=True)
            results.replace(-np.inf, -999, inplace=True)
        else:
            training_values = dataset.data_frame[self.train_data]
            results = dataset.data_frame[self.prediction_data[0]].shift(-self.prediction_window)
        for i in range(self.look_back_window, len(training_values)):
            values = training_values[i-self.look_back_window:i+1]
            values = list(chain.from_iterable(values.values))
            result = results.iloc[i] # Prediction window already calculated with shift
            if np.isnan(np.sum(values)) or np.isnan(np.sum(result)):
                #assert False, 'NaN values found in data while preparing data to fit'
                continue
            if np.inf in values or -np.inf in values or result == np.inf or result == -np.inf:
                #assert False, 'Infinite values found in data while preparing data to fit'
                continue
            self.training_set.append(values)
            self.target_set.append(result)
        # Need to get rid of the last few values that represent things we couldn't predict yet
        # Need to shuffle Training/Target Sets
        self.training_set = self.training_set[:-self.prediction_window]
        self.target_set = self.target_set[:-self.prediction_window]

    def fit(self, compute_importances=True):
        """
        Fits the model as configured.
        """
        assert len(self.training_set) > 0
        assert len(self.target_set) > 0
        if self.ensemble_type == RANDOM_FOREST_REGRESSOR:
            self.ensemble = \
                    RandomForestRegressor(n_estimators=self.number_of_estimators,
                                          max_depth=self.max_depth,
                                          random_state=self.random_state,
                                          min_samples_split=self.min_samples_split,
                                          n_jobs=self.number_of_jobs)
        else: raise UnknownEnsembleType()
        self.ensemble.fit(self.training_set, self.target_set)
        if compute_importances:
            self.feature_importances = self.ensemble.feature_importances_

    def _activate(self, data):
        """
        Activates the ensemble using the data specified.
        Returns the ensemble's prediction.
        """
        #data.replace(-np.inf, -999, inplace=True)
        if np.isnan(np.sum(data)):
            #assert False, 'NaN values found in data while activating the ensemble'
            return np.nan
        if np.inf in data or -np.inf in data:
            #assert False, 'Infinite values found in data while activating the ensemble'
            return np.nan
        return self.ensemble.predict(data)[0]

    def activate_all(self, data_frame):
        """
        Activates the network for all values in the dataframe specified.
        """
        assert self.ensemble != None, 'Please ensure you have fit your ensemble'
        if self.normalize:
            dataframe = np.log(data_frame[self.train_data])
        else:
            dataframe = data_frame[self.train_data]
        res = []
        for i in range(self.look_back_window, len(dataframe)):
            values = dataframe[i-self.look_back_window:i+1]
            values = list(chain.from_iterable(values.values))
            res.append(self._activate(values))
        if self.normalize:
            return np.exp(res)
        else:
            return res
