import os
import json
import time
import requests
from datetime import datetime
import markdown
import html
from dotenv import load_dotenv

try:
    from wordpress_xmlrpc import Client, WordPressPost
    from wordpress_xmlrpc.methods.posts import NewPost
    WP_AVAILABLE = True
except ImportError:
    WP_AVAILABLE = False
    print("WordPress XMLRPC not available. Install with: pip install python-wordpress-xmlrpc")

load_dotenv()

class BlogPublisher:
    def __init__(self):
        self.wp_url = os.getenv("WORDPRESS_URL")
        self.wp_username = os.getenv("WORDPRESS_USERNAME")
        self.wp_password = os.getenv("WORDPRESS_PASSWORD")
        
        self.medium_token = os.getenv("MEDIUM_TOKEN")
        
        self.can_use_wordpress = all([self.wp_url, self.wp_username, self.wp_password]) and WP_AVAILABLE
        self.can_use_medium = bool(self.medium_token)
        
        if not self.can_use_wordpress and not self.can_use_medium:
            print("Warning: No publishing credentials found. Will save posts as HTML files instead.")
    
    def publish_to_wordpress(self, post):
        """Publish a blog post to WordPress"""
        if not self.can_use_wordpress:
            print("WordPress credentials not found or module not installed.")
            return None
            
        try:
            client = Client(
                f"{self.wp_url}/xmlrpc.php",
                self.wp_username,
                self.wp_password
            )
            
            wp_post = WordPressPost()
            wp_post.title = post['title']
            
            content = post['content']
            if post.get('product_image_url'):
                content = f"<img src='{post['product_image_url']}' alt='{post['product_name']}'/>\n\n" + content
                
            if post.get('product_url'):
                content += f"\n\n<p><a href='{post['product_url']}' target='_blank'>Check out the product here</a></p>"
                
            wp_post.content = content
            
            wp_post.terms_names = {
                'post_tag': post.get('keywords', []),
                'category': [post.get('category', 'Products').replace('-', ' ').title()]
            }
            
            wp_post.post_status = 'publish'
            
            post_id = client.call(NewPost(wp_post))
            post_url = f"{self.wp_url}/?p={post_id}"
            
            print(f"Published to WordPress: {post_url}")
            return post_url
            
        except Exception as e:
            print(f"Error publishing to WordPress: {str(e)}")
            return None
    
    def publish_to_medium(self, post):
        """Publish a blog post to Medium"""
        if not self.can_use_medium:
            print("Medium token not found.")
            return None
            
        try:
            url = "https://api.medium.com/v1/users/me/posts"
            
            headers = {
                "Authorization": f"Bearer {self.medium_token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            content = post['content']
            if not content.startswith("<"):
                content = markdown.markdown(content)
                
            if post.get('product_image_url'):
                content = f"<img src='{post['product_image_url']}' alt='{post['product_name']}'/>\n\n" + content
                
            if post.get('product_url'):
                content += f"\n\n<p><a href='{post['product_url']}' target='_blank'>Check out the product here</a></p>"
            
            payload = {
                "title": post['title'],
                "contentFormat": "html",
                "content": content,
                "tags": post.get('keywords', [])[:5],
                "publishStatus": "public"
            }
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            post_url = data.get("data", {}).get("url", "")
            print(f"Published to Medium: {post_url}")
            return post_url
            
        except Exception as e:
            print(f"Error publishing to Medium: {str(e)}")
            return None
    
    def save_as_html(self, post, output_dir="output/html"):
        """Save blog post as an HTML file"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            safe_title = "".join([c if c.isalnum() else "_" for c in post['title']])
            filename = f"{output_dir}/{safe_title}.html"
            
            content = post['content']
            if not content.startswith("<"):
                content = markdown.markdown(content)
            
            html_content = f"""<!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{post['title']}</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        margin: 0;
                        padding: 20px;
                        max-width: 800px;
                        margin: 0 auto;
                        color: #333;
                    }}
                    h1 {{
                        color: #2c3e50;
                        border-bottom: 1px solid #eee;
                        padding-bottom: 10px;
                    }}
                    img {{
                        max-width: 100%;
                        height: auto;
                        margin: 20px 0;
                    }}
                    .product-meta {{
                        background-color: #f8f9fa;
                        padding: 15px;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                    .keywords {{
                        color: #6c757d;
                        font-size: 0.9em;
                    }}
                    .cta {{
                        background-color: #007bff;
                        color: white;
                        padding: 10px 20px;
                        text-decoration: none;
                        border-radius: 5px;
                        display: inline-block;
                        margin-top: 20px;
                    }}
                    .cta:hover {{
                        background-color: #0069d9;
                    }}
                </style>
            </head>
            <body>
                <article>
                    <h1>{post['title']}</h1>
                    
                    <div class="product-meta">
                        <p><strong>Product:</strong> {post['product_name']}</p>
                        <p><strong>Price:</strong> {post.get('product_price', 'N/A')}</p>
                        <p><strong>Category:</strong> {post.get('category', 'N/A').replace('-', ' ').title()}</p>
                        <p class="keywords"><strong>Keywords:</strong> {', '.join(post.get('keywords', []))}</p>
                    </div>
                    
                    {f'<img src="{post["product_image_url"]}" alt="{post["product_name"]}">' if post.get('product_image_url') else ''}
                    
                    <div class="content">
                        {content}
                    </div>
                    
                    {f'<a href="{post["product_url"]}" class="cta" target="_blank">Check out this product</a>' if post.get('product_url') else ''}
                    
                    <footer>
                        <p>Published on {post.get('date_created', datetime.now().strftime("%Y-%m-%d"))}</p>
                    </footer>
                </article>
            </body>
            </html>
            """
            
            # Save the HTML file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            print(f"Saved blog post as HTML: {filename}")
            return filename
            
        except Exception as e:
            print(f"Error saving as HTML: {str(e)}")
            return None

if __name__ == "__main__":
    test_post = {
        'title': "Why This Amazing Product Will Change Your Life",
        'content': "This is a test blog post content. It would normally be longer and more detailed.",
        'product_name': "Test Product",
        'product_price': "$99.99",
        'product_url': "https://example.com/product",
        'product_image_url': "https://example.com/image.jpg",
        'keywords': ["test keyword", "example", "demo"],
        'category': "test-category",
        'date_created': datetime.now().strftime("%Y-%m-%d")
    }
    
    publisher = BlogPublisher()
    html_path = publisher.save_as_html(test_post)
    print(f"Test HTML file created: {html_path}")