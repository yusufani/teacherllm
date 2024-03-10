import os
import textwrap

import matplotlib.pyplot as plt
import openai
import streamlit as st
from dotenv import find_dotenv, load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationSummaryBufferMemory, ReadOnlySharedMemory

wrapper = textwrap.TextWrapper(width=25)


@st.cache_resource
def initialize_ui():
    """
    The initialize_ui function is used to initialize the UI of the Streamlit app.
    It does this by adding a custom CSS style sheet to the page, which will be used
    to create a top bar with configurable options.

    :doc-author: Yusuf
    """
    css = """
    <style>
    /* Custom styles here */
    .top-bar {
        display: flex;
        justify-content: space-around;
        align-items: center;
        padding: 10px;
        background-color: #f1f1f1; /* Example background */
    }
    .top-bar:hover .config-option {
        display: block; /* Show config on hover */
    }
    /* Other styles */
    </style>
    """

    st.markdown(css, unsafe_allow_html=True)


@st.cache_resource
def initialize_llm():
    """
    The initialize_llm function is called by the main function to initialize the
       OpenAI GPT-4 language model, a ConversationSummaryBufferMemory object, and a
       ReadOnlySharedMemory object to use for the project.

    :return: A tuple of three objects
    :doc-author: Yusuf
    """
    print("INFO: initialize_llm")
    _ = load_dotenv(find_dotenv())  # read local .env file
    openai.api_key = os.environ["OPENAI_API_KEY"]
    llm = ChatOpenAI(model_name="gpt-4-1106-preview", temperature=0, verbose=True)
    memory = ConversationSummaryBufferMemory(llm=llm, memory_key="chat_history")
    readonlymemory = ReadOnlySharedMemory(memory=memory, memory_key="chat_history")
    print("INFO: initialize_llm done")
    return llm, memory, readonlymemory


def parse_quiz_output(quiz_output):
    # Split the output into individual questions based on '####'
    """
    The parse_quiz_output function takes the output of the quiz and parses it into a list of tuples.
    Each tuple contains:
        - The question text (string)
        - A list of options (list)
        - The answer to the question (string)
        - An explanation for why that's correct/incorrect

    :param quiz_output: Pass the quiz output to the function
    :return: A list of tuples, where each tuple contains the following:
    :doc-author: Yusuf
    """
    raw_questions = quiz_output.split("####")

    # Initialize an empty list to hold the parsed questions
    parsed_questions = []

    # Iterate through the raw questions
    for raw_question in raw_questions:
        if raw_question.strip():  # Make sure there's content here to parse
            # Each question component is on a new line, so we split by lines
            parts = raw_question.strip().split("\n")

            # Extracting individual components
            question_text = parts[0].strip('" ').lstrip("- ")
            options = eval(
                parts[1].lstrip("- ").strip()
            )  # Using eval to convert string list to actual list
            answer = (
                parts[2].lstrip("- ").strip().replace("Answer: ", "").replace('"', "")
            )
            explanation = parts[3].lstrip("- ").strip('" ')

            # Append the parsed question as a tuple to the list
            parsed_questions.append((question_text, options, answer, explanation))

    return parsed_questions


