import requests

from bs4 import BeautifulSoup

from app.schemas.job import JobCreate, JobResponse
from app.services.ai_extraction_service import extract_job_data_with_AI, merge_rule_based_and_ai_data
from app.services.job_services import createJob, get_job_by_url


def fetch_job_page(job_url: str) -> str:
    html = requests.get(job_url, timeout=10).text
    
    return html


def parse_job_page(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")


def extract_text_from_page(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "aside", "form"]):
        tag.decompose()
    
    text = soup.get_text(separator=" ", strip=True)
    
    clean_text = " ".join(text.split())
    return clean_text


def extract_job_title(soup: BeautifulSoup) -> str | None:
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    
    h1= soup.find("h1")
    if h1:
        return h1.get_text(strip=True)
    
    return None


def extract_company_name(soup: BeautifulSoup) -> str | None:
    og_site_name = soup.find("meta", attrs={"property": "og:site_name"})
    if og_site_name and og_site_name.get("content"):
        return og_site_name["content"].strip()

    application_name = soup.find("meta", attrs={"name": "application-name"})
    if application_name and application_name.get("content"):
        return application_name["content"].strip()

    return None


def extract_location(soup: BeautifulSoup, text: str) -> str | None:
    job_location = soup.find("meta", attrs={"property": "job:location"})
    if job_location and job_location.get("content"):
        return job_location["content"].strip()

    meta_location = soup.find("meta", attrs={"name": "location"})
    if meta_location and meta_location.get("content"):
        return meta_location["content"].strip()

    lower_text = text.lower()

    known_locations = [
        "hyderabad",
        "bengaluru",
        "bangalore",
        "pune",
        "mumbai",
        "delhi",
        "gurugram",
        "noida",
        "chennai",
    ]

    for location in known_locations:
        if location in lower_text:
            return location.title()

    return None


def extract_work_mode(text: str) -> str | None:
    lower_text = text.lower()

    if "hybrid" in lower_text:
        return "hybrid"
    if "remote" in lower_text:
        return "remote"
    if "onsite" in lower_text or "on-site" in lower_text or "wfo" in lower_text or "work from office" in lower_text:
        return "onsite"

    return None


def extract_job_data_from_url(job_url: str) -> dict:
    html_page = fetch_job_page(job_url)
    
    soup = parse_job_page(html_page)
    
    text = extract_text_from_page(soup)
    
    if not text or len(text) < 200:
        raise ValueError("Could not extract meaningful job content from the page.")
    
    title = extract_job_title(soup)
    work_mode = extract_work_mode(text)
    company_name = extract_company_name(soup)
    location = extract_location(soup, text)
    
    rule_based_data = {
        "job_url":job_url,
        "job_title":title,
        "job_description":text,
        "work_mode":work_mode,
        "company_name":company_name, 
        "location":location
    }
    
    ai_data = extract_job_data_with_AI(text)
    
    merged_data = merge_rule_based_and_ai_data(rule_based_data, ai_data)
    
    return merged_data


def ingest_job_url(db, job_url: str) -> JobResponse:
    existing_job = get_job_by_url(db, job_url)
    if existing_job:
        return existing_job
    
    extracted_data = extract_job_data_from_url(job_url)
    
    job = JobCreate(
        job_url=job_url,
        job_title=extracted_data["job_title"],
        job_description=extracted_data["job_description"],
        work_mode=extracted_data["work_mode"],
        company_name=extracted_data["company_name"], 
        location=extracted_data["location"],
        job_summary=extracted_data["job_summary"]
    )
    
    return createJob(db, job)
    

def preview_job_ingestion(job_url: str) -> dict:
    extracted_data = extract_job_data_from_url(job_url)
    
    return {
        "job_url": extracted_data["job_url"],
        "job_title": extracted_data["job_title"],
        "company_name": extracted_data["company_name"],
        "location": extracted_data["location"],
        "work_mode": extracted_data["work_mode"],
        "job_description_preview": extracted_data["job_description"][:500],
        "job_summary": extracted_data["job_summary"]
    }


def preview_job_ingestion_debug(job_url: str) -> dict:
    html_page = fetch_job_page(job_url)

    soup = parse_job_page(html_page)

    text = extract_text_from_page(soup)

    if not text or len(text) < 100:
        raise ValueError("Could not extract meaningful job content from the page.")

    title = extract_job_title(soup)
    work_mode = extract_work_mode(text)
    company_name = extract_company_name(soup)
    location = extract_location(soup, text)

    rule_based_data = {
        "job_url": job_url,
        "job_title": title,
        "company_name": company_name,
        "location": location,
        "work_mode": work_mode,
        "date_posted": None,
        "job_description": text,
    }

    ai_extracted_data = extract_job_data_with_AI(text)

    merged_data = merge_rule_based_and_ai_data(rule_based_data, ai_extracted_data)

    return {
        "rule_based_data": rule_based_data,
        "ai_extracted_data": ai_extracted_data.model_dump(),
        "merged_data": merged_data,
    }


# def push_ingestion_in_job_queue(job_url: str)