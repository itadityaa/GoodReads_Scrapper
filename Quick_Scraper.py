import argparse
from bs4 import BeautifulSoup as soup
import requests as req
import pandas as pd

import warnings
warnings.filterwarnings("ignore")

# Create the argument parser
parser = argparse.ArgumentParser(description='Scrape a Goodreads Listopia list.')
parser.add_argument('url', metavar='url', type=str, help='URL of the Goodreads Listopia list to scrape')
parser.add_argument('-p', '--pages', metavar='pages', type=int, default=1, help='Number of pages to scrape (default is 1)')
parser.add_argument('-o', metavar='output', type=str, help='Output format (csv or console)', default='console')

# Parse the arguments
args = parser.parse_args()

# Set the URL to scrape from the command line argument
final_url = args.url
pages = args.pages

# final_url = 'https://www.goodreads.com/list/show/83741.Kindle_Unlimited_Romance_Favorites'
# pages = 3

print(f'\nGetting the list of your books. Hold your horses!!!\n')

# Send a request to the URL
def get_the_tr_containers(url):
    url_data = req.get(final_url)
    url_soup = soup(url_data.content, 'html.parser')
    tr_container = url_soup.find_all('tr', itemtype='http://schema.org/Book')
    return tr_container

# Initialize the variables.
bookTitle, authors, Average_rating, Total_rating, Total_score, People_voted = [], [], [], [], [], []

# Function to scrape the webpage.
def make_lists(tr_container):
    for book in tr_container:
        
        bookTitle.append(book.find('a', class_='bookTitle').text.strip())
        authors.append(book.find('a', class_="authorName").text.strip())
        
        try:
          temp_rating = book.find('span', class_="greyText smallText uitext").text.strip().split()
          Average_rating.append(temp_rating[0])
          Total_rating.append(temp_rating[4])
        except:
            Average_rating.append('')
            Total_rating.append('')

        try:
          temp_score = book.find('span', class_="smallText uitext").text.strip().split()
          Total_score.append(temp_score[1][:-1])
          People_voted.append(temp_score[3])
        except:
            Total_score.append('')
            People_voted.append('')

# Changing pages
while pages > 0:
    
    temp_url = final_url
    temp_url += f'?page={pages + 1}'
    # print(temp_url)
    
    print(f'Scraping page {pages} of {final_url.split("/")[-1].split(".")[-1]} list.\n')
    tr_container = get_the_tr_containers(url=temp_url)
    
    make_lists(tr_container=tr_container)
    # print(bookTitle[:5])
    pages -= 1

# Create DataFrame
dataFrame = pd.DataFrame({'Book_Title' : bookTitle, 
                          'Author' : authors,
                          'Average_Rating' : Average_rating,
                          'Total_Rating' : Total_rating,
                          'Total_Score' : Total_score,
                          'People_Voted' : People_voted})

print(f'Got the data. Oh, but not so soon!!\n')

# Clean the DataFrame
def clean_df(dataFrame):
    dataFrame["Average_Rating"] = pd.to_numeric(dataFrame["Average_Rating"], errors='coerce')

    dataFrame['Total_Rating'] = dataFrame['Total_Rating'].str.replace(',', '')
    dataFrame['Total_Rating'] = pd.to_numeric(dataFrame['Total_Rating'], errors='coerce')

    dataFrame.dropna(inplace=True)

    ordered_dataFrame = dataFrame.sort_values(by=['Average_Rating', 'Total_Rating'], ascending=False)
    return ordered_dataFrame

# Call the function
print(f'Cleaning the Data.\n')
ordered_dataFrame = clean_df(dataFrame=dataFrame)

# Print the books or save to CSV.
if not args.o == 'csv':
    print(f"\nThe top 5 books are:\n {ordered_dataFrame[['Book_Title', 'Author', 'Average_Rating']].head()}")
    print(f"\nFive Random books:\n {ordered_dataFrame[['Book_Title', 'Author', 'Average_Rating']].sample(n=5)} ")
else:
    filename = final_url.split("/")[-1].split(".")[-1] + '.csv'
    ordered_dataFrame.to_csv(filename, index=False)
    print(f"Result saved to {filename}")