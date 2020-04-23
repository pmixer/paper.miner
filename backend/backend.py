# customized based on https://github.com/chiphuyen/sotawhat and https://github.com/OrganicIrradiation/scholarly

import os
import re
import sys
import warnings
import urllib.error
import urllib.request

import nltk
from nltk.tokenize import word_tokenize
from six.moves.html_parser import HTMLParser

import pandas as pd
from gensim.models.doc2vec import Doc2Vec


from flask import Flask
from flask import jsonify
from flask import request

from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper

import json

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

def crossdomain(origin=None, methods=None, headers=None, max_age=21600,
                attach_to_all=True, automatic_options=True):
    """Decorator function that allows crossdomain requests.
      Courtesy of
      https://blog.skyred.fi/articles/better-crossdomain-snippet-for-flask.html
    """
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    # use str instead of basestring if using Python 3.x
    if headers is not None and not isinstance(headers, str):
        headers = ', '.join(x.upper() for x in headers)
    # use str instead of basestring if using Python 3.x
    if not isinstance(origin, str):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        """ Determines which methods are allowed
        """
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        """The decorator function
        """
        def wrapped_function(*args, **kwargs):
            """Caries out the actual cross domain code
            """
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers
            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            h['Access-Control-Allow-Credentials'] = 'true'
            h['Access-Control-Allow-Headers'] = \
                "Origin, X-Requested-With, Content-Type, Accept, Authorization"
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

app = Flask(__name__)

# modified based on sotawhat

h = HTMLParser()

AUTHOR_TAG = '<a href="/search/?searchtype=author'
TITLE_TAG = '<p class="title is-5 mathjax">'
ABSTRACT_TAG = '<span class="abstract-full has-text-grey-dark mathjax"'
DATE_TAG = '<p class="is-size-7"><span class="has-text-black-bis has-text-weight-semibold">Submitted</span>'


def get_authors(lines, i):
    authors = []
    while True:
        if not lines[i].startswith(AUTHOR_TAG):
            break
        idx = lines[i].find('>')
        if lines[i].endswith(','):
            authors.append(lines[i][idx + 1: -5])
        else:
            authors.append(lines[i][idx + 1: -4])
        i += 1
    return authors, i


def get_next_result(lines, start):
    """
    Extract paper from the xml file obtained from arxiv search.
    Each paper is a dict that contains:
    + 'title': str
    + 'page': str
    + 'date': str
    + 'authors': []
    + 'abstract': str
    """

    result = {}
    l = lines[start + 2]
    l = l[l.find("<a"):]
    result['url'] = l[l.find('https'): l.find('">')]

    start += 4

    while lines[start].strip() != TITLE_TAG:
        start += 1

    title = lines[start + 1].strip()
    title = title.replace('<span class="search-hit mathjax">', '')
    title = title.replace('</span>', '')
    result['title'] = title

    authors, start = get_authors(lines, start + 5)  # orig: add 8

    while not lines[start].strip().startswith(ABSTRACT_TAG):
        start += 1
    abstract = lines[start + 1]
    abstract = abstract.replace('<span class="search-hit mathjax">', '')
    abstract = abstract.replace('</span>', '')
    result['abstract'] = abstract

    result['authors'] = authors

    while not lines[start].strip().startswith(DATE_TAG):
        start += 1

    idx = lines[start].find('</span> ')
    end = lines[start][idx:].find(';')

    result['date'] = lines[start][idx + 8: idx + end]

    return result, start


def clean_empty_lines(lines):
    cleaned = []
    for line in lines:
        line = line.strip()
        if line:
            cleaned.append(line)
    return cleaned


def is_float(token):
    return re.match("^\d+?\.\d+?$", token) is not None


def is_citation_year(tokens, i):
    if len(tokens[i]) != 4:
        return False
    if re.match(r'[12][0-9]{3}', tokens[i]) is None:
        return False
    if i == 0 or i == len(tokens) - 1:
        return False
    if (tokens[i - 1] == ',' or tokens[i - 1] == '(') and tokens[i + 1] == ')':
        return True
    return False


