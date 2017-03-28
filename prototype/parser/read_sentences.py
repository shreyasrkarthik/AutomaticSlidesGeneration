import re
def get_sentences(file_name):
	with open(file_name, 'rb') as fp:
		text = fp.read()
		sentences = re.split('[\.]', text)
		sentences = [x.replace("\n", "") for x in sentences if x]
		return sentences

file_name = 'sample_contents2.txt'
for x in get_sentences(file_name):
	print x 