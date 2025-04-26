import os
import logging
import time
import pandas as pd
from scraper import AmazonProductScraper
from keyword_research import KeywordResearchTool
from content_generator import BlogContentGenerator
from publisher import BlogPublisher
from dotenv import load_dotenv

# Load configuration from .env
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "True").lower() == "true"

def main():
    logging.info("Starting SEO Blog Post Creation Pipeline...")
    
    # Step 1: Get Trending Products
    if USE_MOCK_DATA:
        logging.info("Using mock product data as configured.")
        if os.path.exists("data/trending_products.csv"):
            trending_products = pd.read_csv("data/trending_products.csv").to_dict(orient='records')
        else:
            logging.error("No mock data available in data/trending_products.csv. Exiting.")
            return
    else:
        scraper = AmazonProductScraper()
        logging.info("Attempting to scrape trending products across multiple categories...")
        trending_products = scraper.get_trending_products(limit=3)
        if not trending_products:
            logging.warning("Scraping failed: No products scraped. Falling back to mock data.")
            if os.path.exists("data/trending_products.csv"):
                trending_products = pd.read_csv("data/trending_products.csv").to_dict(orient='records')
            else:
                logging.error("No mock data available. Exiting.")
                return
        os.makedirs("data", exist_ok=True)
        scraper.save_products_to_csv(trending_products, "data/trending_products.csv")
        logging.info("Trending products saved to data/trending_products.csv.")

    # Step 2: SEO Keyword Research
    keyword_tool = KeywordResearchTool()
    logging.info("Researching SEO keywords for each product...")
    products_with_keywords = keyword_tool.research_keywords_for_products(trending_products, output_file="data/product_keywords.csv")
    
    # Step 3: Generate Blog Posts
    generator = BlogContentGenerator()
    logging.info("Generating blog posts for each product...")
    blog_posts = generator.generate_blog_posts(products_file="data/product_keywords.csv", output_file="data/blog_posts.json")
    if not blog_posts:
        logging.error("No blog posts were generated. Exiting.")
        return
    logging.info(f"Generated {len(blog_posts)} blog posts.")
    
    # Display a sample blog post in the terminal
    logging.info("\n--- Sample Blog Post ---")
    sample = blog_posts[0]
    logging.info(f"Title: {sample['title']}")
    logging.info(f"Keywords: {sample['keywords']}")
    logging.info("Content:")
    logging.info(sample['content'])
    
    # Step 4: Publish Blog Posts (Save as HTML only)
    publisher = BlogPublisher()
    published_links = []
    for post in blog_posts:
        html_link = publisher.save_as_html(post)  # Only save as HTML
        published_links.append({"title": post["title"], "html": html_link})
        time.sleep(1)
    
    logging.info("Publishing complete. Summary of published posts:")
    for link in published_links:
        logging.info(link)
    
    logging.info("SEO Blog Post Creation Pipeline finished.")

if __name__ == "__main__":
    main()
