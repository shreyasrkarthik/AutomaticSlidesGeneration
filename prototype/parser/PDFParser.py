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

import requests

def with_pdf (pdf_doc, fn, pdf_pwd, *args):
    result = None
    try:
        # open the pdf file
        fp = open(pdf_doc, 'rb')
        # create a parser object associated with the file object
        parser = PDFParser(fp)
        # create a PDFDocument object that stores the document structure
        doc = PDFDocument(parser)
        # connect the parser and document objects
        parser.set_document(doc)
        # supply the password for initialization
        #doc._initialize_password(pdf_pwd)


        if doc.is_extractable:
            # apply the function and return the result
            result = fn(doc, *args)

        # close the pdf file
        fp.close()
    except IOError:
        # the file doesn't exist or similar problem
        pass
    return result


###
### Table of Contents
###

def _parse_toc (doc):
    """With an open PDFDocument object, get the table of contents (toc) data
    [this is a higher-order function to be passed to with_pdf()]"""
    toc = []
    try:
        outlines = doc.get_outlines()
        for (level,title,dest,a,se) in outlines:
            toc.append( (level, title) )
    except PDFNoOutlines:
        pass
    return toc

def get_toc (pdf_doc, pdf_pwd=''):
    """Return the table of contents (toc), if any, for this pdf file"""
    return with_pdf(pdf_doc, _parse_toc, pdf_pwd)


###
### Extracting Images
###

def write_file (folder, filename, filedata, flags='w'):
    """Write the file data to the folder and filename combination
    (flags: 'w' for write text, 'wb' for write binary, use 'a' instead of 'w' for append)"""
    result = False
    if os.path.isdir(folder):
        try:
            file_obj = open(os.path.join(folder, filename), flags)
            file_obj.write(filedata)
            file_obj.close()
            result = True
        except IOError:
            pass
    return result

def determine_image_type (stream_first_4_bytes):
    """Find out the image file type based on the magic number comparison of the first 4 (or 2) bytes"""
    file_type = None
    bytes_as_hex = b2a_hex(stream_first_4_bytes)
    if bytes_as_hex.startswith('ffd8'):
        file_type = '.jpeg'
    elif bytes_as_hex == '89504e47':
        file_type = '.png'
    elif bytes_as_hex == '47494638':
        file_type = '.gif'
    elif bytes_as_hex.startswith('424d'):
        file_type = '.bmp'
    return file_type

def save_image (lt_image, page_number, images_folder):
    """Try to save the image data from this LTImage object, and return the file name, if successful"""
    result = None
    if lt_image.stream:
        file_stream = lt_image.stream.get_rawdata()
        if file_stream:
            file_ext = determine_image_type(file_stream[0:4])
            if file_ext:
                file_name = ''.join([str(page_number), '_', lt_image.name, file_ext])
                if write_file(images_folder, file_name, file_stream, flags='wb'):
                    result = file_name
    return result


###
### Extracting Text
###

def to_bytestring (s, enc='utf-8'):
    """Convert the given unicode string to a bytestring, using the standard encoding,
    unless it's already a bytestring"""
    if s:
        if isinstance(s, str):
            return s
        else:
            return s.encode(enc)

def update_page_text_hash (h, lt_obj, pct=0.2):
    """Use the bbox x0,x1 values within pct% to produce lists of associated text within the hash"""

    x0 = lt_obj.bbox[0]
    x1 = lt_obj.bbox[2]

    key_found = False
    for k, v in h.items():
        hash_x0 = k[0]
        if x0 >= (hash_x0 * (1.0-pct)) and (hash_x0 * (1.0+pct)) >= x0:
            hash_x1 = k[1]
            if x1 >= (hash_x1 * (1.0-pct)) and (hash_x1 * (1.0+pct)) >= x1:
                # the text inside this LT* object was positioned at the same
                # width as a prior series of text, so it belongs together
                key_found = True
                v.append(to_bytestring(lt_obj.get_text()))
                h[k] = v
    if not key_found:
        # the text, based on width, is a new series,
        # so it gets its own series (entry in the hash)
        h[(x0,x1)] = [to_bytestring(lt_obj.get_text())]

    return h

