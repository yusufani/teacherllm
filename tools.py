import os

import openai

print(f"OpenAI VERSION: {openai.__version__}")
import threading

import streamlit as st
from dotenv import find_dotenv, load_dotenv
from langchain.agents import Tool
from langchain.chains import LLMChain
from streamlit.runtime.scriptrunner import add_script_run_ctx

from chains import get_chains

_ = load_dotenv(find_dotenv())  # read local .env file
openai.api_key = os.environ["OPENAI_API_KEY"]

import pickle


def generate_curriculum(input, curriculum_chain):
    """
    The generate_curriculum function is used to generate a curriculum for the user.
    It takes in an input string and a curriculum chain, which is then run on the input string.
    The resulting output of this function is stored in session state as well as returned to be displayed.
    
    :param input: Generate the curriculum
    :param curriculum_chain: Generate the curriculum
    :return: A string of the curriculum
    :doc-author: Yusuf
    """
    def parse_curriculum(curriculum):
        """
        The parse_curriculum function takes a string of curriculum and splits it into a list of strings.
            The split is done on the delimiter '$$$'.
            It then strips each element in the list to remove any leading or trailing whitespace.
            Finally, it removes any empty elements from the list.
        
        :param curriculum: Split the curriculum into a list of strings
        :return: A list of strings
        :doc-author: Yusuf
        """
        curriculum = curriculum.split("$$$")
        curriculum = [
            c.strip() for c in curriculum if c.strip() != "" and c.strip() != "\n"
        ]
        return curriculum

    path = f'{input.replace(" ", "-")}_{"-".join(st.session_state["configs"])}.pkl'
    os.makedirs(".cache", exist_ok=True)
    path = os.path.join(".cache", path)
    if os.path.exists(path):
        print("INFO: load curriculum from cache")
        with open(path, "rb") as f:
            curriculum = pickle.load(f)
        st.session_state["curriculum"] = parse_curriculum(curriculum)
        st.session_state["memory"].save_context(
            {"input": input}, {"chat": st.session_state["curriculum"]}
        )
        # Put curriculum to memory as llm answer
        return curriculum.replace("$$$", "")
    else:
        print("INFO: Generating curriculum")
        curriculum = curriculum_chain.run(input)
        st.session_state["curriculum"] = parse_curriculum(curriculum)
        with open(path, "wb") as f:
            pickle.dump(curriculum, f)
        return curriculum.replace("$$$", "")


def image_generator(extract_prompt, module_content):
    """
    The image_generator function takes in a prompt and module content, extracts the key content from the module using an extract_prompt, then generates an image that represents the key content.
    
    :param extract_prompt: Extract the key content from the module_content parameter
    :param module_content: Pass the content of the module to be used as a prompt for generating an image
    :return: image url
    :doc-author: Yusuf
    """
    extract_chain = LLMChain(
        llm=st.session_state["llm"],
        prompt=extract_prompt,
        verbose=True,
        output_key="key_content",
    )
    key_content = extract_chain.run({"module_content": module_content})

    extra_prompt = f"Generate an image that represents the following content , Ensure that the text stands out with sufficient contrast and avoid complex backgrounds that could detract from the text's readability.: {key_content}"
    image_url = openai.Image.create(
        model="dall-e-3",
        prompt=extra_prompt,
        size="1024x1024",
        quality="standard",
        n=1,
        response_format="url",
    )

    return image_url


