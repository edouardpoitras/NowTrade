import cPickle
import numpy as np
from itertools import chain
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, \
                             ExtraTreesRegressor, ExtraTreesClassifier, \
                             GradientBoostingRegressor, GradientBoostingClassifier
                             #GradientBoostingRegressor, GradientBoostingClassifier, \
                             #AdaBoostRegressor, AdaBoostClassifier, \
from sklearn.cross_validation import cross_val_score
from nowtrade import logger

RANDOM_FOREST_REGRESSOR = 'Random Forest Regressor'
RANDOM_FOREST_CLASSIFIER = 'Random Forest Classifier'
EXTRA_TREES_REGRESSOR = 'Extra Trees Regressor'
EXTRA_TREES_CLASSIFIER = 'Extra Trees Classifier'
ADA_BOOST_REGRESSOR = 'Ada Boost Regressor'
ADA_BOOST_CLASSIFIER = 'Ada Boost Classifier'
GRADIENT_BOOSTING_REGRESSOR = 'Gradient Boosting Regressor'
GRADIENT_BOOSTING_CLASSIFIER = 'Gradient Boosting Classifier'

class UnknownEnsembleType(Exception): pass

def load(ensemble):
    return cPickle.loads(ensemble)

def load_from_file(filename):
    f = open(filename, 'rb')
    ensemble = cPickle.load(f)
    f.close()
    return ensemble

class Ensemble:
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
        return cPickle.dumps(self)

    def save_to_file(self, filename):
        f = open(filename, 'wb')
        cPickle.dump(self, f)
        f.close()

    def build_ensemble(self, dataset, **kwargs):
        self.training_set = []
        self.target_set = []
        if 'normalize' in kwargs: self.normalize = kwargs['normalize']
        if 'prediction_window' in kwargs: self.prediction_window = kwargs['prediction_window']
        else: assert self.prediction_window != None
        if 'look_back_window' in kwargs: self.look_back_window = kwargs['look_back_window']
        else: assert self.look_back_window != None
        if 'number_of_estimators' in kwargs: self.number_of_estimators = kwargs['number_of_estimators']
        else: assert self.number_of_estimators != None
        if 'max_depth' in kwargs: self.max_depth = kwargs['max_depth']
        #else: assert self.max_depth != None
        if 'random_state' in kwargs: self.random_state = kwargs['random_state']
        #else: assert self.random_state != None
        if 'min_samples_split' in kwargs: self.min_samples_split = kwargs['min_samples_split']
        #else: assert self.min_samples_split != None
        if 'number_of_jobs' in kwargs: self.number_of_jobs = kwargs['number_of_jobs']
        #else: assert self.number_of_jobs != None
        if 'learning_rate' in kwargs: self.learning_rate = kwargs['learning_rate']
        #else: assert self.learning_rate != None
        if self.normalize:
            training_values = np.log(dataset.data_frame[self.train_data])
            #training_values.fillna(method='backfill', inplace=True)
            results = np.log(dataset.data_frame[self.prediction_data[0]].shift(-self.prediction_window))
            #results.fillna(method='backfill', inplace=True)
            # Replace all 0's that have been log'ed to -inf with -999
            # -999 is sufficient as np.exp(-999) brings it back to 0
            training_values.replace(-np.inf, -999, inplace=True)
            results.replace(-np.inf, -999, inplace=True)
        else:
            training_values = dataset.data_frame[self.train_data]
            results = dataset.data_frame[self.prediction_data[0]].shift(-self.prediction_window)
        length = len(training_values)
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
        self.training_set = self.training_set[:-self.prediction_window]
        self.target_set = self.target_set[:-self.prediction_window]
        # TODO: Shuffle Training/Target Sets

    def fit(self, compute_importances=True, get_rating=True):
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
        #if get_rating:
            #self.rating = cross_val_score(self.ensemble,
                                          #self.training_set,
                                          #self.target_set).mean()

    def _activate(self, data):
        #data.replace(-np.inf, -999, inplace=True)
        if np.isnan(np.sum(data)):
            #assert False, 'NaN values found in data while activating the ensemble'
            return np.nan
        if np.inf in data or -np.inf in data:
            #assert False, 'Infinite values found in data while activating the ensemble'
            return np.nan
        return self.ensemble.predict(data)[0]

    def activate_all(self, data_frame):
        assert self.ensemble != None, 'Please ensure you have fit your ensemble'
        if self.normalize: df = np.log(data_frame[self.train_data])
        else: df = data_frame[self.train_data]
        res = []
        for i in range(self.look_back_window, len(df)):
            values = df[i-self.look_back_window:i+1]
            values = list(chain.from_iterable(values.values))
            res.append(self._activate(values))
        if self.normalize: return np.exp(res)
        else: return res
