import yfinance as yf
import matplotlib.pyplot as plt
import os

def plot_market_cap_distribution(directory_path, industry):
    """
    Fetch top companies in a specified industry and plot their market cap distribution as a pie chart.

    Parameters:
    directory_path (str): The directory path where the plot image will be saved.
    industry (str): The industry to fetch top companies from.

    Returns:
    None
    """
    # Fetch top companies in the specified industry
    industry_info = yf.Industry(industry.lower())
    top_companies = industry_info.top_companies.head(10)  # Get the top 10 companies

    # Prepare lists for company names and their market caps
    company_names = []
    market_caps = []

    # Loop through each company symbol to fetch market cap
    for symbol in top_companies.index.to_list():
        company = yf.Ticker(symbol)
        # Get current market cap
        market_cap = company.info.get('marketCap')  # Fetch the market cap
        
        if market_cap is not None:
            company_names.append(company.info['longName'])  # Get the long name
            market_caps.append(market_cap)  # Append market cap

    # Check if directory exists; create if not
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    # Plotting the pie chart
    plt.figure(figsize=(10, 8))
    plt.pie(market_caps, labels=company_names, autopct='%1.1f%%', startangle=140)
    plt.title(f'{industry} Industry Market Cap Distribution')
    plt.axis('equal')  # Equal aspect ratio ensures the pie chart is a circle.

    # Construct file path
    file_path = os.path.join(directory_path, f'market_cap_distribution.jpg')
    
    # Save the plot as a PNG file
    plt.savefig(file_path, bbox_inches='tight')  # Save as PNG with tight layout
    plt.close()  # Close the plot to free up memory

# Example usage
# directory = "output_plots"  # Replace with your desired directory
# industry = "software-infrastructure"  # Replace with your desired industry
# plot_market_cap_distribution(directory, industry)
