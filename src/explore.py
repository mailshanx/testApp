'''
Created on Jul 27, 2012

@author: shankar
'''
import os
import json
import re
import nltk
from nltk.stem import PorterStemmer
from nltk.stem.porter import PorterStemmer
import subprocess
import pickle
from collections import deque

prod_line_re=re.compile(r"^\s+\".*\",$", re.IGNORECASE)
au_tag_re=re.compile(r"^\"AU\",$", re.IGNORECASE)
ce_tag_re=re.compile(r"^\"CE\",$", re.IGNORECASE)
prod_id_tag_re=re.compile(r"^\s+\".*\":\s*\[\s*$")
punctuation_chars=[')','(','.',':','=','\\','-','!','/','|']


def build_term_docID_prodID():
    confirmation=raw_input("are you sure you want to re-build the search index? ")
    if confirmation=='yes':
        os.chdir('/home/shankar/Downloads/TrainingSet')
        term_docID_file=open('term_docID.txt','w')
        docID_prodID_file=open('docID_prodID.txt','w')
        products_file=open('products.json','r')
        docID=-1
        while 1:
            lines=products_file.readlines(10000000) #read a Gig at a time
            if not lines:
                break
            for line in lines:
                if prod_id_tag_re.search(line):
                    prodID_raw=str(prod_id_tag_re.search(line).group()).strip()
                    prodID=re.sub(r"(\")|(:)|(\[)", " ", prodID_raw).strip()
                    docID+=1
                    docID_prodID_file.write(str(docID)+" "+prodID+"\n")
                stemmed_prod_line=getStemmedProdLine(line)
                if stemmed_prod_line:
                    for term in stemmed_prod_line.split():
                        term_docID_file.write(term+" "+str(docID)+"\n")

def getStemmedProdLine(line):
    prod_line_match=prod_line_re.search(line)
    porter_stemmer=PorterStemmer()
    if not prod_line_match:
        return False
    init_match_line=str(prod_line_match.group()).strip()
    au_tag_match=au_tag_re.search(init_match_line)
    ce_tag_match=ce_tag_re.search(init_match_line)
    if not au_tag_match and not ce_tag_match:
        prod_line=re.sub(r"(\")|(,)"," ", init_match_line).lower()
        tokens=list(nltk.word_tokenize(prod_line))
        stemmed_prod_line = ' '.join([porter_stemmer.stem(items) for items in tokens if items not in punctuation_chars])
        return stemmed_prod_line
    pass

def gen_postings_list():
#    input=raw_input("are you sure you want to generate the postings list again???")
    if 'yes'=='yes':
        term_docID_sorted_file=open('term_docID_sorted.txt','r')
        products_postings_file=open('products_postings.pkl','wb')
        postings_dict={}
        iteration=0
        cached_lines=deque([])
        while 1:
            lines=term_docID_sorted_file.readlines(100000000) #read 10 Megs at a time
            if not lines:
                break
            current_term=lines[0].split()[0]
            docID_list=[]
            cached_lines.append(current_term)
            print "no of lines read in = ", len(lines), "iteration = ", iteration
            for lineNo, line in enumerate(lines):                
                (term, docID)=(line.split()[0], line.split()[1])
                if current_term!=term:
                    if len(cached_lines)>5000:
                        current_term_in_dict=(current_term in cached_lines)
                        cached_lines.popleft()
                    else:
                        current_term_in_dict=(current_term in postings_dict.keys())
                    #update postings_dict
                    if current_term_in_dict:
#                        print "found repeated term ",current_term
                        postings=postings_dict[current_term]
                        map(postings.append, docID_list)
                        postings_dict[current_term]=postings
    #                    raise Exception(term, " exists in postings_dict.keys(). something is wrong")
                    else:                    
                        postings_dict[current_term]=docID_list
                        cached_lines.append(current_term)
#                    print "current_term = ", current_term, " postings : ", postings_dict[current_term]
                    #reset current_term, docID_list
                    current_term=term
                    docID_list=[]
                    docID_list.append(docID)
                else:
                    docID_list.append(docID)
    #                print "current_term : ", current_term, " docID : ", docID
                if lineNo%50000==0:
                    print "processed lineNo ", lineNo, ", len(cached_lines) = ", len(cached_lines), ", len(postings_dict) = ", len(postings_dict)
            print "still alive! iteration = ", iteration
            print "len(postings_dict) = ", len(postings_dict)
            iteration+=1 
        pickle.dump(postings_dict, products_postings_file)


def gen_human_readable_training_data():
    train_annotate_filename = 'training-annotated-text.json'
    f = open(train_annotate_filename, 'r')
    json_obj = json.load(f) 
    f.close()
    training_data = json_obj['TextItem']
        
    f=open('training-disambiguated-product-mentions.csv', 'r')
    f.readline()
    with f:
        for line in f:
            (prod_id_list ,text_id, start, stop)= (line.split(",")[1].split(), line.split(":")[0],  
                                                    int(line.split(":")[1].split(",")[0].split("-")[0]),
                                                    int(line.split(":")[1].split(",")[0].split("-")[1]))
            product_list=training_data.get(text_id)[start:stop+1]
            print ' '.join([products for products in product_list]), "   ", prod_id_list
            print ' '.join([tokens for tokens in map(lambda x:x=='<s>' and '\n' or x, training_data.get(text_id))])
#            print [str(prods) for prods in product_list]
            product_list_context=training_data.get(text_id)[start-2:stop+1+2]
#            print [str(prods) for prods in product_list_context]
            print
            print "-------------------------------------------------------------------------------------------------------------------------------"
            print

if __name__ == '__main__':
    os.chdir('/home/shankar/Downloads/TrainingSet')
    cwd=os.getcwd()
#    gen_human_readable_training_data()
    gen_postings_list()
    os.chdir(cwd)




     