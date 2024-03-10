import streamlit as st
from langchain.prompts import PromptTemplate

PREFIX = """
You are an personalized cooking assistant that aims to help the user cook and answer their question about cooking.
If the user want to learn how to cook a dish, you try your best to follow the user's configuration and
provide a suitable and perfect curriculum for them to teach how to cook this dish.
You also be able to answer their questions, you try to answer in as detailed as you can, and make it easy to understand.
When you generated curriculum, you must wait user input to proceed(start teaching) any module.
"""

SUFFIX = """Begin!
{chat_history}
Question: {input}
{agent_scratchpad}
"""


def get_prompts():
    if "config_prompt" not in st.session_state:
        st.session_state["config_prompt"] = ""

    answer_user_question_template = (
        """ 
    You should answer the user's question in detail, and make it easy to understand. Make sure that answer is related to the question.
    Conversation history: {chat_history}
    User question: {input}
    """
        + st.session_state.config_prompt
    )

    answer_question_prompt = PromptTemplate(
        input_variables=["chat_history", "input"],
        template=answer_user_question_template,
    )

    curriculum_template = (
        """ When the user want to learn how to cook {topic}, your responsibility is teaching {topic} to user.
    Create a curriculum for {topic} that contains submodules. Also add directions like what user should learn in each module and submodule to generated context.
    Number of modules is up to you.
    
    
    Put "#" in front of before Modules and ## in front of before submodules, put '$$$' between each module to make it splittable by '$$$'.
    Follow this format to generate the curriculum: 
    
    
    # Module 1: [Module title]
    ###### Directions: [Directions for this module]
    ## :pushpin: Submodule 1.a: [Submodule title]
    ###### Directions: [Directions for this submodule]
    ## :pushpin: Submodule 1.b: [Submodule title]
    ###### Directions: [Directions for this submodule]
    
    $$$      
    
    # Module 2: [Module title]
    ###### Directions: [Directions for this module]
    ## :pushpin: Submodule 2.a: [Submodule title]
    ###### Directions: [Directions for this submodule]
    ## :pushpin: Submodule 2.b: [Submodule title]
    ###### Directions: [Directions for this submodule]
          
          
    Additional Instructions:
        The curriculum should be in markdown format
        Make every module title in bigger font and make bolded text to emphasize important points 
        Number of modules must be 2 or 3 module if user have short time, 3 or 4 modules if user have medium time, and up to 7 if user have long time.
        Dont write wrong :pushpin: since it is an emoji code
        
    
    User Configuration:
    """
        + st.session_state.config_prompt
    )
    curriculum_prompt = PromptTemplate(
        input_variables=["topic"], template=curriculum_template
    )

    module_prompt = (
        """
    Generate content for the following curriculum. Make sure that the generated content is suitable for the user's configuration.
    You can add new submodules if user specifically want to learn something new in this module. You should also be careful {extra_config} while generating the content.
    
    {module}

    User Configuration:
    """
        + st.session_state.config_prompt
    )

    module_prompt = PromptTemplate(
        input_variables=["extra_config", "module"], template=module_prompt
    )
    evaluation_prompt_template = (
        """
    Please generate a set of Single-Choice-Questions following the strict output format provided. Each question should assess the user's understanding of the module content and should align with the user's configuration settings. The number of questions should correspond to the user's configuration preferences.

    For each question, provide four distinct options and clearly indicate the correct answer with an explanation. Ensure that the structure of the output is a list of lists, with each inner list containing exactly four elements: the question text, a list of options, the correct answer prefixed with 'Answer:', and the explanation for the correct answer.

    Below is the module content and user configuration based on which you should generate the questions:

    Module Content:
    {module_content}


    Remember to list the options vertically below each question when presenting them. The format for each question should look like this:

    - "Question Text"
    - ["Option 1", "Option 2", "Option 3", "Option 4"]
    - "Answer: Correct Option"
    - "Explanation for why the correct option is the right answer."

    Repeat this structure for the number of questions specified in the user configuration. Put a #### between each question to make the output splittable.


    Module content: {module_content}
    
    The choices provided are listed vertically below the question
    User Configuration:
    """
        + st.session_state.config_prompt
    )
    evalue_prompt = PromptTemplate(
        input_variables=["module_content"], template=evaluation_prompt_template
    )

    flashcard_template = (
        """
    I want you to act as a professional flashcard creator, able to create flashcards from module content I provided and user inputs and outputs in memory that related to module content .
    The cards only contain the most important information, and the wording of the cards is optimized to ensure that in minimum time the right bulb in your brain lights up.
    Number of word in content is up to you but make sure that it is generally  1-3 words.
     
     
     Regarding the formulation of the card content, you stick to two principles: 
     First, minimum information principle: The material you learn must be formulated in as simple way as it is only possible. 
     Simplicity does not have to imply losing information and skipping the difficult part. 
     Second, optimize wording: The wording of your items must be optimized to ensure that in minimum time the right bulb in your brain lights up. 
     This will reduce error rates, increase specificity, reduce response time, and help your concentration. 
     
     
     Your output should be in this format:
     
     
     First Flash Card #### Second Flash Card #### Third Flash Card  #### Nth Flash Card
     Note: Make sure that output is splittable by '####' characters
    
    Module content: {module_content}
    
    
     User Configuration:
    """
        + st.session_state.config_prompt
    )
    flashcard_prompt = PromptTemplate(
        input_variables=["module_content"], template=flashcard_template
    )

    analysis_module_template = """
    Act as a reviewer and you are supplied with the user wrong answers, and correct answers. Firstly, you should look user statistics on test, write a report for user which includes positive and negative feedbacks if they are exists. 
    Assume that user name is "User" and you are writing a report for "User".
    
    {statistics}
    You should prepare a module content to help the user understand why they are wrong and how to fix it.
    
    
    
    {user_wrong_content}"""
    analysis_module_prompt = PromptTemplate(
        input_variables=["statistics", "user_wrong_content"],
        template=analysis_module_template,
    )

    extract_template = """You should extract the key elements of the module content, which includes the definitions, the examples and this kind of things.
    Module content: {module_content}"""
    extract_prompt = PromptTemplate(
        input_variables=["module_content"], template=extract_template
    )

    return (
        answer_question_prompt,
        curriculum_prompt,
        module_prompt,
        evalue_prompt,
        flashcard_prompt,
        analysis_module_prompt,
        extract_prompt,
    )
