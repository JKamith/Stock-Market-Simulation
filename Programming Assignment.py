#IMP- Trading hours have been activated from 12am to 11:59 pm and trading duration has been set to 6.5 hours. This can be changed by changing the duration on line no 264.
#Notification can be printed by un-commenting the last line of the code
import random
import time

comment = True

class StockExchange:
    def __init__(self,shares_in_market = []):
        self.last_traded_price = 0
        self.best_bid = 0
        self.best_offer = 0
        self.bids = {}      # {order: [price, timestamp]}
        self.offers = {}    # {order: [price, timestamp]}
        self.share_market = shares_in_market

    def get_last_traded_price(self):
        return self.last_traded_price

    def get_best_bid(self):
        return self.best_bid  

    def get_best_offer(self):
        return self.best_offer

    def get_top_5_bids(self,security):
        return self.bids.get(security, [])[:5]

    def get_top_5_offers(self, security):
        return self.offers.get(security, [])[:5]

    def accept_order(self, order):
        if order.side == 'BUY':
            self.bids[order] = [order.security, order.timestamp]
            # best bid is one where highest price to buy a share
            self.bids = dict(sorted(self.bids.items(), key=lambda item: (-item[1][0], item[1][1])))
            k, v = next(iter(self.bids.items()))
            self.best_bid = v[0]
            self.remove_extra_orders(self.bids)
        elif order.side == 'SELL':
            self.offers[order] = [order.security, order.timestamp]
            # best offer is one where lowest price to sell a share
            self.offers = dict(sorted(self.offers.items(), key=lambda item: (item[1][0], item[1][1])))
            k, v = next(iter(self.offers.items()))
            self.best_offer = v[0]
            self.remove_extra_orders(self.offers)

    def trading_hours(self):
        # Assuming trading hours are from 12:00 AM to 11:59 PM
        current_time = time.localtime()
        return 0 <= current_time.tm_hour < 23 and 0 <= current_time.tm_min < 59

    def match_orders(self, share):  # call match_orders 
        bid_found, offer_found = False, False
        for key in self.bids:
            if key.share == share:
                bid_found = True
                bid_order = key
                break
        for key in self.offers:
            if key.share == share:
                offer_found = True
                offer_order = key
                break
        if (share in self.share_market and bid_found):
            cost_price = bid_order.security * bid_order.quantity
            bid_order.trader.order_management_system.withdraw_cash(cost_price)
            bid_order.trader.order_management_system.add_stock(bid_order.share, bid_order.security)
            self.share_market.remove(share)
            self.bids.pop(bid_order)
            self.last_traded_price = bid_order.security
        if (bid_found and offer_found and bid_order.security >= offer_order.security):  # qty of share exchanged are equal in order = 1000
            # Matching condition satisfied, execute trade, remove matched orders
            self.execute_trade(bid_order, offer_order)
            self.bids.pop(bid_order)
            self.offers.pop(offer_order)

    def execute_trade(self, bid_order, offer_order):
        trade_price = (bid_order.security + offer_order.security)/2
        # Transfer money from buyer to seller
        cost_price = trade_price * bid_order.quantity
        selling_price = trade_price * offer_order.quantity
        bid_order.trader.order_management_system.withdraw_cash(cost_price)
        offer_order.trader.order_management_system.add_cash(selling_price)
        # transfer ownership of share from seller to buyer
        offer_order.share.change_owner(bid_order.trader)
        # Update trader's portfolios
        bid_order.trader.order_management_system.add_stock(bid_order.share, trade_price)
        offer_order.trader.order_management_system.remove_stock(offer_order.share, trade_price)
        # Update last traded price
        self.last_traded_price = trade_price

    def remove_extra_orders(self, orders):  
        if len(orders)>5:
            order=list(orders.keys())[-1]
            share_name=order.share.name
            trader=order.trader
            trader.notification.append("Sorry your order for the share" +" " + share_name + " "+"has been deleted")
            del orders[order]


class Order:
    def __init__(self, trader, security, side, share):
        self.trader = trader
        self.security = security    # price at which order is placed
        self.side = side            # action: BUY, SELL
        self.share = share
        self.quantity = 1000
        self.timestamp = time.time()

class OrderManagementSystem:
    def __init__(self, trader):
        self.trader = trader
        self.cash = trader.bank_account
        self.portfolio = trader.initial_portfolio      # portfolio = {share : price}

    def track_cash(self):
        return self.cash

    def add_cash(self, amount):
        self.cash += amount

    def withdraw_cash(self, amount):
        if amount <= self.cash:
            self.cash -= amount
            return True
        else:
            print(self.trader.name + " has insufficient cash")
            return False

    def current_portfolio_value(self):  
        sum = self.cash
        for price in self.portfolio.values():
            sum += 1000 * price
        return sum
    
    def place_buy_order(self, price, share):
        if (self.cash>=price):
            order = Order(self.trader, price, 'BUY', share)
            stock_exchange = self.trader.stock_exchange
            stock_exchange.accept_order(order)

    def place_sell_order(self, price, share):
        if share in self.portfolio.keys():
            order = Order(self.trader, price, 'SELL', share)
            stock_exchange = self.trader.stock_exchange
            stock_exchange.accept_order(order)

    def add_stock(self, order, price):
        self.portfolio[order] = price

    def remove_stock(self, security, price):
        if security in self.portfolio:
            del self.portfolio[security]


