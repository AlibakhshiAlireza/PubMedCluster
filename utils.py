import math
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import pandas as pd
import requests
import urllib.parse
import uuid
import xml.etree.ElementTree as ET
from collections import OrderedDict
from sklearn.cluster import MiniBatchKMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from tqdm import tqdm_notebook as tqdm
from params import *
'''
make query function

base_url: base_url
params: parameter dictionary
        ex) {key1: value1, key2: value2}
'''
def mkquery(base_url, params):
    base_url += '?'
    for key, value in zip(params.keys(), params.values()):
        base_url += '{key}={value}&'.format(key=key, value=value)
    url = base_url[0:len(base_url) - 1]
    print('request url is: ' + url)
    return url

'''
getXmlFromURL
(mkquery wrapper)

base_url: base_url
params: parameter dictionary
        ex) {key1: value1, key2: value2}
'''
def getXmlFromURL(base_url, params):
    response = requests.get(mkquery(base_url, params))
    return ET.fromstring(response.text)

'''
getTextFromNode

root: Xml root node
path: XPath
fill: fill na string
mode: 0 = text, 1 = attribute
attrib: attribute name
'''
def getTextFromNode(root, path, fill='', mode=0, attrib='attribute'):
    if (root.find(path) == None):
        return fill
    else:
        if mode == 0:
            return root.find(path).text
        if mode == 1:
            return root.find(path).get(attrib)


articleDics = []
authorArticleDics = []
authorAffiliationDics = []

def pushData(rootXml):
    for article in rootXml.iter('PubmedArticle'):
        # get article info
        articleDic = {
            'PMID'                    : getTextFromNode(article, 'MedlineCitation/PMID', ''),
            'JournalTitle'            : getTextFromNode(article, 'MedlineCitation/Article/Journal/Title', ''),
            'Title'                   : getTextFromNode(article, 'MedlineCitation/Article/ArticleTitle', ''),
            'doi'                     : getTextFromNode(article, 'MedlineCitation/Article/ELocationID[@EIdType="doi"]', ''),
            'Abstract'                : getTextFromNode(article, 'MedlineCitation/Article/Abstract/AbstractText', ''),
        #    if you want to get data in flat(denormalized), uncomment below. but it's difficult to use for analytics.
        #    'Authors'                 : SEP.join([author.find('ForeName').text + ' ' +  author.find('LastName').text if author.find('CollectiveName') == None else author.find('CollectiveName').text for author in article.findall('MedlineCitation/Article/AuthorList/')]),
        #    'AuthorIdentifiers'       : SEP.join([getTextFromNode(author, 'Identifier', 'None') for author in article.findall('MedlineCitation/Article/AuthorList/')]),
        #    'AuthorIdentifierSources' : SEP.join([getTextFromNode(author, 'Identifier', 'None', 1, 'Source') for author in article.findall('MedlineCitation/Article/AuthorList/')]),
            'Language'                : getTextFromNode(article, 'MedlineCitation/Article/Language', ''),
            'Year_A'                  : getTextFromNode(article, 'MedlineCitation/Article/ArticleDate/Year', ''),
            'Month_A'                 : getTextFromNode(article, 'MedlineCitation/Article/ArticleDate/Month', ''),
            'Day_A'                   : getTextFromNode(article, 'MedlineCitation/Article/ArticleDate/Day', ''),
            'Year_PM'                 : getTextFromNode(article, 'PubmedData/History/PubMedPubDate[@PubStatus="pubmed"]/Year', ''),
            'Month_PM'                : getTextFromNode(article, 'PubmedData/History/PubMedPubDate[@PubStatus="pubmed"]/Month', ''),
            'Day_PM'                  : getTextFromNode(article, 'PubmedData/History/PubMedPubDate[@PubStatus="pubmed"]/Day', ''),
            'Status'                  : getTextFromNode(article, './PubmedData/PublicationStatus', ''),
            'MeSH'                    : SEP.join([getTextFromNode(mesh, 'DescriptorName') for mesh in article.findall('MedlineCitation/MeshHeadingList/')]),
            'MeSH_UI'                 : SEP.join([getTextFromNode(mesh, 'DescriptorName', '', 1, 'UI') for mesh in article.findall('MedlineCitation/MeshHeadingList/')]),
            'Keyword'                 : SEP.join([keyword.text if keyword.text != None else ''  for keyword in article.findall('MedlineCitation/KeywordList/')])
        }
        articleDics.append(OrderedDict(articleDic))

        if article.find('MedlineCitation/MeshHeadingList/MeshHeading/') != None:
            tmp = article

        # get author info
        for author in article.findall('MedlineCitation/Article/AuthorList/'):

            # publish author ID
            # * It's only random id. not use for identify author. if you want to identify author, you can use identifier.
            authorId = str(uuid.uuid4())

            # author article
            authorArticleDic = {
                'authorId'         : authorId,
                'PMID'             : getTextFromNode(article, 'MedlineCitation/PMID', ''),
                'name'             : getTextFromNode(author, 'ForeName') + ' ' +  getTextFromNode(author,'LastName') if author.find('CollectiveName') == None else author.find('CollectiveName').text,
                'identifier'       : getTextFromNode(author, 'Identifier', '') ,
                'identifierSource' : getTextFromNode(author, 'Identifier', '', 1, 'Source')
            }
            authorArticleDics.append(OrderedDict(authorArticleDic))

            # author affiliation(author: affiliation = 1 : n)
            if author.find('./AffiliationInfo') != None:
                for affiliation in author.findall('./AffiliationInfo'):
                    authorAffiliationDic = {
                        'authorId'          : authorId,
                        'affiliation'       : getTextFromNode(affiliation, 'Affiliation', '') ,
                    }
                    authorAffiliationDics.append(OrderedDict(authorAffiliationDic))
