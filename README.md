# SEO Blog Post Creation Pipeline

This project is a modular pipeline that generates SEO-friendly blog posts for products. It consists of four main modules:

- **Scraper:** Collects product data (mock data or scraped from a dummy e‑commerce source).
- **Keyword Research:** Generates SEO keywords using API calls (with fallback to heuristic methods).
- **Content Generator:** Produces engaging blog posts using an AI text generation model (via OpenAI API or local Hugging Face model).
- **Publisher:** Saves the generated blog posts as HTML files, which can be served by a local Flask application.

## Features

- **Modular Architecture:** Each module can run independently and is easily replaceable.
- **Mock Data Option:** Automatically falls back to dummy data if real scraping fails.
- **Local Server Demo:** A simple Flask app (`server.py`) is provided to view the HTML blog posts interactively.
- **Extensible Integration:** Designed to allow further integration with platforms like WordPress or Medium.

## Installation

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
