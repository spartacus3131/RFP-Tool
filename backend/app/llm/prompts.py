"""
Structured extraction prompts for RFP analysis using Claude.
"""

EXTRACTION_SYSTEM_PROMPT = """You are an expert RFP analyst for consulting firms in Canada's AEC (Architecture, Engineering, Construction) sector. Your job is to extract structured data from RFP documents with high accuracy.

CRITICAL REQUIREMENTS:
1. Extract ONLY information explicitly stated in the document
2. For every extracted field, provide the source page number
3. If information is not found, use null - never guess
4. Dates should be in ISO format (YYYY-MM-DD) when possible
5. Be precise with client names - use official entity names

You will receive RFP text with page markers like "--- PAGE X ---". Use these to track source pages."""

EXTRACTION_USER_PROMPT = """Analyze the following RFP document and extract structured data.

<rfp_document>
{rfp_text}
</rfp_document>

Extract the following fields. For each field, provide:
- The extracted value
- The source page number where you found this information
- A brief quote from the source text (max 100 chars)

Respond with valid JSON in this exact format:
{{
  "client_name": {{
    "value": "string or null",
    "source_page": number or null,
    "source_text": "brief quote or null"
  }},
  "rfp_number": {{
    "value": "string or null",
    "source_page": number or null,
    "source_text": "brief quote or null"
  }},
  "opportunity_title": {{
    "value": "string or null",
    "source_page": number or null,
    "source_text": "brief quote or null"
  }},
  "client_contact": {{
    "value": {{
      "name": "string or null",
      "email": "string or null",
      "phone": "string or null",
      "role": "string or null"
    }},
    "source_page": number or null,
    "source_text": "brief quote or null"
  }},
  "published_date": {{
    "value": "YYYY-MM-DD or null",
    "source_page": number or null,
    "source_text": "brief quote or null"
  }},
  "question_deadline": {{
    "value": "YYYY-MM-DD HH:MM or null",
    "source_page": number or null,
    "source_text": "brief quote or null"
  }},
  "submission_deadline": {{
    "value": "YYYY-MM-DD HH:MM or null",
    "source_page": number or null,
    "source_text": "brief quote or null"
  }},
  "contract_duration": {{
    "value": "string or null",
    "source_page": number or null,
    "source_text": "brief quote or null"
  }},
  "scope_summary": {{
    "value": "2-3 sentence summary of project scope",
    "source_page": number or null,
    "source_text": "brief quote or null"
  }},
  "required_internal_disciplines": {{
    "value": ["list of disciplines the firm needs internally"],
    "source_page": number or null,
    "source_text": "brief quote or null"
  }},
  "required_external_disciplines": {{
    "value": ["list of sub-consultant disciplines needed"],
    "source_page": number or null,
    "source_text": "brief quote or null"
  }},
  "evaluation_criteria": {{
    "value": {{
      "technical_weight": number or null,
      "financial_weight": number or null,
      "criteria": ["list of evaluation factors"]
    }},
    "source_page": number or null,
    "source_text": "brief quote or null"
  }},
  "reference_requirements": {{
    "value": {{
      "corporate_references": number or null,
      "team_references": number or null,
      "recency_years": number or null,
      "notes": "string or null"
    }},
    "source_page": number or null,
    "source_text": "brief quote or null"
  }},
  "insurance_requirements": {{
    "value": {{
      "professional_liability": "string or null",
      "general_liability": "string or null",
      "other": "string or null"
    }},
    "source_page": number or null,
    "source_text": "brief quote or null"
  }},
  "risk_flags": {{
    "value": ["list of any concerning terms, unusual requirements, or red flags"],
    "source_page": number or null,
    "source_text": "brief quote or null"
  }}
}}

Important:
- For disciplines, distinguish between work the firm would do internally vs. sub-consultants
- Common external disciplines in AEC: Geotechnical, Survey, Archaeological, Environmental, Traffic, Structural
- Look for evaluation weightings like "80% technical / 20% price"
- Flag unusual insurance amounts, bonding requirements, or payment terms as risk flags"""


def build_extraction_prompt(rfp_text: str, max_chars: int = 150000) -> tuple[str, str]:
    """
    Build the extraction prompt with the RFP text.
    
    Args:
        rfp_text: Full text extracted from the RFP PDF
        max_chars: Maximum characters to include (Claude has ~200K context)
    
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    # Truncate if needed (leave room for response)
    if len(rfp_text) > max_chars:
        rfp_text = rfp_text[:max_chars] + "\n\n[DOCUMENT TRUNCATED - First {} characters shown]".format(max_chars)
    
    user_prompt = EXTRACTION_USER_PROMPT.format(rfp_text=rfp_text)
    
    return EXTRACTION_SYSTEM_PROMPT, user_prompt
