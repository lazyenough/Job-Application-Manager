from app.schemas.ingestion import AIJobExtractionResponse


def extract_job_data_with_AI(job_text: str) -> AIJobExtractionResponse:
    prompt = build_AI_extraction_prompt(job_text)
    
    llm_response = call_llm(prompt)
    
    return parse_llm_output(llm_response)
    

def build_AI_extraction_prompt(job_text: str) -> str:
    return f"""
        You are extracting structured information from a job posting.

        Extract only the following fields:
        - company_name
        - job_title
        - location
        - date_posted
        - job_summary

        Rules:
        - If a field is not clearly present, return null.
        - Do not guess.
        - job_summary should be a short 2-3 sentence summary.
        - date_posted should be in YYYY-MM-DD format if available, otherwise null.
        - Return only a JSON object.
        - Do not include extra text, markdown, or explanation.

        Job posting text:
        {job_text}
    """.strip()


def call_llm(prompt: str):
    return {
        "job_title": "Backend Engineer",
        "job_summary": "This is a backend engineering role focused on API and service development."
    }


def parse_llm_output(llm_response) -> AIJobExtractionResponse:
    return AIJobExtractionResponse(**llm_response)


def merge_rule_based_and_ai_data(rule_data: dict, ai_data: AIJobExtractionResponse) -> dict:
    merged_data = rule_data.copy()

    if not merged_data.get("company_name") and ai_data.company_name:
        merged_data["company_name"] = ai_data.company_name

    if not merged_data.get("job_title") and ai_data.job_title:
        merged_data["job_title"] = ai_data.job_title

    if not merged_data.get("location") and ai_data.location:
        merged_data["location"] = ai_data.location

    if not merged_data.get("date_posted") and ai_data.date_posted:
        merged_data["date_posted"] = ai_data.date_posted

    if ai_data.job_summary:
        merged_data["job_summary"] = ai_data.job_summary

    return merged_data

