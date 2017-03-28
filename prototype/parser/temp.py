# pdfx usage: http://pdfx.cs.man.ac.uk/usage
# requests docs: http://docs.python-requests.org/en/latest/user/quickstart/#post-a-multipart-encoded-file
import requests # get it from http://python-requests.org or do 'pip install requests'

url = "http://pdfx.cs.man.ac.uk"

def pypdfx(filename):
	fin = open(filename + '.pdf', 'rb')
	files = {'file': fin}
	try:
		print 'Sending', filename, 'to', url
		r = requests.post(url, files=files, headers={'Content-Type':'application/pdf'})
		print 'Got status code', r.status_code
	finally:
		fin.close()
	fout = open(filename + '.xml', 'w')
	fout.write(r.content)
	fout.close()
	print 'Written to', filename + '.xml'

if __name__ == '__main__':
  # self promotion - get the pdf file here: http://onlinelibrary.wiley.com/doi/10.1111/j.1558-5646.2012.01576.x/abstract
  	filename = '/home/pramod/AutomaticSlidesGeneration/prototype/parser/InputFiles/ForPoints_Data/ForPoints'
	pypdfx(filename)