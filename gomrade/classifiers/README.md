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
All images to classify: 705
All sources correct: 0.34782608695652173
Imaages accuracy: 0.8936170212765957
              precision    recall  f1-score   support

           0    0.99937   0.99962   0.99949    219971
           1    0.99874   0.99588   0.99731     17466
           2    0.99625   0.99596   0.99610     17068

    accuracy                        0.99912    254505
   macro avg    0.99812   0.99715   0.99763    254505
weighted avg    0.99912   0.99912   0.99912    254505
```
