import os
import logging
from typing import Optional, Dict, Any
from openai import OpenAI
import httpx


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ORG = os.getenv("OPENAI_ORG") or os.getenv("OPENAI_ORG_ID")
OPENAI_PROJECT = os.getenv("OPENAI_PROJECT")
IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")
IMAGE_SIZE = os.getenv("OPENAI_IMAGE_SIZE", "512x512")


def can_generate_images() -> bool:
    return bool(OPENAI_API_KEY)


def try_generate_mermaid_diagram(prompt: str) -> Optional[Dict[str, Any]]:
    """Generate a Mermaid diagram syntax for the prompt.
    Returns a spec with mermaid code."""
    if not OPENAI_API_KEY:
        return None

    http_client = None
    try:
        # Create OpenAI client with custom httpx client that has no proxy
        http_client = httpx.Client(proxy=None, transport=httpx.HTTPTransport(retries=0))
        client = OpenAI(api_key=OPENAI_API_KEY, http_client=http_client)
        # Create a specific prompt for Mermaid generation
        mermaid_prompt = f"""Generate a Mermaid.js diagram for: {prompt}

Create a clear, structured diagram using Mermaid syntax. Choose the most appropriate diagram type:
- flowchart TD/LR for processes, hierarchies, conceptual relationships
- sequenceDiagram for timelines, events, interactions
- graph TD/LR for networks, connections

CRITICAL SYNTAX RULES:
1. Use SIMPLE node IDs without special characters (use: A, B, C1, Node1, etc.)
2. Node labels must be in quotes or brackets: A["Label Text"] or A[Label Text]
3. Do NOT use parentheses () or special chars in node IDs
4. Connection syntax: A --> B or A -->|label| B
5. Keep labels SHORT and simple (max 3-4 words per node)
6. Use alphanumeric node IDs only (A-Z, 0-9, underscore)

Example of CORRECT syntax:
flowchart TD
    A["Artificial Intelligence"] --> B["Machine Learning"]
    B --> C["Deep Learning"]

Guidelines:
- Maximum 12 nodes for clarity
- Keep it minimal and elegant
- Test syntax validity

Return ONLY the valid Mermaid syntax, no explanation, no markdown code blocks."""

        # Use gpt-4o-mini for Mermaid generation (more reliable than gpt-5)
        model = "gpt-4o-mini"
        print(f"[MERMAID] Using model: {model}")

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a Mermaid.js diagram expert. Generate clean, minimal, elegant diagrams."},
                {"role": "user", "content": mermaid_prompt}
            ],
            max_tokens=2000,  # Use max_tokens instead of max_completion_tokens for compatibility
            temperature=0.7,
        )

        print(f"[MERMAID] Response choices: {response.choices}")
        print(f"[MERMAID] Message content: {response.choices[0].message.content}")
        print(f"[MERMAID] Finish reason: {response.choices[0].finish_reason}")

        mermaid_code = response.choices[0].message.content or ""
        mermaid_code = mermaid_code.strip()

        # Clean up the code - remove markdown code blocks if present
        if mermaid_code.startswith("```"):
            lines = mermaid_code.split("\n")
            mermaid_code = "\n".join(lines[1:-1]) if len(lines) > 2 else mermaid_code

        mermaid_code = mermaid_code.strip()

        # Additional cleanup for common syntax issues
        # Remove any remaining ```mermaid or ``` markers
        mermaid_code = mermaid_code.replace("```mermaid", "").replace("```", "").strip()

        # Fix common issues with parentheses in node IDs (convert to brackets)
        # This is a simple heuristic - replace (text) with [text] after -->
        import re
        # Fix pattern like: NodeID(Label) to NodeID["Label"]
        mermaid_code = re.sub(r'(\w+)\(([^)]+)\)', r'\1["\2"]', mermaid_code)

        print(f"[MERMAID FINAL] Returning mermaidCode with length: {len(mermaid_code)}")
        if len(mermaid_code) == 0:
            print("[MERMAID FINAL] WARNING: mermaidCode is EMPTY!")

        return {
            "visualType": "mermaid",
            "mermaidCode": mermaid_code,
            "elements": []  # Empty elements array for compatibility
        }

    except Exception as e:
        logging.getLogger("llm").warning("Mermaid generation error: %s", e, exc_info=True)
        return None
    finally:
        if http_client:
            http_client.close()


def try_generate_image_spec(prompt: str) -> Optional[Dict[str, Any]]:
    """Attempt to generate an image for the prompt and return a spec with an image element.
    Returns None if not possible (no key or API error)."""
    if not can_generate_images():
        return None

    http_client = None
    try:
        # Create OpenAI client with custom httpx client that has no proxy
        http_client = httpx.Client(proxy=None, transport=httpx.HTTPTransport(retries=0))
        client = OpenAI(api_key=OPENAI_API_KEY, http_client=http_client)
        models_to_try = [IMAGE_MODEL]
        # Fallback to another model name if the primary fails
        if IMAGE_MODEL != "dall-e-3":
            models_to_try.append("dall-e-3")
        # Enhance prompt for better educational diagrams
        enhanced_prompt = f"Create a clear, professional educational diagram to {prompt}. Include labels, arrows, and visual elements. Style: clean infographic with good contrast and readability. Educational and informative."

        for model in models_to_try:
            try:
                res = client.images.generate(
                    model=model,
                    prompt=enhanced_prompt,
                    size=IMAGE_SIZE,
                    response_format="b64_json",
                )
                b64 = res.data[0].b64_json
                if not b64:
                    continue
                data_url = f"data:image/png;base64,{b64}"
                return {
                    "elements": [
                        {
                            "type": "image",
                            "x": 100,
                            "y": 60,
                            "width": 512,
                            "height": 512,
                            "src": data_url,
                        }
                    ]
                }
            except Exception as inner:
                logging.getLogger("llm").warning("Image gen failed with %s: %s", model, inner)
        return None
    except Exception as e:
        logging.getLogger("llm").warning("Image gen client error: %s", e, exc_info=True)
        return None
    finally:
        if http_client:
            http_client.close()
