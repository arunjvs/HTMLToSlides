'''
Created on Nov 11, 2013

@author: rohit
'''

class Summarizer(object):
    '''
    Class to take XML specification of the HTML paper, and creates a new similar
    XML after selecting important sentences
    '''


    def __init__(self, xml_file_path):
        '''
        Constructor
        '''
        
        