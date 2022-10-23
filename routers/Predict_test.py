import Predict_Crypto
import Predict_Stock

if __name__ == '__main__':
    #predict_price, predict_per = Predict_Crypto.Predict('BTC')
    predict_price, predict_per = Predict_Stock.Predict('2330')
    print(predict_price)
    print(predict_per)
