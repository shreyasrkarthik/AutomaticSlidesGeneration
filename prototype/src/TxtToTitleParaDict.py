import re


class TxtToTitleParaDict:
    def __init__(self):
        self.title_para_dict={}
        pass

    def readTextFile(self, path):
        with open(path, 'rb') as myfile:
            text = myfile.read()
        text = ''.join([i if ord(i) < 128 else ' ' for i in text])
        return text

    def createTitleParaDict(self, text):
        for line in text.splitlines():
            title = re.sub('[^a-zA-Z]', '', line)
            if title.isupper():
                title = re.sub('[^a-zA-Z \t.,]', '', line)
                self.title_para_dict[title] = []
            else:
                self.title_para_dict[title].append(line)
            print line

TxtToTitleParaDict().createTitleParaDict(TxtToTitleParaDict().readTextFile('sample_3_1.txt'))
