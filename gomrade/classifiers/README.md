## Intro

To develop and test ML models for board and stones recognition, you're going to need to
install dependencies from requirements.txt

## Data format:

Data should be contained in subdirectories, one for each data source e.g. game.
Each subdirectory should have an image and corresponding .txt file with annotation
as in the `data/sample_data/`

## Validation schemas  

Two validation schemas are implemented:

1. Cross-validation on images
2. Cross-validation with one-source-out. 

## Metrics

Metrics chosen for the projects are Accuracy in terms of the game state and weighted F1 score
in terms of field position (`black`, `white` and `empty`)

## Running

Models should use the interfaces implemented in `gomrade/classifiers/gomrade_model.py`

Run `gomrade/classifiers/train_validate.py` for training and testing your model.

## Status 

For full dataset:

- 39 sources
- 1035 images
- 359556 elements to classify

For one-source-out keras model:

```

position acc 0.9944631088347662
position std 0.013440826207001617
test
              precision    recall  f1-score   support

           0    0.99823   0.99548   0.99685    296319
           1    0.98055   0.99471   0.98758     31775
           2    0.97602   0.98710   0.98153     31462

    accuracy                        0.99468    359556
   macro avg    0.98493   0.99243   0.98865    359556
weighted avg    0.99472   0.99468   0.99469    359556

train
              precision    recall  f1-score   support

           0    0.99971   0.99974   0.99972   6175440
           1    0.99942   0.99933   0.99938   1317410
           2    0.99885   0.99879   0.99882   1305268

    accuracy                        0.99954   8798118
   macro avg    0.99933   0.99929   0.99931   8798118
weighted avg    0.99954   0.99954   0.99954   8798118

```
