import os
import sys

sys.path.append(os.path.abspath("."))
import streamlit as st

st.set_page_config(
    page_title="The Chef",
    page_icon="🧑‍🍳",
    layout="wide",
    initial_sidebar_state="auto",
)

from utils import (
    create_conf_buttons,
    display_images,
    display_quiz,
    get_flashcard_color,
    handle_module_click,
    initialize_llm,
    initialize_ui,
    visualize_quiz_results,
)

initialize_ui()
from langchain.callbacks import StreamlitCallbackHandler

from agent import get_agent
from tools import calculate_score


def run_agent(user_input):
    # Add user message to chat history
    """
    The run_agent function is the main function that runs the chatbot.
    It takes in a user input and displays it in a chat message container.
    Then, it calls on an agent to respond to this user input and display its response 
    in another chat message container.
    
    :param user_input: Pass the user's input to the agent
    :doc-author: Yusuf
    """
    st.session_state.messages.append({"role": "user", "content": user_input})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(user_input)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("I am thinking ..."):
            container = st.container()
            st_cb = StreamlitCallbackHandler(container)
            print("\nINFO: User input: ", user_input)
            response = agent.run(user_input, callbacks=[st_cb])
        if response.startswith("Quiz generated "):
            quiz = response.replace("Quiz generated ", "")
            quiz_id = st.session_state.get("quiz_curriculum_id", "quiz_unknown")
            st.session_state.messages.append(
                {"role": "assistant", "content_quiz": quiz, "id": quiz_id}
            )
            display_quiz(quiz_id)
        elif response.startswith("ANALYSIS:"):
            analysis = response.replace("ANALYSIS:", "")
            scores, total = calculate_score(return_string=False)
            visualize_quiz_results(scores, total)
            st.markdown(analysis)
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "analysis": analysis,
                    "scores": scores,
                    "total": total,
                }
            )
        elif response.startswith("Image generated "):
            output = response.replace("Image generated ", "")
            image_url = st.session_state["image_url"][
                st.session_state["last_module_number"]
            ]
            display_images(image_url)
            st.markdown(output)
            st.session_state.messages.append(
                {"role": "assistant", "output": output, "image_url": image_url}
            )

        else:
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        # print(f' Memory: {st.session_state["memory"].load_memory_variables({})}')


if __name__ == "__main__":

    # Display the header and sidebar
    st.header(
        "🧑‍🍳 The Chef: Anytime, Anywhere, Just for You, Understanding You Better Than You Do"
    )
    (
        st.session_state["llm"],
        st.session_state["memory"],
        st.session_state["readonlymemory"],
    ) = initialize_llm()
    agent = get_agent()

    # set user configuration
    user_config = create_conf_buttons()

    if st.session_state.get("config_changed", False):
        if "llm" in st.session_state:
            agent = get_agent()  # Recreate or update the agent
        # Reset the flag
        st.session_state["config_changed"] = False

    if "user_input" not in st.session_state:
        st.session_state["user_input"] = ""
    # Initialize chat history if not already present in session state
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {
                "role": "assistant",
                "content": "Hi, I am personalized cooking assistant for you.",
            }
        ]
        # Configure the Streamlit page
    # if 'user_config' not in st.session_state:
    #    st.session_state["user_config"] = ""

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if "content" in message:
                st.markdown(message["content"])
            elif "content_quiz" in message:
                display_quiz(message["id"])
            elif "analysis" in message:
                visualize_quiz_results(message["scores"], message["total"])
                st.markdown(message["analysis"])
            elif "image_url" in message:
                display_images(message["image_url"])
                st.markdown(message["output"])

    # Initialize session state for prepopulated text if not present
    if "prepopulated_text" not in st.session_state:
        st.session_state["prepopulated_text"] = ""

    # Example prompts
    prompts = """how to cook a steak?"""
    continue_button = st.button(prompts, key=prompts)

    print(
        "INFO: sidebar_request from sidebar: ", st.session_state.get("sidebar_request")
    )
    if (
        user_input := st.chat_input("What is your action?")
        or continue_button
        or st.session_state.get("sidebar_request", None) is not None
    ):
        if continue_button:
            user_input = prompts
        if st.session_state.get("sidebar_request") is not None:
            print(
                "INFO: sidebar_request from sidebar: ",
                st.session_state.get("sidebar_request"),
            )
            user_input = st.session_state.get("sidebar_request")
            st.session_state["sidebar_request"] = None
            print("INFO: Side bar request is detected")
        run_agent(user_input)

    if "curriculum" in st.session_state and st.session_state["curriculum"] != "":
        with st.sidebar:
            st.markdown("# Curriculum")

            # Iterate through each module in the curriculum
            for idx, module_markdown in enumerate(st.session_state["curriculum"]):
                # Split the markdown content by '##' to separate the title from the content
                module_parts = module_markdown.split("##")
                module_title = module_parts[0].split("\n")[0].replace("#", "").strip()
                module_content = "\n".join(module_markdown.split("\n")[1:])

                # Create a unique key for each button based on the module index
                button_key = f"module_button_{idx}"
                quiz_key = f"quiz_button_{idx}"
                # Use columns to place the button next to the module title
                col1, col2 = st.columns([0.8, 0.2], gap="small")
                with col1:
                    with st.expander(module_title):
                        st.markdown(module_content)
                        # Display flashcards under the title
                        if (
                            st.session_state.get("flashcard", None) is not None
                            and st.session_state["flashcard"][idx] is not None
                        ):
                            st.markdown("\n\n--- Flashcards ---")
                            for card_idx, card in enumerate(
                                st.session_state["flashcard"][idx].split("####")
                            ):
                                # Create a colored button for each flashcard
                                button_html = f"<button style='background-color: {get_flashcard_color(card_idx)}; color: white; border: none; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer;'>{card}</button>"
                                st.markdown(button_html, unsafe_allow_html=True)
                with col2:
                    # Create a button with an emoji icon for each module
                    if st.button("📖", key=button_key):
                        handle_module_click(idx, "module")
                        st.experimental_rerun()
                    if st.button("📝", key=quiz_key):
                        handle_module_click(idx, "quiz")
                        st.experimental_rerun()

            c = st.container()
            # Green button
            if c.button("Analyse Me!", key="green_button", args={"color": "green"}):
                handle_module_click(idx, "analyse")
                st.experimental_rerun()
