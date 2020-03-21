#!/usr/bin/env python
# coding: utf-8

# In[2]:


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
from random import randint


# In[3]:


import os.path
from os import path


# In[7]:


import QuestionSAv6 as qsa
import NHSsearchv5 as nhs
import Wikisearchv8 as wks


# In[8]:


from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
from rdflib.namespace import DC, FOAF
import spotlight
import urllib, json
import pandas as pd
from collections import Counter


# In[9]:


cn = Namespace("http://healthchatbot.org/condtion/")


# In[169]:


def qa_chat(que_sentence):
    keywords = ['check','avoid','avoiding','prevent','symptoms','symptom','signs','signs','cause','causes','diagnosis','treatment','treatments','treatings','treating','prevention','preventing','complications','living','diagnosed','risk','diagnosis','diagnose','affected']
    if que_sentence[-1] == '?' or que_sentence[-1] == '.':
        que_sentence = que_sentence[:-1]
    wordsin = que_sentence.split()
    sections = []
    topict = ''
    for w in wordsin:
        wx=''
        if w in keywords:
            if (w =='treatments' or w =='treatings' or w=='treatement'):
                w='treatment'
                wx = 'treat'
            if (w =='prevention' or w =='preventings' or w=='prevent'):
                w='preventions'
                wx = 'prevent'
            if (w =='symptom' or w =='signs' or w=='sign' or w =='symtpoms'):
                w='symptoms'
                wx= 'signs'
            if (w =='avoiding'):
                w='avoid'
            if (w == 'diagnose'):
                w='diagnosis'
            #print (w)
            sections.append(w)
            if wx !='':
                sections.append(wx)
            #print (sections)
    if not sections:
        sections.append('overview')
    related_content_1=''
    searchkey, dbp_ano, textvalue, flag = qsa.sentence_nlp(que_sentence)
    #print(searchkey)
    nhsc=''
    for sect in sections:
        #print(searchkey[0].split(':')[-1])
        topict=searchkey[0].split(':')[-1].replace('_','-')
        #print ('t1: '+topict,'s1: '+sect)
        if topict in keywords:
            ks = searchkey[0].split(':')[2].split(' ')
            #print ('ks: ', ks)
            if len(ks)>1:
                #print (ks)
                if ks[0] in keywords:
                    topict = ks[1]
                elif ks[1] in keywords:
                    topict = ks[0]
                else:
                    topict = ks[0].replace(' ','-')
            else:
                ks1 = ks[0].split(',')
                topicts =[]
                for kk in ks1:
                    if not sect.startswith(kk.lower()):
                        topicts.append(kk)
                topict='-'.join(topicts)
                #print ('haha0'+topict+' '+sect)
                nhsc=nhsc+nhs.NHS_pasering(topict,sect)
        else:
            #print ('hah'+topict+' '+sect)
            nhsc=nhsc+nhs.NHS_pasering(topict,sect)
            #print (nhsc)
    #print ('hah'+topict+' ', sections)
    if nhsc=='':
        for sect in sections:
            topicts =[]
            for sk in searchkey[0].split(':')[2].split():
                #print (sect,sk,searchkey[0])
                if not sect.startswith(sk.lower()):
                    topicts.append(sk)
            topict = '-'.join(topicts)
            #print ('haha1: '+topict+' '+sect)
            nhsc=nhsc+nhs.NHS_pasering(topict,sect)
            if nhsc!='':
                break
            for topk in topict.split(','):
                #print ('haha2', topk, sect)
                nhsc=nhsc+nhs.NHS_pasering(topk,sect)
            if nhsc =='':
                nhsc=nhs.NHS_pasering(topict.replace(',','-'),sect)
                if nhsc=='':
                    nhsc=nhs.NHS_pasering(topict.replace('_','-'),sect)
                    if nhsc!='':
                        topict=topict.replace(',','-')
                else:
                    topict=topict.replace(',','-')
                #print ('nhs: ',nhsc)
    #print ('embeded: '+topict)
    #print (nhsc)
    if nhsc =='':
        topict = []
    if not topict:
        topict=searchkey[0].split(':')[-1].replace('_','-')
    if not sections:
        sections.append('overview')
    robostring = check_knowledge(topict,sections)
    if robostring !='' and nhsc!='':
        return nhsc, 'Robo knowledge: ['+robostring+']', '', sections
    if robostring !='' and nhsc=='':
        return 'Robo knowledge: ['+robostring+']', '', '', sections
    print(topict)
    #print(textvalue)
    related_content_1,rankingkey =wks.wiki_search(searchkey,dbp_ano,textvalue)
    #print (related_content_1)
    if related_content_1=='_' or related_content_1=='___' or related_content_1=='__' or related_content_1=='____' or related_content_1=='______' or not related_content_1:
        #print('in db search')
        related_content_2=wks.wiki_search_dbp(searchkey,dbp_ano)
        answer_txt_1=wks.wiki_answer_ranking_vec(related_content_2,que_sentence,searchkey,rankingkey)
        answer_txt_2=wks.wiki_answer_ranking(related_content_2,que_sentence,searchkey,rankingkey)
        #print('_____________________________________________')
        #print('DBpdia answer1:', answer_txt_2)
        #print('_____________________________________________')
        #print('DBpdia answer2:', answer_txt_1) 
        if nhsc=='':
            return answer_txt_1, answer_txt_2,topict,sections
        else:
            return nhsc, answer_txt_2,topict,sections
    else:
        answer_txt_1=wks.wiki_answer_ranking(related_content_1,que_sentence,searchkey,rankingkey)
        #print('_____________________________________________')
        #print('Answer:', answer_txt_1)
        answer_txt_2=wks.wiki_answer_ranking_vec(related_content_1,que_sentence,searchkey,rankingkey)
        #print('_____________________________________________')
        #print('Additional knowledge:', answer_txt_2)
        if nhsc=='':
            return answer_txt_1, answer_txt_2,topict,sections
        else:
            return nhsc, answer_txt_2,topict,sections
     


