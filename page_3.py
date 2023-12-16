import streamlit as st
import boto3
import json

aws_access_key_id = st.secrets["AWS_Access_key"]
aws_secret_access_key = st.secrets["Secre_AK"]
# Initialize Boto3 S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

# Specify your bucket name and folder path
bucket_name = 'ash-dcsc-project'
folder_path = 'NBA_Live_Data/Current_Matches/'

# List files in the specified S3 bucket directory
response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_path)
files = [item['Key'] for item in response.get('Contents', []) if item['Key'].endswith('.json')]

# Initialize Streamlit app
st.title('Game Details')

# Process each JSON file
for file_key in files:
    # Read file content
    obj = s3.get_object(Bucket=bucket_name, Key=file_key)
    match_data = json.loads(obj['Body'].read().decode('utf-8'))

    # Display match details (assuming each file contains one match)
    with st.container():
        st.subheader(f"Match ID: {match_data['gameId']} - {match_data['gameCode']}")
        col1, col2 = st.columns(2)

        with col1:
            st.header("Home Team")
            st.write(f"Team Name: {match_data['homeTeam']['teamName']}")
            st.write(f"Score: {match_data['homeTeam']['score']}")

        with col2:
            st.header("Away Team")
            st.write(f"Team Name: {match_data['awayTeam']['teamName']}")
            st.write(f"Score: {match_data['awayTeam']['score']}")

        st.markdown("---")  # Separator line