class Trader:
    def __init__(self, name, bank_account, stock_exchange, portfolio = {}) :
        self.name = name
        self.bank_account = bank_account
        self.stock_exchange = stock_exchange
        self.initial_portfolio = portfolio
        self.order_management_system = OrderManagementSystem(self)
        self.notification=[]

    def make_decision(self, share):
        # make decision whether to buy or sell a share and at what price 
        action = random.choice(['BUY', 'SELL'])
        price = 0
        best_bid = self.stock_exchange.get_best_bid()
        best_offer = self.stock_exchange.get_best_offer()
        if (comment):
            print("action chosen for trader ",self.name," is ",action)
        if action == 'BUY':
            action_buy = random.choice(['BEST_BID','MID_PRICE'])
            if (action_buy == 'BEST_BID'):
                if not len(self.stock_exchange.bids):
                    price = best_bid
                else:
                    price = self.stock_exchange.get_last_traded_price() * 1.05
            else:
                price=(best_bid+best_offer)/2 
        elif action == 'SELL':
            action_sell = random.choice(['BEST_ASK','MID_PRICE'])
            if (action_sell == 'BEST_ASK'):
                if not len(self.stock_exchange.offers):
                    price = best_offer
                else:
                    price = self.stock_exchange.get_last_traded_price() * 0.95 
            else:
                price = (best_bid + best_offer)/2

        if (action == 'BUY'):
            self.order_management_system.place_buy_order(price, share)
        else:
            self.order_management_system.place_sell_order(price, share)
        

class Share:
    def __init__(self,name, owner = None ):
        self.owner = owner
        self.name = name
    def change_owner(self, new_owner):
        self.owner = new_owner




# Creating instance of stock exchange class
stock_exchange = StockExchange() 
stock_exchange.best_bid=30
stock_exchange.best_offer=20
stock_exchange.last_traded_price=40


# Trader 1: Ojasvi
Ojasvi_bank_balance = 60000
Ojasvi = Trader('Ojasvi', Ojasvi_bank_balance, stock_exchange)

# Trader 2: Jamith
Jamith_bank_balance = 80000
Jamith = Trader('Jamith', Jamith_bank_balance, stock_exchange)

# Trader 3: Kashish
Kashish_bank_balance = 50000
Kashish = Trader('Kashish', Kashish_bank_balance, stock_exchange)

# Trader 4: Stuti
Stuti_bank_balance = 70000
Stuti = Trader('Stuti', Stuti_bank_balance, stock_exchange)

# Trader 5: Esha
Esha_bank_balance = 55000
Esha = Trader('Esha', Esha_bank_balance, stock_exchange)

traders = [Ojasvi, Jamith, Kashish, Stuti, Esha]

#  creating shares:
AMZ = Share( 'AMZ',Ojasvi)
GGLE = Share('GGLE',Stuti)
MST = Share('MST',Jamith)
A = Share('A')
B = Share('B')
C = Share('C')
D = Share('D')
E = Share('E',Esha)
F = Share('F', Kashish)
G = Share('G')
H = Share('H',Ojasvi)
shares_in_market = [A, B, C, D, G]
all_shares=[A, B, C, D, AMZ, GGLE, MST, E, F, G, H]
stock_exchange.share_market = shares_in_market

Ojasvi.order_management_system.portfolio = {AMZ : 20 , H : 60}
Stuti.order_management_system.portfolio = {GGLE : 80 } 
Jamith.order_management_system.portfolio ={MST: 60}
Esha.order_management_system.portfolio = {E : 50}
Kashish.order_management_system.portfolio = {F : 80}

# Simulation
if (comment):
    print("The logging has been done for trading hours of 15 seconds")

trading_hours = 6.5 * 60 * 60  # 6.5 hours trading day
#trading_hours = 15
current_time = 0
while current_time < trading_hours:
    trader=random.choice(list(traders))
    if (comment):
        print("trader chosen: ",trader.name)
    if trader.bank_account > 0 and len(trader.order_management_system.portfolio)>0:
        share = random.choice(all_shares)
        if (comment):
            print("share trading on: ",share.name)
        trader.make_decision(share)
        stock_exchange.match_orders(share)
    else:
        if (random.random()>0.5):
            trader.bank_account+=random.uniform(1000,10000)       
    current_time += 1
stock_exchange.offers={}
stock_exchange.bids={}


# Ojasvi.make_decision(A
# Esha.make_decision(GGLE, 'SELL')
# Stuti.make_decision(GGLE,'SELL')
# Ojasvi.make_decision(GGLE,'BUY')
# Kashish.make_decision(GGLE,'BUY')
# stock_exchange.match_orders(GGLE)
# Ojasvi.make_decision(A)
# Jamith.make_decision(A,'BUY')
# stock_exchange.match_orders(A)
# print(stock_exchange.share_market)


# Output
for trader in traders:
    initial_balance = trader.bank_account
    portfolio_value = trader.order_management_system.current_portfolio_value()
    profit_loss = portfolio_value - initial_balance
    shares_names = ', '.join(share.name for share in trader.order_management_system.portfolio.keys())
    if (len(shares_names) > 0):
        print(f"{trader.name} : portfolio final = {shares_names}")
    if (profit_loss>=0):
        print(f"{trader.name}: Initial Balance={initial_balance}, Portfolio Value={portfolio_value}, Profit={profit_loss}")
    else:
        print(f"{trader.name}: Initial Balance={initial_balance}, Portfolio Value={portfolio_value}, Loss={profit_loss}")
    #print("The notifications received by the trader", trader.name , "are as follows :",trader.notification)