# In[227]:


#an1,an2,topic,q = qa_chat('What is flu?')
#print (an1)
#print('health chatbot api is loaded!')


# In[228]:


#print(an1)
#terms = db_term_find(an1)
#d_terms = term_process(terms,an1)
#print(d_terms)
#print(an2)


#print('done contents')


# In[229]:


#print(topic)
#print(q)


# In[230]:


#semantic_generation(an1,topic,q)


# In[159]:


def semantic_generation(an1,topic,qu):
    if topic!='':
        terms = db_term_find(an1)
        d_terms = term_process(terms,an1)
        graph_generation(d_terms,topic,qu)


# In[16]:


#procausalwords=['as a result of', 'because of', 'due to', 'since', 'as', 'the resason', 'as a consequence of', 'result in']
#actcausalwords=['so','lead to', 'causes', 'contribute to']


# In[232]:


#def find_causal_relations(relatedContent):
   # print (relatedContent)
    #for sent in relatedContent.split('.'):
        #for word in sent.split():
            #if word in procausalwords:
                #print(sent)
            #elif word in actcausalwords:
                #print(sent+'...')


# In[233]:


def db_term_find(inp_db):
    restAPI='http://api.dbpedia-spotlight.org/en/annotate'
    #inp_word = inp_db.split()
    annotation=[]
    try:
        annotation = spotlight.annotate(restAPI,inp_db,confidence=0.09,support=20)
        #print(annotation)
        #return annotation
    except: 
        e= 'no annoation find in DBpedia'
        print (e)
    return annotation


# In[19]:


def term_process(anno,inp_db):
    inp_word = inp_db.split()
    #print (inp_word)
    reqk=[]
    existk =[]
    #print (len(anno))
    for terms in anno:
        uniterms = unicodedata.normalize('NFKD',terms['URI']).encode('ascii','ignore')
        #print(uniterms)
        sem_key = str(uniterms).split('/')[-1][0:-1].lower()
        #print (sem_key)
        #if (sem_key in inp_word) and (sem_key not in existk):
        if sem_key not in existk:
            existk.append(sem_key)
            #print('in if' + str(uniterms).split('/')[-1][0:-1])
            #print(str(uniterms)+' type: ', db_term_type(str(uniterms).split('/')[-1][0:-1]))
            if db_term_type(str(uniterms).split('/')[-1][0:-1])!='':
                reqk.append(str(uniterms).split('/')[-1][0:-1]+':'+db_term_type(str(uniterms).split('/')[-1][0:-1]))
        #else:
            #sem_key=sem_key.replace('_',' ')
            #print('not in if: '+sem_key)
            #for xs in inp_word:
                #print(xs)
                #if xs[-1]=='?' or xs[-1]=='.':
                    #xs=xs[:-1]
                    #print('DBp anno: '+sem_key,xs)
                #if sem_key.startswith(xs.lower()) or xs.lower().startswith(sem_key) or sem_key.endswith(xs.lower()):
                    #print('2nd: ', db_term_type(str(uniterms).split('/')[-1][0:-1]))
                    #if db_term_type(str(uniterms).split('/')[-1][0:-1])!='':
                        #reqk.append(str(uniterms).split('/')[-1][0:-1]+':'+db_term_type(str(uniterms).split('/')[-1][0:-1]))
                        #print('break')
                        #break
    return list(dict.fromkeys(reqk))