def display_quiz(quiz_id):
    # Retrieve the quiz from messages
    """
    The display_quiz function takes a quiz_id as input and displays the quiz with that id.
    The function also stores the user's answers in session state, so that they can be retrieved later.


    :param quiz_id: Uniquely identify the quiz
    :return: The quiz_results dictionary, which contains the results of each question
    :doc-author: Yusuf
    """
    quiz = next(
        (
            msg
            for msg in st.session_state.messages
            if msg.get("id") == quiz_id and msg.get("content_quiz")
        ),
        None,
    )
    if not quiz:
        st.error("Quiz not found.")
        return
    quiz_content = quiz["content_quiz"]
    quiz_parsed = parse_quiz_output(quiz_content)

    # Initialize user_answers if not already present
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = {}

    if quiz_id not in st.session_state.user_answers:
        st.session_state.user_answers[quiz_id] = [None] * len(quiz_parsed)

    total_correct = 0
    quiz_results = []

    for idx, (question, options, correct_answer, explanation) in enumerate(quiz_parsed):
        st.markdown(f"**Q{idx + 1}: {question}**")

        # Use the stored answer as the default, if available
        default_answer = st.session_state.user_answers[quiz_id][idx]
        selected_answer = st.radio(
            f"Select an option for Q{idx + 1}:",
            options,
            key=f"{quiz_id}_q_{idx}",
            index=options.index(default_answer) if default_answer in options else 0,
        )

        # Store the selected answer in session state
        st.session_state.user_answers[quiz_id][idx] = selected_answer

    if st.button("Submit Answers", key=f"submit_{quiz_id}"):
        user_answers = st.session_state.user_answers[quiz_id]
        # Display results and store them
        for idx, (user_answer, correct_answer, explanation) in enumerate(
            zip(user_answers, [q[2] for q in quiz_parsed], [q[3] for q in quiz_parsed])
        ):
            is_correct = user_answer.strip() == correct_answer.strip()
            if is_correct:
                total_correct += 1

            quiz_results.append(
                {
                    "question": quiz_parsed[idx][0],
                    "user_answer": user_answer,
                    "correct_answer": correct_answer,
                    "is_correct": is_correct,
                }
            )

            color = "#2ECC71" if is_correct else "#E74C3C"
            st.markdown(
                f"<h4 style='color:{color}'>Q{idx + 1}: Your answer: {user_answer} - Correct answer: {correct_answer} - {explanation}</h4> ",
                unsafe_allow_html=True,
            )

        # Store the results in session state
        if "quiz_results" not in st.session_state:
            st.session_state.quiz_results = {}
        if (
            quiz_id not in st.session_state.quiz_results.keys()
            and total_correct / len(user_answers) >= 0.8
        ):
            st.balloons()

        st.session_state.quiz_results[quiz_id] = quiz_results
        st.markdown(f"You got {total_correct} out of {len(user_answers)} correct.")


def get_flashcard_color(index):
    """
    The get_flashcard_color function takes an index and returns a color.
        The colors are chosen from a list of colors, and the function will return the same color for any given index.
        This is useful because it allows us to assign each flashcard its own unique color.

    :param index: Determine which color to return
    :return: A color from the colors list
    :doc-author: Yusuf
    """
    colors = [
        "#FF6347",
        "#4682B4",
        "#32CD32",
        "#e6c200",
        "#FF69B4",
        "#8A2BE2",
        "#FFA500",
        "#00FF7F",
        "#FF00FF",
        "#00FFFF",
        "#0000FF",
        "#FF0000",
    ]
    return colors[index % len(colors)]


def visualize_quiz_results(scores, total):
    # Check if scores and total are provided
    """
    The visualize_quiz_results function takes in the scores and total from the quiz results,
    and displays a bar chart for module-wise quiz results and a pie chart for overall quiz results.
    
    
    :param scores: Pass in the scores of each module
    :param total: Store the total number of correct answers and total questions
    :doc-author: Yusuf
    """
    if scores is None or total is None:
        st.write("No quiz results to display.")
        return

    # Extracting data for visualization
    modules = []
    correct_counts = []
    total_questions = []
    for score in scores:
        if score is not None:
            modules.append(
                wrapper.fill(
                    score.get("module_title").replace(":", ":\n").replace("**", "")
                )
            )
            correct_counts.append(score["correct_answer_count"])
            total_questions.append(score["total_questions"])

    # Bar chart for module-wise quiz results
    fig, axs = plt.subplots(
        1, 2, figsize=(12, 6)
    )  # Adjusting for two subplots side by side

    # Bar chart on the first subplot
    axs[0].bar(modules, correct_counts, color="green")
    axs[0].bar(
        modules,
        [total_questions[i] - correct_counts[i] for i in range(len(correct_counts))],
        bottom=correct_counts,
        color="red",
    )
    axs[0].set_xlabel("Modules")
    axs[0].set_ylabel("Number of Questions")
    axs[0].set_title("Quiz Results per Module")
    axs[0].legend(["Correct Answers", "Wrong Answers"])

    # Pie chart for overall quiz results
    total_correct = total["correct_answer_count"]
    total_incorrect = total["total_questions"] - total_correct
    axs[1].pie(
        [total_correct, total_incorrect],
        labels=["Correct Answers", "Wrong Answers"],
        colors=["green", "red"],
        autopct="%1.1f%%",
        startangle=90,
    )
    axs[1].set_title("Overall Quiz Results")

    # Display the charts
    st.pyplot(fig)

    # Display overall total
    st.write(
        f"Total correct answers across all modules: {total_correct} out of {total['total_questions']}"
    )


