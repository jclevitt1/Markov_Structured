from Basic_Feature_Selection.feature_addition import add_basic_technical_analysis_vars

class Scraper:
    def download_and_add_features(ticker, *args, **kwargs):
        raise "Subclass should implement."

    def add_features(self, data, L=20):
        data['daily_return'] = data['Adj Close'].pct_change()
        data['volume_change'] = data['Volume'].pct_change()
        add_basic_technical_analysis_vars(data)