# In[187]:


def graph_generation(rk,t,q):
    t=t.split(',')[-1]
    sdg = Graph()
    causes = URIRef(cn.causesDisease)
    anatomicOn = URIRef(cn.causeOnAnatomicStructure)
    drug = URIRef(cn.drugTo)
    diag = URIRef(cn.diagnosisTo)
    symptomOf = URIRef(cn.causesSymptom)
    treatment = URIRef(cn.treatmentTo)
    question=  URIRef(cn.question)
    answer = URIRef(cn.answerTo)
    anabout = URIRef(cn.aLabel)
    agegroup = URIRef(cn.causesAffectionToAgeGroup)
    disease = URIRef('http://dbpedia.org/ontology/Disease')
    wikidisease = URIRef('https://www.wikidata.org/wiki/Q12136')
    anat = URIRef('http://dbpedia.org/ontology/AnatomicalStructure')
    wikianat = URIRef('https://www.wikidata.org/wiki/Q4936952')
    symp = URIRef('http://dbpedia.org/resource/Category:Symptoms_and_signs')
    presign = URIRef('http://purl.org/dc/terms/subject')
    drugs = URIRef('http://dbpedia.org/ontology/Drug')
    condition = URIRef('http://umbel.org/umbel/rc/AilmentCondition')
    diseaseProperty = URIRef('http://dbpedia.org/property/diseasesdb')
    diags = URIRef('http://dbpedia.org/page/Medical_diagnosis')
    treats = URIRef('http://dbpedia.org/page/Therapy')
    ages = URIRef('http://dbpedia.org/page/Category:Human_development')
    sex = URIRef('http://dbpedia.org/page/Category:Sex')
    conditionname = t.split(',')
    if len(conditionname)>1:
        rsub = URIRef('http://healthchatbot.org/knowledge/condtion/'+conditionname[-1])
        filepath='cknns/'+conditionname[-1]+'.ttl'
    else:
        rsub = URIRef('http://healthchatbot.org/knowledge/condtion/'+t)
        if t!='':
            filepath='cknns/'+t+'.ttl'
        else:
            filepath='cknns/error.ttl'
    sdg.add( (rsub, RDF.type, disease) ) 
    
    if path.exists(filepath):
        sdg.parse(filepath, format="ttl")
    snode = BNode()
    sdg.add( (rsub, question, snode))
    if not q:
        sdg.add( (snode, anabout, Literal('overview'))) 
    else:
        for qx in q:
            sdg.add( (snode, anabout, Literal(qx)))    
    for r in rk:
        r= r.split(':')
        rterm = r[0]
        rtype = r[1]
        if rtype == 'Symptom':
            robj = URIRef('http://dbpedia.org/page/'+rterm)
            sdg.add( (robj, RDF.type, symp) )
            sdg.add((robj, answer, snode))
            sdg.add( (rsub, symptomOf, robj) )
        elif rtype == 'Disease':
            robj = URIRef('http://dbpedia.org/page/'+rterm)
            sdg.add( (robj, RDF.type, disease) )
            sdg.add( (robj, causes, rsub) )
            sdg.add((robj, answer, snode))
            sdg.add( (rsub, symptomOf, robj) )
        elif rtype == 'AnatomicalStructure':
            robj = URIRef('http://dbpedia.org/page/'+rterm)
            sdg.add( (robj, RDF.type, anat) )
            sdg.add((robj, answer, snode))
            sdg.add( (rsub, anatomicOn, robj) )
        elif rtype == 'Drug':
            robj = URIRef('http://dbpedia.org/page/'+rterm)
            sdg.add( (robj, RDF.type, drugs) )
            sdg.add((robj, answer, snode))
            sdg.add( (robj, drug, rsub) )
        elif rtype == 'Medical_diagnosis':
            robj = URIRef('http://dbpedia.org/page/'+rterm)
            sdg.add( (robj, RDF.type, diags) )
            sdg.add((robj, answer, snode))
            sdg.add( (robj, diag, rsub) )
        elif rtype == 'Medical_treatments':
            robj = URIRef('http://dbpedia.org/page/'+rterm)
            sdg.add( (robj, RDF.type, treats) )
            sdg.add((robj, answer, snode))
            sdg.add( (robj, treatment, rsub) )
        elif rtype == 'AgeGroup':
            robj = URIRef('http://dbpedia.org/page/'+rterm)
            sdg.add( (robj, RDF.type, ages) )
            sdg.add((robj, answer, snode))
            sdg.add( (rsub, agegroup, robj) )
        elif rtype == 'Gender':
            robj = URIRef('http://dbpedia.org/page/'+rterm)
            sdg.add( (robj, RDF.type, sex) )
            sdg.add((robj, answer, snode))
            sdg.add( (rsub, agegroup, robj) )
            
     # ntriples, n3, turtle   
    #print (sdg.serialize(format='turtle'))
    if t!='':
        #globalsdg = Graph()
        #globalpath = 'cknns/glo_cknn.ttl'
        sdg.serialize(destination=filepath, format='turtle')
        #globalsdg.parse(sdg)
        sdg.close()
        #globalsdg.parse(filepath, format="turtle")
        #globalsdg.parse(globalpath, format="turtle")
        #globalsdg.serialize(destination=globalpath, format='turtle')
        #globalsdg.close()