def is_list_numer(tokens, i, value):
    if value < 1 or value > 4:
        return False
    if i == len(tokens) - 1:
        return False

    if (i == 0 or tokens[i - 1] in set(['(', '.', ':'])) and tokens[i + 1] == ')':
        return True
    return False


def has_number(sent):
    tokens = word_tokenize(sent)
    for i, token in enumerate(tokens):
        if token.endswith('\\'):
            token = token[:-2]
        if token.endswith('x'):  # sometimes people write numbers as 1.7x
            token = token[:-1]
        if token.startswith('x'):  # sometimes people write numbers as x1.7
            token = token[1:]
        if token.startswith('$') and token.endswith('$'):
            token = token[1:-1]
        if is_float(token):
            return True
        try:
            value = int(token)
        except:
            continue
        if (not is_citation_year(tokens, i)) and (not is_list_numer(tokens, i, value)):
            return True

    return False


def contains_sota(sent):
    return 'state-of-the-art' in sent or 'state of the art' in sent or 'SOTA' in sent


def extract_line(abstract, keyword, limit):
    lines = []
    numbered_lines = []
    kw_mentioned = False
    abstract = abstract.replace("et. al", "et al.")
    sentences = abstract.split('. ')
    kw_sentences = []
    for i, sent in enumerate(sentences):
        if keyword in sent.lower():
            kw_mentioned = True
            if has_number(sent):
                numbered_lines.append(sent)
            elif contains_sota(sent):
                numbered_lines.append(sent)
            else:
                kw_sentences.append(sent)
                lines.append(sent)
            continue

        if kw_mentioned and has_number(sent):
            if not numbered_lines:
                numbered_lines.append(kw_sentences[-1])
            numbered_lines.append(sent)
        if kw_mentioned and contains_sota(sent):
            lines.append(sent)

    if len(numbered_lines) > 0:
        return '. '.join(numbered_lines), True
    return '. '.join(lines[-2:]), False


def get_paper_data(txt, keyword, num_to_show):
    found = False
    txt = ''.join(chr(c) for c in txt)
    lines = txt.split('\n')
    lines = clean_empty_lines(lines)
    res = []

    for i in range(len(lines)):
        if num_to_show <= 0:
            return unshown, num_to_show, found

        line = lines[i].strip()
        if len(line) == 0:
            continue
        if line == '<li class="arxiv-result">':
            found = True
            paper, i = get_next_result(lines, i)
            res.append(paper)

        if line == '</ol>':
            break
    return res

@app.route('/get_papers', methods=['GET'])
@crossdomain(origin='*')
def get_papers():
    keyword = request.args.get('keyword').lower()
    num_to_show = int(request.args.get('num_to_show'))

    query_temp = 'https://arxiv.org/search/advanced?advanced=&terms-0-operator=AND&terms-0-term={}&terms-0-field=all&classification-computer_science=y&classification-physics_archives=all&date-filter_by=all_dates&date-year=&date-from_date=&date-to_date=&date-date_type=submitted_date&abstracts=show&size={}&order=-announced_date_first&start={}'
    query = query_temp.format(keyword, '100', '0') # query, per_page and starting idx

    req = urllib.request.Request(query)
    try:
        response = urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        print('Error {}: problem accessing the server'.format(e.code))
        return

    txt = response.read()
    paper_data = get_paper_data(txt, keyword, num_to_show)
    return jsonify(paper_data)

# modified based on scholarly
from bs4 import BeautifulSoup

import arrow
import bibtexparser
import codecs
import hashlib
import pprint
import random
import re
import requests
import sys
import time

_GOOGLEID = hashlib.md5(str(random.random()).encode('utf-8')).hexdigest()[:16]
_COOKIES = {'GSP': 'ID={0}:CF=4'.format(_GOOGLEID)}
_HEADERS = {
    'accept-language': 'en-US,en',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/41.0.2272.76 Chrome/41.0.2272.76 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml'
    }
