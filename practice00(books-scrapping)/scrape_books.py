"""
Books Scraper
Author: Kote
University: SEU (Georgian-American University), AI & Data Science, 2nd year
Course homework: web scraping with Beautiful Soup

This script scrapes all 1000 books from https://books.toscrape.com/
(title, price, link) and saves them into a pandas DataFrame and an Excel file.
"""

import os

import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def scrape_books(base_url):
    """Go through all pages of the site and collect the books.

    base_url: link of the first page, e.g. "https://books.toscrape.com/"
    returns: pandas DataFrame with columns Title, Price, URL
    """
    books = []        # here we keep one dict per book
    url = base_url    # we start from the first page

    # Session is faster than calling requests.get() 50 times
    with requests.Session() as session:
        while url:
            response = session.get(url, timeout=30)
            response.raise_for_status()      # stop if the page didn't load
            response.encoding = "utf-8"      # without this the price shows "Â£"

            soup = BeautifulSoup(response.text, "html.parser")

            # every book is inside <article class="product_pod">
            for book in soup.select("article.product_pod"):
                link = book.h3.a

                # the title in the text is cut ("A Light in the ..."),
                # the full title is in the "title" attribute
                title = link["title"]

                price_text = book.select_one("p.price_color").get_text(strip=True)
                price = float(price_text.replace("£", ""))   # "£51.77" -> 51.77

                # href is relative, so we join it with the current page url
                book_url = urljoin(url, link["href"])

                books.append({
                    "Title": title,
                    "Price": price,
                    "URL": book_url,
                })

            # find the "next" button, if there is none we are on the last page
            next_page = soup.select_one("li.next a")
            url = urljoin(url, next_page["href"]) if next_page else None

    return pd.DataFrame(books)


if __name__ == "__main__":
    base_url = "https://books.toscrape.com/"

    # call the function and save the result in a variable
    df = scrape_books(base_url)

    # save to excel
    output_file = "books.xlsx"
    df.to_excel(output_file, index=False)

    print(df.head())
    print("Total books:", len(df))
    print("Excel file created:", os.path.exists(output_file))

    # quick check that we got all the books
    assert len(df) == 1000, "Expected 1000 books"
