# -*- coding: utf-8 -*-

import pandas as pd  
import glob          
import regex
import re            
import pickle        
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize

def clean_nationality(name):
    '''
    Function to clean the format of the names in Schrodt's file
    
    Input:
    name - text of country name/nationality
    
    Output:
    cleanname - cleaned text of name/nationality
    '''
    cleanname = re.sub(r'_$', '', name) # remove _$
    cleanname = re.sub(r'\t', '', cleanname) # remove tabs
    cleanname = re.sub(r'_', ' ', cleanname) # remove _
    return cleanname

def get_country_syns(country_dict):
    '''
    Function to extract country synonyms/nationalities in Schrodt's file
    
    Input:
    country_dict - Schrodt's country actor dictionary
    
    Output:
    dic - python dictionary of name keys and country value pairs
    '''
    country = [] # empty list for country names
    name = [] # empty list for country name synonyms and associated nationalities
    soup = BeautifulSoup(country_dict, 'lxml') # parse the file using BS
    countries = soup.findAll('country') # find all country tags
    for c in countries: # loop through countries
        cname = c.find('countryname').getText() # get text of countryname section
        country.append(clean_nationality(cname)) # append to country list
        name.append(clean_nationality(cname)) # append to name list
        try:
            nationalities = c.find('nationality').getText() # get nationality section
            nationalities = filter(None, nationalities.split('\n')) # get all values in this section
            for n in nationalities: # loop through values
                country.append(clean_nationality(cname)) # append country name to list
                name.append(clean_nationality(n)) # append alternative name or nationality to list
        except AttributeError:
            pass
            print 'No nationalities section for '+str(cname)
    dic = dict(zip(name, country)) # create dictionary of name keys and country value pairs
    return dic
            
def clean_fname(fname):
    '''
    Function to clean up the name of file for use with Schrodt dictionary
    
    Input:
    fname - string of filename
    
    Output:
    fname - cleaned uppercase country name string
    
    '''
    fname = re.sub(r'.txt', '', fname)
    fname = re.sub(r'\.\.', '', fname)
    fname = re.search(r'[A-Za-z\.\_\'\Õ\-]+', fname).group(0)
    fname = re.sub(r'_', ' ', fname)
    fname = fname.upper()
    return fname
    
def split_doc(doc):
    '''
    Function to split document and upper case for use with Schrodt dictionary
    
    Input:
    doc - text of trafficking report for country
    
    Output:
    doc - uppercase string of first paragraph of report
    '''
    split = doc.split('The Government of') # split at specified string
    doc = split[0] # get first string of split
    doc = doc.upper() # upper case the string
    return doc

def extract_entities(doc, dic, fname):
    '''
    Function to extract entities and metadata from documents.
    This function returns entities/metadata at the sentence level.
    This 
    
    Input:
    doc - text of trafficking report for country
    dic - dictionary of country names/nationalities
    fname - file name of document
    
    Output:
    found - list of sentence level dictionaries containing extracted entities and metadata
    '''
    found = [] # empty list for output
    foundents = [] # list for entities found in doc
    # Deal with South Sudan and Cote d'Ivoire entities using regex
    doc = re.sub(pattern='SOUTH SUDANESE', repl='SOUTH SUDANESEAN', string=doc)
    doc = re.sub(pattern="COTE(.+?)IVOIRE", repl="COTE D'IVOIRE", string=doc)
    cleandoc = doc # save 'cleaned' doc for later
    reg = r"\b" + re.escape(clean_fname(fname)) + r"\b" # regex for filename
    doc = re.sub(pattern=reg, repl='', string=doc) # delete this to prevent false positives
    for k in dic: # loop through keys in dic
        if dic[clean_fname(fname)] not in dic[k]: # if not country of report
            k = re.sub(pattern='\.', repl='\.', string=k)
            exp = r"\b" + re.escape(k) + r"\b"
            temp_search = re.findall(pattern=exp, string=doc) # find key/entity in text
            if len(temp_search) > 0: # if there are matches
                doc = re.sub(pattern=exp, repl='', string=doc) # remove this entity for future iterations
                foundents.append(temp_search[0]) # append to list of found entites
    if len(foundents) > 0: # if doc contains entities
        sents = sent_tokenize(unicode(cleandoc, 'utf-8')) # sentence segmentation
        p = regex.compile(r"\b\L<ents>\b", ents=foundents) # regex for finding entities in a given sentence
        for s in sents:
            # remove sentences to tourism but not trafficking
            if p.search(re.sub(pattern=reg, repl='', string=s)) and 'SEX TOURIS' not in s:
                outdic = {}
                sentcountries = []
                sentents = []
                for e in foundents: # search sentences for identified entities
                    exp = r"\b" + re.escape(e) + r"\b"
                    if re.search(pattern=exp, string=s):
                        sentents.append(e)
                        sentcountries.append(dic[e])
                outdic['file'] = fname
                outdic['country'] = dic[clean_fname(fname)]
                outdic['countries'] = ';'.join(list(set(sentcountries)))
                outdic['entities'] = ';'.join(sentents)
                outdic['text'] = s
                found.append(outdic)
            else:
                pass
    return found

########################################################
# Get info from Schrodt dictionaries
########################################################
schrodt = open('Gazetteer.txt', 'r').read()
cnames_dic = get_country_syns(schrodt)
cnames_dic['CUBAN'] = 'CUBA'

# Append missing countries to lists
for year in range(2001, 2016+1):
    files = glob.glob('../' + str(year) + '/*.txt')
    for fname in files:
        if cnames_dic.has_key(clean_fname(fname)):
            pass
        else:
            print fname
            print clean_fname(fname)
            cnames_dic[clean_fname(fname)] = str(clean_fname(fname))  


# Get entities from documents
out = []

for year in range(2001, 2016+1):
    files = glob.glob('../' + str(year) + '/*.txt')
    for fname in files:
        print "Working on "+str(fname)
        doc = open(fname, 'r').read()
        doc = split_doc(doc)
        out.extend(extract_entities(doc=doc, dic=cnames_dic, fname=fname))

out = filter(None, out)
df = pd.DataFrame(out)
df.to_csv('extracted_entities_dictionary_sents_final.csv', encoding='utf-8', index=False)
