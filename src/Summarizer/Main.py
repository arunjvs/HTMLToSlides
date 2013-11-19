#!/usr/bin/python2.7

import sys
import os
import shutil

__all__ = []
__version__ = 0.1
__date__ = '2013-11-17'
__updated__ = '2013-11-17'

from Summarizer import Summarizer

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''
    
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    if len(argv) < 3:
        print "Usage :", program_name, " input_XML, output_XML"
        return
    input_fname = argv[1]
    output_fname = argv[2]
    try:
        ob = Summarizer(input_fname, output_fname)
        ob.summarize()
    except Exception,e:
        sys.stderr.write(">>Summarization Failed : %s<<\n" % str(e))
        shutil.copyfile(input_fname, output_fname)
        return
    sys.stdout.write("Summarization Successful\n")
    
if __name__ == "__main__":
    sys.exit(main())
