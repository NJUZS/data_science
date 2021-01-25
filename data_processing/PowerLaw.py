import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn import linear_model

def DataFitAndVisualization(X,Y):
    # 模型数据准备
    X_parameter=[]
    Y_parameter=[]
    for single_square_feet ,single_price_value in zip(X,Y):
       X_parameter.append([float(single_square_feet)])
       Y_parameter.append(float(single_price_value))

    # 模型拟合
    regr = linear_model.LinearRegression()
    regr.fit(X_parameter, Y_parameter)
    # 模型结果与得分
    print('Coefficients: \n', regr.coef_,)
    print("Intercept:\n",regr.intercept_)
    # The mean square error
    print("Residual sum of squares: %.8f"
      % np.mean((regr.predict(X_parameter) - Y_parameter) ** 2))  # 残差平方和

    # 可视化
    plt.title("Log Data")
    plt.scatter(X_parameter, Y_parameter,  color='black')
    plt.plot(X_parameter, regr.predict(X_parameter), color='blue',linewidth=3)

    # plt.xticks(())
    # plt.yticks(())
    plt.show()

def datasource():

    data  =pd.read_excel('alldata.xlsx','period4_process')
    X = pd.DataFrame(data,columns=['秩'])
    Y = pd.DataFrame(data,columns=['点赞数'])

    plt.title("Raw data")
    plt.scatter(X, Y, color = 'blue')
    plt.show()

    X = np.log10(X)
    Y = np.log10(Y)
    X = np.array(X)
    Y = np.array(Y)

    return X,Y

if __name__=="__main__":
    X,Y = datasource()
    DataFitAndVisualization(X,Y)



