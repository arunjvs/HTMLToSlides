'''
Created on Nov 11, 2013

@author: rohit
'''

import xml.etree.ElementTree as ET
import sys, re
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from KeywordExpander import KeywordExpander

class Summarizer(object):
    '''
    Class to take XML specification of the HTML paper, and creates a new similar
    XML after selecting important sentences
    '''
    
    imgBoost = 3  # Multiplicative boost in score to lines with images

    def __init__(self, xml_file_path, output_file_path):
        '''
        Constructor
        '''
        try:
            self.tree = ET.parse(xml_file_path)
            self.outputFPath = output_file_path
        except Exception, e:
            sys.stderr.write("""Summarizer::__init__:
            Unable to parse XML file \n""")
            raise e
    
    def summarize(self):
        root_element = self.tree.getroot();
        if root_element is None:
            return
        self.keywords = self.getAllKeywords(root_element)
        self.keywords = KeywordExpander.expandSet(self.keywords, root_element)
        intro_element = root_element.find(".//section[@name='Introduction']")
        abstract_element = root_element.find(".//section[@name='Abstract']")
        abstract_text = self.mergeLines(abstract_element)
        self.sumIntro(abstract_text, intro_element)
        conclusion_elt = root_element.find(".//section[@name='Conclusions']")
        self.sumConclusion(conclusion_elt)
        
        for section in root_element.findall(".//section"):
            if section not in [intro_element, 
                               abstract_element, 
                               conclusion_elt]:
                self.sumModelSection(section)
        
        self.tree.write(self.outputFPath)
    
    def sumIntro(self, abstract_text, intro_element):
        '''
        @param abstract_text: string. All the abstract as one large string
        @param intro_element: etree.Element. The root introduction element
        @return: void. The intro_element is modified
        '''
        self.sumSectionsRecursive(abstract_text, intro_element, 2)
        
    def sumConclusion(self, concl_elt):
        '''
        @param concl_elt: etree.Element. The conclusion section element
        @return: void. The above element is modified
        '''
        ref_text = "proposed concluded system model argue better result " + \
                   "present experiment shown key contribution show describe" + \
                   "outline deliver"
        
        self.sumSectionsRecursive(ref_text, concl_elt, 3)
    
    def sumModelSection(self, section):
        '''
        @param section: etree.Element. Some section from model
        @return: void. Summarizes the section using keywords
        '''
        self.sumSectionsRecursive(" ".join(self.keywords), section, 4)
    
    def getAllKeywords(self, root_element):
        '''
        @return: Set. A set of all keywords specified in the paper
        '''
        kwd_elt = root_element.find("keywords")
        return set([kwd.text for kwd in kwd_elt])
    
    def sumSectionsRecursive(self, ref_text, element, topn):
        '''
        @summary: Summarizes each section in the given element recursively
                  using TFIDF scores for lines in each w.r.t ref_text
        @param ref_text: String. The text to compare to
        @param topn: Integer. Number of top elements to preserve, rest delete
        @param element: etree.Element. The tree of elements to summarize
        @return: void
        '''
        if element is None:
            return
        if ref_text is None:
            return
        subsecs = element.findall("section")
        for subsec in subsecs:
            self.sumSectionsRecursive(ref_text, subsec, topn)
        lines = element.findall("line")
        lines_str = [line.text for line in lines]
        if self.tryFindNumberedPoints(lines, element):
            return
        scores = self.computeTFIDFScores(ref_text, lines_str)
        # boost lines with image reference
        for i in range(len(scores)):
            if lines[scores[i][1]].get("img").strip():
                scores[i] = (scores[i][0] * Summarizer.imgBoost, scores[i][1])
        scores = sorted(scores, key = lambda x: (-x[0], x[1]))
        for score in scores[topn:]:
            element.remove(lines[score[1]])
    
    def tryFindNumberedPoints(self, lines, element):
        '''
        @param lines: List<etree.Element>. All the lines in this subsection
        @param element: etree.Element. The current section element
        @return: boolean. True if its able to find numbering in lines, 
        then just keep those lines. Else  return false.
        '''
        lines_str = [line.text.strip() for line in lines]
        
#         # Only for debugging
#         lines_str = []
#         lines_str.append("1. This is a point 1")
#         lines_str.append("Not a point")
#         lines_str.append("2. This is point 2")
        
        regex = "^(\d{1,3})[.),:\s]"
        matches = [re.match(regex, line) for line in lines_str]
        pts_list = []
        line_no = -1
        for match in matches:
            line_no += 1
            if not match:
                continue
            pts_list.append((int(match.group(1)), line_no))
        if not pts_list: 
            # i.e, empty
            return False  # this method fails
        # check if the numbering is consecutive
        for i in range(len(pts_list) - 1):
            if pts_list[i][0] + 1 != pts_list[i + 1][0]:
                return False
        # checked. Now got the points for this section,
        # just remove the rest of lines and return true
        not_del = [item[1] for item in pts_list]
        for i in range(len(lines)):
            if i not in not_del:
                element.remove(lines[i])
        return True
    
    def mergeLines(self, element):
        '''
        @param element: etree.Element. Element with lines
        @return: string. All the lines (even in subsecs) concatinated with " "
        '''
        # all line elements under it (even in subsections)
        if element is None:
            return ""
        lines = element.findall(".//line")
        return " ".join([line.text for line in lines])
        
    def computeTFIDFScores(self, corpus, strings_list): 
        # http://scikit-learn.org/stable/modules/feature_extraction.html
        '''
        @param corpus: String. A corpus to compare each string in the list
        @param strings_list: List<String>. 
        @return: List<Tuple<score, index>>. Sorted in reverse, index wrt
                 original list
        '''
        vect = TfidfVectorizer(min_df=1, tokenizer=LemmaTokenizer())
        all_strings = [string.lower() for string in strings_list] + [corpus.lower()]
        tfidf = None
        try:
            tfidf = vect.fit_transform(all_strings)
        except Exception,e:
            return [(0, i) for i in range(len(strings_list))]
        corpus_vec = tfidf.A[len(strings_list)]
        res = []
        for i in range(len(strings_list)):
            res.append( (np.dot(corpus_vec, tfidf.A[i]) , 
                         i) )
        # sort descending by score, ascending by index
        return sorted(res, key = lambda x: (-x[0], x[1]))

class LemmaTokenizer(object):
    def __init__(self):
        self.wnl = WordNetLemmatizer()
            
    def __call__(self, doc):
        return [self.wnl.lemmatize(t) for t in word_tokenize(doc)]
   
