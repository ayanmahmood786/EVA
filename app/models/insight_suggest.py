from time import time  # Import the time module correctly
import os
import google.generativeai as genai
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI

from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.runnables import RunnablePassthrough
import json

from langgraph.graph import StateGraph, END
from typing import TypedDict, Dict, Any, Optional
from langgraph.graph import START

from core.function import format_answer
# API Key Configuration
os.environ['API_KEY'] = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=os.environ["API_KEY"])

# Initialize model
model = genai.GenerativeModel("gemini-2.0-flash", generation_config={"temperature": 0.50})
llm= GoogleGenerativeAI(model="gemini-2.0-flash",temperature=0.25)

total_tokens = None
output_tokens =None
prompt_tokens=None
elapsed_time = None  
import json

with open(r"dir/insight_format.json","r") as file:
    content=file.read()
    json_file=json.loads(content)
from rapidfuzz import fuzz
def similar_questions(q2):

    try:
        with open(r"dir/insight_format.json", "r", encoding="utf-8") as file:
            json_file = json.load(file)
    except FileNotFoundError:
        return {"Format": "Error: The 'insight_format.json' file was not found."}
    except json.JSONDecodeError:
        return {"Format": "Error: The 'insight_format.json' file is not a valid JSON."}

    best_score = -1
    best_key = None

    # Find the key with the highest similarity score
    for key in json_file.keys():
        similarity_score = fuzz.ratio(key.lower(), q2.lower())
        if similarity_score > best_score:
            best_score = similarity_score
            best_key = key
    
    # Determine which file path to use based on the score
    threshold =87
    if best_score > threshold:
        # A good match was found, use its file path
        file_path_to_read = json_file.get(best_key)
    else:
        # No good match, use the default file path
        file_path_to_read = json_file.get("Default")

    # Read the content from the selected file path
    if file_path_to_read:
        try:
            with open(file_path_to_read, "r", encoding="utf-8") as prompt_file:
                content = prompt_file.read()
            return {"Format": content}
        except FileNotFoundError:
            return {"Format": f"Error: The prompt file '{file_path_to_read}' was not found."}
        except Exception as e:
            return {"Format": f"Error reading file '{file_path_to_read}': {e}"}
    else:
        # This is a fallback in case the "Default" key is missing from the JSON
        return {"Format": os.getenv('DEF_PROMPT')}

def insightsuggestions(question, previous_question,data):
    format=similar_questions(question)
    # Define the prompt template
    prompt="""
    Previous Conversation Question CONTEXT (if relevant): {previous_question}.
    
    Provide Detailed Insights based on user question.


    **Objective**:
    - Provide a clear, data-focused answer to the question: "{question}".

    - Data:{data}
    

    **Answer Requirements**:
    1. **Tone & Audience**:
        - Write in a professional tone, presenting insights with clarity and precision.
        -   Key terms in bold .
        - **Structure**: Use bullet points to present each main insight clearly in short points only.
        - While Providing Numbers use "billions","millions" etc.
        - provide numerical data only using data.
        - Provide the whole insight into html form only.
        - Use emojis
        - DOnt use dollar, any currency sign.

    2. Output Consist Of following Headings in text (Numerical and statistical metrics described in the data use that only):
        {format}


    3. **Follow-Up Question**:
        - 20-30 words long.
        - Easy to answer using 1–2 lines of pandas code.
        - generate questions about breakdowns of values, monthwise breakdowns, Percentage contributions etc. .
        - Do not provide questions about correlation, seasonal trends.
        - Designed to be exploratory or comparative.
        - Focused on filters, groupbys, ranking, or time-based trends.

    4. Formatting:
        - Use Numbers for main title 
        Write answer to user question in html only.
        Scroll bar is mandatory in table card.
    
    
    
    You are a front-end UI expert. Generate a modern, responsive HTML dashboard using **Tailwind CSS**, **Google Fonts (Poppins)**, and **Material Icons**. Follow these design and layout rules:

        1. **Use Tailwind CSS via CDN** (`https://cdn.tailwindcss.com?plugins=forms,container-queries`).
        2. **Use Poppins font** via Google Fonts and apply it to the body.
        3. Use a **gradient header** (`from-indigo-500 to-pink-500`) only a title with 3 - 5 words.
        4. Use **rounded cards** with **shadow**, **hover animation**, and **padding**. Cards should be in a vertical `grid gap-6` layout.
        5. Each card should:
            - Have a **left icon box** using a soft accent background (`purple-100`, `pink-100`, etc.).
            - Include a **section heading** and short description.
            - Contain a **highlighted result or insight**, such as a large number or tag.
            - Always write point tags for lines.
            - For a single card the adjust the width automatically .
            - Dynamically adjust the width of the card.

        6. Ensure responsive spacing (`p-4 md:p-8`) and clean, readable text hierarchy (`text-xl`, `text-2xl`, `font-semibold`, etc.).
        7. Use utility classes for **colors**, **rounded corners**, **flex layout**, **spacing**, and **typography**. No external CSS or JS.
        8. Include relevant **Material Icons** for each section (like `insights`, `lightbulb`, etc.).
        9. Keep the design minimal and modern with **subtle interactivity** (`hover:shadow-2xl`, `hover:-translate-y-1`, etc.).
        10. Insight card should in one card and in one column and have points start with emoji with indentation.
        11. Also show Small Cards and it should be in 2 columns with few words and key figures and centeralized.
        12. Padding for cards show be 10px only.
        14. Adjust all the content width automatically.
        15. No need to provide table unless described in format.
        Do not provide additional questions.
        Do not provide any sample data in the response if you have not gotten any data responsed with I need data for anaylsis.
    
        Output a full HTML file with `<!DOCTYPE html>`, `<html>`, `<head>`, and `<body>` sections.
        Write full code html in Answer_to_user_question.

    **Final Output Format (JSON)**:

        {{
        "Answer_to_user_question": "write whole text in html format no need to suggested question in this",
        "Auto_prompt": {{
            "Question_1": "",
            "Question_2": "",
            "Question_3": ""
        }}
        }}
    """

    try:
        prompt = PromptTemplate(template=prompt, input_variables=["question", "previous_question", "data","format"])
        prompt_formatted_str = prompt.format(question=question, previous_question=previous_question,data=data,format=format['Format'])
        prediction = model.generate_content(prompt_formatted_str)
        return prediction.text

    except ValueError as e:
        print(f"Error parsing JSON: {e}")
        print(status_code=500, detail="Error generating response from AI")



