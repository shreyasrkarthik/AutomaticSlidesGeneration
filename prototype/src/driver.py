from FeatureExtractor import *
import operator

class Driver:
    def getTokens(self, line):
        return line.split(' ')

    def getThreshold(self, featureValuesDict):
        featureValues = list(featureValuesDict.values())
        return sum(featureValues) / float(len(featureValues))

    def driver(self, filePath):
        weights = {'SWP': 0.2, 'NOWT': 0.4, 'NNP': 0.3, 'NVP': 0.1}

        SWPValues = dict()
        NOWTValues = dict()
        NNPValues = dict()
        NVPValues = dict()

        currentLine = 1
        title = "What is a Process"
        finalTextLines = []
        with open(filePath, 'r') as fp:
            for line in fp:
                tokenArray = Driver.getTokens(line)
                SWPValues[currentLine] = FeatureExtractor.getStopWordsPerc(tokenArray)
                NOWTValues[currentLine] = FeatureExtractor.getNumOverlappingWords(title, line)
                NNPValues[currentLine] = FeatureExtractor.getNumNounPhrases(tokenArray)
                NVPValues[currentLine] = FeatureExtractor.getNumVerbPhrases(tokenArray)
                currentLine+=1

        totalLines = currentLine

        SWPThreshold = Driver.getThreshold(SWPValues)
        NOWTThreshold = Driver.getThreshold(NOWTValues)
        NNPThreshold = Driver.getThreshold(NNPValues)
        NVPThreshold = Driver.getThreshold(NVPValues)


        for i in range(1,totalLines):
            if((SWPValues[currentLine] <= SWPThreshold) and (NOWTValues[currentLine] >= NOWTThreshold) and (NNPValues[currentLine] >= NNPThreshold) and (NVPValues[currentLine]) >= NVPThreshold):
                    finalTextLines.append(i)

        # scoreThreshold = 50
        LinesScore = dict()
        for lineNo in finalTextLines:
            score = ((SWPValues[lineNo] * weights['SWP']) + (NOWTValues[lineNo] * weights['NOWT']) + (NNPValues[lineNo] * weights['NNP']) + (NVPValues[lineNo] * weights['NNP']))
            LinesScore[lineNo] = score

        SortedDict = sorted( LinesScore.items(), key=operator.itemgetter(1))



