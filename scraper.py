import os 
import time 
import random 
import logging 
import requests 
import pandas as pd 
from bs4 import BeautifulSoup 

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class AmazonProductScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36' ),
            'Accept-language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        self.base_url = "https://www.amazon.com"
        
    def get_bestsellers_by_category(self, category="electronics"):
        bestseller_url = f"{self.base_url}/Best-Sellers-{category.capitalize()}/zgbs/{category}"
        logging.info(f"Scraping bestsellers from: {bestseller_url}")
        
        try:
            response = requests.get(bestseller_url, headers=self.headers)
            response.raise_for_status()
        except Exception as e:
            logging.error(f"Error fetching page: {e}")
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        products = []
            
        selectors = [
            'div[data-component-type="s-search-result"]',
            'div.zg-item',
            'div.p13n-sc-uncoverable-faceout'
        ]    
        product_items = None 
        for selector in selectors:
            product_items = soup.select(selector)
            if product_items:
                break
        if not product_items:
            logging.warning("No product items found with the current selectors.")
            return []
        
        for item in product_items[:10]:
            try:
                name_elem = (item.select_one('span.a-size-medium') or 
                             item.select_one('div.p13n-sc-truncate') or
                             item.select_one('a.a-link-normal span'))
                price_elem = (item.select_one('span.a-offscreen') or 
                              item.select_one('span.p13n-sc-price'))
                rating_elem = item.select_one('span.a-icon-alt')
                url_elem = item.select_one('a.a-link-normal')
                img_elem = (item.select_one('img.s-image') or
                            item.select_one('img.a-dynamic-image'))
                
                product = {
                    'name': name_elem.get_text(strip=True) if name_elem else "Unknown Product",
                    'price': price_elem.get_text(strip=True) if price_elem else "Price not available",
                    'rating': rating_elem.get_text(strip=True) if rating_elem else "No ratings",
                    'url': self.base_url + url_elem('href') if url_elem and url_elem.has_attr('href') else " ",
                    'image_url': img_elem('src') if img_elem and img_elem.has_attr('src') else " ",
                    'category': category
                }
                products.append(product)
            except Exception as err:
                logging.error(f"Error extracting product info: {err}")
                continue 
            
        logging.info(f"Successfully scraped {len(products)} products from category '{category}'.")
        return products 
    
    def save_products_to_csv(self, products, filename="amazon_products.csv"):
        if not products:
            logging.warning("No products to save.")
            return False 
        
        try:
            df = pd.DataFrame(products)
            df.to_csv(filename, index=False)
            logging.info(f"Successfully saved {len(products)} products to '{filename}'.")
            return True 
        except Exception as e:
            logging.error(f"Error saving products to CSV: {e}")
            return False 
        
    def get_trending_products(self, categories=None, limit=5):
        if categories is None:
            categories = ["electronics", "home-kitchen", "fashion", "toys-games", "beauty"]
            
        all_products = []
        for category in categories:
            logging.info(f"Scraping category: {category}")
            products = self.get_bestsellers_by_category(category)
            if products:
                all_products.extend(products[:limit])
            delay = random.uniform(1.5, 4.0)
            logging.info(f"Waiting {delay:.2f} seconds befor next request...")
            time.sleep(delay)
        return all_products
    
if __name__ == "__main__":
    scraper = AmazonProductScraper()
    
    trending_products = scraper.get_trending_products(limit=3)
    os.makedirs("data", exist_ok=True)
    scraper.save_products_to_csv(trending_products, "data/trending_products.csv")
    logging.info(f"Total products scraped: {len(trending_products)}")
    