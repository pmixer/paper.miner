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

base_url  = "http://openaccess.thecvf.com/" # as most url got are relative path
r = requests.get(base_url + "menu.py")
soup = BeautifulSoup(r.content, "lxml")

# only scribe main conference content, ignore workshops
mc_links = [l["href"] for l in soup.find_all('a') if l.text == "Main Conference"]

blacklist = [
    # "Can_I_teach_a_robot_to_replicate_a_line_art"
]

papers = list()
author_set = set()
paper_authors = list()

for cl in mc_links:
    cid = cl.split(".")[0] # conference id, i.e. CVPR2019 in CVPR2019.py
    index_url = base_url + cl
    index_html_path = os.path.join("working", "html", cid + ".html")
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

    paper_links = [link for link in soup.find_all('a') if "href" in str(link)
                    and link["href"][:8] == "content_"
                    and link["href"][-5:] == ".html"]
    print("%d Papers Found" % len(paper_links))

    temp_path = os.path.join("working", "txt")
    for link in paper_links: # save paper html page and pdf file
        paper_title = link.text.replace(" ", "_") # paper title as paper ID
        info_link = base_url + link["href"]
        pdf_link = info_link.replace(".html", ".pdf").replace("/html/", "/papers/")
        pdf_name = paper_title + ".pdf"
        pdf_path = os.path.join("working", "pdfs", cid, pdf_name)
        print(cid, " ", paper_title) #paper_title.encode('ascii', 'namereplace'))

        # save pdf
        pdf_link = pdf_link.replace("iccv_2017", "ICCV_2017")
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
        paper_info_html_path = os.path.join("working", "html", cid, paper_title+".html")
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

        authors = paper_soup.findChild('div', attrs={"id": "authors"}).findChild("i").text.split(",")
        authors = [a.strip() for a in authors]
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
        papers.append([paper_title, cid[:4], cid[4:], "|".join(authors), info_link, abstract, paper_text])

print(blacklist)

cvf_papers_data = pd.DataFrame(papers, columns=["title", "venue", "year", "authors", "url", "abstract", "paper_text"])
cvf_papers_data.to_csv("output/cvf.csv", index=False)
cvf_papers_data_without_paper_text = cvf_papers_data.drop(columns=["paper_text"])
cvf_papers_data_without_paper_text.to_csv("output/cvf_without_paper_text.csv", index=False)