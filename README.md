# HealthChatbot
A Chatbot that can answer questions to health condition questions

Health Chatbot project is a research project to learning health condtion information from internet such as UK NHS and Wiki pages and transform it as chatbot knowledge. More advance, the chatbot will remember the knowledge through a causality knowledge graph neural network (CKNN). The CKNN then can reasoning the knowledge to answer questions and do predictions based on observation input. 
The couple important files:

A. HealthChatbotv33.py is the python class 
1. Taking questions and provide return anwsers function: qa_chat(question)
2. Generating CKNN triples function: 
semantic_generation(answers,condition_topic, query_section)
3. Testing function to take a condition topic and then automatically answer 6 related questions about the topic with CKNN generating: evaluation_pipe(condition_topic)
4. Global CKNN insert function: global_cknn(condition_topic)

B. Web crawling py APIs:
1. NHSsearchv5.py
2. Wikisearchv8.py
3. QuestionSAv6.py

C. Simple Chatbot interface ipynb file (Jupyter notebook file)
RobGUI.ipynb Run through the cells and the last cell is the the Chatbot interface.

D. The data and evaluation files
The data files all in the 'cknn' folder with our tested 15 condtions and 6 questions for each of them. The glo_cknn is the global cknn repository linked all the triples together in one CKNN graph. The testing results are in a form that you can find in another file called evaluation form.docx

E. Core requirements for running the code:
NLTK API
LXML API
URILIB API
REQUESTS API
SPACY API
WIKI API
RDFLIB API
PANDAS API
OS API
Tkiner API
SPOTLIGHT API
JSON API
