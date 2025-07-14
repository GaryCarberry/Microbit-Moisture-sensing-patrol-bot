# Importing necessary libraries
import numpy as np# good for numerical ops as well as cleaning up large/ inf data
import pandas as pd#data handling, helps csv files
from sklearn.preprocessing import StandardScaler# good for fair comparison against higher weights
from sklearn.cluster import KMeans# learn patterns within the data
import matplotlib.pyplot as plt#plots graphs

data = pd.read_csv("microbit(4).csv")  #loads my csv into the panda frame
humidity_labels = ['High Humidity', 'Medium Humidity', 'Low Humidity']#for labelling centroids
features = ['Time (seconds)', 'temperature', 'Light', 'distance']  #columns for clustering
X = data[features]#extracts the data one more time into a usable format including the labelled features


X_clean = X.replace([np.inf, -np.inf], np.nan)#cleaning up problematic data, swaps with nan which basically means missing
X_clean = X_clean.dropna()#removes rows with missing values

scaler = StandardScaler()# should set up transformation logic with standard deviation and mean
X_scaled = scaler.fit_transform(X_clean), #calculate mean and standard deviation,
#puts them on a level playing field weight wise


kmeans = KMeans(n_clusters=3, random_state=42)#fixes the randomness with a rondomness seed for consistency
kmeans.fit(X_scaled)#uses euclidean distance and trains the model

X_clean['cluster'] = kmeans.labels_#assigns each row a cluster

#Visualize clusters in 3D
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')

colors = ['r', 'g', 'b']
markers = ['o', 's', 'D']

for i in range(3):#begins plotting points based on attributes
    ax.scatter(
        X_scaled[kmeans.labels_ == i, 1],  # temperature
        X_scaled[kmeans.labels_ == i, 2],  # sound
        X_scaled[kmeans.labels_ == i, 3],  # distance
        c=colors[i],
        marker=markers[i],
        label=f"Cluster {i}",
        edgecolor='k'
    )
# Label centroids with predicted humidity status
centroids = kmeans.cluster_centers_
for i, coord in enumerate(centroids):
    ax.text(
        coord[1],  # temperature
        coord[2],  # light
        coord[3],  # distance
        humidity_labels[i],  # e.g., "High Humidity"
        color='black',
        fontsize=10,
        weight='bold'
    )

ax.set_title('3D K-Means Clustering of Microbit Sensor Data')
ax.set_xlabel(f'Standardized {features[1]}')  # temperature
ax.set_ylabel(f'Standardized {features[2]}')  # light
ax.set_zlabel(f'Standardized {features[3]}')  # distance
ax.legend()
plt.show()
