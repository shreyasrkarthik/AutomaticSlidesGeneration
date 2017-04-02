#!/usr/bin/ python

from FeatureExtractor import FeatureExtractor as fe
import operator
from nltk.tokenize import sent_tokenize
from nltk import word_tokenize
from gensim.summarization import summarize, keywords
from bullets_identifier import *
from SlideGenerator import *
from pptx import Presentation
from pptx.util import Inches, Pt
import sys

class Driver:
    
    def getThreshold(self, featureValuesDict):
        featureValues = list(featureValuesDict.values())
        return sum(featureValues) / float(len(featureValues))

    def keywords(self, text):
        return keywords(text, ratio=0.1, split=True)

    def read_sentences(self, filepath, chunk_size=10240):
        last = ""
        with open(filepath) as inp:
            while True:
                buf = inp.read(chunk_size)
                buf = ''.join([i if ord(i) < 128 else ' ' for i in buf])
                if not buf:
                    break
                sentences = sent_tokenize(last + buf)
                last = sentences.pop()
                for sentence in sentences:
                    yield sentence.replace('\n', ' ')
            yield last.replace('\n', ' ')

    def driver(self, filepath):
        weights = {'SWP': 0.1, 'NOWT': 0.5, 'NNP': 0.3, 'NVP': 0.1}

        SWPValues = {}
        NOWTValues = {}
        NNPValues = {}
        NVPValues = {}

        currentSent = 1
        title = "Process control blocks"
        sentences = []
        for sentence in self.read_sentences(filepath):
            sentences.append(sentence)
            tokenArray = word_tokenize(sentence)
            if len(tokenArray) > 2:
                SWPValues[currentSent] = fe().getStopWordsPerc(tokenArray)
                NOWTValues[currentSent] = fe().getNumOverlappingWords(title, sentence)
                NNPValues[currentSent] = fe().getNumNounPhrases(tokenArray)
                NVPValues[currentSent] = fe().getNumVerbPhrases(tokenArray)
                currentSent += 1

        totalSent = currentSent
        LinesScore = {}
        for sent_num in range(1, totalSent-1):
            score = ((SWPValues[sent_num] * weights['SWP']) + (NOWTValues[sent_num] * weights['NOWT']) + (NNPValues[sent_num] * weights['NNP']) + (NVPValues[sent_num] * weights['NNP']))
            LinesScore[sent_num] = (score, sentences[sent_num])

        sortedSentDict = sorted(LinesScore.items(), key=operator.itemgetter(1), reverse=True)
        return sortedSentDict

    def extractSentFromDict(self, sortedSentDict, topSentRatio = 0.4):
        filteredSentDict = dict(sortedSentDict[:int(len(sortedSentDict)*topSentRatio)])
        sortedSentDict = sorted(filteredSentDict.items())#sorted by occurance
        output = []
        for k, v in sortedSentDict:
            sent = v[1]
            output.append((k, sent))
        return output

    def create_presentation(self, file_name, title, sub_title, contents):
        prs = Presentation()
        create_title_slide(prs, title, sub_title)
        bullet_title = "Process and PCBs"
        k = 0
        for i in range(0,len(contents),5):
            bullets = contents[i:i+5]
            bullets.insert(0,"")
            # print bullets
            add_bullet_slide(prs, bullet_title, bullets)
            # setLogo(prs,(i/5)+1,'logo.png')
            setFooter(prs,(i/5)+1, 'PES Institute of Technology ISE Dept.')
        # add_text_slide(prs, ['jksdhflkadhsofhsakdhbf','asdfsfd'], 'TEXT HERE')
        prs.save(file_name+ '.pptx')

if __name__ == '__main__':
    d = Driver()
    print sys.argv[1]
    sortedSentDict = d.driver(sys.argv[1])
    sent_dict = d.extractSentFromDict(sortedSentDict)
    sent_dict = dict(sent_dict)
    important_sent_num =  sent_dict.keys()
    final_list = list(important_sent_num)
    sentences, bullet_map = identify_bullet_sentences(sys.argv[1]   )
    # print important_sent_num
    all_bullet_sentence_nos = []
    for bullet_data in bullets_map.values():
        all_bullet_sentence_nos.append(bullet_data["bullets"])
    # print all_bullet_sentence_nos
    # print len(important_sent_num)

    for sent_num in important_sent_num:
        for bullet_list in all_bullet_sentence_nos:
            if sent_num in bullet_list:
                final_list.extend(bullet_list)
                break

    final_list = sorted(set(final_list))
    sent_list = []
    for num in final_list:
        sent_list.append(sentences[num])
    d.create_presentation("process", "Process-OS", "Reference Slides", sent_list)


