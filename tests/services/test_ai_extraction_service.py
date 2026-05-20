import pytest

from app.schemas.ingestion import AIJobExtractionResponse, JobSummary
from app.services.ai_extraction_service import merge_rule_based_and_ai_data, parse_llm_output


def test_parse_llm_output_success():
    llm_response = """
    {
        "company_name": "Acme",
        "job_title": "Backend Engineer",
        "location": "Pune",
        "date_posted": null,
        "job_summary": {
            "required_experience": "3+ years",
            "key_skills": ["Python", "FastAPI", "SQLAlchemy"]
        }
    }
    """

    result = parse_llm_output(llm_response)

    assert result.company_name == "Acme"
    assert result.job_title == "Backend Engineer"
    assert result.location == "Pune"
    assert result.date_posted is None
    assert result.job_summary is not None
    assert result.job_summary.required_experience == "3+ years"
    assert result.job_summary.key_skills == ["Python", "FastAPI", "SQLAlchemy"]


def test_parse_llm_output_raises_for_invalid_json():
    llm_response = "This is not valid JSON"

    with pytest.raises(ValueError):
        parse_llm_output(llm_response)
        

def test_merge_rule_based_and_ai_data_fills_missing_fields():
    rule_data = {
        "job_url": "https://example.com/job/123",
        "job_title": "Backend Engineer",
        "company_name": None,
        "location": None,
        "work_mode": "hybrid",
        "date_posted": None,
        "job_description": "Long extracted job text",
    }

    ai_data = AIJobExtractionResponse(
        company_name="Acme",
        job_title="Backend Engineer",
        location="Pune",
        date_posted=None,
        job_summary=JobSummary(
            required_experience= "3+ years",
            key_skills= ["Python", "FastAPI", "SQLAlchemy"]
        ),
    )

    result = merge_rule_based_and_ai_data(rule_data, ai_data)

    assert result["job_url"] == "https://example.com/job/123"
    assert result["job_title"] == "Backend Engineer"
    assert result["company_name"] == "Acme"
    assert result["location"] == "Pune"
    assert result["work_mode"] == "hybrid"
    assert result["job_description"] == "Long extracted job text"
    assert result["job_summary"].required_experience == "3+ years"
    assert result["job_summary"].key_skills == ["Python", "FastAPI", "SQLAlchemy"]


def test_merge_rule_based_and_ai_data_does_not_override_existing_fields():
    rule_data = {
        "job_url": "https://example.com/job/123",
        "job_title": "Backend Engineer",
        "company_name": "Rule Based Company",
        "location": "Bengaluru",
        "work_mode": "hybrid",
        "date_posted": None,
        "job_description": "Long extracted job text",
    }

    ai_data = AIJobExtractionResponse(
        company_name="AI Company",
        job_title="AI Backend Engineer",
        location="Pune",
        date_posted=None,
        job_summary=JobSummary(
            required_experience= "3+ years",
            key_skills= ["Python", "FastAPI", "SQLAlchemy"]
        ),
    )

    result = merge_rule_based_and_ai_data(rule_data, ai_data)

    assert result["job_title"] == "Backend Engineer"
    assert result["company_name"] == "Rule Based Company"
    assert result["location"] == "Bengaluru"
    assert result["work_mode"] == "hybrid"
    assert result["job_summary"].required_experience == "3+ years"
    assert result["job_summary"].key_skills == ["Python", "FastAPI", "SQLAlchemy"]
    

def test_parse_llm_output_handles_code_fenced_json():
    llm_response = """
    ```json
    {
        "company_name": "Acme",
        "job_title": "Backend Engineer",
        "location": "Pune",
        "date_posted": null,
        "job_summary": {
            "required_experience": "3+ years",
            "key_skills": ["Python", "FastAPI", "SQLAlchemy"]
        }
    }
    ```
    """

    result = parse_llm_output(llm_response)

    assert result.company_name == "Acme"
    assert result.job_title == "Backend Engineer"
    assert result.location == "Pune"
    assert result.date_posted is None
    assert result.job_summary.required_experience == "3+ years"
    assert result.job_summary.key_skills == ["Python", "FastAPI", "SQLAlchemy"]
    

def test_parse_llm_output_handles_extra_text_around_json():
    llm_response = """
    Here is text:
    ```json
    {
        "company_name": "Acme",
        "job_title": "Backend Engineer",
        "location": "Pune",
        "date_posted": null,
        "job_summary": {
            "required_experience": "3+ years",
            "key_skills": ["Python", "FastAPI", "SQLAlchemy"]
        }
    }
    ```
    """

    result = parse_llm_output(llm_response)

    assert result.company_name == "Acme"
    assert result.job_title == "Backend Engineer"
    assert result.location == "Pune"
    assert result.date_posted is None
    assert result.job_summary.required_experience == "3+ years"
    assert result.job_summary.key_skills == ["Python", "FastAPI", "SQLAlchemy"]