_HOST = 'https://scholar.google.com'
_AUTHSEARCH = '/citations?view_op=search_authors&hl=en&mauthors={0}'
_CITATIONAUTH = '/citations?user={0}&hl=en'
_CITATIONPUB = '/citations?view_op=view_citation&citation_for_view={0}'
_KEYWORDSEARCH = '/citations?view_op=search_authors&hl=en&mauthors=label:{0}'
_PUBSEARCH = '/scholar?q={0}'
_SCHOLARPUB = '/scholar?oi=bibs&hl=en&cites={0}'

_CITATIONAUTHRE = r'user=([\w-]*)'
_CITATIONPUBRE = r'citation_for_view=([\w-]*:[\w-]*)'
_SCHOLARCITERE = r'gs_ocit\(event,\'([\w-]*)\''
_SCHOLARPUBRE = r'cites=([\w-]*)'
_EMAILAUTHORRE = r'Verified email at '

_SESSION = requests.Session()
_PAGESIZE = 100


def use_proxy(http='socks5://127.0.0.1:9050', https='socks5://127.0.0.1:9050'):
    """ Routes scholarly through a proxy (e.g. tor).
        Requires pysocks
        Proxy must be running."""
    _SESSION.proxies ={
            'http': http,
            'https': https
    }


def _handle_captcha(url):
    # TODO: PROBLEMS HERE! NEEDS ATTENTION
    # Get the captcha image
    captcha_url = _HOST + '/sorry/image?id={0}'.format(g_id)
    captcha = _SESSION.get(captcha_url, headers=_HEADERS)
    # Upload to remote host and display to user for human verification
    img_upload = requests.post('http://postimage.org/',
        files={'upload[]': ('scholarly_captcha.jpg', captcha.text)})
    print(img_upload.text)
    img_url_soup = BeautifulSoup(img_upload.text, 'html.parser')
    img_url = img_url_soup.find_all(alt='scholarly_captcha')[0].get('src')
    print('CAPTCHA image URL: {0}'.format(img_url))
    # Need to check Python version for input
    if sys.version[0]=="3":
        g_response = input('Enter CAPTCHA: ')
    else:
        g_response = raw_input('Enter CAPTCHA: ')
    # Once we get a response, follow through and load the new page.
    url_response = _HOST+'/sorry/CaptchaRedirect?continue={0}&id={1}&captcha={2}&submit=Submit'.format(dest_url, g_id, g_response)
    resp_captcha = _SESSION.get(url_response, headers=_HEADERS, cookies=_COOKIES)
    print('Forwarded to {0}'.format(resp_captcha.url))
    return resp_captcha.url


def _get_page(pagerequest):
    """Return the data for a page on scholar.google.com"""
    # Note that we include a sleep to avoid overloading the scholar server
    time.sleep(5+random.uniform(0, 5))
    resp = _SESSION.get(pagerequest, headers=_HEADERS, cookies=_COOKIES)
    if resp.status_code == 200:
        return resp.text
    if resp.status_code == 503:
        # Inelegant way of dealing with the G captcha
        raise Exception('Error: {0} {1}'.format(resp.status_code, resp.reason))
        # TODO: Need to fix captcha handling
        # dest_url = requests.utils.quote(_SCHOLARHOST+pagerequest)
        # soup = BeautifulSoup(resp.text, 'html.parser')
        # captcha_url = soup.find('img').get('src')
        # resp = _handle_captcha(captcha_url)
        # return _get_page(re.findall(r'https:\/\/(?:.*?)(\/.*)', resp)[0])
    else:
        raise Exception('Error: {0} {1}'.format(resp.status_code, resp.reason))


def _get_soup(pagerequest):
    """Return the BeautifulSoup for a page on scholar.google.com"""
    html = _get_page(pagerequest)
    html = html.replace(u'\xa0', u' ')
    return BeautifulSoup(html, 'html.parser')


