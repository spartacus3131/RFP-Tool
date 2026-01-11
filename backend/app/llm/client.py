"""
Claude API client for RFP extraction.
"""
import os
import json
import anthropic
from dataclasses import dataclass
from typing import Optional, Any

from .prompts import build_extraction_prompt, build_contradiction_prompt


@dataclass
class ExtractionResult:
    """Result from Claude extraction."""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    input_tokens: int = 0
    output_tokens: int = 0


def get_client() -> anthropic.Anthropic:
    """Get Anthropic client with API key from environment."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    return anthropic.Anthropic(api_key=api_key)


def extract_rfp_fields(rfp_text: str, model: str = "claude-sonnet-4-20250514") -> ExtractionResult:
    """
    Extract structured fields from RFP text using Claude.
    
    Args:
        rfp_text: Full text extracted from the RFP PDF
        model: Claude model to use (sonnet for speed/cost, opus for accuracy)
    
    Returns:
        ExtractionResult with extracted data or error
    """
    try:
        client = get_client()
        system_prompt, user_prompt = build_extraction_prompt(rfp_text)
        
        message = client.messages.create(
            model=model,
            max_tokens=8192,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        # Extract the response text
        response_text = message.content[0].text
        
        # Parse JSON from response
        # Handle potential markdown code blocks
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]
        
        data = json.loads(response_text.strip())
        
        return ExtractionResult(
            success=True,
            data=data,
            input_tokens=message.usage.input_tokens,
            output_tokens=message.usage.output_tokens,
        )
        
    except json.JSONDecodeError as e:
        return ExtractionResult(
            success=False,
            error=f"Failed to parse Claude response as JSON: {str(e)}",
        )
    except anthropic.APIError as e:
        return ExtractionResult(
            success=False,
            error=f"Claude API error: {str(e)}",
        )
    except Exception as e:
        return ExtractionResult(
            success=False,
            error=f"Extraction failed: {str(e)}",
        )


def parse_extraction_to_fields(extraction_data: dict) -> dict:
    """
    Convert Claude extraction format to flat fields for database storage.
    
    Args:
        extraction_data: Raw extraction data from Claude
    
    Returns:
        Dict with flattened field values
    """
    fields = {}
    
    # Simple string fields
    simple_fields = [
        "client_name", "rfp_number", "opportunity_title", 
        "published_date", "question_deadline", "submission_deadline",
        "contract_duration", "scope_summary"
    ]
    
    for field in simple_fields:
        if field in extraction_data and extraction_data[field].get("value"):
            fields[field] = extraction_data[field]["value"]
    
    # Array fields
    if "required_internal_disciplines" in extraction_data:
        val = extraction_data["required_internal_disciplines"].get("value")
        if val:
            fields["required_internal_disciplines"] = val
    
    if "required_external_disciplines" in extraction_data:
        val = extraction_data["required_external_disciplines"].get("value")
        if val:
            fields["required_external_disciplines"] = val
    
    if "risk_flags" in extraction_data:
        val = extraction_data["risk_flags"].get("value")
        if val:
            fields["risk_flags"] = val
    
    # JSON fields
    if "client_contact" in extraction_data:
        val = extraction_data["client_contact"].get("value")
        if val:
            fields["client_contact_name"] = val.get("name")
            fields["client_contact_email"] = val.get("email")
            fields["client_contact_phone"] = val.get("phone")
    
    if "evaluation_criteria" in extraction_data:
        fields["evaluation_criteria"] = extraction_data["evaluation_criteria"].get("value")
    
    if "reference_requirements" in extraction_data:
        fields["reference_requirements"] = extraction_data["reference_requirements"].get("value")
    
    if "insurance_requirements" in extraction_data:
        fields["insurance_requirements"] = extraction_data["insurance_requirements"].get("value")

    return fields


@dataclass
class ContradictionResult:
    """Result from Claude contradiction detection."""
    success: bool
    contradictions: list = None
    error: Optional[str] = None
    input_tokens: int = 0
    output_tokens: int = 0

    def __post_init__(self):
        if self.contradictions is None:
            self.contradictions = []


def detect_contradictions(rfp_text: str, model: str = "claude-sonnet-4-20250514") -> ContradictionResult:
    """
    Detect contradictions and inconsistencies in RFP text using Claude.

    Args:
        rfp_text: Full text extracted from the RFP PDF
        model: Claude model to use

    Returns:
        ContradictionResult with list of detected contradictions or error
    """
    try:
        client = get_client()
        system_prompt, user_prompt = build_contradiction_prompt(rfp_text)

        message = client.messages.create(
            model=model,
            max_tokens=8192,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )

        # Extract the response text
        response_text = message.content[0].text

        # Parse JSON from response
        # Handle potential markdown code blocks
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        data = json.loads(response_text.strip())
        contradictions = data.get("contradictions", [])

        return ContradictionResult(
            success=True,
            contradictions=contradictions,
            input_tokens=message.usage.input_tokens,
            output_tokens=message.usage.output_tokens,
        )

    except json.JSONDecodeError as e:
        return ContradictionResult(
            success=False,
            error=f"Failed to parse Claude response as JSON: {str(e)}",
        )
    except anthropic.APIError as e:
        return ContradictionResult(
            success=False,
            error=f"Claude API error: {str(e)}",
        )
    except Exception as e:
        return ContradictionResult(
            success=False,
            error=f"Contradiction detection failed: {str(e)}",
        )