def handle_module_click(index, type):
    # For demonstration purposes, we're just printing the index
    """
    The handle_module_click function is called when a user clicks on a module in the curriculum.
    It updates the session state with information about which module was clicked, and what type of action to take next.
    The function takes two arguments: index (the index of the module that was clicked) and type (the type of action to take).
    
    
    :param index: Identify which module was clicked
    :param type: Determine what kind of button is clicked
    :doc-author: Yusuf
    """
    print(f"INFO: Module {index} clicked")
    index = index + 1

    st.session_state["last_module"] = index

    if type == "module":
        st.session_state["sidebar_request"] = f"Proceed to module {index}"
    elif type == "quiz":
        st.session_state["quiz_curriculum_id"] = f"quiz_{index}"
        st.session_state["sidebar_request"] = f"Evaluate me on Module {index}"
    elif type == "analyse":
        st.session_state["sidebar_request"] = "Analyse me"


def create_conf_buttons():
    """
    The create_conf_buttons function creates a set of buttons that allow the user to select their desired configuration.
        The function returns the selected configuration as a list of strings.
    
    :return: A list of user configs
    :doc-author: Yusuf
    """
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        depth_option = st.selectbox("🎯Depth", ["Beginner", "Intermediate", "Expert"])
    with col2:
        style_option = st.selectbox(
            "🥘Dishes Style",
            ["All World", "Asian", "European", "American", "South-American", "African"],
        )
    with col3:
        time_option = st.selectbox("⏱Time", ["Short", "Medium", "Long"])
    with col4:
        communication_option = st.selectbox(
            "🗣️Communication", ["Image-Containing", "Text-Only"]
        )
    with col5:
        language_option = st.selectbox(
            "🌐Language", ["English", "Chinese", "Turkish", "German"]
        )
    # user_config = depth_option + ' ' + style_option + ' ' + time_option + ' ' + dish_option + ' ' + communication_option + ' ' + language_option
    user_config = [
        depth_option,
        style_option,
        time_option,
        communication_option,
        language_option,
    ]

    if st.session_state.get("last_config") != user_config:
        st.session_state["config_changed"] = True
        print("USER CONFIG is changed")
        (
            depth_option,
            style_option,
            time_option,
            communication_option,
            language_option,
        ) = user_config
        st.session_state.config_prompt = f"""
            Here is the user configuration: Make sure that the user your generated content is suitable for the following configs:
                The user is {depth_option} at cooking, user prefers a  dish from {style_option if style_option != 'All World' else 'everywhere so it does not matter'}, user wants to spend a {time_option} time on cooking, and your answer MUST be in {language_option} language.
        """
        st.session_state["configs"] = user_config
        st.session_state["last_config"] = user_config
    else:
        st.session_state["config_changed"] = False
    return user_config

    # Define the function that will be called when a button is clicked


def create_prompt_button(prompt):
    """
    The create_prompt_button function will create a button with the prompt text as its label.
    When the user clicks on this button, it will set the value of chat_input to be equal to that prompt.
    This is useful for creating buttons that can be used to quickly populate chat_input with some pre-defined text.
    
    :param prompt: Set the text of the button
    :return: A function that is called when the button is clicked
    :doc-author: Yusuf
    """
    if st.button(prompt):
        # This will set the text of the chat_input to the selected prompt
        st.session_state["prepopulated_text"] = prompt


def on_prompt_button_clicked(prompt):
    """
    The on_prompt_button_clicked function is called when the user clicks on a prompt button.
    It sets the value of text_input to be equal to the selected prompt, and then calls st.chat_input(prompt)
    
    :param prompt: Set the value of the text_input to the selected prompt
    :return: The value of the selected prompt
    :doc-author: Yusuf
    """
    st.session_state.user_input = (
        prompt  # This sets the value of the text_input to the selected prompt
    )
    # st.chat_input(prompt)


def display_images(image_url):
    """
    The display_images function takes a URL to an image and displays it in the Streamlit app.
    
    
    :param image_url: Display the image in the streamlit app
    :return: An image url
    :doc-author: Yusuf
    """
    if image_url is None:
        st.write("No images to display.")
        return
    print("INFO: Image URL: ", image_url)
    st.markdown(
        f"""
        <style>
        .img-container {{
            border-radius: 15px;  # Adjust the radius as needed
            overflow: hidden;
        }}
        .img-container img {{
            display: block;
            width: 100%;
        }}
        </style>
        <div class="img-container">
            <img src="{image_url}" alt="image">
        </div>
        """,
        unsafe_allow_html=True,
    )