def _search_scholar_soup(soup):
    """Generator that returns Publication objects from the search page"""
    while True:
        for row in soup.find_all('div', 'gs_or'):
            yield Publication(row, 'scholar')
        if soup.find(class_='gs_ico gs_ico_nav_next'):
            url = soup.find(class_='gs_ico gs_ico_nav_next').parent['href']
            soup = _get_soup(_HOST+url)
        else:
            break


def _search_citation_soup(soup):
    """Generator that returns Author objects from the author search page"""
    while True:
        for row in soup.find_all('div', 'gsc_1usr'):
            yield Author(row)
        next_button = soup.find(class_='gs_btnPR gs_in_ib gs_btn_half gs_btn_lsb gs_btn_srt gsc_pgn_pnx')
        if next_button and 'disabled' not in next_button.attrs:
            url = next_button['onclick'][17:-1]
            url = codecs.getdecoder("unicode_escape")(url)[0]
            soup = _get_soup(_HOST+url)
        else:
            break

def _find_tag_class_name(__data, tag, text):
    elements = __data.find_all(tag)
    for element in elements:
        if 'class' in element.attrs and text in element.attrs['class'][0]:
            return element.attrs['class'][0]


class Publication(object):
    """Returns an object for a single publication"""
    def __init__(self, __data, pubtype=None):
        self.bib = dict()
        self.source = pubtype
        if self.source == 'citations':
            self.bib['title'] = __data.find('a', class_='gsc_a_at').text
            self.id_citations = re.findall(_CITATIONPUBRE, __data.find('a', class_='gsc_a_at')['data-href'])[0]
            citedby = __data.find(class_='gsc_a_ac')
            if citedby and not (citedby.text.isspace() or citedby.text == ''):
                self.citedby = int(citedby.text)
            year = __data.find(class_='gsc_a_h')
            if year and year.text and not year.text.isspace() and len(year.text)>0:
                self.bib['year'] = int(year.text)
        elif self.source == 'scholar':
            databox = __data.find('div', class_='gs_ri')
            title = databox.find('h3', class_='gs_rt')
            if title.find('span', class_='gs_ctu'): # A citation
                title.span.extract()
            elif title.find('span', class_='gs_ctc'): # A book or PDF
                title.span.extract()
            self.bib['title'] = title.text.strip()
            if title.find('a'):
                self.bib['url'] = title.find('a')['href']
            authorinfo = databox.find('div', class_='gs_a')
            self.bib['author'] = ' and '.join([i.strip() for i in authorinfo.text.split(' - ')[0].split(',')])
            if databox.find('div', class_='gs_rs'):
                self.bib['abstract'] = databox.find('div', class_='gs_rs').text
                if self.bib['abstract'][0:8].lower() == 'abstract':
                    self.bib['abstract'] = self.bib['abstract'][9:].strip()
            lowerlinks = databox.find('div', class_='gs_fl').find_all('a')
            for link in lowerlinks:
                if 'Import into BibTeX' in link.text:
                    self.url_scholarbib = link['href']
                if 'Cited by' in link.text:
                    self.citedby = int(re.findall(r'\d+', link.text)[0])
                    self.id_scholarcitedby = re.findall(_SCHOLARPUBRE, link['href'])[0]
            if __data.find('div', class_='gs_ggs gs_fl'):
                self.bib['eprint'] = __data.find('div', class_='gs_ggs gs_fl').a['href']
        self._filled = False

    def fill(self):
        """Populate the Publication with information from its profile"""
        if self.source == 'citations':
            url = _CITATIONPUB.format(self.id_citations)
            soup = _get_soup(_HOST+url)
            self.bib['title'] = soup.find('div', id='gsc_vcd_title').text
            if soup.find('a', class_='gsc_vcd_title_link'):
                self.bib['url'] = soup.find('a', class_='gsc_vcd_title_link')['href']
            for item in soup.find_all('div', class_='gs_scl'):
                key = item.find(class_='gsc_vcd_field').text
                val = item.find(class_='gsc_vcd_value')
                if key == 'Authors':
                    self.bib['author'] = ' and '.join([i.strip() for i in val.text.split(',')])
                elif key == 'Journal':
                    self.bib['journal'] = val.text
                elif key == 'Volume':
                    self.bib['volume'] = val.text
                elif key == 'Issue':
                    self.bib['number'] = val.text
                elif key == 'Pages':
                    self.bib['pages'] = val.text
                elif key == 'Publisher':
                    self.bib['publisher'] = val.text
                elif key == 'Publication date':
                    self.bib['year'] = arrow.get(val.text).year
                elif key == 'Description':
                    if val.text[0:8].lower() == 'abstract':
                        val = val.text[9:].strip()
                    self.bib['abstract'] = val
                elif key == 'Total citations':
                    self.id_scholarcitedby = re.findall(_SCHOLARPUBRE, val.a['href'])[0]

            # number of citation per year
            years = [int(y.text) for y in soup.find_all(class_='gsc_vcd_g_t')]
            cites = [int(c.text) for c in soup.find_all(class_='gsc_vcd_g_al')]
            self.cites_per_year = dict(zip(years, cites))

            if soup.find('div', class_='gsc_vcd_title_ggi'):
                self.bib['eprint'] = soup.find('div', class_='gsc_vcd_title_ggi').a['href']
            self._filled = True
        elif self.source == 'scholar':
            bibtex = _get_page(self.url_scholarbib)
            self.bib.update(bibtexparser.loads(bibtex).entries[0])
            self._filled = True
        return self

    def get_citedby(self):
        """Searches GScholar for other articles that cite this Publication and
        returns a Publication generator.
        """
        if not hasattr(self, 'id_scholarcitedby'):
            self.fill()
        if hasattr(self, 'id_scholarcitedby'):
            url = _SCHOLARPUB.format(requests.utils.quote(self.id_scholarcitedby))
            soup = _get_soup(_HOST+url)
            return _search_scholar_soup(soup)
        else:
            return []

    def __str__(self):
        return pprint.pformat(self.__dict__)


