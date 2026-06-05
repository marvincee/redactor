import unittest
from src.nlp.korean import KoreanExtractor

class TestKoreanNLP(unittest.TestCase):
    def setUp(self):
        self.extractor = KoreanExtractor()

    def test_extract_person_names(self):
        text = "홍길동은 이순신 장군을 존경하고 김철수 대리와 친하다."
        entities = self.extractor.extract_entities(text)
        
        # Should extract '홍길동', '이순신', '김철수'
        person_texts = [e["text"] for e in entities if e["type"] == "PERSON"]
        self.assertIn("홍길동", person_texts)
        self.assertIn("이순신", person_texts)
        self.assertIn("김철수", person_texts)
        self.assertNotIn("장군", person_texts)
        self.assertNotIn("대리", person_texts)

    def test_extract_organizations(self):
        text = "서울대학교에서 공부하고 삼성전자와 구글 코리아에 입사 지원을 했습니다."
        entities = self.extractor.extract_entities(text)

        org_texts = [e["text"] for e in entities if e["type"] == "ORG"]
        self.assertIn("서울대학교", org_texts)
        self.assertIn("삼성전자", org_texts)
        self.assertIn("구글 코리아", org_texts)

    def test_filter_locations(self):
        text = "대한민국 서울시 역삼동과 미국 뉴욕을 다녀왔다."
        entities = self.extractor.extract_entities(text)
        
        # Locations like 대한민국, 서울시, 역삼동, 미국, 뉴욕 should NOT be extracted as PERSON or ORG
        extracted_texts = [e["text"] for e in entities]
        self.assertNotIn("대한민국", extracted_texts)
        self.assertNotIn("서울시", extracted_texts)
        self.assertNotIn("역삼동", extracted_texts)
        self.assertNotIn("미국", extracted_texts)
        self.assertNotIn("뉴욕", extracted_texts)

    def test_entity_offsets(self):
        text = "김민수는 졸업했다."
        #       0123
        entities = self.extractor.extract_entities(text)
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0]["text"], "김민수")
        self.assertEqual(entities[0]["start"], 0)
        self.assertEqual(entities[0]["end"], 3)
        self.assertEqual(entities[0]["type"], "PERSON")

        # Slice verification
        self.assertEqual(text[entities[0]["start"]:entities[0]["end"]], "김민수")

    def test_foreign_name(self):
        text = "빌 게이츠를 만났다."
        entities = self.extractor.extract_entities(text)
        
        person_texts = [e["text"] for e in entities if e["type"] == "PERSON"]
        self.assertIn("빌 게이츠", person_texts)

if __name__ == "__main__":
    unittest.main()
