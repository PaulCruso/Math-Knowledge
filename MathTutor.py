from openai import OpenAI
import APIConstants

client = OpenAI(api_key=APIConstants.api_key)

# Upload the math knowledge CSV file
math_knowledge_file = client.files.create(
    file=open("files/math_knowledge.csv", "rb"),
    purpose='assistants'
)

# Create the Math tutor assistant
assistant = client.beta.assistants.create(
    name="Math tutor assistant",
    instructions="你是一名中国数学老师，请您了解csv文件中每一个数字id对应的知识点，"
                 "再请你给出解决图中题目所需要的数学知识点id，例如 3601， 4156",
    model="gpt-4o",
    tools=[{"type": "code_interpreter"}],
    tool_resources={
        "code_interpreter": {
            "file_ids": [math_knowledge_file.id]
        }
    }
)

# Upload the image file
math_image_file = client.files.create(
    file=open("files/1.png", "rb"),
    purpose='vision'
)

# Create a new thread with the image
thread = client.beta.threads.create(
  messages=[
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "首先解决这一道题目，再请问解决图中题目需要什么数学知识点以及其对应的id？"
        },
        {
          "type": "image_file",
          "image_file": {"file_id": math_image_file.id}
        },
      ],
    }
  ]
)

# Start the run
run = client.beta.threads.runs.create(
  thread_id=thread.id,
  assistant_id=assistant.id
)

while run.status != "completed":
    keep_retrieving_run = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )
    print(f"Run status: {keep_retrieving_run.status}")

    if keep_retrieving_run.status == "completed":
        print("\n")
        break

result = client.beta.threads.messages.list(
    thread_id=thread.id
)

print(result.data[0].content[0].text.value)
