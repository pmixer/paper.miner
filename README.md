# PaperMiner

## Overview
PaperMiner is a novel computer science literature search platform for college students. It combines literature search, academic data presentation, interactive visualization, and open-source API for your research.

## Data
In this project, sources of research paper includes:  
[ACL Home Association for Computational Linguistics(ACL)](https://www.aclweb.org/portal/)   
[Computer Vision Foundation(CVF)](http://openaccess.thecvf.com/menu.py)   
[Journal of Machine Learning Research(JMLR)](http://www.jmlr.org)  
[Neural Information Processing Systems Conference(NIPS)](https://papers.nips.cc)  

## Environment

#### Backend
[arrow](https://arrow.readthedocs.io/en/latest/#installation)(Release v0.15.5)  
[beautifulsoup4](https://pypi.org/project/beautifulsoup4/)(Version 4.9.0)  
[bibtexparser](https://bibtexparser.readthedocs.io/en/master/)(Version 1.0.1)  
[pysocks](https://pypi.org/project/PySocks/)(Version 1.7.1)  
[requests](https://requests.readthedocs.io/en/master/)(Release v2.23.0)  
[nltk](https://www.nltk.org)(Version 3.5)  
[six](https://pypi.org/project/six/)(Version 1.14.0)  
[Flask](https://github.com/pallets/flask)(Version 1.1.2)  
[pandas](https://pandas.pydata.org)(Version 1.0.3)

etc. pls check `requirements.txt` for details and refer to [this page](https://github.com/RaRe-Technologies/gensim/issues/1375) if met `gensim` related issues.

Pls download the word2vec model and other required files from our [dropbox folder](https://www.dropbox.com/sh/v605veaawb4ngey/AABRGVeoLXk41xP009oeVqzPa?dl=0), put all files inside `abstract_search` folder on dropbox into local `backend` folder for abstract based paper/researcher/conference recommendation.

#### Frontend

We used `Node.js` for web development, mainly for frontend part of the project, pls have `Node.js` installed then `npm install gulp`, finally `cd frontend` and `gulp node`, the website would be avaiable on `http://localhost:3000`.

## Usage

Pls install the dependencies first(sorry for the workload), then start the backend/frontend service according to instructions in READMEs. Then test APIs by sending GET requests to port 5000 and enjoy our search/trends/explore services by visiting the website `http://localhost:3000` using your browser with internet access.