def learn_module(
    input, curriculum, module_prompt, flashcard_prompt, user_config, extract_prompt
):
    """
    The learn_module function is used to geneate content for given module. It generates content and flashcards for the module. Then, it generates an image if the user configuration contains "Image-Containing".
    It stores flashcards and module content in session state and returns the output of the teach_chain.run function.
    It takes in the following arguments:
    - input: The user's input, which should be of the form Module X##Extra information that needs to be added to the module in speech if exists where X is an integer representing a module number.
    - curriculum: A list of modules, each containing a title and content (a string). This function will use this list as its source for learning modules.
    - module_prompt: A prompt object that contains all prompts related to learning modules (e.g., &quot;What would you like me to teach you?&quot;)
    
    
    :param input: Get the module number and extra information that needs to be added to the module in speech if exists
    :param curriculum: Pass the curriculum to the learn_module function
    :param module_prompt: Define the prompt that will be used to teach the module
    :param flashcard_prompt: Generate flashcards for the module
    :param user_config: Determine if the user wants to generate an image or not
    :param extract_prompt: Extract the image from the module content
    :return: The output of the teach_chain.run function, with Image generated prepended to it if the user_config contains "Image-Containing"
    :doc-author: Yusuf
    """
    if "##" not in input:
        return "Input need to have in this format 'IntegerNumber##Extra information that needs to be added to the module in speech if exists' Where IntegerNumber refers Module Number"
    module_number, extra_config = input.split("##")
    module_number = module_number.replace("Module", "").strip()
    if type(module_number) == str:
        module_number = int(module_number)
    module = curriculum[module_number - 1]

    teach_chain = LLMChain(
        llm=st.session_state["llm"],
        prompt=module_prompt,
        verbose=True,
    )

    if st.session_state.get("module_contents", None) is None:
        st.session_state["module_contents"] = [None] * len(curriculum)

    print("INFO: teach_chain.run")
    output = teach_chain.run({"module": module, "extra_config": extra_config})
    print("INFO: teach_chain.run done")
    st.session_state["module_contents"][module_number - 1] = output

    def run_flashcard_chain():
        """
        The run_flashcard_chain function generates flashcards for the module.
        :doc-author: Yusuf
        """
        flashcard_chain = LLMChain(
            llm=st.session_state["llm"],
            prompt=flashcard_prompt,
            verbose=True,
        )
        if st.session_state.get("flashcard", None) is None:
            st.session_state["flashcard"] = [None] * len(curriculum)
        print("INFO: flashcard_chain.run")
        st.session_state["flashcard"][module_number - 1] = flashcard_chain.run(
            {"module_content": output}
        )
        print(
            f"INFO: flashcard_chain.run done Content: {st.session_state['flashcard'][module_number - 1]}"
        )

    def generate_image():
        """
        The generate_image function is called when the user selects "Image-Containing" in their configuration.
        It calls image_generator, which takes in a prompt and an output, and returns a url to an image.
        The generate_image function then stores this url in session state so that it can be displayed later.
        
        :return: The image url, which is then displayed in the streamlit app
        :doc-author: Trelent
        """
        if st.session_state.get("image_url", None) is None:
            st.session_state["image_url"] = [None] * len(curriculum)
        image_url = image_generator(extract_prompt, output)
        print("INFO: image_generator done")
        st.session_state["image_url"][module_number - 1] = image_url.data[
            0
        ].url  # Fixed indexing issue
        st.session_state["last_module_number"] = module_number - 1
        print(f"INFO: url is: {st.session_state['image_url'][module_number - 1]}")

    flashcard_thread = threading.Thread(target=run_flashcard_chain)
    add_script_run_ctx(flashcard_thread)
    flashcard_thread.start()
    image_thread = None
    if "Image-Containing" in user_config:
        image_thread = threading.Thread(target=generate_image)
        add_script_run_ctx(image_thread)
        image_thread.start()
        output = "Image generated " + output

    # Wait for threads to complete
    flashcard_thread.join()
    if "Image-Containing" in user_config:
        image_thread.join()

    return output


def chat(input):
    """
    The chat function takes in a string and returns it without any modifications since we are only using it to chat with the user.
        
    
    :param input: Store the user's input
    :return: The input
    :doc-author: Yusuf
    """
    return input


def quiz_generator(input, evaluation_chain):
    """
    The quiz_generator function takes in a module number and an evaluation chain.
    It then uses the evaluation chain to generate a quiz based on the content of that module.
    
    :param input: Pass in the module number that is selected by the user
    :param evaluation_chain: Run the evaluation chain
    :return: A string
    :doc-author: Yusuf
    """
    if type(input) == str:
        module_number = int(input)

    if st.session_state.get("module_contents", None) is None:
        content = st.session_state["curriculum"][module_number - 1]
    else:
        content = st.session_state["module_contents"][module_number - 1]

    test_quiz = evaluation_chain.run({"module_content": content})
    print(f"INFO: quiz_generator done Content: {test_quiz}")
    return "Quiz generated " + test_quiz


