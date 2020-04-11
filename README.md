## Intro 

This repository allows you to play GO with strong AI on a real board. 

Gomrade analyses the board state from an image using a computer camera and answers the AI moves using 
a synthesized voice. 

The example video of Gomrade in action can be found here:
todo https://

This is early beta version 0.0.1


## Current state

The current state:
- Works with KataGo 1.3.5.
- Needs some setup clicking before running each game
- The camera needs to stand still and the conditions (light) can't change - after a change, it's possible to continue 
the game after another initial setup
- Makes some errors (but it's good enough with minimal patience)
- Code is ready to extend


## Manifest

We believe that playing GO is a peculiar, wonderful experience on the border of art, science and sport.
Communing with a wooden board and glass stones allows you for deeper feel of the mysticism of Go.

Therefore playing against Gomrade can be a good substitute for a real Go encounter.


## For Go players 
If you want to play against Gomrade, check HOWTOPLAY.md

## For developers

### Comments

Any help appreciated. The project is pretty fascinating. Main challenges are:

- The intelligent decision about whether the move was made 
- Clever simulation (replaying) of the game after the state is being changed against
the rules of GO
- High accuracy - 99% board state accuracy means a few mistakes per game - far too much. Even worse accuracy trap 
in terms of stones accuracy
- Robustness to variable conditions

### Machine learning
At the moment there's no Machine Learning, although many attempts have been made. 

AT THE MOMENT he main purpose of the program is to collect the data and automatically create the labels in 
the controlled environmental conditions.

It happens in the background during the casual Go game.

More on ML in `gomrade/classifiers/`

### Code structure

todo


### Complexity illustration

You can find the examples of variance in the data in `data/sample_data/`


### Future plans

* [ ] make sure it can work with other AI engines
* [ ] add the last move from config to start the game at any point
* [ ] collect a massive number of images 
* [ ] machine learning based board detection 
* [ ] machine learning based stones classifier 

## Acknowledgements

GTP communication inspired here:
https://github.com/jtauber/gtp

There's a fantastic piece of engineering in Imago:
https://github.com/tomasmcz/imago
Which presents the performance of advanced image processing techniques.

Although a pretty sophisticated algorithm and great code are used, the goals of Imago were different than ours. 
We will consider the usage of board detection or some other ideas in the future but at the moment manual 
detectors are more useful and general.
