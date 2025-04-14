from openai import OpenAI

from app.config import OPENAI_API_KEY, SUMMARY_MODEL
from app.text.prompts import TextPrompts

class TextAnalyzer:
    """텍스트 분석 클래스 (중요 내용 추출, 요약)"""
    
    def __init__(self, model=SUMMARY_MODEL, api_key=OPENAI_API_KEY):
        self.model = model
        self.client = OpenAI(api_key=api_key)
        self.prompts = TextPrompts()
    
    def extract_important_content(self, text):
        """중요 내용 추출"""
        print("중요 내용 추출 시작...")
        
        prompt = self.prompts.get_important_content_prompt(text)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "당신은 학생들을 위한 강의 내용 분석 도우미입니다. 강의 대본에서 학업에 중요한 정보를 정확하게 추출하는 역할을 합니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        important_content = response.choices[0].message.content.strip()
        print("중요 내용 추출 완료")
        return important_content
    
    def summarize_text(self, text):
        """텍스트 요약"""
        print("대본 요약 시작...")
        
        prompt = self.prompts.get_summary_prompt(text)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "당신은 학술 내용을 명확하고 간결하게 요약하는 전문가입니다. 강의 내용의 핵심을 유지하면서 불필요한 세부사항은 제외하여 요약합니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        summary = response.choices[0].message.content.strip()
        print("대본 요약 완료")
        return summary
