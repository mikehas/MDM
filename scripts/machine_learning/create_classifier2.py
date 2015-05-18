#! /usr/bin/env python

import nltk
import pickle
from datetime import datetime
from textblob.classifiers import NaiveBayesClassifier

training_data = []
test_set = []
medical = []
names = []

f = open("all_medical_acronyms_uniq.txt", 'rb')
for i, row in enumerate(f):
  tup = (" ".join(list(row.strip())), "medical_title")
  medical.append(tup)
  if i == 100: 
    break
f.close()


f = open("all_names.txt", 'rb')
for i, row in enumerate(f):
  tup = (" ".join(list(row.strip())), "name")
  names.append(tup)
  if i == 100: 
    break
f.close()

training_data = training_data + medical
training_data = training_data + names
test_set = medical[0:99] + names[0:99]
print test_set

# classifier1
print "Creating classifier..."
print datetime.now()

c1 = NaiveBayesClassifier(training_data)

print "Completed creating classifier..."
print datetime.now()

# Saving classifier
outfile = open("classifier1.pickle", 'wb')
pickle.dump(c1, outfile)
outfile.close()

# Running classifier accuracy test...
a = c1.accuracy(test_set)
print('Accuracy: %6.4f' % a)