# In[84]:


def db_term_type(dbp_k):
    flag = ''
    dbpdialink = 'http://dbpedia.org/data/'+dbp_k+'.json'
    with urllib.request.urlopen(dbpdialink) as url:
        jicdata = json.loads(url.read())
        if 'http://dbpedia.org/resource/'+dbp_k not in jicdata:
            return flag
        else:
            firstkey=jicdata['http://dbpedia.org/resource/'+dbp_k]
            #print(firstkey)
            if 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type' in firstkey:
                secondkey=[]
                secondkeylist = firstkey['http://www.w3.org/1999/02/22-rdf-syntax-ns#type']
                for keylist in secondkeylist:
                    secondkey.append(keylist['value'])
                    #print (dbp_k)
                    #print (secondkey)
                if 'http://umbel.org/umbel/rc/AilmentCondition' in secondkey:
                    flag = 'Symptom'
                    return flag
                if 'http://dbpedia.org/ontology/Disease' in secondkey:
                    if 'pain' in dbp_k.split('_'):
                        flag = 'Symptom'
                    else:
                        flag = 'Disease'
                    return flag
                if 'http://dbpedia.org/ontology/AnatomicalStructure' in secondkey:
                    flag = 'AnatomicalStructure'
                    return flag
                if 'http://dbpedia.org/ontology/Drug' in secondkey:
                    if dbp_k!='Adult': 
                        flag = 'Drug'
                    else:
                        flag = 'AgeGroup'
                    return flag
                if 'http://dbpedia.org/ontology/Food' in secondkey:
                    flag = 'Medical_treatments'
                    return flag
                if 'http://dbpedia.org/class/yago/Intervention101240210' in secondkey:
                    flag = 'Medical_diagnosis'
                    return flag
                if flag =='':
                    if 'http://dbpedia.org/property/field' in firstkey:
                        secondkey = firstkey['http://dbpedia.org/property/field']
                        for typei in secondkey:
                            #print (typei)
                            if typei['value'].split('/')[-1] in ['Infectious_disease_(medical_specialty)','Disease']:
                                flag = 'Disease'
                                return flag
                if flag =='':
                    if 'http://dbpedia.org/property/diseasesdb' in firstkey:
                        flag = 'Symptom'
                        return flag
                if flag =='':
                    #print (firstkey)
                    if 'http://purl.org/dc/terms/subject' in firstkey:
                            secondkey=[]
                            secondkeylist = firstkey['http://purl.org/dc/terms/subject']
                            #print (secondkeylist)
                            for keylist in secondkeylist:
                                if keylist['value'].endswith('therapy') or keylist['value'].endswith('treatments'):
                                    flag = 'Medical_treatments'
                                    return flag
                                if '_treatments' in keylist['value'].split('/')[-1]:
                                    flag = 'Medical_treatments'
                                    return flag
                                if '_drugs' in keylist['value'].split('/')[-1]:
                                    flag = 'Medical_treatments'
                                    return flag
                                if 'drugs' in keylist['value'].split('/')[-1].split('_')[-1]:
                                    flag = 'Drug'
                                    return flag
                                #http://dbpedia.org/page/Category:Symptoms_and_signs:_Respiratory_system
                                if keylist['value'].startswith('http://dbpedia.org/page/Category:Symptoms_and_signs'):
                                    flag = 'Symptom'
                                #http://dbpedia.org/page/Category:Human_body
                                if keylist['value'].endswith('Human_body'):
                                    flag = 'AnatomicalStructure'
                                    return flag
                                #print(keylist['value'].split(':')[-1])
                                if keylist['value'].split(':')[-1] in ['Ageing', 'Human_development','Developmental_psychology','Infancy','Youth','Adulthood']:
                                    flag = 'AgeGroup'
                                    return flag
                                if keylist['value'].split(':')[-1] in ['Sex','Females','Males']:
                                    flag = 'Gender'
                                    return flag
            else:
                #print(firstkey)
                if 'http://dbpedia.org/property/field' in firstkey:
                    secondkey = firstkey['http://dbpedia.org/property/field']
                    for typei in secondkey:
                        #print (typei)
                        if typei['value'].split('/')[-1] in ['Infectious_disease_(medical_specialty)','Disease', 'Pediatrics']:
                            flag = 'Symptom'
                            return flag
                if flag =='':
                    if 'http://dbpedia.org/property/diseasesdb' in firstkey:
                        flag = 'Symptom'
                        return flag
    return flag


