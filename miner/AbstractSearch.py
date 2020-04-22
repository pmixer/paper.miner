import pandas as pd
from nltk.tokenize import word_tokenize
from gensim.models.doc2vec import Doc2Vec

def search_abstract(path="", query="", top =10):
    ####Input
    #strl = "Up-propagation is a good algorithm that can invert the whole world"
    strl_tok = word_tokenize(query)
    model = Doc2Vec.load(path+"my_model")
    inferred_vector = model.infer_vector(doc_words=strl_tok, alpha=0.05, steps=500)
    sims = model.docvecs.most_similar([inferred_vector], topn=top)

    result = []
    for count, sim in sims:
        #print(count, sim)
        result.append(count)
    return result

if __name__ == '__main__':
    df = pd.read_csv('papers_with_abstract.csv', header="infer", sep=',', encoding='iso-8859-1')
    df.drop(df[df.isnull().any(axis=1)].index, inplace=True)

    q= "Up-propagation is a good algorithm that can invert the whole world"
    result = search_abstract(query=q)
    print(df.loc[result,:])