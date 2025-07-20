import requests
from bs4 import BeautifulSoup

def test_scraping():
    url = "https://www.artificialintelligence-news.com/artificial-intelligence-news/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status code: {response.status_code}")
        print(f"Title: {response.text[:200]}...")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"Page title: {soup.title.string if soup.title else 'No title'}")
        
        # Try different selectors
        selectors = [
            'h3.td-module-title a',
            'div.td-module-thumb a', 
            'h2.td-module-title a',
            'a[rel="bookmark"]',
            'article a[href*="/20"]',
            'h1 a',
            'h2 a',
            'h3 a',
            'a[href*="artificialintelligence-news.com"]'
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            print(f"\nSelector '{selector}': {len(links)} links found")
            for i, link in enumerate(links[:3]):
                title = link.get('title') or link.get_text().strip()
                href = link.get('href')
                print(f"  {i+1}. {title[:60]}... -> {href}")
        
        # Look for any links with year in URL
        all_links = soup.find_all('a', href=True)
        year_links = [a for a in all_links if '/20' in a.get('href')]
        print(f"\nLinks with year in URL: {len(year_links)}")
        for i, link in enumerate(year_links[:5]):
            print(f"  {i+1}. {link.get_text()[:50]}... -> {link.get('href')}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_scraping() 