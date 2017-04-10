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

    def identify_bullet_sentences(self, file_name):
        acceptable_range = range(32, 128)
        continuous = 0
        non_bullet = 0
        para = 0
        k = 0
        for sentence in self.read_sentences(file_name):
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
                        break
            if not got_bullet:
                non_bullet += 1
            if (para == 1) and (non_bullet > 2):
                # print '------para ends-------',k-(continuous+non_bullet)-1,(k- non_bullet-1),'\n'

                # ideal map format [heading_no:{heading : heading_text, bullets: [bullets sentences]}]
                # for now i am not putting heading
                bullet_set = dict()
                bullet_set['bullets'] = range(k - (continuous + non_bullet) - 1, (k - non_bullet - 1))
                self.bullets_map[k] = bullet_set
                para = 0
                non_bullet = 0
                continuous = 0
            k += 1
        # for s in self.clean_sentences:
        # 	print s,'\n'
        return self.clean_sentences, self.bullets_map

        # file_name = "../src/sample_3_1.txt"
        # identify_bullet_sentences(file_name)
        # f = open("../src/Bullets.log","w")
        # f.write(str(self.bullets_map))
        # print self.bullets_map
        # print self.bullets_map.keys()
        # print self.clean_sentences
