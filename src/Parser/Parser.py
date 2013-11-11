#!/usr/bin/python2.7

"""Parser.py: Parser implementation to convert a paper in standard html to structured xml"""
__author__ = "Arun JVS"
__license__ = "GPL"

import re, sys

class Parser(object):
  """Parser class to convert a paper in standard html to structure xml"""
  def __init__(self, htmlFile, xmlFile):
    htmlFileHandle = open(htmlFile, "r")
    self.html = self.htmlNormalizer(htmlFileHandle.read())
    self.FoundAbout = False
    self.Keywords = []
    self.References = []
    self.Images = []
    htmlFileHandle.close()
    self.xmlFileHandle = open(xmlFile, "w")

  def htmlNormalizer(self, s):
    #Extract body
    s = re.search('\<\s*[bB][oO][dD][yY](\s+[^\>]*)?\>(.*?)\<\s*\/\s*[bB][oO][dD][yY]\s*\>', s, re.DOTALL)
    if (not s): return ""
    s = s.group(2)
    #Remove comments
    s = re.sub('\<\!\-\-.*?\-\-\>', '', s, flags=re.DOTALL)
    #Remove dirty header
    removeTagsWithInnerHTMLAtBeginning = ["table"]
    for tag in removeTagsWithInnerHTMLAtBeginning:
      caseInvariantRegex = ''.join(['['+c+c.upper()+']' for c in tag])
      regex = '^\s*\<\s*'+caseInvariantRegex+'(\s+[^\>]*)?\>(.*?)\<\s*\/\s*'+caseInvariantRegex+'\s*\>'
      s = re.sub(regex, ' ', s, flags=re.DOTALL)
    #Remove dirty html with inner text
    removeTagsWithInnerHTML = ["blockquote", "pre", "script", "sup", "sub"] + ["ol", "dl", "ul"]#TBR
    for tag in removeTagsWithInnerHTML:
      caseInvariantRegex = ''.join(['['+c+c.upper()+']' for c in tag])
      regex = '\<\s*'+caseInvariantRegex+'(\s+[^\>]*)?\>(.*?)\<\s*\/\s*'+caseInvariantRegex+'\s*\>'
      s = re.sub(regex, ' ', s, flags=re.DOTALL)
    #Condense multiple spaces
    s = re.sub('\s+', ' ', s)
    #Remove dirty html tags
    removeTags = [["a",""],
                  ["b",""],
                  ["br","\n"],
                  ["center", "\n"],
                  ["div","\n"],
                  ["font", ""],
                  ["hr", "\n"],
                  ["i", ""],
                  ["p", "\n"],
                  ["table", "\n"],
                  ["thead", "\n"],
                  ["tbody", "\n"],
                  ["tfoot", "\n"],
                  ["th", " "],
                  ["td", " "],
                  ["tr", "\n"],
                  ["tt", ""],
                  ["u", ""],
                  ["img", ""]#TBR
                 ]
    for tag in removeTags:
      caseInvariantRegex = ''.join(['['+c+c.upper()+']' for c in tag[0]])
      regex = '\<\s*\/?\s*' + caseInvariantRegex + '(\s+[^\>]*)?\>'
      s = re.sub(regex, tag[1], s)
    #Condense multiple newlines
    s = re.sub('\s*\n\s*', '\n', s)
    s = s.strip()
    return s

  def titleNormalizer(self, s):
    s = re.sub('^[^a-zA-Z]*','',s)
    s = re.sub('\s+', ' ', s)
    s = s.strip()
    if(len(s.split())==1): s=s.title()
    return s

  def lineSplitter(self, s, sLevel):
    lines = [line.strip() for line in s.split(".") if re.search('\S',line)]
    lines2 = []
    for line in lines:
      if(len(lines2)>0 and (len(line)<7 or len(line.split())<2 or line[0]==',')): lines2[-1]=lines2[-1]+'.'+line+'.'
      else: lines2.append(line+'.')
    lines2 = [re.sub('\.\.','.',line.strip()) for line in lines2 if re.search('\S',line)]
    lines2 = [re.sub('\s+',' ',line) for line in lines2 if line!="."]
    for line in lines2:
      self.xmlFileHandle.write('\t'*sLevel+'<line ref="%s" img="%s">%s</line>\n'%("","",line))

  def authorSplitter(self, s):
    authors = [["author1","author1@example.com","MIT"], ["author2","author2@example.com","CMU"]]
    for author in authors:
      self.xmlFileHandle.write('\t\t\t<author name="%s" email="%s" organization="%s"/>\n'%(author[0],author[1],author[2]))

  def keywordSplitter(self, s):
    self.Keywords += [re.sub('[\.]','',k.strip()) for k in s.split(",")]

  def referencesSplitter(self, s):
    "Hehehe"

  def sectionSplitter(self, s, hLevel, sLevel):
    caseInvariantRegex='[hH]'+str(hLevel)
    regex = '\<\s*'+caseInvariantRegex+'(\s+[^\>]*)?\>(.*?)\<\s*\/\s*'+caseInvariantRegex+'\s*\>'
    sections=[]
    sections_start=0
    for section in re.finditer(regex,s, flags=re.DOTALL):
      if(len(sections)>0): sections[-1][2] = section.start()
      else: sections_start = section.start()
      sections += [[self.titleNormalizer(section.group(2)), section.end(), len(s)]]
    if(len(sections)==0):
      if(hLevel<4): self.sectionSplitter(s, hLevel+1, sLevel)
      else: self.lineSplitter(s, sLevel)
      return
    if(self.FoundAbout==False):
      self.xmlFileHandle.write('\t<about>\n')
      self.xmlFileHandle.write('\t\t<title>'+sections[0][0]+'</title>\n')
      self.xmlFileHandle.write('\t\t<authors>\n')
      self.authorSplitter(s[sections[0][1]:sections[0][2]])
      self.xmlFileHandle.write('\t\t</authors>\n')
      self.xmlFileHandle.write('\t</about>\n')
      self.FoundAbout=True
      if(len(sections)==1):
        self.sectionSplitter(s[sections[0][1]:sections[0][2]], hLevel+1, sLevel)
        return
      sections = sections[1:]
    self.lineSplitter(s[0:sections_start], sLevel)
    for section in sections:
      if   (section[0]=="Keywords"): self.keywordSplitter(s[section[1]:section[2]])
      elif (section[0]=="References"): self.referencesSplitter(s[section[1]:section[2]])
      else:
        self.xmlFileHandle.write('\t'*sLevel+'<section name="%s">\n'%(section[0]))
        self.sectionSplitter(s[section[1]:section[2]], hLevel+1, sLevel+1)
        self.xmlFileHandle.write('\t'*sLevel+'</section>\n')

  def run(self):
    self.xmlFileHandle.write('<?xml version="1.0" encoding="utf-8"?>\n')
    self.xmlFileHandle.write('<doc>\n')
    self.sectionSplitter(self.html, 1, 1)
    self.xmlFileHandle.write('\t<keywords>\n')
    for keyword in self.Keywords:
      self.xmlFileHandle.write('\t\t<keyword>%s</keyword>\n'%keyword)
    self.xmlFileHandle.write('\t<keywords>\n')
    self.xmlFileHandle.write('</doc>\n')
    self.xmlFileHandle.close()
    return 0

if (__name__=="__main__"):
  if(len(sys.argv)!=3):
    print("usage: %s htmlFile xmlFile" %sys.argv[0])
    exit(-1)
  exit(Parser(sys.argv[1], sys.argv[2]).run())
