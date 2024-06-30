import os
from openai import OpenAI

class ChatBot:
    def __init__(self):
        self.api_key = "sk-proj-zwthpQecL2ERMxGVTqyxT3BlbkFJWujkjC3fNdAImjPeask3"
        self.model = "gpt-3.5-turbo"
        self.client = OpenAI(api_key=self.api_key)

    def get_response(self, personal_info, product_info, user_question):
        try:
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "system", "content": f"Personal Information: {personal_info}"},
                {"role": "system", "content": f"Product Information: {product_info}"},
                {"role": "user", "content": user_question}
            ]
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=150,
                stop=None
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error: {e}"

# Create an instance of the ChatBot class
chatbot = ChatBot()
