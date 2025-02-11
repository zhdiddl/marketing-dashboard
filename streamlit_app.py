import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

# 대시보드 제목
st.title("검색량 & 매출 데이터 대시보드")

# FastAPI 서버 URL (현재는 로컬로 설정)
API_BASE_URL = "http://127.0.0.1:8000"


# 검색량 데이터 조회 메서드
def fetch_marketing_data(keyword, start_date, end_date):
    response = requests.get(
        f"{API_BASE_URL}/marketing/search-volume", params={"keyword": keyword, "start_date": start_date, "end_date": end_date}
    )

    if response.status_code == 200:
        data = response.json()
        if data:
            return pd.DataFrame(data)
        else:
            st.warning("검색량 데이터가 존재하지 않습니다.")
            return pd.DataFrame()
    else:
        st.error(f"서버 오류: {response.status_code} | 데이터를 불러올 수 없습니다.")
        return pd.DataFrame()
    

# 매출 데이터 조회 메서드
def fetch_sales_data(start_date, end_date):
    response = requests.get(
        f"{API_BASE_URL}/sales", params={"start_date": start_date, "end_date": end_date}
    )
                            
    if response.status_code == 200:
        data = response.json()
        if data:
            return pd.DataFrame(data)
        else:
            st.warning("매출 데이터가 존재하지 않습니다.")
            return pd.DataFrame()
    else:
        st.error(f"서버 오류: {response.status_code} | 데이터를 불러올 수 없습니다.")
        return pd.DataFrame()
    

# 검색량 & 매출 비교 데이터 조회 메서드
def fetch_comparison_data(keyword, start_date, end_date):
    response = requests.get(
        f"{API_BASE_URL}/analytics/marketing-sales",
        params={"keyword": keyword, "start_date": start_date, "end_date": end_date}
    )
    comparison_data = response.json()

    if response.status_code == 200:
        if comparison_data["missing_data"]:  # 부족한 데이터가 있는 경우 경고 메시지 표시
            st.warning("🚨 " + " / ".join(comparison_data["missing_data"]))
            return pd.DataFrame()  # 차트가 생성되지 않도록 빈 데이터 반환
        else:
            return pd.DataFrame(comparison_data["data"])  # 차트 생성에 필요한 데이터만 반환
    else:
        st.error(f"서버 오류: {response.status_code} | 데이터를 불러올 수 없습니다.")
        return pd.DataFrame()


# Streamlit 시각화 - UI 구성
st.sidebar.header("📌 데이터 필터링")
selected_keyword = st.sidebar.text_input("🔍 검색 키워드 입력", "(예: 스타벅스)")
selected_start_date = st.sidebar.date_input("📅 조회 시작 날짜 입력")
selected_end_date = st.sidebar.date_input("📅 조회 마지막 날짜 입력")

if st.sidebar.button("📥 데이터 조회"):
    # 1. 검색량 데이터 차트 출력
    st.subheader(f"📈 {selected_keyword} 검색량 트렌드")
    marketing_df = fetch_marketing_data(selected_keyword, selected_start_date, selected_end_date)
    if not marketing_df.empty:
        marketing_df["date"] = pd.to_datetime(marketing_df["date"]) # 날짜 변환
        marketing_df = marketing_df.sort_values("date") # 날짜 순 정렬
        # 검색량을 정수로 변환
        marketing_df["search_volume"] = marketing_df["search_volume"].astype(int)

        # 그래프 생성
        fig = px.line(
            marketing_df,
            x="date",
            y="search_volume",
            color="keyword",
            title="검색량 변화 추이",
            labels={"date": "날짜", "search_volume": "검색량", "keyword": "검색어"}
        )

        # 차트 레이아웃 설정
        fig.update_layout(
            xaxis=dict(
                tickformat="%Y-%m-%d", # 날짜 포맷
                dtick="D1",  # 1일 단위로 눈금 표시 (중복 날짜 표기 방지)
                tickangle=-45  # 45도 회전 표시
            ),
            yaxis=dict(
                tickformat="d", # 정수 포맷
                range=[max(0, marketing_df["search_volume"].min() - 1)  , marketing_df["search_volume"].max() + 1]  # y축 범위 자동 조정
            )
        )
        
        st.plotly_chart(fig)  # 그래프로 출력


    # 2. 매출 데이터 차트 출력
    st.subheader("💰 매출 데이터 트렌드")
    sales_df = fetch_sales_data(selected_start_date, selected_end_date)
    if not sales_df.empty:
        sales_df["date"] = pd.to_datetime(sales_df["date"]) # 날짜 변환
        sales_df = sales_df.sort_values("date") # 날짜 순 정렬

        fig = px.bar(
            sales_df, 
            x="date", 
            y="revenue", 
            title="일별 매출 데이터",
            labels={"date": "날짜", "revenue": "매출 (천 단위)"}
        )

        # 차트 레이아웃 설정
        fig.update_layout(
            xaxis=dict(
                tickformat="%Y-%m-%d", # 날짜 포맷
                dtick="D1",  # 1일 단위로 눈금 표시 (중복 날짜 표기 방지)
                tickangle=-45  # 45도 회전 표시
            )
        )

        st.plotly_chart(fig)  # 그래프로 출력


    # 3. 검색량 & 매출 비교 데이터 출력
    st.subheader("📊 검색량 & 매출 비교")
    comparison_df = fetch_comparison_data(selected_keyword, selected_start_date, selected_end_date)

    if comparison_df.empty: # 데이터프레임이 비어있는지 확인
        st.warning("🔎 데이터가 부족해서 시각화할 수 없습니다.")
    else:
        comparison_df["date"] = pd.to_datetime(comparison_df["date"]) # 날짜 변환
        comparison_df = comparison_df.sort_values("date") # 날짜 순 정렬

        fig = go.Figure()  # 그래프 생성에 사용할 Figure 객체 생성

        # 매출 (Bar Chart)
        fig.add_trace(
            go.Bar(
                x=comparison_df["date"],
                y=comparison_df["revenue"],
                name="매출",
                yaxis="y",
                marker=dict(color="blue")  # 마커 색 지정
            )
        )

        # 검색량 (Line Chart)
        fig.add_trace(
            go.Scatter(
                x=comparison_df["date"],
                y=comparison_df["search_volume"],
                name="검색량",
                yaxis="y2",
                mode="lines+markers",
                marker=dict(color="red")
            )
        )

        # y축 설정 (이중 축)
        fig.update_layout(
            title=f"{selected_keyword} 검색량 & 매출 비교",
            xaxis=dict(
                title="날짜",
                tickformat="%Y-%m-%d", # 날짜 포맷
                dtick="D1",  # 1일 단위로 눈금 표시 (중복 날짜 표기 방지)
                tickangle=-45  # 45도 회전 표시
            ),
            yaxis=dict(
                title="매출 (천 단위)", side="left", showgrid=False  # 격자 미표시
            ),
            yaxis2=dict(
                title="검색량", 
                side="right",
                overlaying="y", 
                showgrid=False,
                tickformat="d", # 정수 포맷
                range=[max(0, marketing_df["search_volume"].min() - 1), marketing_df["search_volume"].max() + 1]  # y축 범위 자동 조정
            ),
        )

        st.plotly_chart(fig)  # 그래프로 출력
