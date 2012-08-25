'''
Created on Jul 27, 2012

@author: shankar
'''
import os
import json
import re
import nltk
from nltk.stem import PorterStemmer
import subprocess
import pickle
from collections import deque
from sets import Set
import numpy as np
from copy import copy
import random
import sqlite3 as lite
prod_line_re=re.compile(r"^\s+\".*\",$", re.IGNORECASE)
au_tag_re=re.compile(r"^\"AU\",$", re.IGNORECASE)
ce_tag_re=re.compile(r"^\"CE\",$", re.IGNORECASE)
prod_id_tag_re=re.compile(r"^\s+\".*\":\s*\[\s*$")
punctuation_chars=[')','(','.',':','=','\\','-','!','/','|']
unrolled_file_name_suffix='_unrolled_data.txt'

class ProductRecord(object):
    def __init__(self):
        self.prodID=None
        self.prod_description=None
        self.price=None

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

def build_prod_db():
    '''
    puts the product.json file into a database! note that the product descriptions are stemmed
    '''
    raw_input("are you sure you want to build the product database again? press Ctrl+C to abort now!!!")
    products_json_file=open('/home/shankar/Downloads/TrainingSet/products.json')
    connection=lite.connect('products.db')
    cursor=connection.cursor()
    cursor.executescript('''
    drop table if exists Products;
    create table Products(ProdID text, prod_description text);
    ''')
    connection.commit()
    record=[]
    iteration=0
    while 1:
        print "iteration ", iteration
        iteration+=1
        lines=products_json_file.readlines(10000000)
        if not lines:
            break
        record_list=[]
        for line in lines:
            if prod_id_tag_re.search(line):
                prodID_raw=str(prod_id_tag_re.search(line).group()).strip()
                prodID=re.sub(r"(\")|(:)|(\[)", " ", prodID_raw).strip()
                record.append(prodID)
            stemmed_prod_line=getStemmedProdLine(line)
            if stemmed_prod_line:
                record.append(stemmed_prod_line)
                record_list.append(tuple(record))
                record=[]
        record_list=tuple(record_list)
        cursor.executemany("insert into Products values (?,?)", record_list)
        connection.commit()
    connection.close()
        
def gen_postings_list_from_big_file_sort():
    '''
    generate the file term_docID_big_file_sorted.txt from this command:
    python BigFileSorting -b 8000000 -k "str(line.split()[0])" term_docID_sorted.txt term_docID_big_file_sorted.txt
    Once you have term_docID_big_file_sorted.txt, this function can generate a postings list. Each line consists of 
    term's frequency, term, followed by docIDs.
    Once you have the postings list, you can sort them by term frequency by:
    python BigFileSorting -b 8000000 -k "-1*int(line.split(\":\")[0]) products_postings.txt postings_sorted_by_freq.txt"
    Note: total frequency count of all terms = 145783790. If you want normalised term freq, divide by this number.
    '''
    if 'yes'=='yes':
        term_docID_sorted_file=open('term_docID_big_file_sorted.txt','r')
        products_postings_file=open('products_postings.txt','w')
        iteration=0
        while 1:
            lines=term_docID_sorted_file.readlines(100000000) #read 10 Megs at a time
            if not lines:
                break
            current_term=lines[0].split()[0]
            docID_list=[]
            print "no of lines read in = ", len(lines), "iteration = ", iteration
            for lineNo, line in enumerate(lines):                
                (term, docID)=(line.split()[0], line.split()[1])
                if current_term!=term:
                    products_postings_file.write(str(len(docID_list))+" : "+current_term+" : "+' '.join(docID_list)+"\n")
                    #reset current_term, docID_list
                    current_term=term
                    docID_list=[]
                    docID_list.append(docID)
                else:
                    docID_list.append(docID)
            print "still alive! iteration = ", iteration
            iteration+=1 

        
def gen_unrolled_training_data(input_file):
    '''
    unrolls the tokens from text files like training-annotated-text.json. 
    replacing blank tokens with **
    '''
    filename=open(input_file,'r')
    input_file_prefix=input_file.split("-")[0]
    unrolled_file_name=input_file_prefix+unrolled_file_name_suffix
    unrolled_training_data_file=open(unrolled_file_name,'w')
    raw_text_json=json.load(filename)['TextItem']
    lineNo=0 
    offset=0
    for key, text in raw_text_json.iteritems():
        offset=0
        for token in text:
            if token=='':
                token='**'
            record=str(lineNo)+" "+str(offset)+" "+key+" "+token.strip()+"\n"
            unrolled_training_data_file.write(record)
            lineNo+=1
            offset+=1

def read_unrolled_data(unrolled_data_filename):
    '''
    reads unrolled data file as a list. Each list element is a tuple (<textID>, <offset>, <lineNo>, <token>)
    '''
    unrolled_data=[]
    print "loading unrolled_data into memory"
    raw_unrolled_data=open(unrolled_data_filename).readlines()
    for item in raw_unrolled_data:
        split_items=map(lambda x:x.strip(), item.split())
        (textID,offset,lineNo, token)=(split_items[2], int(split_items[1]), int(split_items[0]), split_items[3])
        unrolled_data.append((textID,offset,lineNo,token))
    return unrolled_data

def gen_Y_ref():
    reference_file_name='training_unrolled_data.txt'
    unrolled_data=read_unrolled_data(unrolled_data_filename=reference_file_name)
    disambigueated_reference_filename=open('training-disambiguated-product-mentions.120725.csv','r')
    Y_ref_filename=open('Y_ref.pkl','wb')
    disambiguated_data=[]
    Y_ref=np.zeros(len(unrolled_data))
    index_list=[]
    print "loading disambiguated data into memory"
    disambigueated_reference_filename.readline()
    raw_disambiguation_data=disambigueated_reference_filename.readlines()
    for item in raw_disambiguation_data:
        (textID, startOffset, endOffset)=(item.split(",")[0].split(":")[0], int(item.split(",")[0].split(":")[1].split("-")[0]), 
                                          int(item.split(",")[0].split(":")[1].split("-")[1]))
        disambiguated_data.append((textID, startOffset, endOffset))
    print "extracting Y_ref indices"
    for i in range(len(unrolled_data)):
        for j in range(len(disambiguated_data)):
            (textID, startOffset, endOffset)=(disambiguated_data[j][0],disambiguated_data[j][1],disambiguated_data[j][2])
            if unrolled_data[i][0]==textID and unrolled_data[i][1]>=startOffset and unrolled_data[i][1]<=endOffset:
                index_list.append(unrolled_data[i][2])
                break
    for i in range(len(index_list)):
        Y_ref[index_list[i]]=1
    print "pickling Y_ref"
    pickle.dump(Y_ref, Y_ref_filename)
    

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
    build_prod_db()
#    os.chdir('/home/shankar/Downloads/TrainingSet')
#    cwd=os.getcwd()
#    gen_human_readable_training_data()
#    gen_postings_list_from_big_file_sort()
#    gen_unrolled_training_data()
#    gen_Y_ref()
#    temp()
#    os.chdir(cwd)

