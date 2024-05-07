import yfinance as yf
from Scrapers.scraper import Scraper

class YFScraper(Scraper):
    def download_and_add_features(self, ticker, start='2010-01-01', end='2024-01-01', L=20):
        data = yf.download(ticker, start=start, end=end)
        # We can better abstract feature selection here to be
        """
        For list of zip(column names, functions):
        data[col_name] = function(data)
        
        Good idea for later to abstract feature selection.
        """
        self.add_features(data, L=L)
        return data

