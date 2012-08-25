'''
Takes an output vector Y_out, and returns a vector with productIDs if they exist 
'''
from sets import Set
import explore
import numpy as np
import pickle
from nltk.stem import PorterStemmer
ps=PorterStemmer()
postings_sorted_by_freq_file_name='postings_sorted_by_freq.txt'

class CatLabels(object):
    def __init__(self, params):
        pass

class QueryDatum(object):
    def __init__(self, query_terms, query_terms_indices):
        self.query_terms=query_terms
        self.query_terms_indices=query_terms_indices
        self.postings=[]
        pass


def retrieveCatLabels(Y_out, training_data_file_name):
    training_data_file_name_prefix=training_data_file_name.split("-")[0]
    unrolled_data_file_name=training_data_file_name_prefix+explore.unrolled_file_name_suffix
    unrolled_data=explore.read_unrolled_data(unrolled_data_filename=unrolled_data_file_name)
    postings_sorted_by_freq_file=open(postings_sorted_by_freq_file_name)
    query_data=getQueryData(unrolled_data=unrolled_data, Y_out=Y_out, use_stemming=True)
    for index in range(len(query_data)):
        query_terms=query_data[index].query_terms
        postings_set=Set([])
        print "processing term ", index
        iteration=0
        while 1:
            print "iteration : ",iteration
            iteration+=1
            lines=postings_sorted_by_freq_file.readlines(100000000)
            if not lines:
                break
            print "initiating temp_dict"
            temp_postings_dict={}
            for line in lines:
                (token, postings)=(ps.stem(line.split(":")[1].lower().strip()), line.split(":")[2].lower().strip().split())
                temp_postings_dict[token]=postings
            #at this point, our temp dictionary is built 
            temp_postings_dict_keys=Set(temp_postings_dict.keys())
            print "completed building temp_dict. len(dict) = ", len(temp_postings_dict)
            for term in query_terms:
                if term in temp_postings_dict_keys:
                    if len(postings_set)==0:
                        postings_set=Set(temp_postings_dict[term])
                    else:
                        postings_set=postings_set & Set(temp_postings_dict[term])
        query_data[index].postings=list(postings_set)
        print "size of postings = ",len(query_data[index].postings), " postings : ", query_data[index].postings[0:10]
        raw_input("continue : ")
                    
            
            
        
        
def getQueryData(unrolled_data, Y_out, use_stemming):
    '''
    returns a list of QueryDatum's from a given unrolled data and reference Y
    '''   
    query_data=[]
    detected_query=False
    query_terms=[]
    query_terms_indices=[]
    for i in range(len(Y_out)):
        if Y_out[i]==1:
            detected_query=True
            (textID, offset, lineNo, token)=unrolled_data[i]
            if use_stemming:
                query_terms.append(ps.stem(token.lower().strip()))
            else:
                query_terms.append(token.lower().strip())
            query_terms_indices.append(i)
        if Y_out[i]==0 and detected_query:
            detected_query=False
            query_data.append(QueryDatum(query_terms=query_terms, query_terms_indices=query_terms_indices))
            query_terms=[]
            query_terms_indices=[]     
    return query_data
        
        
if __name__ == '__main__':
    Y_ref=pickle.load(open('Y_ref.pkl'))
    training_data_file_name='training-annotated-text.json'
    retrieveCatLabels(Y_out=Y_ref, training_data_file_name=training_data_file_name)
    pass




















