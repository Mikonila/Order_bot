def generate_summary(user_info):
    import openai
    from src.config import CHATGPT_API_KEY

    openai.api_key = CHATGPT_API_KEY

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"Please summarize the following information: {user_info}"}
        ]
    )

    summary = response.choices[0].message['content']
    return summary