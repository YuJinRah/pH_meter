import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
import os

# 특정 RGB 기준점과 그에 대응하는 pH 값
rgb_values = np.array([
    [255, 0, 0],     # pH 0 (붉은색)
    [255, 165, 0],   # pH 3 (주황색)
    [255, 255, 0],   # pH 5 (노란색)
    [0, 255, 0],     # pH 7 (초록색)
    [0, 255, 255],   # pH 9 (청록색)
    [0, 0, 255],     # pH 11 (파란색)
    [128, 0, 128]    # pH 14 (보라색)
])
ph_values = np.array([0, 3, 5, 7, 9, 11, 14])

# pH 값을 구간별로 매핑하는 함수
def get_ph_from_rgb(r, g, b):
    # 강산성 (붉은색 계열: pH 0-2)
    if r > 150 and g < 100 and b < 100:
        return 0 + (255 - r) * 0.01  # pH 0에서 2 사이
    # 약산성 (주황색 계열: pH 3-4)
    elif r > 200 and g > 100 and b < 50:
        return 3.0 + (g - 100) * 0.02
    # 약산성 (노란색 계열: pH 5-6)
    elif r > 200 and g > 200 and b < 100:
        return 5.0 + (255 - g) * 0.02
    # 중성 (초록색: pH 7)
    elif r < 100 and g > 200 and b < 100:
        return 7.0
    # 약알칼리성 (청록색 계열: pH 8-9)
    elif r < 100 and g > 150 and b > 150:
        return 8.0 + (b - 150) * 0.02
    # 알칼리성 (파란색 계열: pH 10-11)
    elif r < 100 and g < 100 and b > 200:
        return 10.0 + (255 - b) * 0.01
    # 강알칼리성 (보라색 계열: pH 12-14)
    elif r > 100 and g < 100 and b > 150:
        return 12.0 + (r - 100) * 0.02
    else:
        return 7.0  # 기본값: 중성

# CSV 파일 경로 설정 (저장된 pH 예측값을 저장할 CSV 파일)
DATA_FILE = "ph_predictions.csv"

# CSV 파일 초기화 및 예시 데이터 삽입 (없으면 생성)
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["학번", "물질", "pH", "R", "G", "B"])
    df.to_csv(DATA_FILE, index=False)

# 앱 타이틀
st.title("🎨 pH Prediction App")

# 'pH 구하기' 섹션
st.header("pH 구하기")

# 학번 입력 필드 추가 (10101 ~ 99999 사이의 숫자)
학번 = st.number_input("Enter your student ID (학번)", min_value=10000, max_value=99999)

# 1. 물질 선택
st.write("Choose a material or enter one manually:")
material_list = ["묽은 염산", "수산화 나트륨", "살리실산", "세제", "식초", "증류수"]
material = st.selectbox("Select a material:", material_list + ["직접 입력"])
if material == "직접 입력":
    material = st.text_input("Enter the material manually:")

# 2. RGB 입력 방식 선택
input_method = st.radio("Choose how to input RGB values:", ("RGB 값 입력", "Upload an Image"))

# 3. RGB 슬라이더 선택 또는 이미지 업로드
if input_method == "RGB 값 입력":
    st.write("Choose the RGB values for the color:")
    r = st.slider("Red 값 (R)", 0, 255, 128)
    g = st.slider("Green 값 (G)", 0, 255, 128)
    b = st.slider("Blue 값 (B)", 0, 255, 128)
    

else:
    uploaded_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        img = image.resize((1, 1))  # 1x1 픽셀로 줄여서 RGB 추출
        r, g, b = np.array(img)[0][0]
        st.write(f"Extracted RGB values: R={r}, G={g}, B={b}")

# 4. "pH 값은?" 버튼
if st.button("pH 값은?"):
    predicted_ph = get_ph_from_rgb(r, g, b)
    st.write(f"Predicted pH: {predicted_ph}")

    # 예측 결과를 CSV 파일에 저장
    new_data = pd.DataFrame({"학번": [학번], "물질": [material], "pH": [predicted_ph], "R": [r], "G": [g], "B": [b]})
    df = pd.read_csv(DATA_FILE)
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    st.success("Data saved successfully!")

# '모아보기' 섹션
st.header("모아보기")

# CSV 파일 데이터 불러오기 및 표시
try:
    df = pd.read_csv(DATA_FILE)
    if df.empty:
        st.write("No data available yet.")
    else:
        st.dataframe(df)
except pd.errors.EmptyDataError:
    st.write("No data available yet.")

# 데이터 삭제 기능 추가
st.subheader("Delete a specific entry")

delete_학번 = st.number_input("학번", min_value=10000, max_value=99999, key="delete_학번")
delete_물질 = st.text_input("Enter material to delete:")
delete_ph = st.number_input("Enter pH value to delete:", min_value=0.0, max_value=14.0, step=0.01, key="delete_ph")

if st.button("Delete Entry"):
    df = df[~((df["학번"] == delete_학번) & (df["물질"] == delete_물질) & (df["pH"] == delete_ph))]
    df.to_csv(DATA_FILE, index=False)
    st.success("Entry deleted successfully!")
    st.dataframe(df)
