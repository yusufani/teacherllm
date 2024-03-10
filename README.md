# README for Teaching Assistant Streamlit App
![Alternative Text](poster.png)

## Overview
This Streamlit application, developed by the team at the Technical University of Munich, Germany, is an innovative educational platform designed to revolutionize the learning process. Utilizing the advanced capabilities of OpenAI's GPT-4 Turbo and the Langchain library, it offers a unique, personalized learning experience. Our focus is on delivering an immersive educational journey in the cooking domain, though the technology can be adapted for virtually any subject area. The app dynamically generates personalized curriculum content, interactive quizzes, and utilizes user feedback to continually refine and enhance the learning experience.

## Features
- **Personalized Learning**: Tailors the curriculum and learning material to the user's preferences and skill level.
- **Interactive Learning Modules**: Engages users with interactive quizzes and hands-on modules to test their knowledge.
- **Advanced Performance Feedback**: Utilizes the Analyze Tool for detailed feedback on quiz performances, highlighting strengths and areas for improvement.
- **Multimodal Learning**: Supports text and image-based content, including dynamically generated images for visual learning.
- **Adaptive Learning Path**: Offers flashcards and additional resources for quick learning and revision.
- **Configurable User Experience**: Users can customize settings such as language, depth of knowledge, style, and learning pace.



## Installation
1. Ensure Python is installed on your system.
2. Clone the repository.
3. Install required packages:
    ```
    pip install -r requirements.txt
    ```
4. Set your OpenAI API key in the environment variables. .env file should include following content: 
   ``` 
   OPENAI_API_KEY = sk-...... 
   ``` 
5. Run the Streamlit app: 
   ```
   streamlit run main.py
   ```

## Usage
The application begins with a configuration panel where users set their learning preferences. It guides users through cooking modules based on these settings, providing quizzes and feedback to enhance learning effectiveness.


## Core Functionalities
- **Dynamic Content Generation**: Generates curriculum and learning materials tailored to user preferences.
- **Interactive Quizzes and Flashcards**: Tests knowledge and reinforces learning through quizzes and flashcards.
- **User Performance Analysis**: Offers detailed feedback on quiz results, identifying areas for improvement.
- **Adaptable Learning Experience**: Allows users to adjust preferences at any point to refine their learning journey.
- **Visual and Textual Learning**: Supports diverse learning modes with text-based instructions and generated images.

## Project Members

**Students:**

- Yusuf ANI (yusufani8@gmail.com)
- Yu Wu
- Yuhang Cai

**Advisor:**

- [Tobias Eder](https://soc.cit.tum.de/persons/tobias-eder/)


## Acknowledgments
Special thanks to Tobias Eder for guidance and supervision. Gratitude is also extended to the Social Computing Chair at TUM for providing OpenAI credits essential for this project.

## References

- [TUM Research Group Social Computing](https://www.soc.cit.tum.de/)


---
