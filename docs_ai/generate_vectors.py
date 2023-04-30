import hashlib
import json
import os
import openai
from deepdiff.serialization import json_loads

openai.api_key = os.environ.get('API_KEY', None)
_local_dir = os.path.dirname(__file__)


def summary_file_name(file_name):
    return os.path.join(_local_dir, "content/summary", file_name)


def has_summary(file_name) -> bool:
    file_name = summary_file_name(file_name)
    return os.path.exists(file_name) and os.path.isfile(file_name)


def save_summary(file_name, content):
    file_name = summary_file_name(file_name)
    save_content(file_name, content)


def create_folder_if_not_exists(folder_path):
    # Check if the folder exists
    if not os.path.exists(folder_path):
        # Create the folder
        os.makedirs(folder_path)


def save_content(file_name, content):
    # Save the content to a file with the hash as the file name
    with open(file_name, 'w') as file:
        file.write(content)


def get_ai_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0,
    )
    return response.choices[0].text.strip()


def get_markdown(directory):
    for root, dirs, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith('.md'):
                file_path = os.path.join(root, file_name)
                with open(file_path, 'r') as file:
                    # Parse the markdown file and extract paragraphs
                    markdown_text = file.read()
                    yield os.path.realpath(file_path), markdown_text.strip()


def process(file_path, content) -> bool:
    if content == "" or len(content) < 100:
        return False

    summary_file_name = file_path.replace("/", "."). \
        replace('.home.risto.PycharmProjects.tracardi-api.', '')

    if has_summary(summary_file_name):
        return False

    prompt = f"""Write a verbose summary of information included in the documentation text. 
            Do no use any code just plain text explanation 
            what information is included in the text. Include all most important information
            that you can later use to look up this content. Return at least two paragraphs if text
            is longer then 500 letters. 
            
            Documentation: {content}
            """
    if len(content) > 4096:
        print("Too long", file_path)
        return False

    summary = get_ai_response(prompt)
    save_summary(summary_file_name, summary)

    return True


def yield_paragraphs(document):
    chunk = ""
    for line in document.split("\n"):
        if line.startswith("## "):
            if chunk:
                yield chunk.strip()
            chunk = line
        elif line.startswith("# "):
            if chunk:
                yield chunk.strip()
            chunk = line
        else:
            chunk += f"{line}\n"
    if chunk:
        yield chunk.strip()


# Example usage

directory = os.path.join(_local_dir, '../docs')
question_directory = os.path.join(_local_dir, 'content/question')

create_folder_if_not_exists(question_directory)
os.chdir(question_directory)

number_of_paragraphs = 0
for i, (file_name, document) in enumerate(get_markdown(directory)):

    if document == "":
        continue

    result = process(file_name, document)
    print(i, file_name, result)
    short_file_name = file_name.replace('/home/risto/PycharmProjects/tracardi-api/', '')

    if short_file_name.startswith('docs/flow/action'):
        continue

    for paragraph in yield_paragraphs(document):

        if len(paragraph) < 50:
            print("skipped", paragraph)
            continue

        number_of_paragraphs += 1
        sha1_hash = hashlib.sha1(document.encode()).hexdigest()
        file = f"{sha1_hash}.json"
        print(file)
        if not os.path.exists(file) or not os.path.isfile(file):
            prompt = f"What question the following text answers. Give one question that covers the whole content. " \
                     f"And at least 2 optional questions that cover only part of the text. " \
                     f"Text is in markdown format. Write only one question per line, nothing else." \
                     f"Text:\n{paragraph}\n\n"
            json_question = get_ai_response(prompt)
            print(json_question)
            questions =json_question.split("\n")
            questions = [q for q in questions if q!= "Optional questions:" or q!=""]
            json_content = {
                "file_name": file_name.replace('/home/risto/PycharmProjects/tracardi-api/', ''),
                "questions": questions,
                "answer": paragraph
            }

            save_content(f"{sha1_hash}.json", json.dumps(json_content))


    # if not os.path.exists(file) or not os.path.isfile(file):

    # Parse the markdown file and extract chunks

    # sha1_hash = hashlib.sha1(document.encode()).hexdigest()
    # file = f"{sha1_hash}.answer"
    # if not os.path.exists(file) or not os.path.isfile(file):
    #     prompt = f"What question for the following text answers. Give at least two or more. " \
    #              f"One question per line. Number the questions:\n{document}\n\n"
    #
    #     question = get_ai_response(prompt)
    #     save_content(f"{sha1_hash}.question", question)
    #     save_content(f"{sha1_hash}.answer", document)
    #     print('----')
    #     print(question)
