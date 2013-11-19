#!/usr/bin/env python

import os
import re
import sys
import datetime
import xml.etree.ElementTree as ET
from PIL import Image
from latexslides import *

class Generator(object):
    """ Generator Class to generate slides from a XML file """

    def __init__(self, xml_file_path, out_dir_path, img_dir_path):
        self.MAXIMUM_CHARS_PER_SLIDE = 550
        self.MAXIMUM_CHARS_IN_CAPTION = 110
        self.xml_file_path = xml_file_path
        self.out_dir_path = out_dir_path
        self.tmp_dir_path = os.path.join(self.out_dir_path, "tmp")
        try:
            if not os.path.exists(self.out_dir_path):
                os.makedirs(self.out_dir_path)
            if not os.path.exists(self.tmp_dir_path):
                os.makedirs(self.tmp_dir_path)
        except:
            sys.stderr.write("%s is not a Valid Directory" % (self.tmp_dir_path))
            sys.exit(1)
        self.img_dir_path = img_dir_path
        self.xml_tree = ET.parse(self.xml_file_path)
        self.xml_root = self.xml_tree.getroot()
        self.images = self.get_image_details()
        self.images_considered = []
        self.references = self.get_references_details()
        self.number_of_sections = self.get_number_of_sections()
        self.new_command = """{\\newauthor}[2]{\parbox{0.26\\textwidth}{\\texorpdfstring{\centering #1 \\\\{\scriptsize{\urlstyle{same}\url{#2}\urlstyle{tt}}}}{#1}}}"""

    def generate(self):
        title = self.get_title()
        author_and_inst = self.get_authors_details()
        toc_heading = "Sections"
        if self.number_of_sections > 15:
            toc_heading = None
        short_title = "" #self.get_short_author()
        short_author = " " #self.get_short_author()
        #BeamerThemes: shadow, simula, hpl1, Pittsburgh, Rochester, Montpellier, CambridgeUS, Bergen, Antibes
        #ColorThemes: default, seahorse, beaver, lily, orchid
        slides = BeamerSlides(title=title,
                              author_and_inst=author_and_inst,
                              toc_heading=toc_heading,
                              header_footer=True,
                              beamer_theme="Antibes",
                              beamer_colour_theme="default",
                              short_author=short_author,
                              short_title=short_title,
                              newcommands=[self.new_command]
                             )

        collection = self.get_collection()
        slides.add_slides(collection)

        # Dump to file
        output_file_name = os.path.basename(self.xml_file_path)
        output_file_name = os.path.splitext(output_file_name)[0] + ".tex"
        output_file_name = os.path.join(self.out_dir_path, output_file_name)
        slides.write(output_file_name)
    
    def get_number_of_sections(self):
        return len(self.xml_root.findall("section"))

    def get_short_title(self):
        return ""
        return datetime.date.today().strftime("%B %d, %Y")

    def get_short_author(self):
        short_author = []
        about_element = self.xml_root.find("about")
        authors_element = about_element.find("authors")
        for author in authors_element.findall("author"):
            short_author += [author.get("name").split()[0]]
        return ", ".join(short_author)

    def get_title(self):
        about_element = self.xml_root.find("about")
        title_element = about_element.find("title")
        title = title_element.text
        return title

    def get_authors_details(self):
        authors_details = []
        about_element = self.xml_root.find("about")
        authors_element = about_element.find("authors")
        """
        authors = [author.get("name") for author in authors_element.findall("author")]
        emails = [author.get("email") for author in authors_element.findall("author")]
        organs = [author.get("organization") for author in authors_element.findall("author")]
        maxCharsPerLine = 50
        spaces = "\\ "*((maxCharsPerLine-(sum([len(x) for x in authors])))/(len(authors)-1))
        line1 = spaces.join(authors)
        spaces = "\\ "*((maxCharsPerLine-(sum([len(x) for x in emails])))/(len(emails)-1))
        line2 = spaces.join(emails)
        spaces = "\\ "*((maxCharsPerLine-(sum([len(x) for x in organs])))/(len(organs)-1))
        line3 = spaces.join(organs)
        authors_details = [(line1,line2+'\\newline '+line3)]
        """
        for author in authors_element.findall("author"):
            author_name = author.get("name")
            if len(author_name.strip()) == 0:
                author_name = "Author"
            email = author.get("email")
            if len(email.strip()) == 0:
                email = "email@email.com"
            author_and_email = self.get_author_and_email(author_name, email)
            #details = [author_and_email]
            details = ["\\newauthor{" + author_name + "}{" + email + "}"]
            #details = [author.get("name")]# + "\ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ Email: " + "email@email.com"]
            #details = ["\\texorpdfstring{Author\\newline\url{email@email.com}}{Author}"]
            organizations = []
            if len(author.get("organization").strip()) == 0:
                organizations = ["Organization"]
            else:
                organizations = author.get("organization").split()
            details += organizations
            authors_details += [tuple(details)]
        
        #authors = authors_element.findall("author")
        #authors_details = [tuple(["Author1","a@b.com    c@d.com"])]
        #authors_details += [tuple(['Author1\\newline Author2',""])]
        return authors_details

    def get_author_and_email(self, author_name, email):
        spaces_inbetween = 6
        total_spaces = 60 - (len(author_name) + len(email) + spaces_inbetween)
        author_and_email = author_name
        for i in range(spaces_inbetween):
            author_and_email += "\ "
        author_and_email += email
        for i in range(total_spaces):
            author_and_email = "\ " + author_and_email
        return author_and_email

    def get_image_details(self):
        images = {}
        images_element = self.xml_root.find("images")
        for image in images_element.findall("image"):
            _id = image.get("id")
            img_src = os.path.join(self.img_dir_path, image.get("src"))
            img_name = os.path.basename(img_src)
            img_name = os.path.splitext(img_name)[0]
            new_img_name = os.path.join(self.tmp_dir_path, img_name + ".jpeg")
            image_file = Image.open(img_src)
            width, height = image_file.size
            #image_file = image_file.resize((300, 260), Image.ANTIALIAS)
            if image_file.mode != "RGB":
                image_file = image_file.convert("RGB")
            image_file.save(new_img_name, "JPEG")
            _src = os.path.join("tmp", img_name + ".jpeg")
            _caption = image.get("caption")
            if len(_caption) > self.MAXIMUM_CHARS_IN_CAPTION:
                _caption = ""
            _alt = image.get("alt")
            images[_id] = {"src": _src,
                           "caption": _caption,
                           "alt": _alt,
                           "width": width,
                           "height": height
                          }
        return images

    def get_references_details(self):
        references = {}
        references_element = self.xml_root.find("references")
        for reference in references_element.findall("reference"):
            _id = reference.get("id")
            _text = reference.text
            references[_id] = {"text": _text}
        return references

    def get_collection(self):
        collection = []
        sections = self.xml_root.findall("section")
        for section_element in sections:
            title = section_element.get("name")
            short_title = title
            section = Section(title=title, short_title=short_title)
            collection += [section]
            collection += self.get_slides_for_section(section_element)
        collection += [self.get_end_slide()]
        return collection
    
    def get_end_slide(self):
        slide = RawSlide(rawtext="\\begin{frame}\Huge{\centerline{Thank You!}}\end{frame}")
        return slide

    def escape_special_characters(self, text):
        character_mapping = {"%": "\\%", 
                             "#": "\\#", 
                             "&quot;": "\"", 
                             "&amp;": "\\&", 
                             "&lt;": "$<$", 
                             "&gt;": "$>$",
                             "<": "$<$",
                             ">": "$>$",
                             "&apos;": "'",
                             "&": "\&"
                            }
        for character in character_mapping:
            text = text.replace(character, character_mapping[character])
        return text

    def get_slides_for_lines(self, title, lines):
        slides = []
        number_of_lines = len(lines)
        total_chars = 0
        lines_considered = []
        image_ids = []
        references = "\\bigskip"
        reference_ids_considered = []
        for line in lines:
            line_text = self.escape_special_characters(line.text);
            if line_text is None or len(line_text) == 0:
                continue
            line_length = len(line_text)
            current_references = []
            reference_ids = line.get("ref").split(",")
            for reference_id in reference_ids:
                if not reference_id is None and len(reference_id) != 0 and len(self.references[reference_id]["text"]) != 0 and reference_id not in reference_ids_considered:
                    current_references += ["\\tiny{" + self.escape_special_characters(self.references[reference_id]["text"]) + "}"]
                    reference_ids_considered += [reference_id]
            #reference = "\\\\\n".join(current_references)
            reference = "\\vspace*{1\\baselineskip}".join(current_references)
            if total_chars + line_length + len(reference)/2 > self.MAXIMUM_CHARS_PER_SLIDE:
                slide = Slide(title,
                              [BulletList(lines_considered), Text(text=references)]
                             )
                slides += [slide]
                slides += self.get_slides_for_images(image_ids)
                lines_considered = []
                total_chars = 0
                image_ids = []
                references = "\\bigskip"
                reference_ids_considered = []
            total_chars = total_chars + line_length
            lines_considered += [line_text]
            image_id = line.get("img")
            if not reference is None and len(reference) != 0:
                references = references + "\\vspace*{1\\baselineskip}" + reference
            if not image_id is None and len(image_id) != 0:
                current_image_ids = image_id.split(",")
                for current_image_id in current_image_ids:
                    if current_image_id not in self.images_considered:
                        image_ids += [current_image_id]
                        self.images_considered += [current_image_id]
        if len(lines_considered) > 0:
            slide = Slide(title,
                          [BulletList(lines_considered), Text(text=references)]
                         )
            slides += [slide]
            slides += self.get_slides_for_images(image_ids)
        return slides

    def get_slides_for_images(self, image_ids):
        slides = []
        for image_id in image_ids:
            title = self.escape_special_characters(self.images[image_id]["caption"])
            figure_path = self.images[image_id]["src"]
            figure_fraction_width = 217.0/self.images[image_id]["height"]
            figure_fraction_width = min(figure_fraction_width, 312.0/self.images[image_id]["width"])
            slide = Slide(title=title,
                          figure=figure_path,
                          figure_fraction_width = figure_fraction_width,
                         )
            slides += [slide]
        return slides

    def get_slides_for_section(self, section_element):
        lines = []
        image_ids = []
        slides = []
        title = section_element.get("name")
        lines = section_element.findall("line")
        slides += self.get_slides_for_lines(title, lines)
        for subsection_element in section_element.findall("section"):
            sub_title = subsection_element.get("name")
            subsection = SubSection(title=sub_title)
            #slides += [subsection]
            slides += self.get_slides_for_section(subsection_element)
        return slides


def main(xml_file_path, out_dir_path, img_dir_path):
    generator = Generator(xml_file_path, out_dir_path, img_dir_path)
    generator.generate()

if __name__ == "__main__":
    if(len(sys.argv) != 4):
        print("usage: %s <xmlFile> <outDir> <imgDir>" %sys.argv[0])
        exit(-1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
