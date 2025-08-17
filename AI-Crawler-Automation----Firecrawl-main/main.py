import os
import pandas as pd
from tqdm import tqdm
import time
from firecrawl import FirecrawlApp

# Configurations
INPUT_EXCEL_PATH = "Dataset firecrawl.xlsx"
SAVE_DIR = "Web_Scraped_Data"
OUTPUT_SUMMARY_PATH = "scraping_output_status.xlsx"
FIRE_CRAWL_API_KEY = "fc-9f793349b3ba4623b1ca112a40997e15"  # Replace with your key

# Initialize Firecrawl
app = FirecrawlApp(api_key=FIRE_CRAWL_API_KEY)
os.makedirs(SAVE_DIR, exist_ok=True)

def read_urls_from_excel(file_path):
    """Read URLs from Excel (normalize column names)"""
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip().str.lower()  # Normalize column names
    print("✅ Available columns in Excel:", df.columns.tolist())  # Debug log

    if "url" not in df.columns:
        raise ValueError("❌ Excel must contain a 'url' column.")
    
    return df["url"].dropna().tolist()

def scrape_and_save(url, index):
    """Scrape a URL and save content in .html, .md, and .txt formats"""
    url_folder = os.path.join(SAVE_DIR, f"url_{index}")
    os.makedirs(url_folder, exist_ok=True)

    print(f"\n🔍 Scraping URL {index}: {url}")
    try:
        result = app.scrape_url(url, formats=["markdown", "html"])

        # Save .html
        html_path = os.path.join(url_folder, "scraped_output.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(result.html)

        # Save .md
        md_path = os.path.join(url_folder, "scraped_output.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(result.markdown)

        # Save .txt
        plain_text = result.markdown.replace("#", "").replace("*", "")
        txt_path = os.path.join(url_folder, "scraped_output.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(plain_text)

        print(f"✅ SUCCESS: Data saved in {url_folder}")
        return "SAVED", url
    except Exception as e:
        print(f"❌ FAILED: Could not scrape {url}. Error: {e}")
        return "FAILED", url

def main():
    print("📥 Reading Excel file...")
    urls = read_urls_from_excel(INPUT_EXCEL_PATH)
    print(f"🔗 Total URLs found: {len(urls)}")

    output_records = []

    for idx, url in tqdm(enumerate(urls), total=len(urls), desc="Scraping URLs"):
        status, final_url = scrape_and_save(url, idx+1)
        output_records.append([idx+1, status, final_url])
        time.sleep(3)  # Respect API rate limits

    # Save scraping summary
    df_summary = pd.DataFrame(output_records, columns=["Index", "Status", "URL"])
    df_summary.to_excel(OUTPUT_SUMMARY_PATH, index=False)
    print(f"\n📄 Summary saved to: {OUTPUT_SUMMARY_PATH}")

if __name__ == "__main__":
    main()
