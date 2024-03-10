from langchain.chains import LLMChain, ConversationChain
from prompts import get_prompts

def get_chains(llm, memory):
    answer_question_prompt, curriculum_prompt, module_prompt, evalue_prompt, flashcard_prompt , analysis_module_prompt, extract_prompt = get_prompts()
    answer_question_chain = ConversationChain(llm=llm,
                                              prompt=answer_question_prompt,
                                              verbose=True,
                                              memory=memory
                                              )
    # use the generate curriculum chain to generate curriculum
    generate_curriculum_chain = LLMChain(llm=llm,
                                         prompt=curriculum_prompt,
                                         verbose=True,
                                         )
    evaluation_chain = LLMChain(llm=llm,
                                prompt=evalue_prompt,
                                verbose=True,
                                memory=memory,
                                )
    return answer_question_chain, generate_curriculum_chain, module_prompt, evaluation_chain , flashcard_prompt, analysis_module_prompt, extract_prompt
