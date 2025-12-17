from langchain.prompts import PromptTemplate
from core.function import append_to_excel
from core.utils import get_openai_callback


async def graph(df,llm_chat):
    list1 = [df[i].dtype for i in df.columns]
    prompt_template = """

You are an expert in Python and Pandas. Generate only Python code that visualizes data from the given DataFrame df.

Rules:
- Do not assume or create any sample data. df is already defined and contains real data.
- Do not preview or print the data.
- Do not write the codes in function form.
- Do not include comments or explanations. Output only executable code.
- Do not provide graph related to section count. 
- Do not use section column for plotting the graph.
- Use this:
    import matplotlib.ticker as mticker (mandatory to load this library)
    ax.yaxis.set_major_formatter(mticker.ScalarFormatter())
    ax.ticklabel_format(style='plain', axis='y')

    
Instructions

1. DataFrame Info
- Columns: {df}
- Data types: {datatype}
- Sample data: {sample}

2. Null Value Summary
- Before visualization, compute total missing values in the dataset using:
  missing_total = df.isnull().sum().sum()
- Ensure this variable exists in the code.

3. Visualization Rules
- Use Seaborn if producing a single-plot visualization.
- Use Matplotlib if producing multiple subplots.
- Use exactly one figure (plt.subplots()).
- Use a single color for all bars/plots/lines.
- Save the plot only with:
  plt.tight_layout()
  plt.savefig('output.jpg', dpi=300)
- Do not use plt.show() or fig.show().

4. Axis Formatting
- Disable scientific notation with:
  plt.ticklabel_format(style='plain')
- Rotate x-axis labels 45° with right alignment if labels are long or overlapping:
  ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')

5. Data Selection
- Use only the top 10 records for categorical comparisons.
- Add data labels on bar charts with ax.text().

6. Chart Selection Logic
- Line chart → time series or continuous trend data
- Scatter plot → relationship between two numeric variables
- Histogram → distribution of one numeric variable
- Box plot → comparing distributions across categories
- Pie chart → proportions of a whole (merge slices < 4% into “Others”)
- Bar chart → comparing discrete categorical values

7. General Constraints
- Do not modify or create any data.
- Draw exactly one graph per execution.
- Use DPI = 300.

# Code:
"""

    prompt = PromptTemplate(template=prompt_template, input_variables=["df", "datatype", "sample"])
    prompt_str = {
        
        "df":df.columns.tolist(),
        "datatype":list1,
        "sample":df.head().to_json(),
    }
    prompt_formatted_str = prompt.format(        df=df.columns.tolist(),
        datatype=list1,
        sample=df.head().to_json(),)

    chain = prompt | llm_chat
    with get_openai_callback() as cb:
        result = await chain.ainvoke(prompt_str)
        await append_to_excel("Graph","Generate A Graph for the given dataset",prompt_formatted_str,result.usage_metadata["total_tokens"],result.usage_metadata["input_tokens"],result.usage_metadata["output_tokens"],0,"llm_results.xlsx",result.content)

    return result.content
    
