#! /usr/bin/env python

import nltk
import pickle
from textblob.classifiers import NaiveBayesClassifier

training_data = []
test_set = []
medical = []
names = []


# Loading classifier
f = open("classifier1.pickle", 'rb')
c1 = pickle.load(f)


val = c1.classify ("B S")
print val
