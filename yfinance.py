import yfinance as yf

def download_data(ticker_symbol, start_date, end_date, period):
    ticker_data = yf.Ticker(ticker_symbol)
    data = ticker_data.history(start=start_date, end=end_date, interval=period)
    return data
def format_data(data):
    formatted_data = []
    current_date = None
    daily_data = []
    for index, row in data.iterrows():
        if current_date is None:
            current_date = index.date()
        if index.date() != current_date:
            formatted_data.append("_".join(daily_data))
            daily_data = []
            current_date = index.date()
        daily_data.append(f"{row['Close']},{row['Volume']}")
    if daily_data:  # Don't forget the last day
        formatted_data.append("_".join(daily_data))
    return formatted_data

# Example usage:
data = download_data("CRM", "2021-08-01", "2023-05-05", "1h")
formatted_data = format_data(data)
with open("data.txt", "a") as outfile:
    for item in formatted_data:
        split_item = item.split("_")
        outfile.write('CRM: ' + "_".join(split_item[0:-2]) + "\t" + "_".join(split_item[-2:]) + "\n")


print(formatted_data)
