#!/usr/bin/python2.7

"""Parser.py: Parser implementation to convert a paper in standard html to structured xml"""
__author__ = "Arun JVS"
__license__ = "GPL"

import re, sys

class Parser(object):
  """Parser class to convert a paper in standard html to structured xml"""
  def __init__(self, htmlFile, xmlFile):
    htmlFileHandle = open(htmlFile, "r")
    self.FoundAbout = False
    self.Keywords = []
    self.Images = []
    self.References = []
    self.html = self.htmlNormalizer(htmlFileHandle.read())
    htmlFileHandle.close()
    self.xmlFileHandle = open(xmlFile, "w")

  def run(self):
    self.xmlFileHandle.write('<?xml version="1.0" encoding="utf-8"?>\n')
    self.xmlFileHandle.write('<doc>\n')
    self.sectionSplitter(self.html, 1, 1)
    self.xmlFileHandle.write('\t<keywords>\n')
    for keyword in self.Keywords:
      self.xmlFileHandle.write('\t\t<keyword>%s</keyword>\n'%keyword)
    self.xmlFileHandle.write('\t</keywords>\n')
    self.xmlFileHandle.write('\t<images>\n')
    for image in self.Images:
      self.xmlFileHandle.write('\t\t<image id="%s" src="%s" alt="%s" caption="%s"/>\n'%(image[0],image[1],image[2],image[3]))
    self.xmlFileHandle.write('\t</images>\n')
    self.xmlFileHandle.write('\t<references>\n')
    for reference in self.References:
      self.xmlFileHandle.write('\t\t<reference id="%s">%s</reference>\n'%(reference[0],reference[1]))
    self.xmlFileHandle.write('\t</references>\n')
    self.xmlFileHandle.write('</doc>\n')
    self.xmlFileHandle.close()
    return 0

  def htmlNormalizer(self, s):
    #Remove comments
    s = re.sub('\<\!\-\-.*?\-\-\>', '', s, flags=re.DOTALL)
    #Extract body
    s = re.search('\<\s*body(\s+[^\>]*)?\>(.*?)\<\s*\/\s*body\s*\>', s, flags=re.DOTALL|re.IGNORECASE)
    if (not s): return ""
    s = s.group(2)
    #Remove dirty header
    removeTagsWithInnerHTMLAtBeginning = ["table"]
    for tag in removeTagsWithInnerHTMLAtBeginning:
      regex = '^\s*\<\s*'+tag+'(\s+[^\>]*)?\>(.*?)\<\s*\/\s*'+tag+'\s*\>'
      s = re.sub(regex, ' ', s, flags=re.DOTALL|re.IGNORECASE)
    #Remove dirty html with inner text
    removeTagsWithInnerHTML = ["blockquote", "pre", "script", "sup", "sub"]
    for tag in removeTagsWithInnerHTML:
      regex = '\<\s*'+tag+'(\s+[^\>]*)?\>(.*?)\<\s*\/\s*'+tag+'\s*\>'
      s = re.sub(regex, ' ', s, flags=re.DOTALL|re.IGNORECASE)
    #Condense multiple whitespaces to single space
    s = re.sub('\s+', ' ', s)
    #Remove dirty html tags
    removeTags = [["a",""],
                  ["address","\n"],
                  ["b",""],
                  ["br","\n"],
                  ["center", "\n"],
                  ["div","\n"],
                  ["em",""],
                  ["font", ""],
                  ["hr", "\n"],
                  ["i", ""],
                  ["p", "\n"],
                  ["strong",""],
                  ["table", "\n"],
                  ["thead", "\n"],
                  ["tbody", "\n"],
                  ["tfoot", "\n"],
                  ["th", " "],
                  ["td", " "],
                  ["tr", "\n"],
                  ["tt", ""],
                  ["u", ""],
                  ["ol","\n"],
                  ["ul","\n"],
                  ["dl","\n"],
                  ["li","\n"],
                  ["dt"," "],
                  ["dd","\n"]
                 ]
    for tag in removeTags:
      regex = '\<\s*\/?\s*' + tag[0] + '(\s+[^\>]*)?\>'
      s = re.sub(regex, tag[1], s, flags=re.IGNORECASE)
    #Get images and captions
    imageCaptions = ["figure", "image", "fig", "graph", "table"]
    imageCaptionsRegex = "|".join(imageCaptions)
    regex = '\<\s*\/?\s*img(\s+[^\>]*)?\/?\>(\s*((' + imageCaptionsRegex + ')\s*[\.0-9a-zA-Z])+[^\n]*)?'
    s = re.sub(regex, self.imgSplitter, s, flags=re.IGNORECASE)
    #Condense multiple spaces and newlines independently to preserve semantic seperation
    s = re.sub(' +', ' ', s)
    s = re.sub('\s*\n\s*', '\n', s)
    s = s.strip()
    return s

  def xmlNormalizer(self, s):
    s = re.sub('\<[^\>]*\>', '', s)
    remapEncodings = [
      #These stay as it is (http://en.wikipedia.org/wiki/List_of_XML_and_HTML_character_entity_references):
      ['"', '&quot;'],['\'', '&apos;'],['& ', '&amp; '],['<', '&lt;'],['>', '&gt;'],
      #These get replaced with closest ascii:
      ['&#128;', 'E'],
      ['&#129;', ' '],
      ['&#134;', 'T'],
      ['&#140;', 'CE'],
      ['&#145;', '\''],
      ['&#146;', '\''],
      ['&#147;', '"'],
      ['&#148;', '"'],
      ['&#153;', '(TM)'],
      ['&#160;', ' '],
      ['&#169;', '(C)'],
      ['&#170;', 'a'],
      ['&#174;', '(R)'],
      ['&#176;', 'o'],
      ['&#185;', '1'],
      ['&#228;', 'a'],
      ['&#241;', 'n'],
      ['&#252;', 'u'],
      ['&#59;', ';'],
      ['&alpha;', 'a'],
      ['&auml;', 'a'],
      ['&ccedil;', 'c'],
      ['&eacute;', 'e'],
      ['&ecirc;', 'e'],
      ['&egrave;', 'e'],
      ['&iuml;', 'i'],
      ['&nbsp;', ' '],
      ['&ouml;', 'o'],
      ['&szlig;', 'B'],
      ['&uuml;', 'u']
    ]
    for remap in remapEncodings:
      s = re.sub(re.escape(remap[0]), remap[1], s, flags=re.IGNORECASE)
    s = re.sub('\s+', ' ', s).strip()
    return s

  def titleNormalizer(self, s):
    nonTitles = {"a", "and", "at", "by", "for", "from", "in", "is", "of", "on", "the", "to"}
    s = re.sub('^[^a-zA-Z]*','',s)
    s = re.sub('\s+', ' ', s)
    title = []
    for word in s.strip().split():
      if(len(title)==0 or word.lower() not in nonTitles): title.append(word.title())
      else: title.append(word.lower())
    return self.xmlNormalizer(" ".join(title))

  def sectionSplitter(self, s, hLevel, sLevel):
    regex = '\<\s*h'+str(hLevel)+'(\s+[^\>]*)?\>(.*?)\<\s*\/\s*h'+str(hLevel)+'\s*\>'
    sections=[]
    sections_start=0
    for section in re.finditer(regex,s, flags=re.DOTALL|re.IGNORECASE):
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
      if   (section[0]==""): self.sectionSplitter(s[section[1]:section[2]], hLevel+1, sLevel)
      elif (section[0]=="Keywords"): self.keywordSplitter(s[section[1]:section[2]])
      elif (section[0]=="References"): self.referenceSplitter(s[section[1]:section[2]])
      else:
        self.xmlFileHandle.write('\t'*sLevel+'<section name="%s">\n'%(section[0]))
        self.sectionSplitter(s[section[1]:section[2]], hLevel+1, sLevel+1)
        self.xmlFileHandle.write('\t'*sLevel+'</section>\n')

  def authorSplitter(self, s):
    emails = []
    s = re.sub("\<h[1-9].*$", "", s, flags=re.DOTALL|re.IGNORECASE)
    for email in re.finditer('[\s\,^]([a-zA-Z0-9\-\_\.]+)\s*\@\s*([a-zA-Z0-9\-\_\.]+)[\s\,\;$]', s):
      emails += [(email.group(1)+'@'+email.group(2), email.start(), email.end())]
    for email in re.finditer('[\s\,^](\{|\&lt\;)([a-zA-Z0-9\-\_\.\,\s]+)(\}|\&gt\;)\s*\@\s*([a-zA-Z0-9\-\_\.]+)[\s\,\;$]', s):
      for chunk in email.group(2).split(","):
        emails += [(chunk.strip()+'@'+email.group(4), email.start(), email.end())]
    #print("\n")
    #if(re.search("keywords",s,flags=re.IGNORECASE)): print("key")
    #if(re.search("abstract",s,flags=re.IGNORECASE)): print("abs")
    #print(emails)
    authors = [["author1","author1@example.com","MIT"], ["author2","author2@example.com","CMU"]]
    for author in authors:
      self.xmlFileHandle.write('\t\t\t<author name="%s" email="%s" organization="%s"/>\n'%(author[0],author[1],author[2]))

  def lineSmoothener(self, l, r):
    if(len(r)<7): return True
    if(len(l)<5): return True
    if(len(r.split())<3): return True
    if(len(l.split())<3): return True
    if(not re.match('[A-Z]',r[0])): return True
    if(re.match('\s[^\.]$',l)): return True
    if((l.split()[-1]).lower() in ["eg", "e.g", "vs"]): return True
    if(l.count('(')!=l.count(')')): return True
    if(l.count('[')!=l.count(']')): return True
    if(l.count('{')!=l.count('}')): return True
    if((l.count('&quot;') % 2)==1): return True
    return False

  def imgLineMatcher(self, imgAlt, line):
    if(imgAlt==""): return False
    if(re.search(re.escape(imgAlt.lower())+'([^0-9]|$)',line.lower())): return True
    return False

  def lineRefSplitter(self, r):
    self.ref += r.group(1).split(",")
    return ""

  def lineSplitter(self, s, sLevel):
    if(sLevel<2): return
    if('\n' in s):
      for multiline in s.split('\n'): self.lineSplitter(multiline, sLevel)
      return
    s = self.xmlNormalizer(s)
    lines_broken = [line.strip() for line in s.split(". ") if re.search('\S',line)]
    lines_smoothened = []
    for line in lines_broken:
      if(len(lines_smoothened)>0 and self.lineSmoothener(lines_smoothened[-1], line)):
        lines_smoothened[-1] = lines_smoothened[-1]+'. '+line
      else:
        lines_smoothened.append(line)
    lines = [re.sub('\.+','.',(line.strip()+'.')) for line in lines_smoothened if re.search('\S',line)]
    lines = [re.sub('\s+',' ',line) for line in lines if line!="."]
    for line in lines:
      img=",".join([image[0] for image in self.Images if self.imgLineMatcher(image[2],line)])
      self.ref=[]
      line = re.sub('\[([ 0-9\,]*)\]', self.lineRefSplitter, line)
      ref=",".join([r.strip() for r in self.ref if re.search('\S',r)])
      self.xmlFileHandle.write('\t'*sLevel+'<line ref="%s" img="%s">%s</line>\n'%(ref,img,line))

  def keywordSplitter(self, s):
    self.Keywords += [self.xmlNormalizer(re.sub('[\.]','',k.strip())) for k in s.split(",")]

  def imgSplitter(self, r):
    imgId = str(len(self.Images)+1)
    imgSrc = ""
    imgAlt = ""
    imgCaption = ""
    imgSrcMatch = re.search('src\s*=\s*[\'"]([^\'"]*)[\'"]', r.group(1), flags=re.IGNORECASE)
    if(imgSrcMatch): imgSrc = imgSrcMatch.group(1).replace('"','&quot;')
    imgAltMatch = re.search('alt\s*=\s*[\'"]([^\'"]*)[\'"]', r.group(1), flags=re.IGNORECASE)
    if(imgAltMatch): imgAlt = self.xmlNormalizer(imgAltMatch.group(1))
    if(r.group(2)): imgCaption = self.xmlNormalizer(r.group(2))
    if(r.group(3) and imgAlt==""): imgAlt = self.xmlNormalizer(re.sub('\.','',r.group(3)))
    self.Images += [[imgId, imgSrc, imgAlt, imgCaption]]
    return r.group(2)

  def referenceSplitter(self, s):
    refs = [ref.strip() for ref in s.split("\n") if re.search('\S',ref)]
    refID=1
    for ref in refs:
      ref = re.sub('^'+str(refID)+'\s*\.\s*', '', ref)
      self.References += [[str(refID), self.xmlNormalizer(ref)]]
      refID+=1

#Command line boilerplate
if (__name__=="__main__"):
  if(len(sys.argv)!=3):
    print("usage: %s htmlFile xmlFile" %sys.argv[0])
    exit(-1)
  exit(Parser(sys.argv[1], sys.argv[2]).run())
