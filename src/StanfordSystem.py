'''
Created on Aug 12, 2012

@author: shankar
'''
import pickle, random
import explore
import numpy as np

stanford_ner_predictions_file_suffix='_stanford_ner_predictions.txt'

def get_stanford_ner_signal(input_file):
    '''
    maps the BILOU predictions to numbers. O=-2,B=0,L=1,I=U=0.5,
    '''
    input_file_prefix=input_file.split("-")[0]
    stanford_ner_prediction_file_name=input_file_prefix+stanford_ner_predictions_file_suffix
    stanford_ner_prediction_file=open(stanford_ner_prediction_file_name,'r')
    stanford_ner_predictions=stanford_ner_prediction_file.readlines()
    X_stan=[]
    BILOU_mapping={'O':-2.0,'B':0.0,'L':1.0,'I':0.5,'U':0.5}
    for items in stanford_ner_predictions:
        X_stan.append(BILOU_mapping[items.split("\t")[2].strip()])
    return np.array(X_stan)

def gen_stanford_ner_training_data():
    '''
    use a BILOU annotations scheme: B=beginning, I=inside, L=last, O=outside, U=unit-length
    turns out, the BILOU scheme has ~ 25% F1 score on the stanford system
    '''
    train_test_split=0.25
    Y_ref=pickle.load(open('Y_ref.pkl','r'))
    unrolled_data_filename=open('training_unrolled_data.txt','r')
    stanford_ner_training_data_filename=open('stanford_ner_training_data_25_split.txt','w')
    stanford_ner_testing_data_filename=open('stanford_ner_testing_data.txt','w')
    unrolled_data=explore.read_unrolled_data(unrolled_data_filename=unrolled_data_filename)
    for index in range((len(Y_ref)-1)):
        if Y_ref[index]==0:
            label='O'
        elif Y_ref[index]==1 and Y_ref[index-1]==0 and Y_ref[index+1]==1:
            label='B'
        elif Y_ref[index]==1 and Y_ref[index-1]==1 and Y_ref[index+1]==1: 
            label='I'
        elif Y_ref[index]==1 and Y_ref[index-1]==1 and Y_ref[index+1]==0:
            label='L'
        elif Y_ref[index]==1 and Y_ref[index-1]==0 and Y_ref[index+1]==0:
            label='U'
        record=unrolled_data[index][3]+"\t"+label+"\n"
        if random.random()<train_test_split:
            stanford_ner_training_data_filename.write(record)
        stanford_ner_testing_data_filename.write(record)

if __name__ == '__main__':
    pass