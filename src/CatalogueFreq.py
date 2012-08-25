'''
Created on Aug 8, 2012

@author: shankar
'''
import nltk
from nltk import PorterStemmer
import json
from sets import Set
import numpy as np
total_product_term_freq=145783790
token_occurence_in_catalogue_file_suffix="_tokens_in_catalogue_cache.txt"

            
            
def get_token_occurence_in_catalogue(input_file):
    '''
    Picks up the normalized log frequency from the cache file 'input_file_prefix+token_occurence_in_catalogue_file_suffix'
    and returns it as a numpy array. Cache file is already generated for training-annotated-text.json. For other files, 
    generate the corresponding cache file from the function gen_training_tokens_in_catalogue_cache(input_file) first.
    '''
    input_file_prefix=input_file.split("-")[0]
    cache_file=open(input_file_prefix+token_occurence_in_catalogue_file_suffix)
    token_occurrence_freq=[]
    while 1:
        lines=cache_file.readlines(100000000)
        if not lines:
            break
        for line in lines:
            if len(line.split())==3:
                token_occurrence_freq.append(float(line.split()[2]))
            else:
                #encountered a blank token
                token_occurrence_freq.append(0.0)         
    X_cat_freq=np.array(token_occurrence_freq)
    return X_cat_freq

def gen_training_tokens_in_catalogue_cache(input_file):
    '''
    format of output file:
    <lineNo> <term/token> <normalized_log_frequency>
    sum of product term frequencies = 145783790 
    '''
    ps=PorterStemmer()
    filename=open(input_file,'r')
    input_file_prefix=input_file.split("-")[0]
    training_tokens_in_catalougue_file_name=input_file_prefix+token_occurence_in_catalogue_file_suffix
    print "output file name = ", training_tokens_in_catalougue_file_name
    postings_file=open('postings_sorted_by_freq.txt','r')
    raw_text_json=json.load(filename)['TextItem']
    training_tokens_in_catalougue_file=open(training_tokens_in_catalougue_file_name,'w')
    term_list=[]
    lineNo=0
    for key, text in raw_text_json.iteritems():
        for token in text:
            log_normalized_term_freq=0.0    #default assumption is that things are not found in catalogue
            term=ps.stem(token.encode("utf-8").strip().lower())
            term_list.append([lineNo, term, log_normalized_term_freq])
            lineNo+=1
            pass
    print "term_list size = ", len(term_list)
    iteration=0
    while 1:
        print "iteration = ",iteration
        lines=postings_file.readlines(500000000)
        if not lines:
            break
        #build temp dict
        temp_postings_dict={}
        print "building temp_postings_dict"
        for line in lines:
            (posting_term, term_freq)=(line.split(":")[1].strip(),float(line.split(":")[0]))
            temp_postings_dict[posting_term]=term_freq
        temp_postings_keyset=Set(temp_postings_dict.keys())
        print "updating term_list : "
        for index in range(len(term_list)):
            (lineNo, term, log_normalized_term_freq)=(term_list[index])
            if log_normalized_term_freq==0.0: 
                if term in temp_postings_keyset:
                    term_list[index][2]=np.log(temp_postings_dict[term]/total_product_term_freq)
#                    print "term_list[index] : ", term_list[index][0], term_list[index][1], term_list[index][2], term_list[index][3][:25]
#                    raw_input("continue")
        iteration+=1
    #at this stage, the term_list is updated
    print "writing data to "+training_tokens_in_catalougue_file_name+" : "
    for items in term_list:
        training_tokens_in_catalougue_file.write(str(items[0])+" "+str(items[1])+" "+str(items[2])+"\n")
    print "done!!!"
    
if __name__ == '__main__':
    print get_token_occurence_in_catalogue('training-annotated-text.json')[0:5]
    print len(get_token_occurence_in_catalogue('training-annotated-text.json'))



