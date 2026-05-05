from app.services.ingestion_service import fetch_job_page, parse_job_page, extract_text_from_page

if __name__ == "__main__":
    job_url = f"https://navi.turbohire.co/job/publicjobs/g9oM9RfbFZAKEgTAnDus2yFWAOVPlxDfA8rc0V4s%2FrLKclZCm33WbmOWFzqJf2%2Fz"
    
    html = fetch_job_page(job_url)
    print(html[2500:5000])
    soup = parse_job_page(html)
    text = extract_text_from_page(soup)
    
    print(text[:500])