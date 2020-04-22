#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np
import pandas as pd


# # Coresponding coauthors to each authors

# In[ ]:


#每个作者对应coauthors的数量
authors=pd.read_csv('authors_combined_final.csv', encoding= 'unicode_escape')
authors = authors.iloc[:,[0,1,2,3,4,5,6,7]]
first_authors = authors.groupby('first authors').count().reset_index()
first_authors['number_of_coauthors'] = first_authors['second authors'] + first_authors['third authors'] + first_authors['fourth authors'] +first_authors['fifth authors']
first_authors= first_authors.rename(columns = {'first authors':'authors'})
first_authors=first_authors[['authors','number_of_coauthors']]
second_authors = authors.groupby('second authors').count().reset_index()
second_authors['number_of_coauthors'] = second_authors['first authors'] + second_authors['third authors'] + second_authors['fourth authors'] +second_authors['fifth authors']
second_authors= second_authors.rename(columns = {'second authors':'authors'})
second_authors=second_authors[['authors','number_of_coauthors']]
third_authors = authors.groupby('third authors').count().reset_index()
third_authors['number_of_coauthors'] = third_authors['first authors'] + third_authors['second authors'] + third_authors['fourth authors'] +third_authors['fifth authors']
third_authors= third_authors.rename(columns = {'third authors':'authors'})
third_authors=third_authors[['authors','number_of_coauthors']]
fourth_authors = authors.groupby('fourth authors').count().reset_index()
fourth_authors['number_of_coauthors'] = fourth_authors['first authors'] + fourth_authors['second authors'] + fourth_authors['third authors'] +fourth_authors['fifth authors']
fourth_authors= fourth_authors.rename(columns = {'fourth authors':'authors'})
fourth_authors=fourth_authors[['authors','number_of_coauthors']]
fifth_authors = authors.groupby('fifth authors').count().reset_index()
fifth_authors['number_of_coauthors'] = fifth_authors['first authors'] + fifth_authors['second authors'] + fifth_authors['third authors'] +fifth_authors['fourth authors']
fifth_authors= fifth_authors.rename(columns = {'fifth authors':'authors'})
fifth_authors=fifth_authors[['authors','number_of_coauthors']]


# In[ ]:


authors_temp1 = pd.concat([first_authors, second_authors], ignore_index=True)
authors_temp2 = pd.concat([authors_temp1, third_authors], ignore_index=True)
authors_temp3 = pd.concat([authors_temp2, fourth_authors], ignore_index=True)
authors_final = pd.concat([authors_temp3, fifth_authors], ignore_index=True)


# In[ ]:


authors_final = authors_final.groupby('authors').sum().reset_index()


# # 7 venues' word cloud

# In[ ]:


##word cloud
from wordcloud import WordCloud, STOPWORDS 
import matplotlib.pyplot as plt 
import pandas as pd 


# In[ ]:


#four venues cvs imported
papers_nips= pd.read_csv("nips_without_paper_text.csv")
papers_nips.head()
#papers_nips = papers_nips.loc[papers_nips.abstract != 'Abstract Missing']
papers_nips.head()
print(len(papers_nips))


# In[ ]:


papers_acl= pd.read_csv("acl_without_paper_text.csv")
#papers_acl = papers_acl.loc[papers_acl.abstract != 'Abstract Missing']
papers_acl.head()
print(len(papers_acl))


# In[ ]:


papers_cvf= pd.read_csv("cvf_without_paper_text.csv")
#papers_cvf = papers_cvf.loc[papers_cvf.abstract != 'Abstract Missing']
papers_cvf.head()
print(len(papers_cvf))


# In[ ]:


papers_jmlr= pd.read_csv("jmlr_without_paper_text.csv")
#papers_jmlr = papers_jmlr.loc[papers_jmlr.abstract != 'Abstract Missing']
papers_jmlr.head()
print(len(papers_jmlr))


# In[ ]:


#combine rows of data
papers_row_reindex_temp1 = pd.concat([papers_nips, papers_acl], ignore_index=True)
papers_row_reindex_temp2 = pd.concat([papers_row_reindex_temp1, papers_cvf], ignore_index=True)
papers_row_combined = pd.concat([papers_row_reindex_temp2, papers_jmlr], ignore_index=True)


# In[ ]:


comment_words = '' 
stopwords = set(STOPWORDS)


# In[ ]:


#ACL <- 修改会议名 再跑即可
papers_ACL = papers_row_combined.loc[papers_row_combined.venue == 'ACL']


# In[ ]:


# iterate through the csv file 
for val in papers_ACL.abstract: 
      
    # typecaste each val to string 
    val = str(val) 
  
    # split the value 
    tokens = val.split() 
      
    # Converts each token into lowercase 
    for i in range(len(tokens)): 
        tokens[i] = tokens[i].lower() 
      
    comment_words += " ".join(tokens)+" "
  
wordcloud = WordCloud(width = 800, height = 800, 
                background_color ='white', 
                stopwords = stopwords, 
                min_font_size = 10).generate(comment_words)


# In[ ]:


# plot the WordCloud image                        
plt.figure(figsize = (8, 8), facecolor = None) 
plt.imshow(wordcloud) 
plt.axis("off") 
plt.tight_layout(pad = 0) 
  
plt.show()


# In[ ]:


#authors_combined
authors=pd.read_csv('authors_combined_final.csv', encoding= 'unicode_escape')
authors = authors.iloc[:,[0,1,2,3,4,5,6,7]]
authors


# # the number of pulications to each authors in venues

# In[ ]:


#authors_combined
authors=pd.read_csv('authors_combined_final.csv', encoding= 'unicode_escape')
authors = authors.iloc[:,[0,1,2,3,4,5,6,7]]
authors


# In[ ]:


#first authors count
first_authors_venue_pub_numbers=authors.groupby(['first authors','venue'])['title'].count()
first_authors_venue_pub_numbers
first_authors_venue_pub_numbers = pd.DataFrame(first_authors_venue_pub_numbers)
first_authors_venue_pub_numbers
first_authors_venue_pub_numbers.rename(columns = {'title':'publication_numbs'}, inplace = True)
first_authors_venue_pub_numbers
#second authors count
second_authors_venue_pub_numbers=authors.groupby(['second authors','venue']).count()['title']
second_authors_venue_pub_numbers = second_authors_venue_pub_numbers.reset_index()
#third authors count
third_authors_venue_pub_numbers=authors.groupby(['third authors','venue']).count()['title'].reset_index()
third_authors_venue_pub_numbers
#fourth authors count
fourth_authors_venue_pub_numbers=authors.groupby(['fourth authors','venue']).count()['title'].reset_index()
fourth_authors_venue_pub_numbers
#fifth authors count
fifth_authors_venue_pub_numbers=authors.groupby(['fifth authors','venue']).count()['title'].reset_index()
fifth_authors_venue_pub_numbers


# In[ ]:


first_authors_venue_pub_numbers=authors.groupby(['first authors','venue'])['title'].count()
first_authors_venue_pub_numbers
first_authors_venue_pub_numbers = pd.DataFrame(first_authors_venue_pub_numbers)
first_authors_venue_pub_numbers = first_authors_venue_pub_numbers.reset_index()
first_authors_venue_pub_numbers.rename(columns = {'first authors':'authors'}, inplace = True)
#first_authors_venue_pub_numbers['title']
first_authors_venue_pub_numbers


# In[ ]:


##
second_authors_venue_pub_numbers.rename(columns = {'second authors':'authors'}, inplace = True)
third_authors_venue_pub_numbers.rename(columns = {'third authors':'authors'}, inplace = True)
fourth_authors_venue_pub_numbers.rename(columns = {'fourth authors':'authors'}, inplace = True)
fifth_authors_venue_pub_numbers.rename(columns = {'fifth authors':'authors'}, inplace = True)


# In[ ]:


authors_temp1 = pd.concat([first_authors_venue_pub_numbers, second_authors_venue_pub_numbers], ignore_index=True)
authors_temp2 = pd.concat([authors_temp1, third_authors_venue_pub_numbers], ignore_index=True)
authors_temp3 = pd.concat([authors_temp2, fourth_authors_venue_pub_numbers], ignore_index=True)
authors_temp4 = pd.concat([authors_temp3, fifth_authors_venue_pub_numbers], ignore_index=True)

#authors[(authors.authors == 'A. N. Rajagopalan')& (authors.venue =='CVPR') ]
authors = authors_temp4.groupby(['authors','venue']).count().reset_index()
authors = authors.rename(columns = {'title':'publication_numbers'})
authors
authors = authors.sort_values(by=['venue'])
#authors = authors.sort_values(by=['authors'])
authors.to_csv('authors_venue_papercounts.csv',index=False)