# Initialize model (assuming you have this configured)
model = GoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.5)

# def similar_questions(question):
#     """Function to get similar questions format - placeholder implementation"""
#     return {"Format": "Main Insights, Key Metrics, Detailed Analysis"}

def conversion_module(question, previous_question, data, Instructions=""):
    """
    Handles the conversion of data into insights and HTML formatting
    """
    print(Instructions)
    if Instructions == "":
        format_info = similar_questions(question)
        format_info = format_info['Format']
    else:
        format_info = Instructions
    print(format_info)
    # print(format_info[:100])
    conversion_prompt = """
**Objective**:
- Do not provide any additional text or explanations about html.
- Provide comprehensive, data-driven insights with deep analysis based on the question: "{question}"
- Data Source: {data}



- Previous Context (if relevant): {previous_question}

- Every content should in html card form only.


**Insights format show be  build on the  this instructions only**: {format}

**Answer Requirements**:

1. **Tone & Audience**:
   - Professional, executive-level presentation with strategic insights
   - Data-driven storytelling with clear narrative flow
   - **Key terms in bold** for emphasis
   - Use **"billions"**, **"millions"**, **"thousands"** appropriately for large numbers
   - **Absolute numerical precision** - always provide exact figures alongside scaled versions
   - **No currency symbols** - use descriptive terms instead (e.g., "revenue" instead of "$")
   - Strategic recommendations based on data patterns
   


3. **Visual Design Requirements**:
   - **Modern HTML dashboard** using Tailwind CSS via CDN
   - **Poppins font** from Google Fonts with proper weight hierarchy
   - **Gradient header** (indigo-500 to pink-500) with concise 3-5 word title
   - **Rounded cards** with shadow, hover animation, and consistent 10px padding
   - **Two-column layout** for metric cards with centralized alignment
   - **Single-column layout** for detailed insight cards
   - **Icon system**: Material Icons with soft accent backgrounds (purple-100, pink-100, etc.)
   - **Responsive spacing**: p-4 md:p-8 for containers
   - **Typography hierarchy**: Clear text sizing (xl, 2xl, etc.) with semantic emphasis

4. **Data Presentation Standards**:
   - **All numbers formatted properly**: 1,20,200 format for large numbers
   - **Emoji usage**: Relevant emojis for quick visual scanning.
   - **Right-aligned numbers** for easy comparison
   - **Color-coded indicators** for positive/negative trends (green/red accents)
   - **Percentage changes** shown with directional indicators (↑↓)
   - **Bullet Point** while presenting a sentence inside the card. 
   - **Benchmark comparisons** where data allows

6. **Technical Implementation**:
   - Use Tailwind CSS via CDN with forms and container-queries plugins
   - Include Google Fonts (Poppins) and Material Icons properly
   - Ensure mobile-responsive design with breakpoint handling
   - Implement hover effects: hover:shadow-2xl, hover:-translate-y-1
   - Maintain clean, production-ready HTML without external CSS/JS
   - Automatic width adjustment for all content elements

7. **Section Organization**:
   - **Header**: Gradient banner with main title
   - **Executive Overview**: 3-5 key metrics with largest impact
   - **Detailed Analysis**: Multiple cards with emoji-led bullet points
   - **Comparative Metrics**: Two-column cards with benchmark data
   - **Trend Analysis**: Time-based patterns and seasonal insights
   - **Recommendations**: Actionable insights with priority ranking



**Critical Instructions**:
- Provide numerical data with exact figures AND scaled versions
- Include both absolute numbers and percentage changes
- Use emojis as visual anchors for each insight point
- Maintain professional tone while making complex data accessible
- Ensure every insight has clear business relevance
- Connect data points to tell a cohesive story in a card form
- Highlight unexpected findings and anomalies
- Provide everything into a card form.

Generate comprehensive HTML dashboard with deep, multi-layered insights.
"""

    try:
        prompt = PromptTemplate(
            template=conversion_prompt, 
            input_variables=["question", "previous_question", "data", "format"]
        )
        prompt_formatted_str = {
            "question":question, 
            "previous_question":previous_question, 
            "data":data, 
            "format":format_info
        }
        print(format_info)
        html_chain={"question":RunnablePassthrough(),"previous_question":RunnablePassthrough(),"data":RunnablePassthrough(),"format":RunnablePassthrough() } |  prompt | model
        return {"answer": html_chain.invoke(prompt_formatted_str)}

    except Exception as e:
        print(f"Error in conversion module: {e}")
        return {"answer": f"Error in conversion: {str(e)}"}


