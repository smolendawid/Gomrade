## Running

Run `python3 run.py`

#### Huge request
__If you played at least a few moves with the Gomrade, please send the `logs/` directory to 
_github username_ at gmail.com
It will GREATLY help with the development od the Gomrade__


## Detailed installation

At the moment setting up the repository requires a minimal programming initiative.

- Install KataGo on your computer. Make sure something like

    `katago gtp -config $(brew list --verbose katago | grep gtp) -model $(brew list --verbose katago | grep .gz | head -1)`
    works on your computer. You should be able to run it in console and get the response from KataGo

- Install Python 3.6 or newer on your computer. Check something like:
    `python3 -V`
    Python  version should be printed in the console


- Navigate to the downloaded repository in the console and run `python3 -m pip install -r requirements.txt`
No errors should occur. It installs the projects dependencies

- Run 
`python3 utils/synthetize_moves.py`
You can see moves of AI in the console but the best way to play against it (for now) is to hear it's decisions.
You need the waves with moves recorder to hear it. Right now you have to generate it for yourself using some 
speech synthesizer, f.e. google, as in the script above

- Run `python3 run.py`


If you need help, you can contact me: my username at gmail.com 

__If you played at least a few moves with the Gomrade, please send the `logs/` directory to 
_github username_ at gmail.com
It will GREATLY help with the development od the Gomrade__


#### Even more:
- To run with different parameters (KataGo level, color, responding time, board size) edit `config.yml`
- To play with different engines, you may try to edit lines in `run.py`