# In[240]:


#print(db_term_type('Woman'))


# In[23]:


def check_knowledge(tp,section):
    topistring=''
    sdg = Graph()
    causes = URIRef(cn.causesDisease)
    anatomicOn = URIRef(cn.causeOnAnatomicStructure)
    drug = URIRef(cn.drugTo)
    diag = URIRef(cn.diagnosisTo)
    symptomOf = URIRef(cn.causesSymptom)
    treatment = URIRef(cn.treatmentTo)
    question=  URIRef(cn.question)
    answer = URIRef(cn.answerTo)
    anabout = URIRef(cn.aLabel)
    disease = URIRef('http://dbpedia.org/ontology/Disease')
    wikidisease = URIRef('https://www.wikidata.org/wiki/Q12136')
    anat = URIRef('http://dbpedia.org/ontology/AnatomicalStructure')
    wikianat = URIRef('https://www.wikidata.org/wiki/Q4936952')
    symp = URIRef('http://dbpedia.org/resource/Category:Symptoms_and_signs')
    presign = URIRef('http://purl.org/dc/terms/subject')
    drugs = URIRef('http://dbpedia.org/ontology/Drug')
    condition = URIRef('http://umbel.org/umbel/rc/AilmentCondition')
    diseaseProperty = URIRef('http://dbpedia.org/property/diseasesdb')
    diags = URIRef('http://dbpedia.org/page/Medical_diagnosis')
    treats = URIRef('http://dbpedia.org/page/Therapy')
    ages = URIRef('http://dbpedia.org/page/Category:Human_development')
    sdg = Graph()
    filepath='cknns/'+tp+'.ttl'
    if path.exists(filepath):
        sdg.parse(filepath, format="ttl")
        if not section:
            print('check user input')
        else:
            counter = 0
            querystring = "SELECT DISTINCT ?t ?p WHERE {"
            if not section:
                querystring = querystring + "?d <"+question+"> ?n . ?n <"+anabout+"> ?s FILTER regex(str(?s), 'concept') ."
            #print (section)
            for sx in section:
                if counter ==0:
                    #print(counter)
                    querystring = querystring + "{?d <"+question+"> ?n . ?n <"+anabout+"> ?s FILTER regex(str(?s), '"+sx+"') ."
                else:
                    querystring = querystring + "} UNION {?d <"+question+"> ?n . ?n <"+anabout+"> ?s FILTER regex(str(?s), '"+sx+"')}"
                counter=counter+1
            if len(section)>1:
                querystring = querystring+" . ?t <"+answer+"> ?n . ?t <"+RDF.type+"> ?p ." 
            else:

                querystring = querystring+" ?t <"+answer+"> ?n . ?t <"+RDF.type+"> ?p .}"

            querystring = querystring+"}"
            #print (querystring)
            qres = sdg.query(querystring)
            sympstring=''
            drugstring=''
            tretstring=''
            diagstring=''
            onbostring=''
            disestring=''
            agegstring=''
            if (len(qres)!=0):
                #print (qres)
                topistring=tp.replace('-',' ')+' is a human disease.'
                for row in qres:
                    p = str(row.asdict()['p'].toPython())
                    t = str(row.asdict()['t'].toPython()).split('/')[-1].replace('_',' ')
                    #print(t,tp.replace('-',' '))
                    if t!= '':
                        if p!='' and p=='http://dbpedia.org/ontology/Disease' and t.lower()!=tp.replace('-',' '):
                            if t.lower()!='disease':
                                disestring=disestring+t+", "
                        elif p!='' and p=='http://dbpedia.org/resource/Category:Symptoms_and_signs' and t.lower()!=tp.replace('-',' '):
                            if t.lower()!='disease':
                                sympstring=sympstring+t+", "
                        elif p!='' and p=='http://dbpedia.org/ontology/Drug' and len(t)>3:
                            drugstring=drugstring+t+", "
                        elif p!='' and p=='http://dbpedia.org/page/Therapy':
                            tretstring=tretstring+t+", "
                        elif p!='' and p=='http://dbpedia.org/page/Medical_diagnosis':
                            diagstring=diagstring+t+", "
                        elif p!='' and p=='http://dbpedia.org/ontology/AnatomicalStructure':
                            onbostring=onbostring+t+", "
                        elif p!='' and (p=='http://dbpedia.org/page/Category:Human_development' or p=='http://dbpedia.org/page/Category:Sex'):
                            if t.lower()!='people':
                                agegstring=agegstring+t.lower()+", "
                if disestring !='' and len(disestring)>2:
                    topistring=topistring+' It is normally related or has complications to other kinds of dieases, e.g. '+disestring[:-2] +'.'
                if tretstring !='' and len(tretstring)>2:
                    topistring=topistring+' The types of treatments (depending on your own condition) may include: '+tretstring[:-2]+'.'
                if drugstring !='' and len(drugstring)>2:
                    topistring=topistring+' The treatment drugs are available e.g. '+ drugstring[:2] +'.\n'
                if diagstring !='' and len(diagstring)>2:
                    topistring=topistring+' The methods for diagnosis '+tp.replace('-',' ')+' are(but not limited to): '+diagstring[:2] +'.'
                if sympstring !='' and len(sympstring)>2:
                    topistring=topistring+' The main symptoms as the condition progresses include: '+ sympstring[:-2]+'.'
                if onbostring !='' and len(onbostring)>2:
                    topistring=topistring+' With this condition you may feel unwell on: '+ onbostring[:-2] +'.\n'
                if agegstring !='' and len(agegstring)>2:
                    topistring=topistring+' The groups have an increased risk are '+ agegstring[:-2] +' people.'
    return topistring


