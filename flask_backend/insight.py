import json
import requests
import yfinance as yf
import pandas as pd
import os

# Function to fetch company summary using Google Custom Search API
def get_company_summary(company_name):
    API_KEY = 'AIzaSyBLMz1HU6cTGsCdRq6Nsnyu8YtTu_DX2vY'  # Replace with your API key
    CSE_ID = 'f7b4bb29bdd2e466a'  # Replace with your Custom Search Engine ID
    query = f"{company_name} what it does OR company description OR about"
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': API_KEY,
        'cx': CSE_ID,
        'q': query,
        'num': 3  # Number of results to fetch
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        search_results = response.json().get('items', [])
        combined_snippet = [result['snippet'] for result in search_results]
        return " ".join(combined_snippet) if combined_snippet else "Summary not available."
    except requests.exceptions.RequestException as e:
        return f"Error fetching summary: {e}"

# Function to parse the DataFrame
def parse_company_data(data):
    companies = []
    
    # Get only the top 10 companies
    top_10_data = data.head(10)  # Select the first 10 rows

    for index, row in top_10_data.iterrows():
        symbol = index  # Access the symbol from the index
        name = row['name']  # Change to the correct column name
        rating = row['rating']  # Change to the correct column name
        market_weight = row['market weight']  # Change to the correct column name

        # Get the company summary
        summary = get_company_summary(name)

        # Fetch market cap and price
        ticker = yf.Ticker(symbol)
        market_cap = ticker.info.get('marketCap', 0)
        price = ticker.info.get('currentPrice', 0)  # Replace 'last_price' with 'currentPrice' if needed

        companies.append({
            "symbol": symbol,
            "name": name,
            "rating": rating,
            "market_weight": market_weight,
            "summary": summary,
            "market_cap": market_cap,
            "current_price": price
        })
    
    return companies

# Main function to create Markdown data
def create_md_data(industry, companies):
    md_data = f"# {industry.capitalize()} Industry - Top Companies\n\n"
    
    for company in companies:
        md_data += f"## {company['name']} ({company['symbol']})\n"
        md_data += f"- **Rating**: {company['rating']}\n"
        md_data += f"- **Market Weight**: {company['market_weight']}\n"
        md_data += f"- **Market Cap**: ${company['market_cap']:,.0f}\n"
        md_data += f"- **Current Price**: ${company['current_price']:,.2f}\n"
        md_data += f"- **Summary**: {company['summary']}\n\n"
    
    return md_data

# Function to get news about the top companies
def get_company_news(companies):
    news_data = []
    for company in companies:
        # Assume company['name'] contains the company name for news search
        news = get_company_summary(company['name'])
        news_data.append({"name": company['name'], "news": news})
    return news_data

def generate_market_insights(news_data, competitor_data, market_cap_data, user_brief, industry):
    api_key = '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'  # Replace with your OpenAI API key
    endpoint = "https://api.openai.com/v1/chat/completions"
    
    messages = [
        {"role": "system", "content": "You are an insightful market analyst and also predict future trends. In the insights include the top 3 market Competitors in short, What is the recent sentiment and whether the industry will grow. Also how well the user brief can fit in the market and what does the stock price and market cap show. Also include some growth strategies."},
        {"role": "user", "content": f"Here is the market overview for the {industry} industry."},
        {"role": "user", "content": f"User Brief: {user_brief}"},
        {"role": "user", "content": f"Market Cap Data: {json.dumps(market_cap_data)}"},
        {"role": "user", "content": f"Competitor Company Data: {json.dumps(competitor_data)}"},
        {"role": "user", "content": f"Recent News: {json.dumps(news_data)}"}
    ]

    payload = {
        "model": "gpt-4o-mini",  # or "gpt-4"
        "messages": messages,
        "max_tokens": 1000
    }

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    response = requests.post(endpoint, headers=headers, json=payload)

    if response.status_code == 200:
        response_data = response.json()
        insights = response_data['choices'][0]['message']['content']
        return insights
    else:
        return f"Error: {response.status_code}, {response.text}"


# Function to execute the complete process and save outputs
def save_industry_analysis(directory_path, industry, user_brief):
    # Create the directory if it does not exist
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    # Main execution
    industry_info = yf.Industry(industry.lower())
    data = industry_info.top_companies

    # Parse company data and get market cap & price
    companies_data = parse_company_data(data)

    # Get news for the companies
    company_news = get_company_news(companies_data)

    # Create Markdown data for the industry
    md_data = create_md_data(industry, companies_data)

    # Generate market insights
    market_cap_data = [{"symbol": company['symbol'], "market_cap": company['market_cap']} for company in companies_data]
    competitor_data = {"companies": [{"symbol": company['symbol'], "name": company['name']} for company in companies_data]}
    # user_brief = "I want to expand into the AI market and increase market share."
    
    insights = generate_market_insights(company_news, competitor_data, market_cap_data, user_brief, industry)

    # Save insights to a Markdown file
    insights_file_path = os.path.join(directory_path, 'insights.md')
    with open(insights_file_path, 'w') as file:
        file.write(f"# Market Insights for {industry.capitalize()} Industry\n\n")
        file.write(insights)

    print(f"Insights saved to {insights_file_path}.")

    # Save company data to a Markdown file
    data_file_path = os.path.join(directory_path, 'data.md')
    with open(data_file_path, 'w') as file:
        file.write(md_data)

    print(f"Company data saved to {data_file_path}.")

# Sample usage
# directory = "output_analysis"  # Replace with your desired directory
# industry = "software-infrastructure"  # Replace with your desired industry
# save_industry_analysis(directory, industry)
