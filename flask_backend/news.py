import yfinance as yf
import os

def save_industry_news(directory_path, industry):
    """
    Fetch news articles for the top companies in a specified industry and save them to a Markdown file.

    Parameters:
    directory_path (str): The directory path where the Markdown file will be saved.
    industry (str): The industry to fetch top companies from.

    Returns:
    None
    """
    # Fetch top companies in the specified industry
    industry_info = yf.Industry(industry.lower())
    top_companies = industry_info.top_companies.head(5)  # Get the top 5 companies

    # List to hold news articles
    news_articles = {}

    # Loop through each company symbol to fetch news
    for symbol in top_companies.index.to_list():
        company_data = yf.Ticker(symbol)
        news = company_data.news  # Fetch news articles
        news_articles[symbol] = news

    # Check if directory exists; create if not
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    # Construct file path
    file_path = os.path.join(directory_path, 'news.md')
    
    # Save the news articles for the top companies to a Markdown file
    with open(file_path, 'w') as file:
        file.write(f"# News for Top 5 Companies in {industry.capitalize()} Industry\n\n")
        
        for symbol, articles in news_articles.items():
            file.write(f"## News for {symbol}:\n\n")
            for article in articles:
                file.write(f"- **{article['title']}** ({article['publisher']})\n")
            file.write("\n")  # Add an extra newline for better formatting

    print(f"News articles saved to {file_path}.")

# Example usage
# directory = "output_news"  # Replace with your desired directory
# industry = "software-infrastructure"  # Replace with your desired industry
# save_industry_news(directory, industry)
