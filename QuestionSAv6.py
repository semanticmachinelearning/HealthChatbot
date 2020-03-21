#!/usr/bin/env python
# coding: utf-8

# In[1]:


from lxml import html
from collections import namedtuple
from dateutil.parser import parse
from collections import OrderedDict
import urllib, json
import urllib.request
import requests
import spotlight
import unicodedata
import spacy
from spacy import displacy
from collections import Counter
import en_core_web_sm
nlp = en_core_web_sm.load()
import nltk
from nltk.tokenize import word_tokenize
from nltk.chunk import ne_chunk
import re
from nltk.util import ngrams
import re
import numpy as np
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer


# In[2]:


STARTWORDS = ['who', 'what', 'when', 'where', 'why', 'how', 'is', 'can', 'does', 'do', 'which', 'am', 'are', 'was', 'were', 'may', 'might', 'can', 'could', 'will', 'shall', 'would', 'should', 'has', 'have', 'had', 'did']


# In[3]:


words = set(stopwords.words('english'))
stop_words = set(stopwords.words('english')) 


# In[4]:


def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try: 
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False


# In[5]:


def dbpedia_annoations(inp_db):
    restAPI='http://api.dbpedia-spotlight.org/en/annotate'
    reqk=[]
    inp_word = inp_db.split()
    try:
        annotation = spotlight.annotate(restAPI,inp_db,confidence=0.09,support=20)
        for terms in annotation:
            uniterms = unicodedata.normalize('NFKD',terms['URI']).encode('ascii','ignore')
            #print(uniterms)
            sem_key = str(uniterms).split('/')[-1][0:-1].lower()
            #print (sem_key)
            if sem_key in inp_word and sem_key !='the_who':
                reqk.append(str(uniterms).split('/')[-1][0:-1])
            else:
                if sem_key !='the_who':
                    sem_key=sem_key.replace('_',' ')
                    for xs in inp_word:
                        if xs[-1]=='?' or xs[-1]=='.':
                            xs=xs[:-1]
                        #print('DBp anno: '+sem_key,xs)
                        if sem_key.startswith(xs.lower()) or xs.lower().startswith(sem_key) or sem_key.endswith(xs.lower()):
                            reqk.append(str(uniterms).split('/')[-1][0:-1])
                            break
    except: 
        e= 'no annoation find in DBpedia'
        #print (e)
    return reqk


# In[6]:


def if_disease_q(wiki_key):
    flag=0
    for dbp_k in wiki_key:
        dbpdialink = 'http://dbpedia.org/data/'+dbp_k+'.json'
        with urllib.request.urlopen(dbpdialink) as url:
            jicdata = json.loads(url.read())
            if 'http://dbpedia.org/resource/'+dbp_k not in jicdata:
                print('no information find')
            else:
                firstkey=jicdata['http://dbpedia.org/resource/'+dbp_k]
                if 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type' in firstkey:
                    secondkey = firstkey['http://www.w3.org/1999/02/22-rdf-syntax-ns#type']
                    for typei in secondkey:
                        #print (typei['value'])
                        if typei['value'].split('/')[-1].lower()[:7]=='disease':
                            flag=1
    return flag
    


# In[20]:


def sentence_nlp(inp):
    reqkey=dbpedia_annoations(inp)
    word_tokens = word_tokenize(inp)
    texts = [w for w in word_tokens if not w in stop_words] 
    ps = PorterStemmer()
    text=[]
    for w in texts:
        text.append(ps.stem(w))
        #text.append(w)
    textk=' '.join(text)
    #print (text)
    txttypeinput = ' '.join(texts)

    last_w = -1
    if text[-1]== '?' or text[-1]== '.':
        last_w = -2
    sentence_tag = nltk.pos_tag(text)

    #ne_tree
    ne_tree=ne_chunk(sentence_tag)
    #print('ne_tree: ', ne_tree)

    #pattern
    pattern = 'NP: {<DT>?<JJ>*<NN>}'
    cp = nltk.RegexpParser(pattern)
    cs = cp.parse(sentence_tag)
    #print('pattern', cs)

    list_kt=[]
    #reqkey=[]
    inp_word = textk.split()
    qc_yes = 'UNK'
    date_yes = 'N'
    inp_kt_tag='_'
    inp_kt='_'
    kb='_'
    if text[0].lower() in STARTWORDS: 
        qc_yes = 'QA'
    else:
        qc_yes = 'ST'
    qc_type='DESC'
    #spacy
    doc = nlp(inp)
    typedoc=[]
    #print('spacy: ', [(X.text, X.label_) for X in doc.ents])
    if not doc.ents:
        if (len(sentence_tag)>=3):
            #print ('len: ', len(sentence_tag), sentence_tag[0][1])
            if sentence_tag[1][1][:2]=='JJ':
                #print('JJ')
                inp_kt_tag = sentence_tag[2][1]
                inp_kt = inp_word[1]+' '+inp_word[0]
                #print('JJ: ', inp_kt)
            else:
                inp_kt_tag = sentence_tag[1][1]
                #print (inp_word)
                inp_kt = inp_word[0]
                #print('not JJ 1: ', inp_kt)
                k1=''
                k2=''
                for tags in sentence_tag:
                    #print (tags[1][:2],tags[0])
                    if tags[1][:2]=='NN' and k1=='':
                        k1 = tags[0]
                    if tags[1][:2]=='NN' and k1!='':
                        klist = k1.split(' ')
                        if tags[0] not in klist:
                            k1 = k1+' '+tags[0]
                    if tags[1][:2]=='JJ' and k2=='':
                        k2 = tags[0]
                if k2=='':
                    inp_kt = k1
                else:
                    inp_kt = k2+' '+k1
        else:
            inp_kt = ','.join(text)
            inp_kt_tag = 'unknown'
    else:
        #print ('in else')
        inp_kt=''
        for X in doc.ents:
            #print('spacy term: ',X.label_)
            inp_kt = inp_kt+X.text+','+''
            typedoc.append(X.label_)
            qc_type= X.label_
        if sentence_tag[1][1][:2]=='JJ':
            #print('JJ')
            inp_kt_tag = sentence_tag[2][1]
            inp_kt = inp_kt+inp_word[1]+' '+inp_word[0]
            #print('JJ: ', inp_kt)
        else:
            inp_kt_tag = sentence_tag[1][1]
            inp_kt = inp_word[0]
            #print (inp_word)
            #print('not JJ 2: ', inp_kt)
            k1=''
            k2=''
            for tags in sentence_tag:
                print (tags[1][:2],tags[0])
                if tags[1][:2]=='NN' and k1=='':
                    k1 = tags[0]
                if tags[1][:2]=='NN' and k1!='':
                    klist = k1.split(' ')
                    if tags[0] not in klist:
                        k1 = k1+' '+tags[0]
                if tags[1][:2]=='JJ' and k2=='':
                    k2 = tags[0]
            if k2=='':
                inp_kt = k1
            else:
                inp_kt = k2+' '+k1
    if not reqkey:
        print('')
    else:
        reqkey_lower=[x.lower() for x in reqkey]
        reqkey_tag = nltk.pos_tag(reqkey_lower)
        if reqkey_tag[-1][1][:2]=='VB':
            kb = reqkey[-2]
        else:
            kb = reqkey[-1]
    if is_date(text[last_w]):
        date_yes = text[last_w]
        qc_type = 'DAY'
    appentity = qc_yes+':'+qc_type+':'+inp_kt+':'+inp_kt_tag+':'+date_yes+':'+kb.lower()
    list_kt.append(appentity)
    dislist = inp_kt.split(',')
    checkword = ['symptom','cause','disease','condition']
    flag=0
    if((kb.lower() in checkword) or if_disease_q(reqkey)==1):
        flag=1 
        print ('I see this question related to a health condition...')
    #print (list_kt)
    return list_kt, reqkey, texts, flag


# In[21]:


#que_sentence='what are the symptoms of pneumonia?'
#que_sentence='What is cancer'

#searchkey, dbp_ano, textvalue, flag =sentence_nlp(que_sentence)

#print (searchkey)
#print (dbp_ano)
print ('Qustion analysis API has been processed!')


# In[ ]:





# In[ ]:




