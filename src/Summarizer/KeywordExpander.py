'''
Created on Nov 17, 2013

@author: rohit
'''

from nltk.corpus import stopwords
from nltk.tokenize.punkt import PunktWordTokenizer
from collections import Counter
import re, string

class KeywordExpander(object):
    '''
    Algorithm to expand a set of keywords
    '''
    verbose = True
    
    @staticmethod
    def expandSet(kwd_set, root_elt):
        '''
        Expands a given set of keywords using the whole text and
        co-occurance probabilities
        @param kwd_set: Set<string>. List of mentioned kwds
        @param root_elt: etree.Element. The root element of the document
        '''
        lines = [elt.text for elt in root_elt.findall(".//line")]
        stop_words = set(stopwords.words("english"))
        tokenizer = PunktWordTokenizer()
        all_pairs = []
        for line in lines:
            for kwd in kwd_set:
                if re.match(kwd, line):
                    tokens = filter(lambda x: x not in stop_words and
                                        x not in string.punctuation,
                                    tokenizer.tokenize(line))
                    for token in tokens:
                        all_pairs.append((kwd, token))
        top_pairs = [pair for pair, freq in Counter(all_pairs).iteritems()
                     if freq >= 2]
        for pair in top_pairs:
            if KeywordExpander.verbose and pair[1] not in kwd_set:
                print "Expanding kwd with : ", pair[1]
            kwd_set.add(pair[1]);
            
        return kwd_set