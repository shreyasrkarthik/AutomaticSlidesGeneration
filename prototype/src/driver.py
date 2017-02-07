from FeatureExtractor import FeatureExtractor as fe
import operator
from nltk.tokenize import sent_tokenize
from nltk import word_tokenize


class Driver:
    
    def getThreshold(self, featureValuesDict):
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
        filteredSentences = []

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

        SWPThreshold = self.getThreshold(SWPValues)
        NOWTThreshold = self.getThreshold(NOWTValues)
        NNPThreshold = self.getThreshold(NNPValues)
        NVPThreshold = self.getThreshold(NVPValues)
        count = 0

        # for i in range(1, totalSent-1):
        #     if((SWPValues[i] <= SWPThreshold) or (NOWTValues[i] >= NOWTThreshold) or (NNPValues[i] >= NNPThreshold) or (NVPValues[i]) >= NVPThreshold):
        #             print "----", sentences[i]
        #             filteredSentences.append(sentences[i])
        #     else: count += 1
        # print filteredSentences, len(filteredSentences), count

        LinesScore = {}
        for sent_num in range(1, totalSent-1):
            score = ((SWPValues[sent_num] * weights['SWP']) + (NOWTValues[sent_num] * weights['NOWT']) + (NNPValues[sent_num] * weights['NNP']) + (NVPValues[sent_num] * weights['NNP']))
            if score > 10.0:
                filteredSentences.append(sentences[sent_num])
            LinesScore[sent_num] = (score, sentences[sent_num])

        SortedDict = sorted(LinesScore.items(), key=operator.itemgetter(1), reverse=True)
        return SortedDict

    def extractSentFromDict(self, sortedSentDict):
        num_sent = len(sortedSentDict)
        num_extract = int(num_sent * 0.3)
        output = []
        count=1
        for k,v in sortedSentDict:
            sent = v[1]
            output.append(sent)
            if(count > num_extract):
                return output
            count += 1
        return output

if __name__ == '__main__':
    d = Driver()
    sortedSentDict = d.driver("sample_3_1.txt")
    print(d.extractSentFromDict(sortedSentDict))