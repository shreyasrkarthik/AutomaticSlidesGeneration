#!/usr/bin/python

# Run file as executable
# ./PDFParser.py

import sys
import os
from binascii import b2a_hex

from lxml import html
import ntpath

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument, PDFNoOutlines
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure, LTImage, LTChar





###
### Extracting Text
###






###
### Processing Pages
###





class ElementsForSlides():
    pass


def PDFToHTML(path_to_file):
    """One can use pdf2html utility of PDFMiner to get points."""
    old_working_directory = os.getcwd()
    file_name = ntpath.basename(path_to_file)
    file_name_without_extension, file_extension = os.path.splitext(file_name)
    os.chdir("InputFiles")
    input_file_folder = file_name_without_extension + "_Data"
    os.system("mkdir " + input_file_folder)
    os.chdir(input_file_folder)
    # do not know if this is not needed
    os.system("cp "+path_to_file+" "+file_name)
    # get images as separate files as well as group images by page
    os.system("pdftohtml -s "+file_name)
    converted_html_file = file_name_without_extension+"-html.html"
    os.chdir(old_working_directory)

def GetRecognisedElements(path_to_html_file):
    """
    Titles -
        Main Title of pdf usually has class - "ft10"
        in pages usually have font sizes more in their classes
            requires heavy work because of diversity
        Bold tags <b> can help in identifying sections and subsections
    Bullets of same level And Paragraph-
        Are enclosed in same <p> tag with <br> tag between them.
        To differentiate between points and paragraph requires NLP I guess.
    Pages are separated by divs with different ids - "page*-div"
    :param path_to_html_file: The full path of the html file generated for the pdf input
    :return: object of title, bullets as of now
    """
    recognised_elements = ElementsForSlides()
    file_descriptor = open(path_to_html_file,"r")
    html_string = "".join(file_descriptor.readlines())
    htmlTreeParser = html.fromstring(html_string)
    recognised_elements.main_heading = htmlTreeParser.xpath('//p[@class="ft10"]//text()')[0]
    recognised_elements.all_pTags_in_pdf = htmlTreeParser.xpath('//p//text()')
    return recognised_elements




# PDFToHTML("/home/sudharshanasl/Downloads/imagefile.pdf")
"""
    file : imagefile.pdf
    description : pdf with paragraphs and images
    comments :
        1) pdf has paragraph with different font.
            - this caused malformed lines in html
        2) images and text are grouped by page in html
        3) need to check if images are recognised with formats and generated
"""
# PDFToHTML("/home/sudharshanasl/PycharmProjects/AutomaticSlidesGeneration/prototype/parser/InputFiles/ForPoints.pdf")
# PDFToHTML("/home/sudharshanasl/Education/GitHub/The-Git-Tutorial-1.pdf")

elements_of_html = GetRecognisedElements("/home/sudharshanasl/PycharmProjects/AutomaticSlidesGeneration/prototype/parser/InputFiles/imagefile_Data/imagefile-html.html")
print elements_of_html.main_heading
