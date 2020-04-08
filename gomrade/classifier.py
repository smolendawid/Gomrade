import numpy as np


def kmeans(img):
    print("Kmeans")
    import numpy as np
    import cv2
    from sklearn.cluster import KMeans

    img2 = cv2.blur(img, ksize=(50, 50))

    img2 = img2.reshape((img2.shape[0] * img2.shape[1], 3))

    def centroid_histogram(clt):
        # grab the number of different clusters and create a histogram
        # based on the number of pixels assigned to each cluster
        numLabels = np.arange(0, len(np.unique(clt.labels_)) + 1)
        (hist, _) = np.histogram(clt.labels_, bins=numLabels)
        # normalize the histogram, such that it sums to one
        hist = hist.astype("float")
        hist /= hist.sum()
        # return the histogram
        return hist

    clt = KMeans(n_clusters=7)
    clt.fit(img2)

    # plt.figure(figsize=(8,8))
    # plt.imshow(img2)
    hist = centroid_histogram(clt)


    def plot_colors(hist, centroids):
        # initialize the bar chart representing the relative frequency
        # of each of the colors
        bar = np.zeros((50, 300, 3), dtype = "uint8")
        startX = 0
        # loop over the percentage of each cluster and the color of
        # each cluster
        for (percent, color) in zip(hist, centroids):
            # plot the relative percentage of each cluster
            endX = startX + (percent * 300)
            cv2.rectangle(bar, (int(startX), 0), (int(endX), 50),
                color.astype("uint8").tolist(), -1)
            startX = endX

        # return the bar chart
        return bar

    ind = [i[0] for i in sorted(enumerate(hist), key=lambda x:x[1], reverse=True)]

    return clt.cluster_centers_[ind][:2]


def get_mean_color(a):
    return np.median(np.median(a, axis=0), axis=0)


def unique_count_app(a):
    colors, count = np.unique(a.reshape(-1,a.shape[-1]), axis=0, return_counts=True)
    return colors[count.argmax()]


def classify_brightness(rgb_tuple, dominant_color):

    dominant_brightness = sum(dominant_color)

    brightness = sum(rgb_tuple)
    if brightness < 80:
        color = "k"
    elif brightness > 600:
        color = "w"
    else:
        color = "v"

    return color


def closest_color(rgb_tuple, board_colors, black_colors, white_colors):
    colors = []

    for color in board_colors:
        colors.append(('.', color))

    for color in white_colors:
        colors.append(('W', color))

    for color in black_colors:
        colors.append(('B', color))

    manhattan = lambda x,y : abs(x[0] - y[0]) + abs(x[1] - y[1]) + abs(x[2] - y[2])
    # manhattan = lambda x,y : abs(x[2] - y[2])
    distances = {k: manhattan(v, rgb_tuple) for k, v in colors}
    color = min(distances, key=distances.get)

    return color
