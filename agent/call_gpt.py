from openai import OpenAI

client = OpenAI()

def get_gpt_response(prompt: str, user_content: str) -> str:
    response = client.responses.create(
        model="gpt-4.1",
        input=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_content}
        ],
        text={
            "format": {
                "type": "text"
            }
        },
        reasoning={},
        tools=[],
        temperature=0.05,
        max_output_tokens=16384,
        top_p=1,
        store=True
    )
    return response.output[0].content[0].text