def parse_lt_objs (lt_objs, page_number, images_folder, text=[]):
    """Iterate through the list of LT* objects and capture the text or image data contained in each"""
    text_content = []

    page_text = {} # k=(x0, x1) of the bbox, v=list of text strings within that bbox width (physical column)
    for lt_obj in lt_objs:
        if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
            # text, so arrange is logically based on its column width
            page_text = update_page_text_hash(page_text, lt_obj)
        elif isinstance(lt_obj, LTImage):
            # an image, so save it to the designated folder, and note its place in the text
            saved_file = save_image(lt_obj, page_number, images_folder)
            if saved_file:
                # use html style <img /> tag to mark the position of the image within the text
                text_content.append('<img src="'+os.path.join(images_folder, saved_file)+'" />')
            else:
                print >> sys.stderr, "error saving image on page", page_number, lt_obj.__repr__
        elif isinstance(lt_obj, LTFigure):
            # LTFigure objects are containers for other LT* objects, so recurse through the children
            text_content.append(parse_lt_objs(lt_obj, page_number, images_folder, text_content))

    for k, v in sorted([(key,value) for (key,value) in page_text.items()]):
        # sort the page_text hash by the keys (x0,x1 values of the bbox),
        # which produces a top-down, left-to-right sequence of related columns
        text_content.append(''.join(v))

    return '\n'.join(text_content)


###
### Processing Pages
###

def _parse_pages (doc, images_folder):
    """With an open PDFDocument object, get the pages and parse each one
    [this is a higher-order function to be passed to with_pdf()]"""
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    text_content = []
    for i, page in enumerate(PDFPage.create_pages(doc)):
        interpreter.process_page(page)
        # receive the LTPage object for this page
        layout = device.get_result()
        # layout is an LTPage object which may contain child objects like LTTextBox, LTFigure, LTImage, etc.
        text_content.append(parse_lt_objs(layout, (i+1), images_folder))

    return text_content

def get_pages (pdf_doc, pdf_pwd='', images_folder='/tmp'):
    """Process each of the pages in this pdf file and
    return a list of strings representing the text found in each page"""
    return with_pdf(pdf_doc, _parse_pages, pdf_pwd, *tuple([images_folder]))


class ElementsForSlides():
    pass


def PDFToHTMLOrXML(path_to_file, to_xml = False):
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
    converted_file = None
    if not to_xml:
        os.system("pdftohtml -s "+file_name) #-s single html file
        converted_file = file_name_without_extension+"-html.html"
    else:
        os.system("pdftohtml -xml " + file_name)
        converted_file = file_name_without_extension + ".xml"
    os.chdir(old_working_directory)

def GetRecognisedElementsHTML(path_to_html_file):
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

def GetXMLFromOnlineAPI(path_to_file):
    """
    Get XML output from online API
    :param path_to_file: Full Path to the input PDF file.
    """
    api_url = "http://pdfx.cs.man.ac.uk"
    file_descriptor = open(path_to_file, 'rb')
    files_payload = {'file': file_descriptor}
    try:
        print 'Sending', path_to_file, 'to', api_url
        xml_result = requests.post(api_url, files=files_payload, headers={'Content-Type': 'application/pdf'})
        print 'Got status code', xml_result.status_code
    finally:
        file_descriptor.close()
    xml_result_file = open(path_to_file + '_API.xml', 'w')
    xml_result_file.write(xml_result.content)
    xml_result_file.close()
    print 'Written to', path_to_file + '.xml'

# arr = get_pages('sample.pdf','','/images')
# f = open('sample_contents.txt','w')
# for line in arr:
#     f.write(line)
#     f.write('\n')