# In[234]:


#evaluation_pipe('chickenpox')


# In[235]:


def global_cknn(dname):
    dname=dname.replace(' ','-')
    filepath='cknns/'+dname+'.ttl'
    globalsdg = Graph()
    globalpath = 'cknns/glo_cknn.ttl'
    globalsdg.parse(filepath, format="turtle")
    globalsdg.parse(globalpath, format="turtle")
    globalsdg.serialize(destination=globalpath, format='turtle')
    globalsdg.close()


# In[236]:


#global_cknn('diabetes-mellitus')


# In[180]:


import time


# In[237]:


def evaluation_pipe(dname):
    td,topic = testing(dname)
    e = evaluation_cknn(topic)
    for ex in e:
        for element in ex[0]:
            print(element+':'+str(ex[0].get(element)))
    #print(td)
    global_cknn(topic)
    


# In[238]:


def testing(dname):
    testing_data=[]
    question_list = ['What is the ','What are the symptoms of ','who is affected by ','what are the causes of ', 'How to diagnose ','What are the treatments of ']
    q_counter=0
    for q in question_list:
        question = q+dname
        #print(question)
        an1,an2,topic,qu = qa_chat(question)
        if an1!='' and an1!='_':
            testing_data.append('Q'+str(q_counter)+':Y')
            #print(an1)
            #print(topic)
        else:
            testing_data.append('Q'+str(q_counter)+':N')
        semantic_generation(an1,topic,qu)
        time.sleep(5)
        #print('-----------')
        q_counter=q_counter+1
    return testing_data,topic


