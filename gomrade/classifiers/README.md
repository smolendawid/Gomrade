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
todo
