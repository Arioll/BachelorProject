import re
import numpy as np
from deeppavlov import configs, build_model


class NER:

    def __init__(self):
        self.model = build_model(configs.ner.ner_rus, download=True)
    
    def extract_ner(self, string_corp):
        ids = []
        prepared_corp = []
        for i, par in enumerate(string_corp):
            # split every string into sentences to avoid out of max length error
            sentences = [s.strip() + '.' for s in par.split('.') if s != '']
            prepared_corp += sentences
            ids += [i] * len(sentences)
        
        ner_result = self.model(prepared_corp)

        ner_result_final = []
        last_class = -1
        for i, (tokens, classes) in enumerate(zip(ner_result[0], ner_result[1])):
            if last_class != ids[i]:
                ner_result_final[0].append(tokens)
                ner_result_final[1].append(classes)
            else:
                ner_result_final[0][-1] += tokens
                ner_result_final[1][-1] += classes
            last_class = ids[i]
        return ner_result_final

    def ner_decomposition(self, string_corp, batch_size):

        ner_result = [[], []]
        for i in range(len(string_corp) // batch_size + 1):
            ner_res_loc = self.extract_ner(string_corp[i*batch_size:(i+1)*batch_size])
            ner_result[0] += ner_res_loc[0]
            ner_result[1] += ner_res_loc[1]

        decomp_result = []
        for tokens, classes in ner_result:
            ner_set = set()
            appendix = []
            last_token = ''
            for token, cl in zip(tokens, classes):
                if cl != 'O':
                    if cl[0] == 'B':
                        ner_set.add(last_token)
                        last_token = token
                    else:
                        last_token += ' ' + token
                else:
                    clear = re.sub(r'[\W]', '', token)
                    if clear != '' and len(clear) > 1:
                        appendix.append(token)
            appendix = ' '.join(appendix)
            decomp_result.append((ner_set, appendix))
            
        return decomp_result