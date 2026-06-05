from kiwipiepy import Kiwi
from typing import List, Dict, Any

class KoreanExtractor:
    """
    Extracts Korean Named Entities (PERSON and ORG) from text using morphological
    analysis (kiwipiepy) and rule-based heuristics to filter out locations and general nouns.
    """
    def __init__(self):
        # Initialize Kiwi analyzer. It loads wiki/namuwiki default dicts containing many proper nouns.
        self.kiwi = Kiwi()

        # Common Korean surnames
        self.korean_surnames = {
            "김", "이", "박", "최", "정", "강", "조", "윤", "장", "임", "한", "오", "서", "신", "권", "황", "안", "송", 
            "전", "홍", "유", "고", "문", "양", "손", "배", "백", "허", "남", "심", "노", "하", "곽", "성", "차", "주", 
            "우", "구", "민", "유", "류", "진", "지", "엄", "채", "원", "천", "방", "공", "현", "함", "변", "염", "여", 
            "추", "도", "소", "석", "선", "설", "마", "길", "연", "표", "기", "명", "반", "왕", "금", "옥", "육", "인", 
            "맹", "제", "탁", "국", "어", "은", "편", "남궁", "독고", "황보", "제갈", "사공"
        }

        # Common suffixes/indicators of an organization (ORG)
        self.org_suffixes = (
            "회사", "주식회사", "연구소", "대학", "대학교", "병원", "은행", "그룹", "공사", "협회", "재단", 
            "센터", "학회", "정부", "부처", "위원회", "코리아", "네트웍스", "솔루션", "홀딩스", "인터내셔널", 
            "제약", "금융", "항공", "호텔", "백화점", "연구원", "학교", "초등학교", "중학교", "고등학교",
            "연구회", "학원", "언론사", "방송사", "방송", "의료원", "공단", "서", "청", "부", "처",
            "전자", "자동차", "중공업", "화학", "생명", "화재", "카드", "증권", "투자", "정보", "미디어", 
            "통신", "제철"
        )

        # Top Korean and multinational organizations that may not have standard suffixes
        self.known_orgs = {
            "구글", "네이버", "카카오", "애플", "마이크로소프트", "메타", "삼성", "현대", "LG", "SK", 
            "한화", "롯데", "테슬라", "넷플릭스", "아마존", "오픈AI", "쿠팡", "배달의민족", "토스"
        }

        # Common suffixes for locations (LOC/GPE) to filter them out of redacting
        self.loc_suffixes = (
            "시", "도", "구", "동", "읍", "면", "리", "길", "로", "국", "주"
        )

        # Well-known country and city names
        self.countries_and_cities = {
            "한국", "대한민국", "미국", "중국", "일본", "영국", "프랑스", "독일", "러시아", "캐나다", "호주", 
            "이탈리아", "스페인", "브라질", "인도", "베트남", "태국", "필리핀", "싱가포르", "말레이시아",
            "서울", "부산", "인천", "대구", "대전", "광주", "울산", "세종", "경기도", "강원도", "충청도", 
            "전라도", "경상도", "제주도", "뉴욕", "런던", "파리", "도쿄", "베이징", "시드니", "워싱턴", 
            "로스앤젤레스", "샌프란시스코", "시카고", "보스턴", "베를린", "뮌헨", "프랑크푸르트", "로마", 
            "밀라노", "마드리드", "바르셀로나", "모스크바"
        }

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Tokenizes the input text and groups consecutive NNP proper nouns.
        Classifies them into 'PERSON' or 'ORG'. Filters out 'LOC' or other categories.
        Returns a list of dicts: [{'text': str, 'start': int, 'end': int, 'type': str}]
        """
        if not text.strip():
            return []

        tokens = list(self.kiwi.tokenize(text))
        entities = []
        i = 0
        n = len(tokens)

        while i < n:
            if tokens[i].tag == 'NNP':
                start_char = tokens[i].start
                end_char = tokens[i].start + tokens[i].len

                # Merge consecutive NNP tokens if they are adjacent or separated only by spaces
                j = i + 1
                while j < n:
                    if tokens[j].tag == 'NNP':
                        gap = text[end_char:tokens[j].start]
                        if gap.strip() == "":
                            end_char = tokens[j].start + tokens[j].len
                            j += 1
                        else:
                            break
                    else:
                        break

                entity_text = text[start_char:end_char].strip()
                entity_type = self._classify_entity(entity_text)

                if entity_type in ("PERSON", "ORG"):
                    entities.append({
                        "text": entity_text,
                        "start": start_char,
                        "end": end_char,
                        "type": entity_type
                    })
                i = j
            else:
                i += 1

        return entities

    def _classify_entity(self, text: str) -> str:
        clean_text = text.strip()
        if not clean_text:
            return "UNKNOWN"

        # 1. Exact match checks first (highest priority)
        if clean_text in self.countries_and_cities:
            return "LOC"
        if clean_text in self.known_orgs:
            return "ORG"

        # 2. Check if it's a Person based on Korean surname rules
        # If it starts with a surname and has a typical name length (2 to 4),
        # we classify it as PERSON, unless it ends with unambiguous administrative district suffixes (시, 도, 구, 군, 국).
        # Note: We bypass "동", "읍", "면", "리", "주" for surname-starting strings because names like "홍길동" end with "동".
        is_surname_starting = False
        if 2 <= len(clean_text) <= 4:
            if len(clean_text) >= 3 and clean_text[:2] in self.korean_surnames:
                is_surname_starting = True
            elif clean_text[0] in self.korean_surnames:
                is_surname_starting = True

        if is_surname_starting:
            if clean_text.endswith(("시", "도", "구", "군", "국")):
                return "LOC"
            return "PERSON"

        # 3. Check general location suffixes
        if len(clean_text) > 1 and clean_text.endswith(self.loc_suffixes):
            return "LOC"

        # 4. Check general organization suffixes
        if any(clean_text.endswith(suffix) for suffix in self.org_suffixes):
            return "ORG"

        # 5. Check if it contains a space (e.g. foreign names like "빌 게이츠")
        if " " in clean_text:
            return "PERSON"

        # Default to PERSON if it's a proper noun that isn't classified
        return "PERSON"

