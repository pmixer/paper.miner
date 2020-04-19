from bs4 import BeautifulSoup
import json
import os
import pandas as pd
import re
import requests
import subprocess

def text_from_pdf(pdf_path):
    txt_path = pdf_path.replace("pdfs", "txts").replace(".pdf", ".txt")
    if not os.path.exists(os.path.dirname(txt_path)):
        os.makedirs(os.path.dirname(txt_path))
    if not os.path.exists(txt_path):
        subprocess.call(["pdftotext", pdf_path, txt_path])
    f = open(txt_path, encoding="utf8")
    text = f.read()
    f.close()
    return text

base_url = "http://proceedings.mlr.press/"
r = requests.get(base_url + "index.html")
soup = BeautifulSoup(r.content, "lxml")

# second is the set of accessible proceeding
ready_proceedings = soup.find_all('ul', attrs={"class": "proceedings-list"})[1].find_all('li')

blacklist = [
    # "Can_I_teach_a_robot_to_replicate_a_line_art"
]

papers = list()
author_set = set()
paper_authors = list()
needed = set(["AISTATS", "ICML", "ACML", "COLT"])

for li in ready_proceedings:
    venue_keywords = set(li.contents[2].strip().split())
    venue = venue_keywords & needed
    if (len(venue) > 0 and "Workshop" not in venue_keywords):
        cid = list(venue)[0]
        for kw in venue_keywords:
            if kw.isnumeric():
                year = int(kw)
        index_url = base_url + li.findChild("a")["href"]
    else:
        continue

    index_html_path = os.path.join("working", "html", cid+str(year) + ".html")
    # save main conference pages as index for retriving papers
    if not os.path.exists(index_html_path):
        r = requests.get(index_url)
        if not os.path.exists(os.path.dirname(index_html_path)):
            os.makedirs(os.path.dirname(index_html_path))
        with open(index_html_path, "wb") as index_html_file:
            index_html_file.write(r.content)
    # then read from saved conference page cache
    with open(index_html_path, "rb") as f:
       html_content = f.read()
    soup = BeautifulSoup(html_content, "lxml")
    paper_divs = soup.find_all("div", attrs={"class":"paper"})
    temp_path = os.path.join("working", "txt")

    for div in paper_divs: # save paper html page and pdf file
        paper_title = div.findChild("p", attrs={"class", "title"}).text.replace(" ", "_")
        if "Preface" in  paper_title: continue
        info_link = div.find_all("a")[0]["href"]
        pdf_link = div.find_all("a")[1]["href"]
        pdf_name = paper_title + ".pdf"
        pdf_path = os.path.join("working", "pdfs", cid+str(year), pdf_name)
        print(cid, " ", str(year), " ", paper_title) #paper_title.encode('ascii', 'namereplace'))

        # save pdf
        if not os.path.exists(pdf_path):
            pdf = requests.get(pdf_link)
            if pdf.status_code != 200: # always meet broken links... somewhere
                blacklist.append([cid, paper_title])
                continue
            if not os.path.exists(os.path.dirname(pdf_path)):
                os.makedirs(os.path.dirname(pdf_path))
            pdf_file = open(pdf_path, "wb")
            pdf_file.write(pdf.content)
            pdf_file.close()

        # save html
        paper_info_html_path = os.path.join("working", "html", cid+str(year), paper_title+".html")
        if not os.path.exists(paper_info_html_path):
            r = requests.get(info_link)
            if not os.path.exists(os.path.dirname(paper_info_html_path)):
                os.makedirs(os.path.dirname(paper_info_html_path))
            with open(paper_info_html_path, "wb") as f:
                f.write(r.content)
        with open(paper_info_html_path, "rb") as f:
           html_content = f.read()
        
        # load saved paper html page
        paper_soup = BeautifulSoup(html_content, "lxml")
        try: 
            abstract = paper_soup.findChild('div', attrs={"id": "abstract"}).text
        except:
            print("Abstract not found %s" % paper_title.encode("ascii", "replace"))
            abstract = ""
            blacklist.append([cid, paper_title])
            continue
        authors = paper_soup.findChild('div', attrs={"id": "authors"}).text.strip(" \n;").split(",")
        authors = [a.strip(" \n") for a in authors]
        for author in authors:
            author_set.add(author)
            paper_authors.append([len(paper_authors)+1, paper_title, author])

        with open(pdf_path, "rb") as f:
            if f.read(15)==b"<!DOCTYPE html>":
                print(paper_title + "PDF MISSING")
                blacklist.append([cid, paper_title])
                continue
       
        # pdf2txt for extracting content from downloaded pdf files
        paper_text = text_from_pdf(pdf_path)
        papers.append([paper_title, cid, year, "|".join(authors), info_link, abstract, paper_text])

print(blacklist)

jmlr_papers_data = pd.DataFrame(papers, columns=["title", "venue", "year", "authors", "url", "abstract", "paper_text"])
jmlr_papers_data.to_csv("output/jmlr.csv", index=False)
jmlr_papers_data_without_paper_text = jmlr_papers_data.drop(columns=["paper_text"])
jmlr_papers_data_without_paper_text.to_csv("output/jmlr_without_paper_text.csv", index=False)