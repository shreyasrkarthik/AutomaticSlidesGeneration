import FeatureExtractor as fe
import operator

class Driver:
    def getTokens(self, line):
        return line.split(' ')

    def getThreshold(self, featureValuesDict):
        featureValues = list(featureValuesDict.values())
        return sum(featureValues) / float(len(featureValues))

    def driver(self, filePath):
        weights = {'SWP': 0.2, 'NOWT': 0.4, 'NNP': 0.3, 'NVP': 0.1}

        SWPValues = {}
        NOWTValues = {}
        NNPValues = {}
        NVPValues = {}

        currentLine = 1
        title = "Process"
        finalTextLines = []

        with open(filePath, 'r') as fp:
            for line in fp:
                print line
                tokenArray = self.getTokens(line)
                SWPValues[currentLine] = fe.getStopWordsPerc(tokenArray)
                NOWTValues[currentLine] = fe.getNumOverlappingWords(title, line)
                NNPValues[currentLine] = fe.getNumNounPhrases(tokenArray)
                NVPValues[currentLine] = fe.getNumVerbPhrases(tokenArray)
                currentLine += 1

        totalLines = currentLine

        SWPThreshold = self.getThreshold(SWPValues)
        NOWTThreshold = self.getThreshold(NOWTValues)
        NNPThreshold = self.getThreshold(NNPValues)
        NVPThreshold = self.getThreshold(NVPValues)


        for i in range(1,totalLines):
            if((SWPValues[currentLine] <= SWPThreshold) and (NOWTValues[currentLine] >= NOWTThreshold) and (NNPValues[currentLine] >= NNPThreshold) and (NVPValues[currentLine]) >= NVPThreshold):
                    finalTextLines.append(i)

        # scoreThreshold = 50
        LinesScore = {}
        for lineNo in finalTextLines:
            score = ((SWPValues[lineNo] * weights['SWP']) + (NOWTValues[lineNo] * weights['NOWT']) + (NNPValues[lineNo] * weights['NNP']) + (NVPValues[lineNo] * weights['NNP']))
            LinesScore[lineNo] = score

        SortedDict = sorted(LinesScore.items(), key=operator.itemgetter(1))
        return SortedDict

if __name__ == '__main__':
    d = Driver()
    print d.driver("sample_3_1.txt")


