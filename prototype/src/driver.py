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
                    yield sentence
            yield last

    def driver(self, filepath):
        weights = {'SWP': 0.2, 'NOWT': 0.4, 'NNP': 0.3, 'NVP': 0.1}

        SWPValues = {}
        NOWTValues = {}
        NNPValues = {}
        NVPValues = {}

        currentSent = 1
        title = "Process"
        sentences = []
        filteredSentences = []

        for sentence in self.read_sentences(filepath):
            sentences.append(sentence)
            tokenArray = word_tokenize(sentence)
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


        for i in range(1, totalSent):
            if((SWPValues[i] <= SWPThreshold) and (NOWTValues[i] >= NOWTThreshold) and (NNPValues[i] >= NNPThreshold) and (NVPValues[i]) >= NVPThreshold):
                    filteredSentences.append(sentences[i])
        print filteredSentences

        LinesScore = {}
        # for sentNum in filteredSentences:
        #     score = ((SWPValues[sentNum] * weights['SWP']) + (NOWTValues[sentNum] * weights['NOWT']) + (NNPValues[sentNum] * weights['NNP']) + (NVPValues[sentNum] * weights['NNP']))
        #     LinesScore[sentNum] = score
        #
        # SortedDict = sorted(LinesScore.items(), key=operator.itemgetter(0))
        # return SortedDict


if __name__ == '__main__':
    d = Driver()
    print(d.driver("sample_3_1.txt"))

