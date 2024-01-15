import numpy as np
# const
BASEURL_INFO = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi'
BASEURL_SRCH = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
BASEURL_FTCH = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'

# parameters
SOURCE_DB    = 'pubmed'
TERM         = 'parkinson prediction'
DATE_TYPE    = 'pdat'       # Type of date used to limit a search. The allowed values vary between Entrez databases, but common values are 'mdat' (modification date), 'pdat' (publication date) and 'edat' (Entrez date). Generally an Entrez database will have only two allowed values for datetype.
MIN_DATE     = '2018/01/01' # yyyy/mm/dd
MAX_DATE     = '2019/12/31' # yyyy/mm/dd
SEP          = '|'
BATCH_NUM    = 1000

# seed
RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)