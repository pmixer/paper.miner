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

base_url = "https://www.aclweb.org/anthology/"
r = requests.get(base_url + "index.html")
soup = BeautifulSoup(r.content, "lxml")

# second is the set of accessible proceeding
selected_proceedings = (
    ['ACL', 2017, 'P17', [[1001, 1195], [2001, 2107]]],
    ['ACL', 2018, 'P18', [[1001, 1256], [2001, 2125]]],
    ['ACL', 2019, 'P19', [[1001, 1660]]],
    ['EMNLP', 2017, 'D17', [[1001, 1323]]],
    ['EMNLP', 2018, 'D18', [[1001, 1549]]],
    ['EMNLP', 2019, 'D19', [[1001, 1682]]]
)

blacklist = [
    # "Can_I_teach_a_robot_to_replicate_a_line_art"
]

papers = list()

for cid, year, header, ranges in selected_proceedings:
    pids = []
    for r in ranges:
        pids += list(range(r[0], r[1] + 1))
    
    for pid in pids:
        if cid == 'EMNLP' and year == 2019 and pid == 1479:
            continue # wried stuff, another missing paper
        info_link = base_url + header + "-" + str(pid)
        # save paper info page
        paper_info_html_path = os.path.join("working", "html", cid+str(year), header+"-"+str(pid)+".html")
        if not os.path.exists(paper_info_html_path):
            r = requests.get(info_link)
            if not os.path.exists(os.path.dirname(paper_info_html_path)):
                os.makedirs(os.path.dirname(paper_info_html_path))
            with open(paper_info_html_path, "wb") as f:
                f.write(r.content)

        # load saved paper html page
        with open(paper_info_html_path, "rb") as f:
            html_content = f.read()
        paper_soup = BeautifulSoup(html_content, "lxml")

        # grab title, author, abstract etc.        
        paper_title = paper_soup.find("h2", attrs={"id":"title"}).text.replace(" ", "_")
        print("processing: " + cid, " ", str(year), " ", paper_title)
        # import pdb; pdb.set_trace()
        authors = [content.text for content in paper_soup.find('p', attrs={"class": "lead"}).contents if "</a>" in str(content)]
        abstract = paper_soup.find('div', attrs={"class": "acl-abstract"}).text

        # save pdf
        pdf_link = info_link + ".pdf"
        pdf_name = paper_title + ".pdf"
        pdf_path = os.path.join("working", "pdfs", cid+str(year), pdf_name)
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

        # pdf2txt for extracting content from downloaded pdf files
        paper_text = text_from_pdf(pdf_path)
        papers.append([paper_title, cid, year, "|".join(authors), info_link, abstract, paper_text])

print(blacklist)

acl_papers_data = pd.DataFrame(papers, columns=["title", "venue", "year", "authors", "url", "abstract", "paper_text"])
acl_papers_data.to_csv("output/acl.csv", index=False)
acl_papers_data_without_paper_text = acl_papers_data.drop(columns=["paper_text"])
acl_papers_data_without_paper_text.to_csv("output/acl_without_paper_text.csv", index=False)