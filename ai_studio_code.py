import streamlit as st
import sympy
import pandas as pd
import plotly.express as px
import openai
import os

# Configuration
st.set_page_config(page_title="Alpha-Replica", layout="wide")
st.title("∑ Alpha Computational Engine")

# Replace with your API Key or use an environment variable
os.environ["OPENAI_API_KEY"] = "your-api-key-here"
client = openai.OpenAI()

def parse_query_with_llm(query):
    """
    Uses an LLM to translate natural language into Python/SymPy code.
    """
    prompt = f"""
    You are a mathematical translator. Convert the user's request into a single executable Python code block.
    Use the 'sympy' library for math. The result must be stored in a variable named 'output'.
    
    User Query: "{query}"
    
    Return ONLY the python code. No explanations.
    Example: 
    Input: "derivative of x squared"
    Output: 
    import sympy
    x = sympy.symbols('x')
    output = sympy.diff(x**2, x)
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.replace("```python", "").replace("```", "")

def execute_computation(code):
    """
    Executes the generated code safely.
    """
    local_vars = {}
    try:
        exec(code, {}, local_vars)
        return local_vars.get('output', "No output generated.")
    except Exception as e:
        return f"Error in computation: {str(e)}"

# --- UI Layout ---
query = st.text_input("Enter your query (e.g., 'Integrate sin(x)', 'Factor x^2 + 2x + 1'):", 
                     placeholder="Compute something...")

if query:
    with st.spinner('Computing...'):
        # 1. Parse the intent into code
        python_code = parse_query_with_llm(query)
        
        # 2. Show the "Interpretation" (Wolfram Style)
        st.subheader("Input Interpretation")
        st.code(python_code, language='python')
        
        # 3. Execute and show results
        result = execute_computation(python_code)
        
        st.subheader("Result")
        if isinstance(result, sympy.Basic):
            st.latex(sympy.latex(result))
        else:
            st.write(result)
            
        # 4. Generate a plot if applicable
        if "x" in query.lower() and "symbols" in python_code:
            st.subheader("Visual Plot")
            try:
                # Basic plotting logic
                f = sympy.lambdify(sympy.symbols('x'), result, 'numpy')
                import numpy as np
                x_vals = np.linspace(-10, 10, 400)
                y_vals = f(x_vals)
                df = pd.DataFrame({'x': x_vals, 'y': y_vals})
                fig = px.line(df, x='x', y='y', title=f"Plot of {query}")
                st.plotly_chart(fig)
            except:
                st.info("Visual plot not available for this query type.")