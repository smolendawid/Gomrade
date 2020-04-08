## These are initial commits to this repo so beware it's a huge todo that may not work yet.

## Intro 

This repository allows you to play GO with strong AI on a real board. 

Gomrade analyses the board state from an image using a computer camera and answers the AI moves using 
a synthesized voice. 

The example video of Gomrade in action can be found here:

https://


## Current state

The current state:
- Works with KataGo 1.3.5.
- Needs some setup clicking before running each game
- The camera needs to stand still and the conditions (light) can't change - after a change, it's possible to continue 
the game after another setup
- Makes some errors (but ok for patient ppl)
- Code is ready to extend

## For GO players 
At the moment setting up the repository requires a minimal programming initiative.
- Install KataGo on your computer. Make sure something like
`katago gtp -config $(brew list --verbose katago | grep gtp) -model $(brew list --verbose katago | grep .gz | head -1)`
works on your computer
- Install Python 3.6 or newer on your computer. Check something like:
`python3 -V`
- Navigate to the downloaded repository in the console and run `python3 -m pip install -r requirements.txt`
- Run `python3 utils/synthetize_moves.py`
- Run `python3 run.py`

If you need help, you can contact me: my username at gmail.com 

__If you played at least a few moves with the Gomrade, please send the images and text files generated in `data/`
directory. It will GREATLY help with the development od the Gomrade__

#### Even more:
- To run with different parameters (KataGo level, color, responding time, board size) edit `config.yml`
- To play with different engines, you may try to edit lines in `run.py`


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
At the moment there's no Machine Learning, although many attempts have been made. The main purpose of the program is to collect the data
and automatically create the labels using game logic in controlled conditions.

### Code structure

We believe the playing with Gomrade can be a 


## Complexity illustration

You can find the examples of variance in the data in `sample_data/`


## Future plans

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

Although a pretty sophisticated algorithm and great code are used, the goals of Imago were different than ours. We consider
the usage of board detection or some other ideas in the future but at the moment manual 
detectors are more useful and general.
