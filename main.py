from utils import *
from params import *


rootXml = getXmlFromURL(BASEURL_SRCH, {
    'db': SOURCE_DB,
    'term': TERM,
    'usehistory': 'y',
    'datetype': DATE_TYPE,
    'mindate': MIN_DATE,
    'maxdate': MAX_DATE})
Count = rootXml.find('Count').text
QueryKey = rootXml.find('QueryKey').text
WebEnv = urllib.parse.quote(rootXml.find('WebEnv').text)

iterCount = math.ceil(int(Count) / BATCH_NUM)

# get all data
for i in tqdm(range(iterCount)):
    rootXml = getXmlFromURL(BASEURL_FTCH, {
        'db': SOURCE_DB,
        'query_key': QueryKey,
        'WebEnv': WebEnv,
        'retstart': i * BATCH_NUM,
        'retmax': BATCH_NUM,
        'retmode': 'xml'})

    pushData(rootXml)

df_article = pd.DataFrame(articleDics)
df_author = pd.DataFrame(authorArticleDics)
df_affiliation = pd.DataFrame(authorAffiliationDics)
df_article.to_csv('pubmed_article.csv')
df_author.to_csv('pubmed_author.csv')
df_affiliation.to_csv('pubmed_affiliation.csv')
