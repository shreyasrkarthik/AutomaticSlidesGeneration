from nltk import word_tokenize

class BulletIdentifier:
    def __init__(self):
        self.clean_sentences = []
        self.bullets_map = dict()

    def tokenize(self, sentence):
        sentence = sentence.replace('\n', ' ')
        return sentence.split('.')

    def read_sentences(self, filepath, chunk_size=10240):
        last = ""
        with open(filepath) as inp:
            while True:
                buf = inp.read(chunk_size)
                if not buf:
                    break
                data = last + buf
                data = data.replace('?', '.')
                data = data.replace(';', '.')
                sentences = self.tokenize(data)

                last = sentences.pop()
                for sentence in sentences:
                    yield sentence.replace('\n', ' ')
            yield last.replace('\n', ' ')

    def get_sentences(self, file_name):
        valid_sentences = []
        for sentence in self.read_sentences(file_name):
            num_words = len(word_tokenize(sentence))
            if num_words in xrange(2, 30):
                valid_sentences.append(sentence)
        return valid_sentences

    def identify_bullet_sentences(self, file_name):
        acceptable_range = range(32, 128)
        continuous = 0
        non_bullet = 0
        para = 0
        k = 0
        bullet_set = []
        valid_sentences = self.get_sentences(file_name)#sentences with word count in range(2,30)
        for sentence in valid_sentences:
            self.clean_sentences.append(''.join([i if ord(i) < 128 else ' ' for i in sentence]))
            got_bullet = 0
            sentence = sentence.strip()
            for ch in sentence:
                if not got_bullet:
                    if ord(ch) not in acceptable_range:
                        got_bullet = 1
                        continuous += 1
                        para = 1
                        non_bullet = 0
                        bullet_set.append(k)
                        break
            if not got_bullet:
                non_bullet += 1
            if (para == 1) and (non_bullet > 2):
                bullet_set = range(min(bullet_set), max(bullet_set)+1)

                # print "para ends", sentence
                # print '------para ends-------',k-(continuous+non_bullet)-1,(k- non_bullet-1),'\n'

                # ideal map format [heading_no:{heading : heading_text, bullets: [bullets sentences]}]
                # for now i am not putting heading

                self.bullets_map[k] = bullet_set
                bullet_set = []
                para = 0
                non_bullet = 0
                continuous = 0
            k += 1
        if got_bullet == 1:
            self.bullets_map[k] = bullet_set
        return self.clean_sentences, self.bullets_map


# if __name__ == '__main__':
#
#     file_name = "../src/sample_3_1.txt"
#     bi = BulletIdentifier()
#     bi.identify_bullet_sentences(file_name)
#     print bi.bullets_map
#     # print bi.bullets_map.keys()
#     # print bi.clean_sentences
