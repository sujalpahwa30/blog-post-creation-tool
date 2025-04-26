import pandas as pd
import os
import json
from datetime import datetime

def generate_mock_products(output_file="data/trending_products.csv"):
    """Generate mock product data to bypass scraping restrictions"""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    mock_products = [
        {
            "name": "Wireless Bluetooth Earbuds with Noise Cancellation",
            "price": "$49.99",
            "rating": "4.5 out of 5 stars",
            "url": "https://www.amazon.com/example/product1",
            "image_url": "https://example.com/image1.jpg",
            "category": "electronics"
        },
        {
            "name": "Smart Home Security Camera System",
            "price": "$129.99",
            "rating": "4.3 out of 5 stars",
            "url": "https://www.amazon.com/example/product2",
            "image_url": "https://example.com/image2.jpg",
            "category": "electronics"
        },
        {
            "name": "Non-Stick Ceramic Cookware Set",
            "price": "$89.95",
            "rating": "4.7 out of 5 stars",
            "url": "https://www.amazon.com/example/product3",
            "image_url": "https://example.com/image3.jpg",
            "category": "home-kitchen"
        },
        {
            "name": "Ergonomic Office Chair with Lumbar Support",
            "price": "$199.99",
            "rating": "4.4 out of 5 stars",
            "url": "https://www.amazon.com/example/product4",
            "image_url": "https://example.com/image4.jpg",
            "category": "home-kitchen"
        },
        {
            "name": "Moisture-Wicking Athletic Performance T-Shirts (3-Pack)",
            "price": "$24.95",
            "rating": "4.2 out of 5 stars",
            "url": "https://www.amazon.com/example/product5",
            "image_url": "https://example.com/image5.jpg",
            "category": "fashion"
        },
        {
            "name": "Professional Chef Knife Set with Block",
            "price": "$79.99",
            "rating": "4.6 out of 5 stars",
            "url": "https://www.amazon.com/example/product6",
            "image_url": "https://example.com/image6.jpg",
            "category": "home-kitchen"
        },
        {
            "name": "Portable Bluetooth Speaker with Enhanced Bass",
            "price": "$39.95",
            "rating": "4.1 out of 5 stars", 
            "url": "https://www.amazon.com/example/product7",
            "image_url": "https://example.com/image7.jpg",
            "category": "electronics"
        },
        {
            "name": "Digital Air Fryer with Smart Temperature Control",
            "price": "$119.99",
            "rating": "4.8 out of 5 stars",
            "url": "https://www.amazon.com/example/product8",
            "image_url": "https://example.com/image8.jpg",
            "category": "home-kitchen"
        },
        {
            "name": "Adjustable Dumbbell Set for Home Gym",
            "price": "$249.99",
            "rating": "4.5 out of 5 stars",
            "url": "https://www.amazon.com/example/product9",
            "image_url": "https://example.com/image9.jpg",
            "category": "sports-outdoors"
        },
        {
            "name": "Organic Cotton Bedding Set with Duvet Cover",
            "price": "$89.99", 
            "rating": "4.4 out of 5 stars",
            "url": "https://www.amazon.com/example/product10",
            "image_url": "https://example.com/image10.jpg",
            "category": "home-kitchen"
        }
    ]
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(mock_products)
    df.to_csv(output_file, index=False)
    print(f"Generated mock product data with {len(mock_products)} products")
    
    # Also create a mock product_keywords.csv file to ensure the pipeline continues
    keywords_file = os.path.join(os.path.dirname(output_file), "product_keywords.csv")
    products_with_keywords = []
    
    for product in mock_products:
        product_copy = product.copy()
        # Generate mock keywords based on product name and category
        name_parts = product['name'].lower().split()
        category = product['category'].replace('-', ' ')
        
        # Create some realistic looking keywords
        keywords = [
            f"best {name_parts[0]} {name_parts[1]}",
            f"{category} {name_parts[0]}",
            f"top rated {name_parts[0]}",
            f"{name_parts[0]} {name_parts[1]} review"
        ]
        
        product_copy['keywords'] = ', '.join(keywords)
        products_with_keywords.append(product_copy)
    
    # Save products with keywords
    keywords_df = pd.DataFrame(products_with_keywords)
    keywords_df.to_csv(keywords_file, index=False)
    print(f"Generated mock keyword data for {len(products_with_keywords)} products")
    
    # Also create mock blog posts in case the content generation fails
    blog_posts_file = os.path.join(os.path.dirname(output_file), "blog_posts.json")
    blog_posts = []
    
    for product in products_with_keywords:
        keywords = [k.strip() for k in product['keywords'].split(',')]
        
        blog_post = {
            'title': f"Why the {product['name']} is a Game-Changer in {datetime.now().year}",
            'content': generate_mock_blog_content(product['name'], product['category'], keywords),
            'product_name': product['name'],
            'product_price': product['price'],
            'product_url': product['url'],
            'product_image_url': product['image_url'],
            'keywords': keywords,
            'category': product['category'],
            'date_created': datetime.now().strftime("%Y-%m-%d")
        }
        
        blog_posts.append(blog_post)
    
    # Save mock blog posts
    os.makedirs(os.path.dirname(blog_posts_file), exist_ok=True)
    with open(blog_posts_file, 'w') as f:
        json.dump(blog_posts, f, indent=2)
    
    print(f"Generated {len(blog_posts)} mock blog posts")
    
    return mock_products

def generate_mock_blog_content(product_name, category, keywords):
    """Generate a mock blog post content"""
    category_name = category.replace('-', ' ')
    
    # Create a templated blog post with the keywords intelligently inserted
    content = f"""Looking for the perfect addition to your {category_name} collection? The {product_name} has been gaining popularity among enthusiasts for good reason.

When searching for {keywords[0]}, this product stands out with its exceptional quality and performance. The {product_name} offers features that make it a {keywords[2]} in today's market.

Many {keywords[1]} options are available, but few match the versatility and reliability of this particular model. As detailed in numerous {keywords[3]}, users consistently praise its intuitive design and durability.

Whether you're a beginner or experienced in {category_name}, the {product_name} offers excellent value for your investment. Check it out today and experience the difference for yourself!"""

    return content

if __name__ == "__main__":
    generate_mock_products()