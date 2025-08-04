# TikTok Video Data Scraper API (FastAPI + Selenium)

This is a FastAPI-based web application that scrapes TikTok video data like **likes, comments, and favorites** using Selenium automation. The API supports optional proxy usage for anonymity or bypassing IP restrictions.

---

##  Features

- Accepts a TikTok video URL via POST request
- Automates browser using Selenium to extract:
  -  Likes
  -  Comments
  -  Favorites
- Optionally supports proxy for web scraping
- Saves results to a local CSV file
- Gracefully handles driver reinitialization

---

## Technologies Used

- **Python 3**
- **FastAPI** (Web framework)
- **Selenium** (Web automation)
- **Undetected ChromeDriver**
- **Webdriver Manager**
- **CSV** (Data storage)

---

## Installation

Install the required dependencies:

```bash
pip install fastapi selenium uvicorn webdriver-manager
