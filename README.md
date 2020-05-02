## Intro 

This repository allows you to play GO with strong AI on a real board. 

Gomrade analyses the board state from an image using a computer camera and answers the AI moves using 
a synthesized voice. 

The example video of Gomrade in action can be found here:

todo https://

This is early beta version 0.0.1


## Current state

The current state:
- In development
- Works with KataGo 1.3.5.
- Needs some setup clicking before running each game
- The camera needs to stand still and the conditions (light) can't change - after a change, 
- It is possible to continue game from some point
- Generates SGF file or more files if some illegal moves (mainly due to errors) are detected
- Makes some mistakes (but it's good enough with minimal patience)


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
- High accuracy - 99.9% board state accuracy means a few mistakes per game - far too much. Even worse accuracy trap 
in terms of stones accuracy
- Robustness to variable conditions
- Real-time processing

### Machine learning

One of the purposes of the program is to collect the data and automatically create the labels in 
the controlled environmental conditions.

It happens in the background during the casual Go game.

More on ML in `gomrade/classifiers/`

### Data

At the moment I didn't decide to share the training dataset. You can find some details in `gomrade/classifiers/`

### Code structure

- gomrade - main program scripts
  - go_game_annotator - tools for labeling. See README.md in `go_game_annotator/`
  - classifiers - classification algorithms. See README.md in `go_game_annotator/`
- gomrade_tests - unit, integration and system tests
- gtp - scripts for talking with gtp engine

### Complexity illustration

You can find the examples of variance in the data in `data/sample_data/`


### Future plans

Read ROADMAP.md

## Acknowledgements

GTP communication inspired here:
https://github.com/jtauber/gtp

### Imago
There's a fantastic piece of engineering in Imago:
https://github.com/tomasmcz/imago
Which presents the performance of advanced image processing techniques.

Although a pretty sophisticated algorithm and great code are used, the goals of Imago were different than ours. 
We will consider the usage of board detection or some other ideas in the future but at the moment manual 
detectors are more useful and general.

### VideoKifu

I used some images from VideoKifu `http://www.oipaz.net/VideoKifu.html` for training and testing.
I appreciate the support of the creators, thank you!

Although there are some similarities, the goals of VideoKifu seem to be different than ours. 
VideoKifu is used for automatic game transcription, not artificial opponent.
We gave up automatic board detection and focus on stones recognition with solid validation and efficiency.
