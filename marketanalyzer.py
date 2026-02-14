import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import re


class Product:
    def __init__(self, name, price, rating):
        self._name = name
        self._price = price
        self._rating = rating

    def to_dict(self):
        return {
            "Name": self._name,
            "Price": self._price,
            "Rating": self._rating
        }


class Scraper:
    def __init__(self, url):
        self.url = url

    def fetch_products(self):
        products = []

        try:
            response = requests.get(self.url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            items = soup.find_all("article", class_="product_pod")

            for item in items:
                # Product name
                name = item.h3.a["title"]

                price_text = item.find("p", class_="price_color").text

                price = float(re.sub(r"[^\d.]", "", price_text))

                # Rating
                rating_class = item.find("p", class_="star-rating")["class"][1]

                rating_map = {
                    "One": 1,
                    "Two": 2,
                    "Three": 3,
                    "Four": 4,
                    "Five": 5
                }

                rating = rating_map.get(rating_class, 0)

                products.append(Product(name, price, rating))

        except requests.exceptions.RequestException as e:
            print(" Network error:", e)

        except Exception as e:
            print(" Parsing error:", e)

        return products



class DataAnalyzer:
    def __init__(self, filename):
        self.filename = filename

    def save_to_csv(self, products):
        try:
            df = pd.DataFrame([p.to_dict() for p in products])
            df.to_csv(self.filename, index=False)
            print(" Data saved to CSV.")

        except Exception as e:
            print(" File saving error:", e)

    def analyze_data(self):
        try:
            df = pd.read_csv(self.filename)

            print("\n--- Data Summary ---")
            print(df.head())

            print("\n📊 Statistics:")
            print("Average Price:", df["Price"].mean())
            print("Highest Price:", df["Price"].max())
            print("Lowest Price:", df["Price"].min())

            return df

        except Exception as e:
            print(" Analysis error:", e)

    def visualize_data(self, df):
        try:
            plt.figure()
            df["Price"].plot(kind="hist", bins=10)
            plt.title("Price Distribution")
            plt.xlabel("Price")
            plt.ylabel("Frequency")
            plt.tight_layout()
            plt.show()

        except Exception as e:
            print(" Visualization error:", e)

def main():
    url = "http://books.toscrape.com/catalogue/page-1.html"

    print("Fetching product data...")

    scraper = Scraper(url)
    products = scraper.fetch_products()

    if not products:
        print(" No products fetched.")
        return

    analyzer = DataAnalyzer("products.csv")
    analyzer.save_to_csv(products)

    df = analyzer.analyze_data()

    if df is not None:
        analyzer.visualize_data(df)


if __name__ == "__main__":
    main()
