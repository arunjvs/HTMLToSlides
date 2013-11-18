#!/usr/bin/python

"""Test.py: Extracts test cases and runs HTMLToSlides on them"""
__author__ = "Arun JVS"

import os,sys,re

# Paper List
# Generated using: awk 'BEGIN{ RS="<A *HREF *= *\""} NR>2 {sub(/".*/,"");print; }' papers.htm
Papers = [
  "Papers/Weisband/sw_txt.htm",
  "Papers/Button/jpd_txt.htm",
  "Papers/Schumann/chi96fi.html",
  "Papers/Levy/lev_txt.htm",
  "Papers/Yamaashi/ky_txt.htm",
  "Papers/Bowers/jb_txt.htm",
  "Papers/Raman/paper.html",
  "Papers/Mereu/rnk-txt.htm",
  "Papers/Robertson/spr_txt.htm",
  "Papers/Chatty/sc_txt.htm",
  "Papers/Oviatt/slo_txt.htm",
  "Papers/Rice/jpr_txt.htm",
  "Papers/Card/skc1txt.html",
  "Papers/Pirolli_2/pp2.html",
  "Papers/Noma/nh_txt.html",
  "Papers/Stafford-Fraser/qsf_txt.htm",
  "Papers/Darken/Rpd_txt.htm",
  "Papers/Karsenty/lk_txt.htm",
  "Papers/Hansen/hb_txt.html",
  "Papers/Marx/mtm_txt.htm",
  "Papers/Roy/paper.html",
  "Papers/Eisenberg/me_txt.htm",
  "Papers/Soloway/es_txt.htm",
  "Papers/Pane/jfp_txt.htm",
  "Papers/Koenemann/jk1_txt.htm",
  "Papers/Pirolli/pp_txt.htm",
  "Papers/Plaisant/cps1txt.htm",
  "Papers/Hartson/hrh_txt.htm",
  "Papers/Virzi/RAVtext.htm",
  "Papers/Kasik/djk_txt.htm",
  "Papers/Wolber/dww_txt.htm",
  "Papers/Myers/bam_com.htm",
  "Papers/Ackerman/ack_txt.htm",
  "Papers/Whittaker/sw_txt.htm",
  "Papers/Kraut/rek_txt.htm",
  "Papers/Graham/edg_txt.htm",
  "Papers/Mithal/Akm_txt.htm",
  "Papers/Zhai/sz_txt.htm",
  "Papers/Perez/map1txt.htm",
  "Papers/Kitajima/mk_txt.htm",
  "Papers/Bhavnani/bs_txt.htm",
  "Papers/Page/srp_txt.htm",
  "Papers/Ishizaki/si_bdy.htm",
  "Papers/Terveen/lgt_txt.htm",
  "Papers/Gale/srg_txt.htm",
  "Papers/Miller/am_txt.htm",
  "Papers/Sawyer/ps_txt.htm",
  "Papers/Kamba/tk_txt.htm",
  "Papers/Harrison/blh_txt.htm",
  "Papers/Douglas/sad_txt.htm",
  "Papers/Tweedie/lt1txt.htm",
  "Papers/Lokuge/sag_txt.htm",
  "Papers/Comstock/Emc_txt.htm"
]


ParserExecutable = "../src/Parser/Parser.py"
SummarizerExecutable = "../src/Parser/Summarizer.py"
GeneratorExecutable = "../src/Parser/Generator.py"


def printUsage():
	sys.stderr.write("Usage %s extract | list | runall | run <InputHTML> | clean\n"%sys.argv[0])
	exit(-1)


def runHTMLToSlides(fileName):
	ParserTarget = re.sub("^Papers\/", "Parser/",fileName)
	ParserTarget = re.sub("\.html?$", ".xml", ParserTarget)
	ParserTargerDir = os.path.dirname(ParserTarget)
	os.system("mkdir -p '%s'"%ParserTargerDir)
	os.system("%s '%s' '%s'"%(ParserExecutable, fileName, ParserTarget))

if(len(sys.argv)==2):
	if(sys.argv[1]=="extract"): os.system("tar xf Papers.tar.gz")
	elif(sys.argv[1]=="list"): print("\n".join(Papers))
	elif(sys.argv[1]=="runall"):
		for fileName in Papers: runHTMLToSlides(fileName)
	elif(sys.argv[1]=="clean"): os.system("rm -rf Papers Parser Summazier Generator")
	else: printUsage()
elif(len(sys.argv)==3 and sys.argv[1]=="run"):
	runHTMLToSlides(sys.argv[2])
else:
	printUsage()

