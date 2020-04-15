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

- 23 sources
- 704 images
- 254144 elements to classify

For one-source-out:

```
All images to classify: 704
All sources correct: 0.4090909090909091
Accuracy: 0.8011363636363636
              precision    recall  f1-score   support

           0       1.00      0.99      0.99    219628
           1       0.98      0.99      0.99     17448
           2       0.91      0.99      0.95     17068
```
