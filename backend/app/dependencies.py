from fastapi import Query

# 공통으로 적용할 한글 검색어 검증 로직
def get_valid_keyword(keyword: str = Query(..., min_length=1, max_length=100, title="검색 키워드")):
    return keyword
