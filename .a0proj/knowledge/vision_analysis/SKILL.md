# Vision Analysis Skill

## Overview
Perform image analysis and vision tasks using OpenRouter API. Use this skill when you need to analyze UI mockups, screenshots, diagrams, or any visual content.

## Prerequisites

### Environment Setup
Ensure `OPENROUTER_API_KEY` is set in one of these locations:
- `/a0/usr/.env` (primary)
- `/a0/usr/projects/salon_flow/.a0proj/secrets.env`
- Environment variable: `export OPENROUTER_API_KEY="your_key"`

**Verify setup:**
```bash
env | grep OPENROUTER_API_KEY
```

## Quick Start

### Method 1: Using vision_load Tool (Preferred)
```json
{
  "tool_name": "vision_load",
  "tool_args": {
    "paths": ["/path/to/image.png"]
  }
}
```

**Note:** If you get "OPENROUTER_API_KEY environment variable not set" error, use Method 2.

### Method 2: Python Workaround (Reliable)
Use this Python script for reliable vision analysis:

```python
import base64
import requests
from pathlib import Path

def analyze_image(image_path: str, prompt: str = "Describe this image in detail.") -> str:
    """
    Analyze an image using OpenRouter vision API.
    
    Args:
        image_path: Absolute path to image file
        prompt: Analysis prompt/question
        
    Returns:
        Analysis text from the vision model
    """
    # API key (from environment or direct)
    api_key = "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"
    
    # Read and encode image
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Call OpenRouter API
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://salon-flow.com",
            "X-Title": "SalonFlow"
        },
        json={
            "model": "anthropic/claude-3.5-sonnet",  # Reliable vision model
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_data}"
                            }
                        }
                    ]
                }
            ]
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        return result['choices'][0]['message']['content']
    else:
        return f"Error: {response.status_code} - {response.text}"


# Example usage
if __name__ == "__main__":
    # Analyze a mockup
    result = analyze_image(
        "/a0/usr/projects/salon_flow/docs/mockups/01_onboarding_welcome_1.png",
        "Describe this UI mockup. What elements, layout, colors, and purpose does it have?"
    )
    print(result)
```

## Supported Models

| Model | Provider | Vision | Best For |
|-------|----------|--------|----------|
| `anthropic/claude-3.5-sonnet` | Anthropic | ✅ | General analysis, UI mockups |
| `google/gemini-2.0-flash-001` | Google | ✅ | Fast analysis, screenshots |
| `google/gemini-2.5-pro` | Google | ✅ | Detailed analysis |
| `qwen/qwen2.5-vl-72b-instruct` | Alibaba | ✅ | Specialized vision tasks |

## Common Use Cases

### 1. UI Mockup Analysis
```python
prompt = """
Analyze this UI mockup for Salon Flow:
1. What screen is this?
2. What UI elements are present?
3. What is the visual hierarchy?
4. Suggest improvements for accessibility
"""
```

### 2. Screenshot Comparison
```python
# Analyze before/after screenshots
def compare_screenshots(before_path: str, after_path: str) -> str:
    """Compare two screenshots and identify changes."""
    # Implementation that analyzes both images
    pass
```

### 3. Code from Image
```python
prompt = """
Extract any code visible in this image and provide it in a code block.
If it's a diagram, describe the architecture shown.
"""
```

### 4. Accessibility Audit
```python
prompt = """
Review this UI for accessibility issues:
- Color contrast
- Text size
- Interactive element sizing
- Screen reader compatibility
"""
```

## Batch Analysis

Analyze multiple images at once:

```python
import os
from pathlib import Path

def analyze_mockups_folder(folder_path: str, output_file: str = None):
    """Analyze all mockups in a folder."""
    folder = Path(folder_path)
    results = []
    
    for image_file in sorted(folder.glob("*.png")):
        print(f"Analyzing: {image_file.name}")
        
        analysis = analyze_image(
            str(image_file),
            f"Describe this Salon Flow UI screen: {image_file.stem}. "
            "What is its purpose, key elements, and user flow?"
        )
        
        results.append({
            "file": image_file.name,
            "analysis": analysis
        })
    
    # Save to file if specified
    if output_file:
        with open(output_file, 'w') as f:
            for r in results:
                f.write(f"\n## {r['file']}\n\n{r['analysis']}\n")
    
    return results

# Usage
results = analyze_mockups_folder(
    "/a0/usr/projects/salon_flow/docs/mockups",
    "/a0/usr/projects/salon_flow/docs/MOCKUP_ANALYSIS.md"
)
```

## Image Generation (Reverse)

Generate mockups from descriptions:

```python
def generate_image(prompt: str, output_path: str):
    """Generate image using OpenRouter image generation models."""
    api_key = "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"
    
    response = requests.post(
        "https://openrouter.ai/api/v1/images/generations",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "black-forest-labs/flux-schnell",
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024"
        }
    )
    
    # Download and save image
    image_url = response.json()['data'][0]['url']
    img_data = requests.get(image_url).content
    
    with open(output_path, 'wb') as f:
        f.write(img_data)
    
    return output_path

# Example
generate_image(
    "Modern mobile app UI for salon booking, clean minimalist design, "
    "white background, blue accents, calendar view, iOS style",
    "/a0/usr/projects/salon_flow/docs/mockups/generated.png"
)
```

## Best Practices

### ✅ Do
- Use absolute paths for images
- Include specific questions in prompts
- Handle API errors gracefully
- Cache results for repeated analysis
- Use appropriate models for the task

### ❌ Don't
- Send images > 10MB (resize first)
- Use vision for text-heavy documents (use OCR)
- Rely on vision for precise measurements
- Forget to handle API rate limits

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `OPENROUTER_API_KEY not set` | Set key in `/a0/usr/.env` or use Python workaround |
| `404 Model not found` | Use supported vision model from table above |
| `Image too large` | Resize image to < 10MB before sending |
| `Timeout` | Increase request timeout or use smaller image |
| `No content in response` | Check model supports vision; try different model |

## Integration with Other Tools

### With document_query
```python
# First analyze mockups, then query documentation
analysis = analyze_image("mockup.png")
document_query(
    document="requirements.md",
    queries=[f"Does this cover: {analysis}?"]
)
```

### With code_execution_tool
```python
# Use vision analysis to generate code
analysis = analyze_image("ui_mockup.png")
# Then implement based on analysis
code_execution_tool(runtime="python", code=generate_code(analysis))
```

## References

- OpenRouter Docs: https://openrouter.ai/docs
- Vision Models: https://openrouter.ai/models?supported_parameters=tools%2Cimage
- API Errors: https://openrouter.ai/docs/api-reference/errors
