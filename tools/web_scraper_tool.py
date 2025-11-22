import requests
from bs4 import BeautifulSoup

# --- Our Python Function ---

def scrape_website_text(url: str) -> str:
    """
    Fetches a webpage and extracts all clean text content.
    
    Args:
        url: The URL of the webpage to scrape.
        
    Returns:
        The extracted text, or an error message.
    """
    print(f"Scraping URL: {url}")
    try:
        # Set a user-agent to pretend we're a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Fetch the webpage
        response = requests.get(url, headers=headers, timeout=10)
        # Raise an exception if the request failed
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()
        
        # Get all the text
        text = soup.get_text()
        
        # Clean up the text: break into lines and remove extra whitespace
        lines = (line.strip() for line in text.splitlines())
        # Re-join lines, but only if they're not empty
        clean_text = '\n'.join(line for line in lines if line)
        
        if not clean_text:
            return f"Error: No text content found at {url}"
            
        return clean_text
        
    except requests.exceptions.RequestException as e:
        return f"An error occurred while fetching the URL: {e}"
    except Exception as e:
        return f"An error occurred during scraping: {e}"

