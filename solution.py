from sklearn.feature_selection import VarianceThreshold, RFECV, SelectKBest, SelectPercentile, f_classif

from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, ExtraTreesClassifier
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.lda import LDA
from sklearn.qda import QDA

from sklearn import cross_validation

import matplotlib.pyplot as plt

import pandas as pd
import numpy as np
import pickle
import os
from preprocessing import *

classifiers = {
	'knn': KNeighborsClassifier( 3 ),
	'svm_linear': SVC(kernel="linear", C=0.025),
	'svm': SVC(gamma=2, C=1),
	'tree': DecisionTreeClassifier(max_depth=5),
	'rf': RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
	'adb': AdaBoostClassifier(),
	'etc': ExtraTreesClassifier(),
	'gauss': GaussianNB(),
	'mult_gauss': MultinomialNB(),
	'lda': LDA(),
	'qda': QDA()
}

def feature_selection( training_data, target_data, test_data ):
	training_data = training_data.drop( 'Is_Emerging_Market', axis=1 )
	X = np.array( training_data ).astype(np.float)
	y = np.array( target_data ).astype(np.float)
	# X_index = training_data.columns.values
	X_index = np.arange(X.shape[-1])

	# Classifier coefficients
	clf = ExtraTreesClassifier()
	X_new = clf.fit( X, y ).transform( X )
	print clf.feature_importances_
	print X_new.shape
	
	# Variance Threshold
	sel = VarianceThreshold(threshold=(.8 * (1 - .8)))
	X_new = sel.fit_transform(X)
	print X_new.shape

	# Univariate feature selection with F-test for feature scoring
	sel = SelectPercentile( f_classif, percentile=10 ).fit( X, y )
	scores = -np.log10(sel.pvalues_)
	# scores /= scores.max()
	print X_index
	print scores
	plt.figure()
	plt.bar( X_index - .45, scores, width=.2, label=r'Univariate score ($-Log(p_{value})$)', color='g' )

	clf = classifiers['svm']
	clf.fit(X, y)
	svm_weights = (clf.coef_ ** 2).sum(axis=0)
	svm_weights /= svm_weights.max()
	plt.bar(X_indices - .25, svm_weights, width=.2, label='SVM weight', color='r')

	plt.show()

def classification( training_data, target_data, test_data ):
	result_index = test_data.index
	X = np.array( training_data ).astype(np.float)
	y = np.array( target_data ).astype(np.float)
	X_test = np.array( test_data ).astype(np.float)
	
	clf_key = 'svm'
	clf = classifiers[clf_key]
	clf.fit( X, y )
	result = clf.predict( X_test )
	result = pd.DataFrame( result, columns=['ISIN','Risk_Stripe'], index=result_index)


def cross_val( training_data, target_data, test_data ):
	train = np.array( training_data ).astype(np.float)
	target = np.array( target_data ).astype(np.float)
	# for clf_key, clf in classifiers.iteritems():
	clf_key = 'svm'
	clf = classifiers[clf_key]
	scores = cross_validation.cross_val_score( clf, train, target, cv=5 )
	print clf_key, scores.mean()

def main():
	if not os.path.exists('objects/clean_training_data.p'):
		prepare_data()

	training_data = pickle.load( open( "objects/clean_training_data.p", "r" ) )
	target_data = pickle.load( open( "objects/clean_target_data.p", "r" ) )
	test_data = pickle.load( open( "objects/clean_test_data.p", "r" ) )

	feature_selection( training_data, target_data, test_data )
	# cross_val( training_data, target_data, test_data )

if __name__ == '__main__':
	main()