class Author(object):
    """Returns an object for a single author"""
    def __init__(self, __data):
        if isinstance(__data, str):
            self.id = __data
        else:
            self.id = re.findall(_CITATIONAUTHRE, __data('a')[0]['href'])[0]
            self.url_picture = _HOST+'/citations?view_op=medium_photo&user={}'.format(self.id)
            self.name = __data.find('h3', class_=_find_tag_class_name(__data, 'h3', 'name')).text
            affiliation = __data.find('div', class_=_find_tag_class_name(__data, 'div', 'aff'))
            if affiliation:
                self.affiliation = affiliation.text
            email = __data.find('div', class_=_find_tag_class_name(__data, 'div', 'eml'))
            if email:
                self.email = re.sub(_EMAILAUTHORRE, r'@', email.text)
            self.interests = [i.text.strip() for i in
                           __data.find_all('a', class_=_find_tag_class_name(__data, 'a', 'one_int'))]
            citedby = __data.find('div', class_=_find_tag_class_name(__data, 'div', 'cby'))
            if citedby and citedby.text != '':
                self.citedby = int(citedby.text[9:])
        self._filled = False

    def fill(self):
        """Populate the Author with information from their profile"""
        url_citations = _CITATIONAUTH.format(self.id)
        url = '{0}&pagesize={1}'.format(url_citations, _PAGESIZE)
        soup = _get_soup(_HOST+url)
        self.name = soup.find('div', id='gsc_prf_in').text
        self.affiliation = soup.find('div', class_='gsc_prf_il').text
        self.interests = [i.text.strip() for i in soup.find_all('a', class_='gsc_prf_inta')]
        
        # h-index, i10-index and h-index, i10-index in the last 5 years
        index = soup.find_all('td', class_='gsc_rsb_std')
        if index:
            self.citedby = int(index[0].text)
            self.citedby5y = int(index[1].text)
            self.hindex = int(index[2].text)
            self.hindex5y = int(index[3].text)
            self.i10index = int(index[4].text)
            self.i10index5y = int(index[5].text)
        else:
            self.hindex = self.hindex5y = self.i10index = self.i10index5y = 0

        # number of citations per year
        years = [int(y.text) for y in soup.find_all('span', class_='gsc_g_t')]
        cites = [int(c.text) for c in soup.find_all('span', class_='gsc_g_al')]
        self.cites_per_year = dict(zip(years, cites))

        # co-authors
        self.coauthors = []
        for row in soup.find_all('span', class_='gsc_rsb_a_desc'):
            new_coauthor = Author(re.findall(_CITATIONAUTHRE, row('a')[0]['href'])[0])
            new_coauthor.name = row.find(tabindex="-1").text
            new_coauthor.affiliation = row.find(class_="gsc_rsb_a_ext").text
            self.coauthors.append(new_coauthor)


        self.publications = list()
        pubstart = 0
        while True:
            for row in soup.find_all('tr', class_='gsc_a_tr'):
                new_pub = Publication(row, 'citations')
                self.publications.append(new_pub)
            if 'disabled' not in soup.find('button', id='gsc_bpf_more').attrs:
                pubstart += _PAGESIZE
                url = '{0}&cstart={1}&pagesize={2}'.format(url_citations, pubstart, _PAGESIZE)
                soup = _get_soup(_HOST+url)
            else:
                break

        self._filled = True
        return self

    def __str__(self):
        return pprint.pformat(self.__dict__)