def question_generation_module(question, previous_question, data):
    """
    Handles the generation of follow-up questions
    """
    question_prompt = """
    Based on the user question: "{question}"
    Previous context: "{previous_question}"
    And the available data: {data}

    Generate 3 follow-up questions that are:
    - 12–15 words long
    - Include a measurable metric, number, or stat visible in the data
    - Easy to answer using 10-20 lines of pandas code
    - Designed to be exploratory or comparative
    - Focused on filters, groupbys, ranking, or time-based trends
    - Third question should be a little bit advanced like growth rates etc.

    Return ONLY a JSON object with the following structure:
    {{
        "Question_1": "first question here",
        "Question_2": "second question here", 
        "Question_3": "third question here"
    }}
    """

    try:
        prompt = PromptTemplate(
            template=question_prompt,
            input_variables=["question", "previous_question", "data"]
        )
        # prompt_formatted_str = prompt.format(
        #     question=question,
        #     previous_question=previous_question,
        #     data=data
        # )
        chain=prompt | model
        prediction = chain.invoke({"question": question, "previous_question": previous_question, "data": data})
        
        # Parse the JSON response
        print(prediction)
        prediction=prediction.replace("```json","").replace("```","")
        questions = json.loads(prediction)
        return {"questions": questions}

    except Exception as e:
        print(f"Error in question generation module: {e}")
        return {"questions": {
            "Question_1": "What are the top performing categories by sales volume?",
            "Question_2": "How has customer acquisition trended over the last quarter?",
            "Question_3": "Which regions show the highest growth in user engagement?"
        }}



class AgentState(TypedDict):
    question: str
    previous_question: str
    data: Any
    conversion_result: Dict[str, Any]
    question_result: Dict[str, Any]
    final_output: Dict[str, Any]
    Instructions: Optional[str] = ""


def create_insight_suggestion_graph():
    # Initialize the graph
    workflow = StateGraph(AgentState)
    
    # Define nodes
    def conversion_node(state: AgentState):
        print("Running conversion node...")
        result = conversion_module(
            state["question"],
            state["previous_question"],
            state["data"],
            state["Instructions"]
        )
        return {"conversion_result": result}
    
    def question_generation_node(state: AgentState):
        print("Running question generation node...")
        result = question_generation_module(
            state["question"],
            state["previous_question"],
            state["data"]
        )
        return {"question_result": result}
    
    # Add nodes
    workflow.add_node("conversion", conversion_node)
    workflow.add_node("question_generation", question_generation_node)
    
    # Add parallel execution
    workflow.add_conditional_edges(
        START,
        lambda state: ["conversion", "question_generation"],
        ["conversion", "question_generation"]
    )
    
    # Add merge node
    def merge_results(state: AgentState):
        print("Merging results...")
        return {
            "final_output": {
                "Answer_to_user_question": format_answer(state["conversion_result"]["answer"].replace("```html","").replace("```","")),
                "Auto_prompt": state["question_result"]["questions"]
            }
        }
    
    workflow.add_node("merge", merge_results)
    workflow.add_edge("conversion", "merge")
    workflow.add_edge("question_generation", "merge")
    
    # Add final edge
    workflow.add_edge("merge", END)
    
    # Compile the graph
    return workflow.compile()

# Create the graph instance
insight_graph = create_insight_suggestion_graph()

# Simple synchronous version using invoke instead of ainvoke
def insightsuggestions(question, previous_question, data, Instructions):
    """
    Simple synchronous version using .invoke() instead of .ainvoke()
    """
    # Initialize state
    initial_state = AgentState(
        question=question,
        previous_question=previous_question,
        data=data,
        conversion_result={},
        question_result={},
        final_output={},
        Instructions=Instructions
    )
    
    try:
        # Execute the graph synchronously
        result = insight_graph.invoke(initial_state)
        return result["final_output"]
    
    except Exception as e:
        print(f"Error in insightsuggestions: {e}")
        return {
            "Answer_to_user_question": f"Error processing request: {str(e)}",
            "Auto_prompt": {
                "Question_1": "What are the main trends in the data?",
                "Question_2": "Which categories show the highest performance?",
                "Question_3": "How has the data changed over time?"
            }
        }

