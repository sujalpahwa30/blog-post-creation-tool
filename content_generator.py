import os
import time
import json
import random
import logging
from datetime import datetime
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class BlogContentGenerator:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            logging.warning("OpenAI API key not found. Will use fallback content generation.")
        self.model = "gpt-3.5-turbo"
        # Ensure blog_templates attribute is defined
        self.blog_templates = [
            "Discover Why {product_name} is Trending Right Now",
            "Top Reasons to Consider the {product_name} in {current_year}",
            "Is the {product_name} Worth Your Money? Our Take",
            "Why the {product_name} is a Game-Changer for {category} Enthusiasts",
            "The {product_name}: A Comprehensive Review"
        ]
    
    def generate_blog_title(self, product):
        template = random.choice(self.blog_templates)
        current_year = datetime.now().year
        product_name = ' '.join(product['name'].split()[:6])
        title = template.format(
            product_name=product_name,
            category=product['category'].replace('-', ' ').title(),
            current_year=current_year
        )
        return title
    
    def generate_content_with_openai(self, product, keywords):
        if not self.openai_api_key:
            return self.generate_fallback_content(product, keywords)
        product_name = product['name']
        product_category = product['category'].replace('-', ' ')
        product_price = product['price']
        keywords_str = ', '.join(keywords)
        prompt = (
            f"Write a concise, engaging 150-200 word blog post about the product \"{product_name}\" "
            f"which is in the {product_category} category and priced at {product_price}. "
            "The post should have an attention-grabbing introduction, "
            "highlight key features and benefits, include a call to action, "
            f"and naturally incorporate these keywords: {keywords_str}. "
            "Format the response as a complete blog post with paragraphs."
        )
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_api_key}"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a professional content writer specializing in SEO-friendly product reviews."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        try:
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"].strip()
            return content
        except Exception as e:
            logging.error(f"Error generating content with OpenAI: {e}")
            return self.generate_fallback_content(product, keywords)
    
    def generate_fallback_content(self, product, keywords):
        product_name = product['name']
        product_category = product['category'].replace('-', ' ')
        product_price = product['price']
        current_year = datetime.now().year
        keyword_sentences = []
        for keyword in keywords:
            if "best" in keyword.lower():
                keyword_sentences.append(f"When looking for the {keyword}, the {product_name} stands out.")
            elif "review" in keyword.lower():
                keyword_sentences.append(f"In our {keyword}, we found the {product_name} impressive.")
            elif "guide" in keyword.lower():
                keyword_sentences.append(f"Any {keyword} would be incomplete without the {product_name}.")
            else:
                keyword_sentences.append(f"The {product_name} is great for those searching for {keyword}.")
        blog_content = (
            f"Exploring the {product_name}: A {current_year} Must-Have\n\n"
            f"Are you in the market for a new {product_category}? The {product_name}, priced at {product_price}, has caught the attention of many. "
            f"{keyword_sentences[0] if len(keyword_sentences) > 0 else ''}\n\n"
            f"With a unique combination of features and quality, the {product_name} offers excellent value. "
            f"{keyword_sentences[1] if len(keyword_sentences) > 1 else ''}\n\n"
            f"{keyword_sentences[2] if len(keyword_sentences) > 2 else ''}\n\n"
            f"Whether you're a beginner or an expert in {product_category}, consider the {product_name} to elevate your experience. "
            f"{keyword_sentences[3] if len(keyword_sentences) > 3 else ''}\n\n"
            "Don't miss out on experiencing what could be the perfect addition to your collection!"
        )
        return blog_content
    
    def generate_blog_posts(self, products_file="data/product_keywords.csv", output_file="data/blog_posts.json"):
        try:
            df = pd.read_csv(products_file)
            products = df.to_dict(orient='records')
            blog_posts = []
            for product in products:
                logging.info(f"Generating blog post for: {product['name']}")
                keywords = [k.strip() for k in product.get('keywords', '').split(',') if k.strip()]
                title = self.generate_blog_title(product)
                content = self.generate_content_with_openai(product, keywords)
                blog_post = {
                    'title': title,
                    'content': content,
                    'product_name': product['name'],
                    'product_price': product['price'],
                    'product_url': product.get('url', ''),
                    'product_image_url': product.get('image_url', ''),
                    'keywords': keywords,
                    'category': product['category'],
                    'date_created': datetime.now().strftime("%Y-%m-%d")
                }
                blog_posts.append(blog_post)
                time.sleep(2)
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(blog_posts, f, indent=2)
            logging.info(f"Generated {len(blog_posts)} blog posts and saved to {output_file}")
            return blog_posts
        except Exception as e:
            logging.error(f"Error generating blog posts: {e}")
            return []

if __name__ == "__main__":
    generator = BlogContentGenerator()
    blog_posts = generator.generate_blog_posts()
    if blog_posts:
        sample = blog_posts[0]
        logging.info("\n--- Sample Blog Post ---")
        logging.info(f"Title: {sample['title']}")
        logging.info(f"Keywords: {sample['keywords']}")
        logging.info("Content:")
        logging.info(sample['content'])
        