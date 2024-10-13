import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import os

def plot_industry_performance(directory_path, industry):
    """
    Fetch top companies in a specified industry and plot their closing prices over the last year.

    Parameters:
    directory_path (str): The directory path where the plot image will be saved.
    industry (str): The industry to fetch top companies from.

    Returns:
    None
    """
    # Fetch top companies in the specified industry
    industry_info = yf.Industry(industry.lower())
    top_companies = industry_info.top_companies.head(10)  # Get the top 10 companies

    # Create an empty DataFrame to store the adjusted close prices
    price_data = pd.DataFrame()

    # Loop through each company symbol to fetch historical data
    for symbol in top_companies.index.to_list():
        company_data = yf.Ticker(symbol)
        # Fetch historical market data
        hist = company_data.history(period="1y")  # You can change the period as needed
        price_data[symbol] = hist['Close']  # Store the closing prices

    # Plot the data
    plt.figure(figsize=(14, 8))
    for symbol in price_data.columns:
        plt.plot(price_data.index, price_data[symbol], label=symbol)

    plt.title(f'{industry} Industry Performance - Last Year')
    plt.xlabel('Date')
    plt.ylabel('Closing Price (USD)')
    plt.legend()
    plt.grid()
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Check if directory exists; create if not
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    # Construct file path
    file_path = os.path.join(directory_path, f'performance_graph.jpg')
    
    # Save the graph as a PNG file
    plt.savefig(file_path)  # Specify the file name and format
    plt.close()  # Close the figure to free memory

    print(f"Graph saved as {file_path}.")

# Example usage
# directory = "output_plots"  # Replace with your desired directory
# industry = "software-infrastructure"  # Replace with your desired industry
# plot_industry_performance(directory, industry)