def calculate_score(return_string=False):
    """
    The calculate_score function is used to calculate the user's score for each module and overall.
    It returns a list of dictionaries containing the following keys:
        - correct_answer_count: The number of questions in this module that were answered correctly by the user.
        - total_questions: The total number of questions in this module.
        - module_title: The title of this particular quiz/module.
    
    :param return_string: Return the results as a string or as a dictionary
    :return: A tuple of two elements
    :doc-author: Yusuf
    """
    results = st.session_state.get("quiz_results")
    if results is None:
        return None, None
    else:
        total_questions = 0
        total_correct_answers = 0
        if return_string:
            scores, user_wrong_content = "", ""
            for c in range(len(st.session_state.get("curriculum"))):
                if results.get(f"quiz_{c + 1}") is not None:
                    module_markdown = st.session_state["curriculum"][c]
                    module_parts = module_markdown.split("##")
                    module_title = (
                        ":".join(module_parts[0].split(":")[:2])
                        .replace("#", "")
                        .strip()
                    )

                    correct_answer_count = len(
                        [r for r in results[f"quiz_{c + 1}"] if r["is_correct"]]
                    )
                    total_questions += len(results[f"quiz_{c + 1}"])
                    if correct_answer_count != len(results[f"quiz_{c + 1}"]):

                        user_wrong_content += f"{module_title}"
                        for r in results[f"quiz_{c + 1}"]:
                            if not r["is_correct"]:
                                user_wrong_content += f"\nQuestion: {r['question']}\nUser Answer: {r['user_answer']}\nCorrect Answer: {r['correct_answer']}\n"

                    scores += f"Module {module_title}: User correct answer accuracy {correct_answer_count}/{len(results[f'quiz_{c + 1}'])}\n"
                    total_correct_answers += correct_answer_count
            scores += f"\n\nTotal All modules user correct answer accuracy: {total_correct_answers}/{total_questions}"
            return scores, user_wrong_content
        else:
            scores = [None] * len(st.session_state.get("curriculum"))
            for c in range(len(st.session_state.get("curriculum"))):
                if results.get(f"quiz_{c + 1}") is not None:
                    module_markdown = st.session_state["curriculum"][c]
                    module_parts = module_markdown.split("##")
                    module_title = (
                        ":".join(module_parts[0].split(":")[:2])
                        .replace("#", "")
                        .strip()
                    )

                    correct_answer_count = len(
                        [r for r in results[f"quiz_{c + 1}"] if r["is_correct"]]
                    )
                    total_questions += len(results[f"quiz_{c + 1}"])
                    scores[c] = {
                        "correct_answer_count": correct_answer_count,
                        "total_questions": len(results[f"quiz_{c + 1}"]),
                        "module_title": module_title,
                    }
                    total_correct_answers += correct_answer_count

            total = {
                "correct_answer_count": total_correct_answers,
                "total_questions": total_questions,
            }
            return scores, total


def analyze(_, analysis_module_prompt):
    """
    The analyze function is called when the user clicks on the Analyze button.
    It takes in a single argument, which is a string containing all of the content
    that was displayed to the user during their quiz session. The analyze function
    should return a string that will be displayed to users after they click on 
    the Analyze button.
    
    :param _: Pass the user input to the function
    :param analysis_module_prompt: Specify the prompt that will be used to generate the analysis
    :return: A string
    :doc-author: Yusuf
    """
    scores, user_wrong_content = calculate_score(return_string=True)
    if scores is None:
        return "No quiz results found"
    analysis_chain = LLMChain(
        llm=st.session_state["llm"],
        prompt=analysis_module_prompt,
        verbose=True,
    )
    output = analysis_chain.run(
        {"statistics": scores, "user_wrong_content": user_wrong_content}
    )

    return "ANALYSIS:" + output.replace("[Your Name]", "")


def get_tools():
    """
    The get_tools function is used to return a list of Tool objects.
    Each Tool object has the following attributes:
        name (str): The name of the tool, which will be displayed in the UI.
        func (func): A function that takes an input string and returns a string output. This function should be able to handle any user input, but it's recommended that you use tools for specific purposes when possible so users can get more consistent results from your bot!
        description (str): A short description explaining what this tool does and how it works. This will also be displayed in the UI.
    
    :return: A list of tool objects
    :doc-author: Yusuf
    """
    (
        answer_question_chain,
        generate_curriculum_chain,
        module_prompt,
        evaluation_chain,
        flashcard_prompt,
        analysis_module_prompt,
        extract_prompt,
    ) = get_chains(st.session_state["llm"], st.session_state["memory"])
    tools = [
        Tool(
            name="answer_user_question",
            func=answer_question_chain.run,
            description="Useful when user ask a question about content generated, and you need to generate answer. Never use this tool to switch to next module. Input of this tool is the question that user ask",
            return_direct=True,
        ),
        Tool(
            name="generate_curriculum",
            func=lambda input: generate_curriculum(input, generate_curriculum_chain),
            description="Useful when the user want to learn how to cook something. Input of this tool is the topic that user want to learn. Wait user message use other tools after run this tool.  ",
            return_direct=True,
        ),
        Tool(
            name="module_content",
            func=lambda input: learn_module(
                input,
                st.session_state["curriculum"],
                module_prompt,
                flashcard_prompt,
                st.session_state["configs"],
                extract_prompt,
            ),
            description="If the user wants to proceed to module and curriculum is generated before, use this tool generate content of the module. Input of this tool in this format 'int##str' where int refers to Module number and str refers that needs to be added to the module in speech if exists otherwise put empty string",
            return_direct=True,
        ),
        Tool(
            name="evaluation",
            func=lambda input: quiz_generator(input, evaluation_chain),
            description="Useful when users need some tests or exercises to test their knowledge. Return directly the output, don't add anything. Input of this tool in this format 'int' where int refers to Module number",
            return_direct=True,
        ),
        Tool(
            name="analyze",
            func=lambda x: analyze(x, analysis_module_prompt),
            description="Useful when user wants to be analyzed after quizes. Input of this tool is empty.",
            return_direct=True,
        ),
        Tool(
            name="chat",
            func=chat,
            description="Only use this if user input is not suitable for any other tool and you want to chat with user. Input of this tool is the user message.",
            return_direct=True,
        ),
    ]
    return tools
