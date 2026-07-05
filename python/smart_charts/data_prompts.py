import base64

def build_analysis_prompt(context: str, description: str, chartData: str, question: str= '') -> str:    
    """
        build a json prompt for older support (non chat completions)
    """
    prompt = f"""{context}\n 
    {chartData}\n
    {description}\n
    {question}
    """
        
    return prompt


def build_chart_prompt(chartInfo: dict) -> str:    
    """
    Converts chart data dictionary into a natural language string with bullet points.
    """
    prompt_parts = []
    for key, value in chartInfo.items():
        if isinstance(value, list):
            if isinstance(value[0], (int, float)): # Check if list contains numbers
                # value_str = ", ".join(map(str, value))
                value_str = ", ".join([f"{item:.5f}" for item in value]) # Round numeric list items
            else:
                value_str = "- " + "\n- ".join(map(str, value)) # handles lists of string
        elif isinstance(value, (int, float)):            
            value_str = f"{value:.5f}"  # Round numeric values
        else:
            value_str = value
        prompt_parts.append(f"* {key.capitalize()}: {value_str}")
    return "\n".join(prompt_parts)



def build_chart_image_prompt(image_path: str,chart_type, chartData) -> str:
    """
    Analyzes a chart image using Google Generative AI.

    Args:
        image_path: Path to the chart image file.

    Returns:
        str: Textual analysis of the chart.
    """

    with open(image_path, "rb") as image_file:
        image_data = image_file.read()

    base64_encoded_image = base64.b64encode(image_data).decode('utf-8')

    prompt_img = f"""
    Analyze the following {chart_type} image and data:
    [Image of {base64_encoded_image}]\n
    {chartData}\n
    """

    prompt_text = f"""  
    Provide a concise description of the chart, including:
    Type of chart (e.g., bar chart, line chart, pie chart)
    Key trends and patterns observed in the data
    Any notable features or anomalies 

    Be as specific as possible in your description.
    """
    
    prompt = prompt_img + prompt_text
    
    return prompt