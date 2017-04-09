import operator
from prototype.parser.BulletIdentifier import BulletIdentifier as bi
from nltk.tokenize import sent_tokenize
from FeatureExtractor import FeatureExtractor as fe
from prototype.SlideGenerator.SlideGenerator import SlideGenerator as sg
import argparse
from nltk import word_tokenize


class Driver:
    
    def get_threshold(self, featureValuesDict):
        featureValues = list(featureValuesDict.values())
        return sum(featureValues) / float(len(featureValues))

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

    def extract_sent_from_dict(self, sortedSentDict, topSentRatio = 0.4):
        filteredSentDict = dict(sortedSentDict[:int(len(sortedSentDict)*topSentRatio)])
        sortedSentDict = sorted(filteredSentDict.items())#sorted by occurance
        output = []
        for k, v in sortedSentDict:
            sent = v[1]
            output.append((k, sent))
        return output

if __name__ == '__main__':
    d = Driver()
    bi = bi()
    sg = sg()
    
    '''
        6 args
        1. text_file_path
        2. Title
        3. Subtitle
        4. output PPTX file name
        5. footer
        6. logo
    '''
    ap = argparse.ArgumentParser()
    ap.add_argument("-I", "--inputfile", required=True, help="Path to the input file")
    ap.add_argument("-O", "--outputfile", required=True, help="Name of the output file")
    ap.add_argument("-T", "--title", required=True, help="PPTX Title")
    ap.add_argument("-S", "--subtitle", required=False, help="PPTX SubTitle", default='')
    ap.add_argument("-F", "--footer", required=False, help="PPTX Footer", default='')
    ap.add_argument("-L", "--logo", required=False, help="PPTX logo", default='../SlideGenerator/logo.png')
    args = vars(ap.parse_args())
    
    input_file_path = args['inputfile']
    output_file_name = args['outputfile']
    ppt_title = args['title']
    ppt_sub_title = args['subtitle']
    ppt_footer = args['footer']
    ppt_logo = args['logo']
    
    sortedSentDict = d.driver(input_file_path)
    sent_dict = dict(d.extract_sent_from_dict(sortedSentDict))
    important_sent_num = sent_dict.keys()
    sent_num_list = list(important_sent_num)
    sentences, bullet_map = bi.identify_bullet_sentences(input_file_path)
    all_bullet_sentence_nos = []
    for bullet_data in bullet_map.values():
        all_bullet_sentence_nos.append(bullet_data["bullets"])

    for sent_num in important_sent_num:
        for bullet_list in all_bullet_sentence_nos:
            if sent_num in bullet_list:
                sent_num_list.extend(bullet_list)
                break

    sent_num_list = sorted(set(sent_num_list))
    sent_list = []
    for num in sent_num_list:
        sent_list.append(sentences[num])
    sg.create_presentation(output_file_name, ppt_title, ppt_sub_title, ppt_footer, ppt_logo, sent_list)


