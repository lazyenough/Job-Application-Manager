from bs4 import BeautifulSoup
import pytest

from app.services.ingestion_service import extract_company_name, extract_job_data_from_url, extract_job_title, extract_work_mode, extract_location


def test_extract_work_mode_remote():
    text = "This is a fully remote software engineering role."
    result = extract_work_mode(text)
    assert result == "remote"


def test_extract_work_mode_hybrid():
    text = "We are hiring for a hybrid backend developer position."
    result = extract_work_mode(text)
    assert result == "hybrid"


def test_extract_work_mode_no_match():
    text = "We are looking for a software engineer with strong Python skills."
    result = extract_work_mode(text)
    assert result is None
    
    
def test_extract_location_from_meta_tag():
    html = '<meta name="location" content="Bengaluru">'
    soup = BeautifulSoup(html, "lxml")

    result = extract_location(soup, "Some text")
    assert result == "Bengaluru"


def test_extract_location_from_text():
    soup = BeautifulSoup("<html></html>", "lxml")
    text = "This role is based in Pune and requires Python experience."

    result = extract_location(soup, text)
    assert result == "Pune"


def test_extract_location_no_match():
    soup = BeautifulSoup("<html></html>", "lxml")
    text = "We are looking for a backend engineer with strong API design skills."

    result = extract_location(soup, text)
    assert result is None

def test_extract_job_data_from_url_success(monkeypatch):
    def mock_fetch_job_page(job_url: str):
        return "<html><head><title>Mock Job</title></head><body>Mock page</body></html>"

    def mock_parse_job_page(html: str):
        return BeautifulSoup("<html></html>", "lxml")

    def mock_extract_text_from_page(soup):
        return "This is a hybrid backend engineering role based in Pune." * 5

    def mock_extract_job_title(soup):
        return "Backend Engineer"

    def mock_extract_work_mode(text: str):
        return "hybrid"

    def mock_extract_company_name(soup):
        return "Acme"

    def mock_extract_location(soup, text: str):
        return "Pune"

    monkeypatch.setattr(
        "app.services.ingestion_service.fetch_job_page",
        mock_fetch_job_page,
    )
    monkeypatch.setattr(
        "app.services.ingestion_service.parse_job_page",
        mock_parse_job_page,
    )
    monkeypatch.setattr(
        "app.services.ingestion_service.extract_text_from_page",
        mock_extract_text_from_page,
    )
    monkeypatch.setattr(
        "app.services.ingestion_service.extract_job_title",
        mock_extract_job_title,
    )
    monkeypatch.setattr(
        "app.services.ingestion_service.extract_work_mode",
        mock_extract_work_mode,
    )
    monkeypatch.setattr(
        "app.services.ingestion_service.extract_company_name",
        mock_extract_company_name,
    )
    monkeypatch.setattr(
        "app.services.ingestion_service.extract_location",
        mock_extract_location,
    )

    result = extract_job_data_from_url("https://example.com/job/123")

    assert result["job_url"] == "https://example.com/job/123"
    assert result["job_title"] == "Backend Engineer"
    assert result["company_name"] == "Acme"
    assert result["location"] == "Pune"
    assert result["work_mode"] == "hybrid"
    assert "hybrid backend engineering role" in result["job_description"].lower()



def test_extract_job_data_from_url_failure(monkeypatch):
    def mock_fetch_job_page(job_url: str):
        return "<html><head><title>Mock Job</title></head><body>Mock page</body></html>"

    def mock_parse_job_page(html: str):
        return BeautifulSoup("<html></html>", "lxml")

    def mock_extract_text_from_page(soup):
        return "Too Short"

    monkeypatch.setattr(
        "app.services.ingestion_service.fetch_job_page",
        mock_fetch_job_page,
    )
    monkeypatch.setattr(
        "app.services.ingestion_service.parse_job_page",
        mock_parse_job_page,
    )
    monkeypatch.setattr(
        "app.services.ingestion_service.extract_text_from_page",
        mock_extract_text_from_page,
    )

    with pytest.raises(ValueError, match="Could not extract meaningful job content from the page."):
        extract_job_data_from_url("https://example.com/job/123")
        

def test_extract_company_name_from_og_site_name():
    html = '<meta property="og:site_name" content="Acme Corp">'
    soup = BeautifulSoup(html, "lxml")

    result = extract_company_name(soup)

    assert result == "Acme Corp"


def test_extract_company_name_from_application_name():
    html = '<meta name="application-name" content="TurboHire">'
    soup = BeautifulSoup(html, "lxml")

    result = extract_company_name(soup)

    assert result == "TurboHire"


def test_extract_company_name_returns_none_when_missing():
    soup = BeautifulSoup("<html><body><p>No company metadata</p></body></html>", "lxml")

    result = extract_company_name(soup)

    assert result is None


def test_extract_job_title_from_title_tag():
    soup = BeautifulSoup(
        "<html><head><title>Backend Engineer</title></head><body></body></html>",
        "lxml",
    )

    result = extract_job_title(soup)

    assert result == "Backend Engineer"


def test_extract_job_title_from_h1_tag():
    soup = BeautifulSoup("<html><body><h1>Analyst</h1></body></html>", "lxml")
    
    result = extract_job_title(soup)
    
    assert result == "Analyst"


def test_extract_job_title_return_none_when_missing():
    soup = BeautifulSoup("<html><body><p>Analyst</p></body></html>", "lxml")
    
    result = extract_job_title(soup)
    
    assert result == None