# @app.route('/get_paper', methods=['GET'])
def search_pubs_query(query):
    """Search by scholar query and return a generator of Publication objects"""
    # query = requests.args.get('title').lower()
    url = _PUBSEARCH.format(requests.utils.quote(query))
    soup = _get_soup(_HOST+url)
    return _search_scholar_soup(soup)


@app.route('/get_author', methods=['GET'])
@crossdomain(origin='*')
def search_author():
    """Search by author name and return a generator of Author objects"""
    name = request.args.get('name').lower()
    url = _AUTHSEARCH.format(requests.utils.quote(name))
    soup = _get_soup(_HOST+url)
    # import pdb; pdb.set_trace()
    author = next(_search_citation_soup(soup))
    res = {}
    res['gscholar_url'] = 'https://scholar.google.com/citations?user=' + author.id
    res['gscholar_photo_url'] = author.url_picture
    res['name'] = author.name
    res['affiliation'] = author.affiliation
    return jsonify(res)


@app.route('/abstract_search',methods = ['GET'])
def search_abstract(path="", top =10):
    """Search the most similary abstract based on inpit query"""

    # path: path of training model
    # query: input scentence
    # top: # of return

    df = pd.read_csv('papers_with_abstract.csv', header="infer", sep=',', encoding='iso-8859-1')
    df.drop(df[df.isnull().any(axis=1)].index, inplace=True)

    # get the input query and num_to_show DEFULT:10
    query = request.args.get("query")
    top = int(request.args.get("num_to_show"))

    strl_tok = word_tokenize(query)

    # Load the Doc2Vec model
    model = Doc2Vec.load(path+"my_model")
    inferred_vector = model.infer_vector(doc_words=strl_tok, alpha=0.05, steps=500)
    sims = model.docvecs.most_similar([inferred_vector], topn=top)

    result = []
    for count, sim in sims:
        result.append(count)

    resultdf = df.loc[result,:]
    resultdict = resultdf.to_dict('records')
    return jsonify(resultdict)


def search_keyword(keyword):
    """Search by keyword and return a generator of Author objects"""
    url = _KEYWORDSEARCH.format(requests.utils.quote(keyword))
    soup = _get_soup(_HOST+url)
    return _search_citation_soup(soup)


def search_pubs_custom_url(url):
    """Search by custom URL and return a generator of Publication objects
    URL should be of the form '/scholar?q=...'"""
    soup = _get_soup(_HOST+url)
    return _search_scholar_soup(soup)


def search_author_custom_url(url):
    """Search by custom URL and return a generator of Publication objects
    URL should be of the form '/citation?q=...'"""
    soup = _get_soup(_HOST+url)
    return _search_citation_soup(soup)

if __name__ == '__main__':
    app.run()