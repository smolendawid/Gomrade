import os


if __name__ == '__main__':

    data = 'data/sample_data/'

    images = [f for f in os.listdir(data) if f.endswith('.jpg')]
    labels = [image.split('.')[0] + '.txt' for image in images]

