class DocumentProcessor:
    """문서 처리 기본 인터페이스"""
    
    def process(self, file_path):
        """문서 처리 메서드"""
        raise NotImplementedError
    
    def extract_text(self, file_path):
        """문서에서 텍스트 추출"""
        raise NotImplementedError
