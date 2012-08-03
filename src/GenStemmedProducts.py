'''
transforms products.json to lower case and applies a porter stemmer
'''
import os
import json
import re
import nltk
from nltk.stem import PorterStemmer

prod_line_re=re.compile(r"^\s+\".*\",$", re.IGNORECASE)
au_tag_re=re.compile(r"^\"AU\",$", re.IGNORECASE)
ce_tag_re=re.compile(r"^\"CE\",$", re.IGNORECASE)
punctuation_chars=[')','(','.',':','=','\\','-','!','/','|']


if __name__ == '__main__':
    os.chdir('/home/shankar/Downloads/TrainingSet')
    fh=open('products_mod_mod.json','w')
    porter_stemmer=PorterStemmer()
    with open('products.json') as f:
        for line in f:
            prod_line_match=prod_line_re.search(line)
            if prod_line_match:
                init_match_line=str(prod_line_match.group()).strip()
                au_tag_match=au_tag_re.search(init_match_line)
                ce_tag_match=ce_tag_re.search(init_match_line)
                if not au_tag_match and not ce_tag_match:
                    prod_line=re.sub(r"(\")|(,)"," ", init_match_line).lower()
                    tokens=list(nltk.word_tokenize(prod_line))
                    stemmed_prod = ' '.join([porter_stemmer.stem(items) for items in tokens if items not in punctuation_chars])+'\n'
                    fh.write(stemmed_prod)
            else:
                fh.write(line+'\n')
    fh.close()
                
