#!/usr/bin/env python
# coding: utf-8

# In[26]:


from lxml import html
import pandas as pd
from collections import namedtuple
from dateutil.parser import parse
import requests
from nltk.stem import PorterStemmer


# In[47]:


def NHS_pasering(topic,section):
    ps = PorterStemmer()
    reqlink = 'https://www.nhs.uk/conditions/'+topic+'/'
    #print(reqlink)
    page = requests.get(reqlink)
    tree = html.fromstring(page.content)
    xpathquery = "//div[@class='nhsuk-grid-column-two-thirds']/section/a[@id ='"+section+"']/../p//text() | //div[@class='nhsuk-grid-column-two-thirds']/section/a[@id ='"+section+"']/../ul/li/text() | //div[@class='nhsuk-grid-column-two-thirds']/section/a[@id ='"+section+"']/../ul/li/a/text()"
    sections = tree.xpath(xpathquery)
    #subsections = tree.xpath('//span[@class="nhsuk-grid-column-two-thirds"]/section/text()')
    #leftelements = tree.xpath('//div[@class="body"]/ul/li[@id="t-wikibase"]/a/@href')
    #print (page.content)
    sectname = section
    if not sections:
        section = section.capitalize()
        xpathquery = "//div[@class='nhsuk-grid-column-two-thirds']//section//*[contains(text(), '"+section+"')]/../p//text() | //div[@class='nhsuk-grid-column-two-thirds']//section//*[contains(text(), '"+section+"')]/../ul/li/text() | //div[@class='nhsuk-grid-column-two-thirds']//section//*[contains(text(), '"+section+"')]/../ul/li/a/text()"
        #print (xpathquery)
        sections = tree.xpath(xpathquery)
    if not sections:
        section = section.lower()
        xpathquery = "//div[@class='nhsuk-grid-column-two-thirds']//section//*[contains(text(), '"+section+"')]/../p//text() | //div[@class='nhsuk-grid-column-two-thirds']//section//*[contains(text(), '"+section+"')]/../ul/li/text() | //div[@class='nhsuk-grid-column-two-thirds']//section//*[contains(text(), '"+section+"')]/../ul/li/a/text()"
        #print ('lower1:: '+xpathquery)
        sections = tree.xpath(xpathquery)
    if not sections:
        section=ps.stem(section)
        section = section.capitalize()
        xpathquery = "//div[@class='nhsuk-grid-column-two-thirds']//section//*[starts-with(text(), '"+section+"')]/../p//text() | //div[@class='nhsuk-grid-column-two-thirds']//section//*[starts-with(text(), '"+section+"')]/../ul/li/text() | //div[@class='nhsuk-grid-column-two-thirds']//section//*[contains(text(), '"+section+"')]/../ul/li/a/text()"
        #print (xpathquery)
        sections = tree.xpath(xpathquery)
    if not sections:
        section=ps.stem(section)
        section = section.lower()
        xpathquery = "//div[@class='nhsuk-grid-column-two-thirds']//section//*[starts-with(text(), '"+section+"')]/../p//text() | //div[@class='nhsuk-grid-column-two-thirds']//section//*[starts-with(text(), '"+section+"')]/../ul/li/text() | //div[@class='nhsuk-grid-column-two-thirds']//section//*[contains(text(), '"+section+"')]/../ul/li/a/text()"
        #print ('lower2:: '+xpathquery)
        sections = tree.xpath(xpathquery)
    if not sections:
        secondlink = reqlink+sectname.lower()+'/'
        #print (secondlink)
        secondpage = requests.get(secondlink)
        secondtree = html.fromstring(secondpage.content)
        xpathquery = "//div[@class='nhsuk-grid-column-two-thirds']/section/h2/text() | //div[@class='nhsuk-grid-column-two-thirds']/section/ul/li//text() | //div[@class='nhsuk-grid-column-two-thirds']//section//*[contains(text(), '"+section+"')]/../ul/li/a/text()"
        sections = secondtree.xpath(xpathquery)
    return ' '.join(sections)


# In[48]:


#t = NHS_pasering('pneumonia',"symptoms")


# In[50]:


#print(t)


# In[30]:


print('NHSsearchAPI is loaded!')


# In[ ]:





# In[ ]:




