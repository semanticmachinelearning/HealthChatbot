#!/usr/bin/env python
# coding: utf-8

# In[7]:


import wikiprocessv1 as wikip
from nltk.stem import PorterStemmer
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


# In[8]:


def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)


# In[9]:


symplist=['symptom,symptoms,sympt,Symptom,Symptoms,Sympt,sign,Sign']


# In[10]:


def check_keypair(wiki_kx, rkx):
    ps = PorterStemmer()
    wiki_w=wiki_kx.split('_')
    rkx_w = rkx.split('_')
    rk_tem = []
    check_flag = 0
    for rw in rkx_w:
        for ww in wiki_w:
            #print(rw, ww)
            #print('stem: ',ps.stem(rw),ww)
            if  ps.stem(rw).lower() ==  ps.stem(ww).lower():
                #print('stem: ',rw,ww)
                check_flag = 1
                break
    return check_flag 


# In[11]:


def wiki_search(list_key,reqkey,textv):
    content_ans = ''
    keypair =[]
    #print (list_key)
    for wiki_key in list_key:
        wiki_ke = wiki_key.split(':')[-4]
        if wiki_ke !='':
            for x_key in wiki_ke.split(','):
                if x_key!='':
                    #print('in search:',x_key)
                    wiki_k = x_key.replace(' ','_')
                    if wiki_k !='':
                        #print(wiki_k)
                        if not reqkey:
                            print('no section request for wiki search')
                        else:
                            for rk in reqkey:
                                #print(wiki_k,rk)
                                flag = check_keypair(wiki_k, rk)
                                if flag==0:
                                    if rk.lower()+','+wiki_k.lower() not in keypair:
                                        keypair.append(rk.lower()+','+wiki_k.lower())
                                    #print(wiki_key,rk)
                                    #print('not same:', wiki_k.capitalize(),rk.capitalize())
                                    if wiki_k.capitalize() in symplist: 
                                        wikiapir ='_'
                                    else:
                                        wikiapir=wikip.wikiparser(wiki_k.capitalize(),rk.capitalize())
                                    if str(wikiapir) != '_':
                                        #print ('section haha 1: ',wikiapir)
                                        #print(type(wikiprocessv2.wikiparser(wiki_key,rk.capitalize())))
                                        content_ans=content_ans+str(wikiapir)
                                    else:
                                        for wiki_k_x in wiki_k.split('_'):
                                            wikiapir=''
                                            #print ('_ 1.1 search: ', wiki_k_x.capitalize(),rk.capitalize())
                                            if wiki_k_x.capitalize() in symplist:
                                                wikiapir='_'
                                            else:
                                                wikiapir=wikip.wikiparser(wiki_k_x.capitalize(),rk.capitalize())
                                                #print(wikiapir)
                                                if str(wikiapir) == '_':
                                                    wikiapir=''
                                                    #print ('_ 1.2 search: ', rk.capitalize(), wiki_k_x.capitalize())
                                                    wikiapir=wikip.wikiparser(rk.capitalize(),wiki_k_x.capitalize())
                                                    #print('_1.2 result: ',wikiapir)
                                                    if str(wikiapir) == '_':
                                                        wikiapir=''
                                                        for rki in reqkey:
                                                            flag = check_keypair(rki, rk)
                                                            if flag==0:
                                                            #print ('_ 1.3 search: ', rki.capitalize(), rk.capitalize())
                                                                wikiapir=wikip.wikiparser(rki.capitalize(),rk.capitalize())
                                                            #print('_1.3 result: ',wikiapir)
                                                    if str(wikiapir) == '_':
                                                        wikiapir=''
                                                        for txt in textv:
                                                            #print(txt,rk)
                                                            flag = check_keypair(txt, rk)
                                                            if flag==0:
                                                                #print ('_ 1.4 search: ', rk.capitalize(), txt.capitalize())
                                                                wikiapir=wikip.wikiparser(rk.capitalize(), txt.capitalize())
                                                                #print('_1.4 result: ',wikiapir)
                                            content_ans=content_ans+str(wikiapir)
    #print('first search:',content_ans)
    return content_ans, keypair


# In[2]:


def wiki_search_dbp(list_key,reqkey):
    content_ans = ''
    for wiki_key in list_key:
        #print(wiki_key)
        if wiki_key !='':
            wiki_k = wiki_key.split(':')[-4]
            for wiki_ke in wiki_k.split(','):
                if wiki_ke!='':
                    wiki_k = wiki_k.replace(' ','_')
                    #print('in 2nd wiki search:',wiki_k)
                    if wiki_k !='': 
                        for rk in reqkey:
                           # print(wiki_k,rk)
                            flag = check_keypair(rk,wiki_k)
                            if flag==0:
                                #print('not same',rk,wiki_k)
                                wikiapir=wikip.wikiparser(rk,wiki_k.capitalize())
                                if str(wikiapir) != '_':
                                    content_ans=content_ans+str(wikiapir)
                                else:
                                    #print('in 1st dbp serach:',rk)
                                    content_ans=content_ans+'.'+dbp_query(rk)
                                    content_ans=content_ans+'.'+dbp_query(wiki_k.capitalize())
                                    #print(content_ans)
                            else:
                                #print('in 2nd dbp serach:', rk)
                                content_ans=content_ans+'.'+dbp_query(rk)
                                content_ans=content_ans+'.'+dbp_query(wiki_k.capitalize())
    return content_ans


# In[13]:


def dbp_query(wiki_key):
    wiki_ke = wiki_key.split(',')
    #print('in dbp_query function: '+wiki_key)
    longDescription=''
    for dbp_k in wiki_ke:
        dbpdialink = 'http://dbpedia.org/data/'+dbp_k+'.json'
        with urllib.request.urlopen(dbpdialink) as url:
            jicdata = json.loads(url.read())
            if 'http://dbpedia.org/resource/'+dbp_k not in jicdata:
                print('no term find')
            else:
                firstkey=jicdata['http://dbpedia.org/resource/'+dbp_k]
                if 'http://dbpedia.org/ontology/abstract' in firstkey:
                    secondkey = firstkey['http://dbpedia.org/ontology/abstract']
                    for abstract in secondkey:
                        if abstract['lang'] == 'en':
                            longDescription=longDescription+abstract['value']
    
                
    return longDescription


# In[14]:


def wiki_answer_ranking(longDescription,inp,list_key,rankkeys):
    wiki_key = list_key[0].split(':')[1]
    texts=longDescription.split('.')
    highest_position=0
    j=0
    highest_score=0.0
    if inp[-1] =='.' or inp[-1] =='?':
        inp=inp[0:-1]
    for txti in texts:
        X_list = word_tokenize(inp)  
        Y_list = word_tokenize(txti) 
        #print(X_list,Y_list)
        sw = stopwords.words('english')
        l1 =[];l2 =[] 
  
        # remove stop words from string 
        X_set = {w for w in X_list if not w in sw}  
        Y_set = {w for w in Y_list if not w in sw}
        counts=0.0
            #print('additonal score:'+rk)     
        #ngram
        #ngrams_1 = list(ngrams(X_set, 3))
        #ngrams_2 = list(ngrams(Y_set, 3))
        #simicount =0
        #if not ngrams_1 or not ngrams_2:
        #    continue
        #else:
         #   for ngx in ngrams_1[0]:
          #      for ngy in ngrams_2:
           #         if ngy:
            #            for ngyx in ngy:
             #               if ngyx==ngx:
              #                  simicount += 1
               #                 print (ngyx)
        #add_score = 0*0.05
        # form a set containing keywords of both strings
        rvector = X_set.union(Y_set)
        for w in rvector: 
            if w in X_set: l1.append(1) # create a vector 
            else: l1.append(0) 
            if w in Y_set: l2.append(1) 
            else: l2.append(0) 
        c = 0
        for i in range(len(rvector)): 
            c+= l1[i]*l2[i] 
        if float((sum(l1)*sum(l2))**0.5) != 0:
            cosine = c / float((sum(l1)*sum(l2))**0.5)
            if wiki_key == 'NUM':
                if hasNumbers(txti):
                    cosine = cosine+0.2
                    #print('NUM')
                else:
                    cosine = cosine-0.2
        else: cosine=0.0
        cosine = cosine + counts
        if cosine>highest_score:
            highest_score=cosine
            highest_position = j
        #print("similarity-", j,' : ', cosine) 
        #print (texts[highest_position])
        j+=1
    #print (texts[highest_position])
    if highest_position+1<len(texts):
        #print('this is text 0: ', texts[2][-1])
        answer_txt =texts[1]+'.'+texts[2]+'.'+texts[highest_position]+'.'+texts[highest_position+1]
        if texts[2][-1].isdigit():
            answer_txt =texts[1]+'.'+texts[2]+'.'+texts[3]+'.'+texts[highest_position]+'.'+texts[highest_position+1]
    else:
        if len(texts)>3:
            answer_txt =texts[1]+'.'+texts[2]+'.'+texts[highest_position]
        else:
            answer_txt= texts
    if wiki_key == 'DESC':
        answer_txt = texts[0:4]
    return ''.join(answer_txt)


# In[15]:


import warnings 
  
warnings.filterwarnings(action = 'ignore') 
  
import gensim 
from gensim.models import Word2Vec 
import re
from nltk.util import ngrams


# In[6]:


def wiki_answer_ranking_vec(longDescription,inp,list_key,rankkeys):
    wiki_key = list_key[0].split(':')[1]
    texts=longDescription.split('.')
    highest_position=0
    j=0
    highest_score=0.0
    if inp[-1] =='.' or inp[-1] =='?':
        inp=inp[0:-1]
    for txti in texts:
        X_list = nlp(inp)  
        Y_list = nlp(txti) 
        #print(X_list,Y_list)
        sw = stopwords.words('english')
        #l1 =[];l2 =[] 
  
        # remove stop words from string 
        #X_set = {w for w in X_list if not w in sw}  
        #Y_set = {w for w in Y_list if not w in sw}
        #counts=0.0
        #X_tokens = nlp("dog cat banana")
        cosine = Y_list.similarity(X_list)
        if wiki_key == 'NUM':
            if hasNumbers(txti):
                cosine = cosine+0.2
                #print('NUM')
            else:
                cosine = cosine-0.2
        if cosine>highest_score:
            highest_score=cosine
            highest_position = j
        #print("similarity-", j,' : ', cosine) 
        #print (texts[highest_position])
        j+=1
    #print (texts[highest_position])
    if highest_position+1<len(texts):
        answer_txt = texts[highest_position]+'.'+texts[highest_position+1]
    else:
        answer_txt = texts[highest_position]
    return ''.join(answer_txt)


# In[35]:


#searchkey=['QA:DESC:symptom:VBD:N:Pneumonia']
#dbp_ano = ['Symptom', 'Pneumonia']
#textvalue = ['What', 'symptoms', 'pneumonia', '?']
#related_content_1 = wiki_search(searchkey,dbp_ano,textvalue) 
#related_content_2 = wiki_search_dbp(searchkey,dbp_ano)
print ('Wiki and DBpedia search is loaded')
#print (related_content_2)


# In[ ]:




