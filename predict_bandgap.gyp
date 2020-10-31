!pip install scikit-learn
!pip install numpy
!pip install pymatgen

from pymatgen import Composition, Element
from numpy import zeros

trainFile = open("/Users/yuichiro/Desktop/bandgap_train.csv","r").readlines()

def naiveVectorize(composition):
       vector = zeros((MAX_Z))
       for element in composition:
               #elementは原子。fractionはその原子が組成に含まれる割合
               fraction = composition.get_atomic_fraction(element)
               vector[element.Z - 1] = fraction
       return(vector)

materials_train = []
bandgaps_train = []
naiveFeatures_train = []

MAX_Z = 100 #特徴量ベクトル最大長さ

for line in trainFile:
       split = str.split(line, ',')
       material = Composition(split[0])
       materials_train.append(material) #化学式
       naiveFeatures_train.append(naiveVectorize(material)) #特徴量ベクトル生成
       bandgaps_train.append(float(split[1])) #バンドギャップの読み込み

from sklearn import ensemble

#sklearnのランダムフォレスト回帰
rfr = ensemble.RandomForestRegressor(n_estimators=100)
rfr.fit(naiveFeatures_train, bandgaps_train)

testFile = open("/Users/yuichiro/Desktop/bandgap_test.csv","r").readlines()

materials_test = []
bandgaps_test = []
naiveFeatures_test = []

MAX_Z = 100 #特徴量ベクトル最大長さ

for line in testFile:
       split = str.split(line, ',')
       material = Composition(split[0])
       materials_test.append(material) #化学式
       naiveFeatures_test.append(naiveVectorize(material)) #特徴量ベクトル生成
       bandgaps_test.append(float(split[1])) #バンドギャップの読み込み

bandgap_predicted = rfr.predict(naiveFeatures_test)

print(bandgap_predicted)
print(bandgaps_test)

np.sqrt(metrics.mean_squared_error(bandgaps_test, bandgap_predicted))

import matplotlib.pyplot as plt
fig = plt.figure()
plt.scatter(bandgaps_test, bandgap_predicted, s=1, c="pink", alpha=0.5, linewidths="2",
            edgecolors="red")
plt.xlabel("bandgap_raw")
plt.ylabel("bandgap_predicted")
plt.xlim(0, 8)
plt.ylim(0, 8)