class TextPrompts:
    """Class for managing text analysis prompts"""

    def get_important_content_prompt(self, text):
        """Prompt for extracting important content"""
        return f"""
        다음은 강의 대본입니다. 이 대본에서 다음과 같은 중요한 내용을 추출해주세요:

        1. 시험 관련 정보 (시험 날짜, 범위, 형식, 주의사항 등)
        2. 과제 관련 정보 (제출 기한, 형식, 주제, 요구사항 등)
        3. 중요한 공지사항이나 특이사항
        4. 교수가 특별히 강조한 개념이나 내용
        5. 수업 참여나 출석에 관한 중요 정보

        각 항목별로 정리하고, 해당 내용이 없으면 '해당 정보 없음'이라고 표시해주세요.
        정보를 추출할 때 가능한 원문의 표현을 유지하고, 시간 정보나 구체적인 지시사항이 있다면 반드시 포함해주세요.

        강의 대본:
        {text}
        """

    def get_summary_prompt(self, text):
        """Prompt for summarizing content"""
        return f"""
        다음은 강의 대본입니다. 이 대본의 주요 내용을 간결하게 요약해주세요.
        요약은 다음 형식을 따라주세요:

        1. 강의 주제 및 목표
        2. 주요 논의 내용 (핵심 개념, 이론, 사례 등)
        3. 결론 및 핵심 메시지

        요약은 원래 내용의 10~15% 정도 분량으로 작성하고, 중요한 용어나 개념은 그대로 유지해주세요.

        강의 대본:
        {text}
        """
