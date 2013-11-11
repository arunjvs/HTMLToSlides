#!/usr/bin/env python

import os
import sys
import xml.etree.ElementTree as ET
from latexslides import *

class Generator(object):
    """ Generator Class to generate slides from a XML file """

    def __init__(self, xml_file_path):
        self.xml_file_path = xml_file_path
        self.xml_tree = ET.parse(self.xml_file_path)
        self.xml_root = self.xml_tree.getroot()
        self.images = self.get_image_details()
        self.references = self.get_references_details()
        self.MAXIMUM_CHARS_PER_SLIDE = 440
        
    def generate(self, output_file_name="presentation"):
        title = self.get_title()
        author_and_inst = self.get_authors_details()
        slides = BeamerSlides(title=title,
                              author_and_inst=author_and_inst,
                              toc_heading=None,
                              header_footer=True,
                              beamer_theme="shadow"
                             )

        collection = self.get_collection()
        slides.add_slides(collection)

        # Dump to file
        slides.write(output_file_name)

    def get_title(self):
        about_element = self.xml_root.find("about")
        title_element = about_element.find("title")
        title = title_element.text
        return title

    def get_authors_details(self):
        authors_details = []
        about_element = self.xml_root.find("about")
        authors_element = about_element.find("authors")
        for author in authors_element.findall("author"):
            details = [author.get("name")]
            details += author.get("organization").split()
            authors_details += [tuple(details)]
        return authors_details

    def get_image_details(self):
        images = {}
        images_element = self.xml_root.find("images")
        for image in images_element.findall("image"):
            _id = image.get("id")
            _src = image.get("src")
            _caption = image.get("caption")
            _alt = image.get("alt")
            images[_id] = {"src": _src,
                           "caption": _caption,
                           "alt": _alt
                          }
        return images

    def get_references_details(self):
        references = {}
        references_element = self.xml_root.find("references")
        for reference in references_element.findall("reference"):
            _id = reference.get("id")
            _text = reference.get("text")
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
        return collection

    def get_slides_for_lines(self, title, lines):
        slides = []
        number_of_lines = len(lines)
        total_chars = 0
        lines_considered = []
        for line in lines:
            line_length = len(line)
            if total_chars + line_length > self.MAXIMUM_CHARS_PER_SLIDE:
                slide = Slide(title,
                              [BulletList(lines_considered)]
                             )
                slides += [slide]
                lines_considered = []
                total_chars = 0
            total_chars = total_chars + len(line)
            lines_considered += [line]
        return slides

    def get_slides_for_images(self, image_ids):
        slides = []
        for image_id in image_ids:
            title = self.images[image_id]["caption"]
            figure_path = self.images[image_id]["src"]
            slide = Slide(title=title,
                          figure=figure_path
                         )
            slides += [slide]
        return slides

    def get_slides_for_section(self, section_element):
        lines = []
        image_ids = []
        slides = []
        title = section_element.get("name")
        for line in section_element.findall("line"):
            image_id = line.get("img")
            if image_id is not None and len(image_id) != 0:
                image_ids += [image_id]
            if line.text is not None and len(line.text) != 0:
                lines += [line.text]
        slides += self.get_slides_for_lines(title, lines)
        slides += self.get_slides_for_images(image_ids)
        for subsection_element in section_element.findall("section"):
            sub_title = subsection_element.get("name")
            subsection = SubSection(title=sub_title)
            #slides += [subsection]
            slides += self.get_slides_for_section(subsection_element)
        return slides


def main(xml_file_path):
    generator = Generator(xml_file_path)
    generator.generate("sample.tex")

if __name__ == "__main__":
    if(len(sys.argv)!=2):
        print("usage: %s xmlFile" %sys.argv[0])
        exit(-1)
    main(sys.argv[1])
