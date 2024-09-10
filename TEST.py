import streamlit as st
import pandas as pd
import pytesseract
import cv2
from PIL import Image
from io import BytesIO
import numpy as np

# Function to process the uploaded Excel file
def process_excel_file(file):
    df = pd.read_excel(file)
    return categorize_data(df)

# Function to process the image and extract data using OCR
def process_image(file):
    img = Image.open(file)
    img = np.array(img)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Use pytesseract to do OCR on the image
    ocr_result = pytesseract.image_to_string(gray)
    
    # Process OCR result into a DataFrame
    data = []
    for line in ocr_result.splitlines():
        # Assuming a simple space/tab-separated format
        if line.strip():  # Skip empty lines
            data.append(line.split())
    
    if not data:
        st.error("No data found in the image.")
        return None, None, None, None
    
    # Convert list of lists into DataFrame
    df = pd.DataFrame(data[1:], columns=data[0])  # Assuming first row as header
    return categorize_data(df)

# Function to categorize data into Pass, Fail, Absent, and Detained
def categorize_data(df):
    marks_column = 'MARKS'
    
    if marks_column not in df.columns:
        st.error(f"Column '{marks_column}' not found in the data.")
        return None, None, None, None

    pass_df = df[df[marks_column].apply(lambda x: isinstance(x, (int, float)) and x > 21)]
    fail_df = df[df[marks_column].apply(lambda x: isinstance(x, (int, float)) and x < 22)]
    absent_df = df[df[marks_column].astype(str).str.upper() == 'A']
    detained_df = df[df[marks_column].astype(str).str.upper() == 'D']
    
    return pass_df, fail_df, absent_df, detained_df

# Streamlit UI
def main():
    st.title("Student Data Processing App")
    
    option = st.selectbox("Choose input method:", ["Upload Excel File", "Upload Image File"])
    
    if option == "Upload Excel File":
        uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")
        if uploaded_file is not None:
            st.write("Processing file...")
            pass_df, fail_df, absent_df, detained_df = process_excel_file(uploaded_file)
            
    elif option == "Upload Image File":
        uploaded_file = st.file_uploader("Upload an image of the data", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            st.write("Processing image...")
            pass_df, fail_df, absent_df, detained_df = process_image(uploaded_file)
    
    if uploaded_file and pass_df is not None:
        # Create downloadable Excel files
        def create_excel_buffer(df, sheet_name):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            output.seek(0)
            return output
        
        if not pass_df.empty:
            pass_buffer = create_excel_buffer(pass_df, "Passed Students")
            st.download_button(
                label="Download Passed Students Excel file",
                data=pass_buffer,
                file_name="pass.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        if not fail_df.empty:
            fail_buffer = create_excel_buffer(fail_df, "Failed Students")
            st.download_button(
                label="Download Failed Students Excel file",
                data=fail_buffer,
                file_name="fail.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        if not absent_df.empty:
            absent_buffer = create_excel_buffer(absent_df, "Absent Students")
            st.download_button(
                label="Download Absent Students Excel file",
                data=absent_buffer,
                file_name="absent.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        if not detained_df.empty:
            detained_buffer = create_excel_buffer(detained_df, "Detained Students")
            st.download_button(
                label="Download Detained Students Excel file",
                data=detained_buffer,
                file_name="detained.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == "__main__":
    main()
