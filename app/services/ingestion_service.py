import requests

from bs4 import BeautifulSoup

from app.schemas.job import JobCreate, JobResponse
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


def extract_location(soup: BeautifulSoup) -> str | None:
    pass


def extract_work_mode(text: str) -> str | None:
    lower_text = text.lower()

    if "hybrid" in lower_text:
        return "hybrid"
    if "remote" in lower_text:
        return "remote"
    if "onsite" in lower_text or "on-site" in lower_text or "wfo" in lower_text or "work from office" in lower_text:
        return "onsite"

    return None


def ingest_job_url(db, job_url: str) -> JobResponse:
    existing_job = get_job_by_url(db, job_url)
    if existing_job:
        return existing_job
    
    html_page = fetch_job_page(job_url)
    
    soup = parse_job_page(html_page)
    
    text = extract_text_from_page(soup)
    
    title = extract_job_title(soup)
    work_mode = extract_work_mode(text)
    company_name = extract_company_name(soup)
    
    job = JobCreate(
        job_url=job_url,
        job_title=title,
        job_description=text,
        work_mode=work_mode,
        company_name=company_name
    )
    
    return createJob(db, job)
    