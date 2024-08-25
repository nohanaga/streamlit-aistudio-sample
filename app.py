import streamlit as st
import urllib.request
import json
import os
import ssl
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

AZURE_ENDPOINT_KEY = os.environ['AZURE_ENDPOINT_KEY']
AZURE_ENDPOINT_URL = os.environ['AZURE_ENDPOINT_URL']
AZURE_MODEL_DEPLOYMENT = os.environ['AZURE_MODEL_DEPLOYMENT']

# Streamlit UI components
st.image("logo.png", width=200)
st.title(' Welcome to your Assistant!')
st.sidebar.title(" Copilot for XXX!")
st.sidebar.caption("Made by an Microsoft")
st.sidebar.info("""
message
    """)

def allowSelfSignedHttps(allowed):
    # Bypass the server certificate verification on the client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

def main():
    allowSelfSignedHttps(True)
    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for interaction in st.session_state.chat_history:
        if interaction["inputs"]["question"]:
            with st.chat_message("user"):
                st.write(interaction["inputs"]["question"])
        if interaction["outputs"]["answer"]:
            with st.chat_message("assistant"):
                st.write(interaction["outputs"]["answer"])

    # React to user input
    if user_input := st.chat_input("Ask me anything..."):
        # Display user message in chat message container
        st.chat_message("user").markdown(user_input)

        # Query API
        data = {"chat_history": st.session_state.chat_history, 'question': user_input}
        print(data)
        body = json.dumps(data).encode('utf-8')
        url = AZURE_ENDPOINT_URL
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {AZURE_ENDPOINT_KEY}',
            'azureml-model-deployment': AZURE_MODEL_DEPLOYMENT
        }
        req = urllib.request.Request(url, body, headers)

        try:
            response = urllib.request.urlopen(req)
            response_data = json.loads(response.read().decode('utf-8'))

            # Check if 'answer' key exists in the response_data
            if 'answer' in response_data:
                with st.chat_message("assistant"):
                    st.markdown(response_data['answer'])

                st.session_state.chat_history.append(
                    {"inputs": {"question": user_input},
                     "outputs": {"answer": response_data['answer']}}
                )

            else:
                st.error("The response data does not contain a 'answer' key.")
        except urllib.error.HTTPError as error:
            st.error(f"The request failed with status code: {error.code}")

if __name__ == "__main__":
    main()