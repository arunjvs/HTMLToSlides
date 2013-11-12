'''
Created on Nov 11, 2013

@author: rohit
'''

import xml.etree.ElementTree as ET
import sys
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

class Summarizer(object):
    '''
    Class to take XML specification of the HTML paper, and creates a new similar
    XML after selecting important sentences
    '''


    def __init__(self, xml_file_path):
        '''
        Constructor
        '''
        try:
            self.tree = ET.parse(xml_file_path)
        except Exception, e:
            sys.stderr.write("""Summarizer::__init__:
            Unable to parse XML file : """ + str(e))
    
    def summarize(self):
        root_element = self.tree.getroot();
        intro_element = root_element.find(".//section[@name='Introduction']")
        abstract_element = root_element.find(".//section[@name='Abstract']")
        abstract_text = self.mergeLines(abstract_element)
        self.sumIntro(abstract_text, intro_element)
        
        self.tree.write("../../test/Summarizer/result.xml")
    
    def sumIntro(self, abstract_text, intro_element):
        '''
        @param abstract_text: string. All the abstract as one large string
        @param intro_element: etree.Element. The root introduction element
        @return: etree.Element. The intro_element modified
        '''
        self.sumSectionsRecursive(abstract_text, intro_element, 2)
        
    def sumSectionsRecursive(self, ref_text, element, topn):
        '''
        @summary: Summarizes each section in the given element recursively
                  using TFIDF scores for lines in each w.r.t ref_text
        @param ref_text: String. The text to compare to
        @param topn: Integer. Number of top elements to preserve, rest delete
        @param element: etree.Element. The tree of elements to summarize
        '''
        subsecs = element.findall("section")
        for subsec in subsecs:
            self.sumSectionsRecursive(ref_text, subsec, topn)
        lines = element.findall("line")
        lines_str = [line.text for line in lines]
        scores = self.computeTFIDFScores(ref_text, lines_str)
        for score in scores[topn:]:
            element.remove(lines[score[1]])
    
    def mergeLines(self, element):
        '''
        @param element: etree.Element. Element with lines
        @return: string. All the lines concatinated with " "
        '''
        lines = element.findall("line")
        return " ".join([line.text for line in lines])
        
    def computeTFIDFScores(self, corpus, strings_list):
        '''
        @param corpus: String. A corpus to compare each string in the list
        @param strings_list: List<String>. 
        @return: List<Tuple<score, index>>. Sorted in reverse, index wrt
                 original list
        '''
        vect = TfidfVectorizer(min_df=1)
        all_strings = strings_list + [corpus]
        tfidf = vect.fit_transform(all_strings)
        corpus_vec = tfidf.A[len(strings_list)]
        res = []
        for i in range(len(strings_list)):
            res.append( (np.dot(corpus_vec, tfidf.A[i]) , 
                         i) )
        return sorted(res, reverse = True)
   
if __name__ == '__main__':     
    ob = Summarizer("../../test/Parser/Rice/jpr_txt.xml")
    ob.summarize()
    print ob.computeTFIDFScores("corpus is this is ", ["corpus ", "corpus corpus"]);