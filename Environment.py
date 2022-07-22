import time

from binance import Client


class TradeEnvironment:
    # Set the environment action and observation
    def __init__(self, apiKey, apiSecret, symbol, quantity, testnet=False,
                 order_id=None, initial_balance=None, reward=None):
        self.apiKey = apiKey
        self.apiSecret = apiSecret
        self.symbol = symbol
        self.quantity = quantity
        self.testnet = testnet
        self.order_id = order_id
        self.initial_balance = initial_balance
        self.reward = reward
        self.client = Client(self.apiKey, self.apiSecret, testnet=self.testnet)
        # Subclass model
        super().__init__()
        # Setup spaces
        self.action_space = None

    # What is called to do something in the game
    def step(self, action):
        # Action key - 0: do nothing, 1: long, 2: short, 3: close

        if action == 0:
            return self.get_observation()
        elif action == 1:
            self.initial_balance = self.client.futures_account_balance(symbol=self.symbol)
            order = self.client.futures_create_order(symbol=self.symbol, side="BUY", type="STOP_MARKET",
                                                     quantity=self.quantity, closePosition=True)

            self.order_id = order['orderId']
            return self.get_observation()

        elif action == 2:
            self.initial_balance = self.client.futures_account_balance(symbol=self.symbol)
            order = self.client.futures_create_order(symbol=self.symbol, side="SELL", type="STOP_MARKET",
                                                     quantity=self.quantity, closePosition=True)
            self.order_id = order['orderId']
            return order, self.get_observation()
        elif action == 3:
            self.client.futures_cancel_order(symbol=self.symbol, orderId=self.order_id)
            new_balance = self.client.futures_account_balance(symbol=self.symbol)
            profit = new_balance['marginBalance'] - self.initial_balance['marginBalance']

            if profit > 0:
                self.reward = 10
            elif profit <= 0:
                self.reward = -10

            return self.get_observation(), self.reward,

    # Restart the environment
    def reset(self):
        time.sleep(2)
        self.client = Client(self.apiKey, self.apiSecret, testnet=self.testnet)
        self.client.futures_cancel_all_open_orders(symbol=self.symbol)
        return self.get_observation()

    # Get the current state of the environment
    def get_observation(self):
        return self.client.get_historical_klines(symbol=self.symbol, interval="1h", limit=24)
