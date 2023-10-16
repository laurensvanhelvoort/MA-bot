import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import math


class MovingAverageCrossover:
    def __init__(self, stock_symbol, start_date, end_date, short_term_MA, long_term_MA, initial_cash, shares_to_buy):
        self.stock_symbol = stock_symbol
        self.start_date = start_date
        self.end_date = end_date
        self.st_MA = short_term_MA
        self.lt_MA = long_term_MA
        self.initial_cash = initial_cash
        self.shares_to_buy = shares_to_buy

    def download_data(self):
        # Download historical stock data and save it to a CSV file
        data = yf.download(self.stock_symbol, start=self.start_date, end=self.end_date)
        adj_close_data = data['Adj Close']
        adj_close_data.to_csv(f'stockdata/{self.stock_symbol}_data.csv')
        return data

    def calculate_signals(self, data):
        # Calculate moving averages and generate buy/sell signals
        data[f'SMA{self.st_MA}'] = data['Adj Close'].rolling(self.st_MA).mean()
        data[f'SMA{self.lt_MA}'] = data['Adj Close'].rolling(self.lt_MA).mean()
        # Define warm-up periods for the short-term and long-term moving averages
        short_term_warmup = self.st_MA
        long_term_warmup = self.lt_MA

        # Initialize the 'Signal' column as 'Hold'
        data['Signal'] = 'Hold'

        # Create buy and sell signals after the warm-up period
        for index, row in data.iterrows():
            if index >= data.index[0] + pd.DateOffset(days=max(short_term_warmup, long_term_warmup)):
                if row[f'SMA{self.st_MA}'] > row[f'SMA{self.lt_MA}']:
                    data.at[index, 'Signal'] = 'Buy'
                elif row[f'SMA{self.st_MA}'] < row[f'SMA{self.lt_MA}']:
                    data.at[index, 'Signal'] = 'Sell'

        return data

    def simulate_portfolio(self, data):
        # Simulate the portfolio based on buy/sell signals
        cash = self.initial_cash
        shares = 0
        portfolio_value = []

        for index, row in data.iterrows():
            if row['Signal'] == 'Buy':
                shares_to_purchase = min(self.shares_to_buy, cash // row['Adj Close'])
                shares += shares_to_purchase
                cash -= shares_to_purchase * row['Adj Close']
            elif row['Signal'] == 'Sell':
                cash += shares * row['Adj Close']
                shares = 0

            total_value = cash + shares * row['Adj Close']
            portfolio_value.append(total_value)

        return portfolio_value

    def plot_results(self, data, portfolio_value):
        # Print final results
        final_portfolio_value = portfolio_value[-1]
        profit_or_loss = final_portfolio_value - self.initial_cash
        print(f"Initial Cash: {self.initial_cash}")
        print(f"Final Portfolio Value: {final_portfolio_value}")
        print(f"Profit/Loss: {profit_or_loss}")
        print(f"ROI: {round((final_portfolio_value - self.initial_cash) / self.initial_cash * 100)}%")

        # Plot stock price and SMAs
        data[['Adj Close', f'SMA{self.st_MA}', f'SMA{self.lt_MA}']].plot(label='Data', figsize=(16, 8))
        buy_marker = '^'
        sell_marker = 'v'
        buy_indices = data[data['Signal'] == 'Buy'].index
        sell_indices = data[data['Signal'] == 'Sell'].index

        # Sparsely plot buy/sell signals
        step_size = math.floor(len(data.index) / 83)
        plt.scatter(buy_indices[::step_size], data.loc[buy_indices[::step_size], f'SMA{self.st_MA}'],
                    label='Buy Signal', marker=buy_marker, color='g')
        plt.scatter(sell_indices[::step_size], data.loc[sell_indices[::step_size], f'SMA{self.st_MA}'],
                    label='Sell Signal', marker=sell_marker, color='r')

        plt.title(
            f'{self.stock_symbol} adj. closing price and {self.st_MA}-day / {self.lt_MA}-day SMAs with Buy/Sell Signals (Sparse)')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.show()

    def run_strategy(self):
        # Main function to run the entire strategy
        data = self.download_data()
        data = self.calculate_signals(data)
        portfolio_value = self.simulate_portfolio(data)
        self.plot_results(data, portfolio_value)


strategy = MovingAverageCrossover(stock_symbol='META',
                                  start_date='2018-10-16',
                                  end_date='2023-10-16',
                                  short_term_MA=50,
                                  long_term_MA=200,
                                  initial_cash=220,
                                  shares_to_buy=10)
strategy.run_strategy()
