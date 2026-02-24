#!/usr/bin/env python3
"""
Vision Analysis Module for Agent Zero
Replaces broken vision_load tool with direct OpenRouter API integration
"""

import base64
import requests
import os
from pathlib import Path
from typing import List, Union

class VisionAnalyzer:
    """Analyze images using OpenRouter vision API"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get('OPENROUTER_API_KEY') or                       "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"
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    def encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')

    def analyze(
        self, 
        image_paths: Union[str, List[str]], 
        prompt: str = "Describe this image in detail.",
        model: str = "anthropic/claude-3.5-sonnet"
    ) -> Union[str, List[str]]:
        """
        Analyze one or more images

        Args:
            image_paths: Single path or list of paths
            prompt: Analysis prompt
            model: Vision model to use

        Returns:
            Analysis text(s)
        """
        if isinstance(image_paths, str):
            image_paths = [image_paths]

        results = []
        for path in image_paths:
            image_data = self.encode_image(path)

            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://salon-flow.com",
                    "X-Title": "SalonFlow"
                },
                json={
                    "model": model,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/png;base64,{image_data}"}
                                }
                            ]
                        }
                    ]
                }
            )

            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                results.append(content)
            else:
                results.append(f"Error: {response.status_code} - {response.text}")

        return results[0] if len(results) == 1 else results

    def analyze_mockup(self, image_path: str) -> dict:
        """Specialized analysis for UI mockups"""
        prompt = """Analyze this UI mockup for Salon Flow. Provide:
        1. Screen name/purpose
        2. Key UI elements
        3. Layout structure
        4. Color scheme
        5. User flow implications"""

        analysis = self.analyze(image_path, prompt)
        return {
            "file": Path(image_path).name,
            "analysis": analysis
        }

    def batch_analyze(self, folder_path: str, output_file: str = None) -> List[dict]:
        """Analyze all images in a folder"""
        folder = Path(folder_path)
        results = []

        for image_file in sorted(folder.glob("*.png")):
            print(f"Analyzing: {image_file.name}")
            result = self.analyze_mockup(str(image_file))
            results.append(result)

        if output_file:
            with open(output_file, 'w') as f:
                for r in results:
                    f.write(f"\n## {r['file']}\n\n{r['analysis']}\n")

        return results


def vision_load(paths: Union[str, List[str]], prompt: str = None) -> str:
    """
    Drop-in replacement for vision_load tool

    Args:
        paths: Image path(s) to analyze
        prompt: Optional custom prompt

    Returns:
        Analysis text
    """
    analyzer = VisionAnalyzer()
    default_prompt = prompt or "Describe this image in detail. What do you see?"

    if isinstance(paths, str):
        paths = [paths]

    results = []
    for path in paths:
        result = analyzer.analyze(path, default_prompt)
        results.append(f"**{Path(path).name}**:\n{result}")

    return "\n\n---\n\n".join(results)


# CLI usage
if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Analyze images with vision AI")
    parser.add_argument("paths", nargs="+", help="Image paths to analyze")
    parser.add_argument("--prompt", "-p", default="Describe this image in detail.", 
                       help="Analysis prompt")
    parser.add_argument("--output", "-o", help="Output file for results")

    args = parser.parse_args()

    analyzer = VisionAnalyzer()

    if len(args.paths) == 1:
        result = analyzer.analyze(args.paths[0], args.prompt)
        print(result)
    else:
        results = analyzer.batch_analyze(os.path.dirname(args.paths[0]), args.output)
        for r in results:
            print(f"\n## {r['file']}\n{r['analysis'][:200]}...")