# In[203]:


def evaluation_cknn(tp):
    evaluation_data=[]
    sdg = Graph()
    causes = URIRef(cn.causesDisease)
    anatomicOn = URIRef(cn.causeOnAnatomicStructure)
    drug = URIRef(cn.drugTo)
    diag = URIRef(cn.diagnosisTo)
    symptomOf = URIRef(cn.causesSymptom)
    treatment = URIRef(cn.treatmentTo)
    question=  URIRef(cn.question)
    answer = URIRef(cn.answerTo)
    anabout = URIRef(cn.aLabel)
    disease = URIRef('http://dbpedia.org/ontology/Disease')
    wikidisease = URIRef('https://www.wikidata.org/wiki/Q12136')
    anat = URIRef('http://dbpedia.org/ontology/AnatomicalStructure')
    wikianat = URIRef('https://www.wikidata.org/wiki/Q4936952')
    symp = URIRef('http://dbpedia.org/resource/Category:Symptoms_and_signs')
    presign = URIRef('http://purl.org/dc/terms/subject')
    drugs = URIRef('http://dbpedia.org/ontology/Drug')
    condition = URIRef('http://umbel.org/umbel/rc/AilmentCondition')
    diseaseProperty = URIRef('http://dbpedia.org/property/diseasesdb')
    diags = URIRef('http://dbpedia.org/page/Medical_diagnosis')
    treats = URIRef('http://dbpedia.org/page/Therapy')
    ages = URIRef('http://dbpedia.org/page/Category:Human_development')
    sdg = Graph()
    tp=tp.replace(' ','-')
    filepath='cknns/'+tp+'.ttl'
    if path.exists(filepath):
        sdg.parse(filepath, format="ttl")
        querystring = "SELECT DISTINCT ?t ?p WHERE {"
            
        querystring = querystring + "?t <"+RDF.type+"> ?p ." 

        querystring = querystring+"}"
        #print (querystring)
        qres = sdg.query(querystring)
        sympstring=0
        drugstring=0
        tretstring=0
        diagstring=0
        onbostring=0
        disestring=0
        agegstring=0
        if (len(qres)!=0):
            #print (qres)
            topistring=tp.replace('-',' ')+' is a human disease.'
            for row in qres:
                p = str(row.asdict()['p'].toPython())
                t = str(row.asdict()['t'].toPython()).split('/')[-1].replace('_',' ')
                #print(t,tp.replace('-',' '))
                if t!= '':
                    if p!='' and p=='http://dbpedia.org/ontology/Disease' and t.lower()!=tp.replace('-',' '):
                        if t.lower()!='disease':
                            disestring=disestring+1
                    elif p!='' and p=='http://dbpedia.org/resource/Category:Symptoms_and_signs' and t.lower()!=tp.replace('-',' '):
                        if t.lower()!='disease':
                            sympstring=sympstring+1
                    elif p!='' and p=='http://dbpedia.org/ontology/Drug' and len(t)>3:
                        drugstring=drugstring+1
                    elif p!='' and p=='http://dbpedia.org/page/Therapy':
                        tretstring=tretstring+1
                    elif p!='' and p=='http://dbpedia.org/page/Medical_diagnosis':
                        diagstring=diagstring+1
                    elif p!='' and p=='http://dbpedia.org/ontology/AnatomicalStructure':
                        onbostring=onbostring+1
                    elif p!='' and (p=='http://dbpedia.org/page/Category:Human_development' or p=='http://dbpedia.org/page/Category:Sex'):
                        if t.lower()!='people':
                            agegstring=agegstring+1
            evaluation_data.append([{'Related_disease':disestring,'Symptoms':sympstring,'Drugs':drugstring,'Treatments':tretstring,'Diagnosis_methods':diagstring,'anatomical_structure':onbostring,'age_group/gender':agegstring}])
    return evaluation_data


# In[ ]:





# In[ ]:




