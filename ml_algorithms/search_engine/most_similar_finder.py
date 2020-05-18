import numpy as np
import pickle as pkl
import re
from deeppavlov import configs, build_model
from gensim.models import FastText
from database.connection_provider import *

class SearchEngine:

    def __init__(self, path_to_dictionaries, ner_model):
        self.path_to_dictionaries = path_to_dictionaries
        self.conn_provider = ConnectionProvider()
        self.ner_model = ner_model
        self.fasttext = None

    def add_news_to_database(self, new_ids, new_titles, new_descrs, new_links, new_providers, new_pubdates):
        self.conn_provider.add_articles(new_ids, new_titles, new_descrs, new_links, new_providers, new_pubdates)

    def find_match(self, new_id, top_n=5):

        new = self.conn_provider.get_article(new_id)
        new_entities = new.named_entities
        others = self.conn_provider.get_news_by_predicate(lambda x: x.global_id != id)

        if self.fasttext is None:
            self.fasttext = FastText(size=360, window=3, min_count=1, iter=100, workers=-1, min_n=1, max_n=5)
            name_corpus = np.array([[c.appendix] for c in others.iterator()])
            self.fasttext.build_vocab(name_corpus)
            corp_count = self.fasttext.corpus_count
            n_iter = 100
            self.fasttext.train(name_corpus, total_examples=corp_count, epochs=n_iter)
            del name_corpus

        scores = []
        for candidate in others.iterator():
            score = 0
            for ent in new.named_entities:
                if ent in new_entities:
                    score += 1
            score += self.fasttext.similarity(new.appendix, candidate.appendix)
            score = score / (len(new_entities) + 1)
            scores.append((candidate.global_id, score))

        scores = sorted(scores, key=lambda x: -x[1])
        return scores[:top_n]

    def __build_ner_for_news(self):
        news = self.conn_provider.get_news_by_predicate(lambda x: x.named_entities.is_null(True))

        strings = [new.title + ' ' + new.description if new.description != '' else new.title for new in news]
        ner_map = self.ner_model.ner_decomposition(strings)

        for i, new in enumerate(news):
            new.named_entities = ner_map[i][0]
            new.appendix = ner_map[i][1]
        
        self.conn_provider.update_articles(news, ['named_entities', 'appendix'])

    def __build_supportive_dicts(self, unimap):
        entity_dict = {}
        for k, v in unimap.items():
            for ent in v[0]:
                if ent in entity_dict:
                    entity_dict[ent].add(k)
                else:
                    entity_dict[ent] = set([k])
        return entity_dict

    def __extract_one_new(self, news_ner):
        keys = np.array(news_ner[0])[np.array(news_ner[1]) != 'O']
        indexes = []
        for i, mark in enumerate(news_ner[1]):
            if mark != 'O': 
                continue
            clear = re.sub(r'[\W]', '', news_ner[0][i])
            if clear != '' and len(clear) > 1:
                indexes.append(i)
        appendix = np.array(news_ner[0])[indexes]
        return (keys, ' '.join(appendix))

    def __extract_features(self, maps):
        result = {}
        for k, v in maps.items():
            result[k] = self.__extract_one_new(v)
        return result

    def __build_unimap_dict(self, ner_title_map, ner_descr_map):

        title_maps_match = self.__extract_features(ner_title_map)
        descr_maps_match = self.__extract_features(ner_descr_map)

        unimap = {}
        for k, v in title_maps_match.items():
            if k in descr_maps_match:
                descr_val = descr_maps_match[k]
                unimap[k] = (np.union1d(v[0], descr_val[0]), v[1], descr_val[1])
            else:
                unimap[k] = v
        return unimap