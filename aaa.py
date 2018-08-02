
#coding:utf-8
from pandas import DataFrame
from pandas import concat
import lightgbm as lgb
import matplotlib.pyplot as plt

def series_to_supervised(data, n_in=1, n_out=20, dropnan=True):
    """
    Frame a time series as a supervised learning dataset.
    Arguments:
        data: Sequence of observations as a list or NumPy array.
        n_in: Number of lag observations as input (X).
        n_out: Number of observations as output (y).
        dropnan: Boolean whether or not to drop rows with NaN values.
    Returns:
        Pandas DataFrame of series framed for supervised learning.
    """
    n_vars = 1 if type(data) is list else data.shape[1]
    df = DataFrame(data)
    cols, names = list(), list()
    # input sequence (t-n, ... t-1)
    for i in range(n_in, 0, -1):
        cols.append(df.shift(i))
        names += [('var%d(t-%d)' % (j + 1, i)) for j in range(n_vars)]
    # forecast sequence (t, t+1, ... t+n)
    for i in range(0, n_out):
        cols.append(df.shift(-i))
        if i == 0:
            names += [('var%d(t)' % (j + 1)) for j in range(n_vars)]
        else:
            names += [('var%d(t+%d)' % (j + 1, i)) for j in range(n_vars)]
    # put it all together
    agg = concat(cols, axis=1)
    agg.columns = names
    # drop rows with NaN values
    if dropnan:
        agg.dropna(inplace=True)
    return agg
import pandas as pd
train = pd.read_table('data/train_20171215.txt',engine='python')
train = train.groupby(['date','day_of_week'],as_index=False).cnt.sum()
time_cnt = list(train['cnt'].values)
# nin 前看 nout后看 这个题目需要前看
time2sup = series_to_supervised(data=time_cnt,n_in=276,dropnan=True)

gbm0 = lgb.LGBMRegressor(
    objective='regression',
    num_leaves=64,
    learning_rate=0.12,
    n_estimators=10000)

print(time2sup.shape)
print(time2sup)

x_train = time2sup[time2sup.index<755]
x_test = time2sup[time2sup.index>755]
# 这个方式其实是最简单的，后面还可以很多改善，比如滚动预测一类
# print(x_train.values)
# print(x_test.shape)

y_train = x_train.pop('var1(t)')
y_test = x_test.pop('var1(t)')

# 损失函数mse
gbm0.fit(x_train.values,y_train,eval_set=[(x_test.values,y_test)],eval_metric='mse',early_stopping_rounds=15)

print(gbm0.predict(x_test.values))


from sklearn.metrics import mean_squared_error
line1 = plt.plot(range(len(x_test)),gbm0.predict(x_test.values),label=u'predict')
line2 = plt.plot(range(len(y_test)),y_test.values,label=u'true')
plt.legend()
# plt.show()