from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk.tag import pos_tag
from nltk.tokenize import sent_tokenize

class FeatureExtractor:
    def __init__(self):
        pass

    def getStopWordsPerc(self, token_list):
        word_count = len(token_list)
        filtered_words = [word for word in token_list if word not in stopwords.words('english') and len(word)>2]
        filtered_word_count = len(filtered_words)
        return (filtered_word_count*100)/word_count

    def getNumNounPhrases(self, token_list):
        tagged_sent = pos_tag(token_list)
        noun_count = 0
        for word, tag in tagged_sent:
            if 'NN' in tag or 'nn' in tag:
                noun_count += 1
        return noun_count

    def getNumVerbPhrases(self, token_list):
        verb_count = 0
        tagged_sent = pos_tag(token_list)
        for word, tag in tagged_sent:
            if 'VB' in tag or 'vb' in tag:
                verb_count += 1
        return verb_count

    def getNumOverlappingWords(self, sentence, title):
        sent_token_list = word_tokenize(sentence.lower())
        title_token_list = word_tokenize(title.lower())
        return len(set(sent_token_list) & set(title_token_list))

    def getSentencePosition(self, paragraph, sentence):
        sentences = sent_tokenize(paragraph)
        return sentences.index(sentence)

    def getAvgSentenceLength(self, paragraph):
        sentences = sent_tokenize(paragraph)
        sum_len = 0
        for sentence in sentences:
            sum_len += len(sentence)
        return (sum_len)/len(sentences)

#unit testing
if __name__ == '__main__':
    sentence = "A computer platform consists of a collection of hardware resources, such as the processor,\
     main memory, I/O modules, timers, disk drives, and so on. This is a sub sentence." #dummy sentence
    title = "Computer Processor" #dummy title
    sub_sentence = "This is a sub sentence."

    token_list = word_tokenize(sentence.lower())
    featureExtractor = FeatureExtractor()
    stop_words_per = featureExtractor.getStopWordsPerc(token_list)
    num_nouns = featureExtractor.getNumNounPhrases(token_list)
    num_verbs = featureExtractor.getNumVerbPhrases(token_list)
    overlapping_word_count = featureExtractor.getNumOverlappingWords(sentence.lower(), title.lower())
    sentence_pos = featureExtractor.getSentencePosition(sentence.lower(), sub_sentence.lower())
    avg_sent_len = featureExtractor.getAvgSentenceLength(sentence)
    print(stop_words_per, num_nouns, num_verbs, overlapping_word_count, avg_sent_len)
