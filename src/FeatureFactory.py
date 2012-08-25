'''
Created on Aug 13, 2012

@author: shankar
'''
import explore
import re
import numpy as np
from sets import Set

def get_cprod_baseline_dict_mapping(input_file_name):
    '''
    whether a given token is a brandname, common english word or not found in dictionary supplied by the competition baseline2.
    '''
    cprod_baseline_dict_mapping_prods={'brandname':1.0, 'merchant':2.0} #if not found, mark it as -1.0.
    cprod_baseline_dict_mapping_lang={'encommonword':1.0, 'grammaticalword':2.0}
    input_file_name_prefix=input_file_name.split("-")[0]
    unrolled_file_name_suffix='_unrolled_data.txt'
    unrolled_file_name=input_file_name_prefix+unrolled_file_name_suffix
    unrolled_data=explore.read_unrolled_data(unrolled_data_filename=unrolled_file_name)
    cprod_data=read_n_filter_cprod_baseline_dict()
    cprod_keys=Set(cprod_data.keys())
    X_prods=np.ones(len(unrolled_data))*-1.0    #the default assumption is that the avg token is not a brandname or merchant name
    X_lang=np.zeros(len(unrolled_data))         #if token is not found in dictionary, it is likely close to a common english word
    for index, item in enumerate(unrolled_data):
        (textID, offset, lineNo, token)=item
        token=token.lower().strip()
        if token in cprod_keys:
            label=cprod_data[token]
            if label in cprod_baseline_dict_mapping_prods:
                X_prods[index]=cprod_baseline_dict_mapping_prods[label]
            if label in cprod_baseline_dict_mapping_lang:
                X_lang[index]=cprod_baseline_dict_mapping_lang[label]   
    return (X_prods, X_lang)
    
def read_n_filter_cprod_baseline_dict():
    '''
    suppose the dictionary line is 1\ Idea\ Italia\ Telecommunications=BRANDNAME
    this is transformed to the list [1, idea, italia, telecommun, brandname]
    every element is lowercased, the \'s are removed, and the the token is stemmed. 
    '''
    cprod_baseline_dict_file=open('dictionary.dat')
    cprod_baseline_dict_file.readline() #need to skip the first line
    raw_cprod_dict_data=cprod_baseline_dict_file.readlines()
    filtered_cprod_data={}
    for items in raw_cprod_dict_data:
        (tokens, label)=items.split("=")
        for token in tokens.split():
            token=re.sub(r"\\$","",token.lower().strip())
            filtered_cprod_data[token]=label.lower().strip()
    return filtered_cprod_data    
        


if __name__ == '__main__':
    get_cprod_baseline_dict_mapping('training-annotated-text.json')
    
    
    
    