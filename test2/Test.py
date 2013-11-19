#!/usr/bin/python

"""Test.py: Extracts test cases and runs HTMLToSlides on them"""
__author__ = "Arun JVS"

import os,sys,re

# Paper List. Generated using:
# awk 'BEGIN{ RS="<A *HREF *= *\""} NR>2 {sub(/".*/,"");print; }' papers.htm
Papers = [
  "Papers/Weisband/sw_txt.htm",
  "Papers/Button/jpd_txt.htm",
  "Papers/Schumann/chi96fi.html",
  "Papers/Levy/lev_txt.htm",
  "Papers/Yamaashi/ky_txt.htm",
  "Papers/Bowers/jb_txt.htm",
  #"Papers/Raman/paper.html",                     #BAD FORMAT: Multipage document
  "Papers/Mereu/rnk-txt.htm",
  "Papers/Robertson/spr_txt.htm",
  "Papers/Chatty/sc_txt.htm",
  #"Papers/Oviatt/slo_txt.htm",                   #BAD FORMAT: Multipage document
  "Papers/Rice/jpr_txt.htm",
  #"Papers/Card/skc1txt.html",                    #BAD FORMAT: Incompletely downloaded html
  "Papers/Pirolli_2/pp2.html",
  "Papers/Noma/nh_txt.html",
  "Papers/Stafford-Fraser/qsf_txt.htm",
  "Papers/Darken/Rpd_txt.htm",
  "Papers/Karsenty/lk_txt.htm",
  "Papers/Hansen/hb_txt.html",
  #"Papers/Marx/mtm_txt.htm",                     #BAD FORMAT: No heading hierarchy
  "Papers/Roy/paper.html",
  "Papers/Eisenberg/me_txt.htm",
  #"Papers/Soloway/es_txt.htm",                   #BAD FORMAT: No heading hierarchy
  "Papers/Pane/jfp_txt.htm",
  "Papers/Koenemann/jk1_txt.htm",
  "Papers/Pirolli/pp_txt.htm",
  #"Papers/Plaisant/cps1txt.htm",                 #BAD FORMAT: Bad heading hierarchy
  #"Papers/Hartson/hrh_txt.htm",                  #BAD FORMAT: Heading Tag Nesting Broken
  "Papers/Virzi/RAVtext.htm",
  "Papers/Kasik/djk_txt.htm",
  #"Papers/Wolber/dww_txt.htm",                   #BAD FORMAT: No author details
  #"Papers/Myers/bam_com.htm",                    #BAD FORMAT: No author email
  "Papers/Ackerman/ack_txt.htm",
  #"Papers/Whittaker/sw_txt.htm",                 #BAD FORMAT: Incompletely downloaded html
  "Papers/Kraut/rek_txt.htm",
  "Papers/Graham/edg_txt.htm",
  "Papers/Mithal/Akm_txt.htm",
  "Papers/Zhai/sz_txt.htm",
  "Papers/Perez/map1txt.htm",
  "Papers/Kitajima/mk_txt.htm",
  "Papers/Bhavnani/bs_txt.htm",
  "Papers/Page/srp_txt.htm",
  #"Papers/Ishizaki/si_bdy.htm",                  #BAD FORMAT: No heading hierarchy
  "Papers/Terveen/lgt_txt.htm",
  "Papers/Gale/srg_txt.htm",
  #"Papers/Miller/am_txt.htm",                    #BAD FORMAT: No heading hierarchy
  "Papers/Sawyer/ps_txt.htm",
  #"Papers/Kamba/tk_txt.htm",                     #BAD FORMAT: No author email; Abstract & Keywords not in a heading
  "Papers/Harrison/blh_txt.htm",
  "Papers/Douglas/sad_txt.htm",
  "Papers/Tweedie/lt1txt.htm",
  "Papers/Lokuge/sag_txt.htm",
  "Papers/Comstock/Emc_txt.htm"
]


ParserExecutable = "../src/Parser/Parser.py"
SummarizerExecutable = "../src/Summarizer/Main.py"
GeneratorExecutable = "../src/Generator/Generator.py"

def printUsage():
	sys.stderr.write("Usage %s extract | list | runall | run <InputHTML> | clean\n"%sys.argv[0])
	exit(-1)

def runHTMLToSlides(fileName):
	sys.stdout.write(fileName+"\n")
	sys.stdout.flush()
	#Parser
	ParserTarget = re.sub("^Papers\/", "Parser/",fileName)
	ParserTarget = re.sub("\.html?$", ".xml", ParserTarget)
	ParserTargerDir = os.path.dirname(ParserTarget)
	os.system("mkdir -p '%s'"%ParserTargerDir)
	os.system("%s '%s' '%s'"%(ParserExecutable, fileName, ParserTarget))
	#Summarizer
	SummarizerTarget = re.sub("^Papers\/", "Summarizer/",fileName)
	SummarizerTarget = re.sub("\.html?$", ".xml", SummarizerTarget)
	SummarizerTargerDir = os.path.dirname(SummarizerTarget)
	os.system("mkdir -p '%s'"%SummarizerTargerDir)
	os.system("%s '%s' '%s'"%(SummarizerExecutable, ParserTarget, SummarizerTarget))
	#Generator
	GeneratorTarget = re.sub("^Papers\/", "Generator/",fileName)
	GeneratorTarget = os.path.dirname(GeneratorTarget)
	os.system("mkdir -p '%s'"%GeneratorTarget)
	os.system("%s '%s' '%s' '%s'"%(GeneratorExecutable,SummarizerTarget,GeneratorTarget, os.path.dirname(fileName)))

if(len(sys.argv)==2):
	if(sys.argv[1]=="extract"): os.system("tar xf Papers.tar.gz")
	elif(sys.argv[1]=="list"): print("\n".join(Papers))
	elif(sys.argv[1]=="runall"):
		for fileName in Papers: runHTMLToSlides(fileName)
	elif(sys.argv[1]=="clean"): os.system("rm -rf Papers Parser Summarizer Generator")
	else: printUsage()
elif(len(sys.argv)==3 and sys.argv[1]=="run"):
	runHTMLToSlides(sys.argv[2])
else:
	printUsage()
