[Flask](https://github.com/pallets/flask) based `json` data feeder and miner generated `.csv` file container(for > 1MB files, pls put it on [dropbox](https://www.dropbox.com/sh/v605veaawb4ngey/AABRGVeoLXk41xP009oeVqzPa?dl=0) etc.).

`python backend.py` to start the application after all dependencies installed.

send http get request like `http://127.0.0.1:5000/get_papers?keyword=waveglow&num_to_show=5` to retrive (paper_title, abstract, publication_date, authors, arxiv_url) list from Arxiv for recent work.

send http get request like `http://127.0.0.1:5000/get_author?name=Zan_Huang` to retrive (name, gscholar_url, gscholar_photo_url, affilication) data about the author.