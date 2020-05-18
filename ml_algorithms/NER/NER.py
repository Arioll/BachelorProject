import re
from deeppavlov import configs, build_model


class NER:

    def __init__(self):
        self.model = build_model(configs.ner.ner_rus_bert, download=True)
    
    def extract_ner(self, string_corp):
        ids = []
        prepared_corp = []
        for i, par in enumerate(string_corp):
            # split every string into sentences to avoid out of max length error
            sentences = [s.strip() + '.' if s != '' for s in par.split('.')]
            prepared_corp += sentences
            ids += [i] * len(sentences)
        
        ner_result = self.model(prepared_corp)

        ner_result_final = []
        last_class = -1
        for i, (tokens, classes) in enumerate(ner_result):
            if last_class != ids[i]:
                ner_result_final[0].append(tokens)
                ner_result_final[1].append(classes)
            else:
                ner_result_final[0][-1] += tokens
                ner_result_final[1][-1] += classes
            last_class = ids[i]
        return ner_result_final

    def ner_decomposition(self, string_corp):
        ner_result = self.extract_ner(string_corp)

        decomp_result = []
        for tokens, classes in ner_result:
            ner_array = []
            appendix = []
            for token, cl in zip(tokens, classes):
                if cl != 'O':
                    ner_array.append(token)
                else:
                    clear = re.sub(r'[\W]', '', token)
                    if clear != '' and len(clear) > 1:
                        appendix.append(token)
            appendix = ' '.join(appendix)
            decomp_result.append((ner_array, appendix))
            
        return decomp_result