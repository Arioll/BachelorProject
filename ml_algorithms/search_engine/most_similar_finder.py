import numpy as np
import re
from gensim.models import FastText
from database.connection_provider import ConnectionProvider

class SearchEngine:

    def __init__(self, connection_provider):

        print('Search engine initialization')

        self.conn_provider = connection_provider

        self.fasttext = FastText(size=720, window=3, min_count=1, iter=100, workers=-1, min_n=1, max_n=5)
        name_corpus = np.array([[c.appendix] for c in self.conn_provider.get_all_articles().iterator()])
        self.fasttext.build_vocab(name_corpus)
        corp_count = self.fasttext.corpus_count
        n_iter = 1000
        self.fasttext.train(name_corpus, total_examples=corp_count, epochs=n_iter)
        del name_corpus

        print('Done')

    def find_match(self, new_id, top_n=5):

        new = self.conn_provider.get_article(new_id)
        new_entities = new.named_entities
        others = self.conn_provider.get_news_by_predicate(lambda x: x.global_id != id)

        scores = []
        for candidate in others.iterator():
            score = 0
            cand_entities = set(candidate.named_entities)
            for ent in new_entities:
                if ent in cand_entities:
                    score += 1
            score += self.fasttext.similarity(new.appendix, candidate.appendix)
            score = score / (len(new_entities) + 1)
            scores.append((candidate.global_id, score))

        scores = sorted(scores, key=lambda x: -x[1])
        return scores[:top_n]
