from openai import OpenAI

from app.config import OPENAI_API_KEY, SUMMARY_MODEL
from app.services.text.prompts import TextPrompts


class TextAnalyzer:
    """Text analysis class (extract important content, summarize)"""

    def __init__(self, model=SUMMARY_MODEL, api_key=OPENAI_API_KEY):
        self.model = model
        self.client = OpenAI(api_key=api_key)
        self.prompts = TextPrompts()

    def extract_important_content(self, text):
        """Extract important content"""
        print("Starting to extract important content...")

        prompt = self.prompts.get_important_content_prompt(text)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system",
                 "content": "You are an assistant that helps students analyze lecture content. Your role is to accurately extract important information from lecture transcripts."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        important_content = response.choices[0].message.content.strip()
        print("Important content extraction completed")
        return important_content

    def summarize_text(self, text):
        """Summarize text"""
        print("Starting to summarize transcript...")

        prompt = self.prompts.get_summary_prompt(text)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system",
                 "content": "You are an expert at clearly and concisely summarizing academic content. You maintain the core of the lecture content while excluding unnecessary details."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        summary = response.choices[0].message.content.strip()
        print("Transcript summarization completed")
        return summary
