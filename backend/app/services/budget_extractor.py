"""
Budget extraction and matching service.

Uses Claude to extract line items from capital budget PDFs
and performs semantic matching to RFP scopes.
"""
import os
import json
import re
import anthropic
from dataclasses import dataclass, field
from typing import Optional, List, Any
from difflib import SequenceMatcher


@dataclass
class BudgetExtractionResult:
    """Result of budget line item extraction."""
    success: bool
    items: List[dict] = field(default_factory=list)
    error: Optional[str] = None
    input_tokens: int = 0
    output_tokens: int = 0


BUDGET_EXTRACTION_PROMPT = """You are an expert at analyzing municipal capital budgets. Extract project line items from the following budget document.

<budget_document>
{budget_text}
</budget_document>

Municipality: {municipality}

Extract each capital project/line item you find. For each project, provide:
- project_name: The name of the project
- project_id: Any project code/ID if present
- department: The department or service area
- total_budget: Total approved budget in dollars (number only, no commas)
- current_year_budget: Budget for current fiscal year if shown
- funding_type: Type of work (Planning, Design, Engineering, Construction, etc.)
- description: Brief description of the project
- source_page: Page number where you found this

Return valid JSON array:
[
  {{
    "project_name": "string",
    "project_id": "string or null",
    "department": "string or null",
    "total_budget": number or null,
    "current_year_budget": number or null,
    "funding_type": "string or null",
    "description": "string",
    "source_page": number or null
  }}
]

Focus on infrastructure, engineering, and construction projects. Look for:
- Road reconstruction/rehabilitation
- Water/sewer infrastructure
- Bridge repairs
- Transit projects
- Facility improvements
- Environmental projects

Return only the JSON array, no other text."""


def extract_budget_items(budget_text: str, municipality: str, max_chars: int = 100000) -> BudgetExtractionResult:
    """
    Extract budget line items using Claude.
    
    Args:
        budget_text: Full text from the budget PDF
        municipality: Name of the municipality
        max_chars: Maximum characters to send to Claude
    
    Returns:
        BudgetExtractionResult with extracted items
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return BudgetExtractionResult(success=False, error="ANTHROPIC_API_KEY not set")

    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        # Truncate if needed
        if len(budget_text) > max_chars:
            budget_text = budget_text[:max_chars] + "\n\n[DOCUMENT TRUNCATED]"
        
        prompt = BUDGET_EXTRACTION_PROMPT.format(
            budget_text=budget_text,
            municipality=municipality,
        )
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8192,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text
        
        # Parse JSON
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]
        
        items = json.loads(response_text.strip())
        
        return BudgetExtractionResult(
            success=True,
            items=items,
            input_tokens=message.usage.input_tokens,
            output_tokens=message.usage.output_tokens,
        )
        
    except json.JSONDecodeError as e:
        return BudgetExtractionResult(success=False, error=f"Failed to parse response: {e}")
    except anthropic.APIError as e:
        return BudgetExtractionResult(success=False, error=f"Claude API error: {e}")
    except Exception as e:
        return BudgetExtractionResult(success=False, error=f"Extraction failed: {e}")


def calculate_text_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two texts using SequenceMatcher."""
    if not text1 or not text2:
        return 0.0
    
    # Normalize texts
    text1 = text1.lower().strip()
    text2 = text2.lower().strip()
    
    return SequenceMatcher(None, text1, text2).ratio()


def extract_keywords(text: str) -> set:
    """Extract meaningful keywords from text."""
    if not text:
        return set()
    
    # Common infrastructure keywords
    infra_keywords = {
        'road', 'street', 'highway', 'bridge', 'culvert', 
        'water', 'sewer', 'storm', 'drainage', 'sanitary',
        'reconstruction', 'rehabilitation', 'replacement', 'repair',
        'design', 'engineering', 'construction', 'planning',
        'transit', 'bus', 'rail', 'station',
        'facility', 'building', 'park', 'trail',
        'intersection', 'signal', 'traffic', 'sidewalk',
        'line', 'main', 'pipe', 'infrastructure',
    }
    
    # Extract words
    words = set(re.findall(r'\b[a-z]+\b', text.lower()))
    
    # Return intersection with infrastructure keywords + any proper nouns (capitalized words)
    proper_nouns = set(re.findall(r'\b[A-Z][a-z]+\b', text))
    
    return (words & infra_keywords) | {w.lower() for w in proper_nouns}


def match_rfp_to_budget(
    rfp_scope: str,
    rfp_client: str,
    rfp_title: str,
    budget_items: List[Any],
) -> List[dict]:
    """
    Match an RFP to budget line items using keyword and semantic matching.
    
    Args:
        rfp_scope: RFP scope summary
        rfp_client: Client name from RFP
        rfp_title: RFP title
        budget_items: List of BudgetLineItem objects
    
    Returns:
        List of matches sorted by confidence
    """
    matches = []
    
    # Extract keywords from RFP
    rfp_text = f"{rfp_title} {rfp_scope}"
    rfp_keywords = extract_keywords(rfp_text)
    
    for item in budget_items:
        # Build item text for matching
        item_text = f"{item.project_name} {item.description or ''}"
        item_keywords = extract_keywords(item_text)
        
        # Calculate keyword overlap
        if rfp_keywords and item_keywords:
            keyword_overlap = len(rfp_keywords & item_keywords) / max(len(rfp_keywords), 1)
        else:
            keyword_overlap = 0
        
        # Calculate text similarity
        text_sim = calculate_text_similarity(rfp_scope, item.description or "")
        
        # Calculate title similarity
        title_sim = calculate_text_similarity(rfp_title, item.project_name)
        
        # Combined confidence score
        confidence = (keyword_overlap * 0.4) + (text_sim * 0.3) + (title_sim * 0.3)
        
        # Generate match reason
        common_keywords = rfp_keywords & item_keywords
        if common_keywords:
            reason = f"Matching keywords: {', '.join(list(common_keywords)[:5])}"
        elif text_sim > 0.3:
            reason = "Similar project description"
        elif title_sim > 0.3:
            reason = "Similar project name"
        else:
            reason = "Partial match"
        
        if confidence > 0.1:  # Minimum threshold
            matches.append({
                "item": item,
                "confidence": round(confidence, 3),
                "reason": reason,
            })
    
    # Sort by confidence descending
    matches.sort(key=lambda x: x["confidence"], reverse=True)
    
    return matches
