#coding:utf-8
import pandas as pd
from sklearn.metrics import mean_squared_error

train = pd.read_csv('data/train_20171215.txt',sep='\t')
an = pd.read_csv('data/answer_A_20180225.txt',sep='\t',header=None)
an.rename(columns={0:'date',1:'cnt'},inplace=True)
# print an
# exit()
new_train = pd.DataFrame()
new_data = []
brand = []
for i in range(1032):
    for j in range(5):
        new_data.append(i+1)
        brand.append(j+1)

day_of_week = train.groupby('date',as_index=False).day_of_week.mean()
new_train['date'] = list(new_data)
new_train['brand'] = list(brand)

train = pd.merge(new_train,train,on=['date','brand'],how='left')
del train['day_of_week']
train = pd.merge(train,day_of_week,on=['date'],how='left')
train['cnt'] = train['cnt'].fillna(0)

##########################################################
test = pd.read_csv('data/test_B_20171225.txt',sep='\t')
print test

new_test = pd.DataFrame()
new_data_ = []
brand_ = []
test_len = 1307 - 1032 + 1

print 'Ԥ������',test_len

for i in range(test_len):
    for j in range(5):
        new_data_.append(i+1308)
        brand_.append(j+1)

new_test['date'] = list(new_data_)
new_test['brand'] = list(brand_)

test = pd.merge(new_test,test,on=['date'],how='left')


##########################################################
train = train.copy()
test = test.copy()

val_data = train[train['date'] > 1032 - test_len]
test['cnt'] = 1111
val_data = test


to_sub_val_data = val_data.copy()
print 'val_date',1032 - 757 + 1

train_data = train[(train['date'] <= 1032 - test_len) & (train['date'] > 480)]

print len(train_data.date.unique())


history_rule_mean = train_data.groupby(['brand','day_of_week'],as_index=False).cnt.mean()
history_rule_median = train_data.groupby(['brand','day_of_week'],as_index=False).cnt.median()
history_rule = train_data.groupby(['brand'],as_index=False).cnt.mean()
day_of_week_rule = train_data.groupby(['day_of_week'],as_index=False).cnt.mean()

history_rule_mean.rename(columns={'cnt':'h_mean_cnt'},inplace=True)
history_rule_median.rename(columns={'cnt':'h_median_cnt'},inplace=True)
history_rule.rename(columns={'cnt':'h_brand_cnt'},inplace=True)
day_of_week_rule.rename(columns={'cnt':'h_day_of_week_cnt'},inplace=True)

val_data = pd.merge(val_data,history_rule_median,on=['brand','day_of_week'])
val_data = pd.merge(val_data,history_rule_mean,on=['brand','day_of_week'])
val_data = pd.merge(val_data,history_rule,on=['brand'])
val_data = pd.merge(val_data,day_of_week_rule,on=['day_of_week'])


# val_data = val_data[val_data['cnt']!=0]

tmp = val_data.groupby(['date'],as_index=False)['cnt','h_mean_cnt','h_median_cnt','h_brand_cnt','h_day_of_week_cnt'].sum()
val_data = pd.merge(val_data[['date']],tmp,on=['date'])
# print val_data

# print mean_squared_error(val_data['cnt'],val_data['h_mean_cnt'] * 0.95 + val_data['h_median_cnt'] * 0.05)
# print mean_squared_error(val_data['cnt'],val_data['h_mean_cnt'] * 1.1)
# print mean_squared_error(val_data['cnt'],val_data['h_brand_cnt'])
# print mean_squared_error(val_data['cnt'],val_data['h_median_cnt'])
# print mean_squared_error(val_data['cnt'],val_data['h_day_of_week_cnt'])
#
# print mean_squared_error(val_data['cnt'],val_data['h_day_of_week_cnt'] * 1.1)
#
# print mean_squared_error(val_data['cnt'],val_data['h_day_of_week_cnt'] * 0.5 + val_data['h_mean_cnt'] * 0.5)
#


val_data = pd.merge(val_data,to_sub_val_data,on=['date'])


val_data = val_data[['date','h_mean_cnt','day_of_week','h_day_of_week_cnt']]
val_data = pd.DataFrame(val_data).drop_duplicates(['date'])
val_data = val_data.sort_values(['date'])
import numpy as np

val_data.loc[val_data['day_of_week']<=5,'cnt'] = val_data.loc[val_data['day_of_week']<=5,'h_day_of_week_cnt'] * 1.1
val_data.loc[val_data['day_of_week']>6,'cnt'] = val_data.loc[val_data['day_of_week']>6,'h_day_of_week_cnt'] * 0.5
val_data.loc[val_data['day_of_week']==6,'cnt'] = val_data.loc[val_data['day_of_week']==6,'h_day_of_week_cnt'] * 1.75

val_data[['date','cnt']].to_csv('result/20180226.txt',index=False,header=False,sep='\t')
print val_data[['date','cnt']]

ind = []
res = []

for i,data in enumerate(val_data[['date','cnt','day_of_week']].values):
    if i % 4 == 0:
        if data[2] == 7:
            # data[1] * 0.7
            ind.append(data[0])
            res.append(data[1] * 0.5)
        else:
            ind.append(data[0])
            res.append(data[1])
    else:
        ind.append(data[0])
        res.append(data[1])

# print res

val_data = pd.DataFrame()
val_data['date'] = list(ind)
val_data['cnt'] = list(res)
val_data['date'] = val_data['date'].astype(int)
# val_data['cnt'] = val_data['cnt'] - 1
val_data[['date','cnt']].to_csv('result/20180226.txt',index=False,header=False,sep='\t')
#
answer = pd.read_csv('data/answer_A_20180225.txt',sep='\t',header=None)
answer.rename(columns={0:'date',1:'t_cnt'},inplace=True)
print(111)
print answer
print val_data[['date','cnt']]


#
# #
# anl = pd.merge(val_data,answer,on=['date'])


# anl.loc[anl['date']==1032,'cnt'] = 600
# print anl

print mean_squared_error(answer['t_cnt'],val_data['cnt'])
#
# print anl