"""
    file : imagefile.pdf
    description : pdf with paragraph, section, subsection, images
    file : ForPoints.pdf
    description : PDF with only points
    file : os-sample.pdf
    description : PDF of random pages from OS textbook
    file : The-Git-Tutorial-1.pdf
    description : PDF of Git tutorial
    PDF to HTML comments :
        Advantages :
            1) Easy to identify important words/ keypoints.
            2) Images and text are grouped by page in html.
            3) Images are recognised with formats and generated.
            4) Per Page analysis can be done for recognising section and subsection by looking into CSS3 class' font attribute values.
        Disadvantages :
            1) Tough to identify paragraphs.
            2) Tough to differentiate between bullets and paragraphs.
            3) Generated HTML DOM tree varies for each pdf.
                - Patterns for section, subsection and content will vary.
            4) PDF has paragraph with different font.
                - this caused malformed lines in html
            5) Logos or images repetition needs to be handled via hash history of images.
            6) Tables and Diagrams using shapes pose a serious problem.
        Next Steps :
            a) Write code for recognising paragraphs.
                - And then try to analyze if it is a point.
            b) Test code against many PDF inputs.
            c) Handle redundant generated images.
            d) Try to identify the section, subsection, key points, etc.,.
    PDF to XML comments :
        Advantages :
            1) Paragraphs can be identified in the files we have tested.
            2) There seems to be a pattern based on attributes of text tags through which we can recognise Tables.
            3) Unstructured Text Output can be suggested to user as diagram.
            4) Similar XML output for the PDFs we have tested against.
            5) Styling tags present to extract key points.
            6) Images grouped and named corresponding to page.
        Disadvantages :
            1) Need complex Tree Parsing algorithms to pick out the points because of varied styles employed by Authors
        Next Steps :
            1) Algorithm to identify paragraphs and tables.
            2) Pick images according to page numbers and generate slides.
            3) Also identify key points and put them into slide corresponding to page number.
    PDF to XML using API :
        Advantages :
            1) Paragraphs are already grouped.
            2) Titles are found withing tags with title in their names.
            3) Page Numbers can be identified.
        Disadvantages :
            1) Font styling is lost. Need to use NLP or Word2Vec to extract key points.
            2) Relying on the API. API server can go down without a notification from their side.
            3) Online Data extraction.
            4) Tough to test for 100s of PDFs.
            5) Images were not returned.
        Next Steps :
            1) Identify key points.
            2) Map paragraphs to page numbers and generate slides.
            3) Need to look into what other data one can extract from API result.
"""
# PDFToHTMLOrXML("/home/sudharshanasl/PycharmProjects/AutomaticSlidesGeneration/prototype/parser/InputFiles/imagefile.pdf")
# PDFToHTMLOrXML("/home/sudharshanasl/PycharmProjects/AutomaticSlidesGeneration/prototype/parser/InputFiles/ForPoints.pdf")
# PDFToHTMLOrXML("/home/sudharshanasl/Education/GitHub/The-Git-Tutorial-1.pdf")
# PDFToHTMLOrXML("/home/sudharshanasl/PycharmProjects/AutomaticSlidesGeneration/prototype/parser/InputFiles/os-sample.pdf")
# PDFToHTMLOrXML("//home/sudharshanasl/PycharmProjects/AutomaticSlidesGeneration/prototype/parser/InputFiles/imagefile.pdf",to_xml = True)
# PDFToHTMLOrXML("/home/sudharshanasl/PycharmProjects/AutomaticSlidesGeneration/prototype/parser/InputFiles/ForPoints.pdf",to_xml = True)
# PDFToHTMLOrXML("/home/sudharshanasl/Education/GitHub/The-Git-Tutorial-1.pdf",to_xml = True)
# PDFToHTMLOrXML("/home/sudharshanasl/PycharmProjects/AutomaticSlidesGeneration/prototype/parser/InputFiles/os-sample.pdf",to_xml=True)


# elements_of_html = GetRecognisedElementsHTML("/home/sudharshanasl/PycharmProjects/AutomaticSlidesGeneration/prototype/parser/InputFiles/imagefile_Data/imagefile-html.html")
# print elements_of_html.main_heading

GetXMLFromOnlineAPI("/home/sudharshanasl/PycharmProjects/AutomaticSlidesGeneration/prototype/parser/InputFiles/imagefile.pdf")
GetXMLFromOnlineAPI("/home/sudharshanasl/PycharmProjects/AutomaticSlidesGeneration/prototype/parser/InputFiles/os-sample.pdf")