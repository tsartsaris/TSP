# TSP

Solving the Travelling Salesman Problem with Genetic Algorithms and Python 3.

A Tkinter GUI loads a [TSPLIB](http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/) problem,
builds an initial population of tours and evolves it with a genetic algorithm, plotting the
best tour found so far as it improves.

## Requirements

- Python 3 (tested on 3.12) with Tkinter, which ships with the standard Windows and macOS installers
- numpy and matplotlib

```
pip install numpy matplotlib
```

## Running

```
python tsp_gui.py
```

1. **Open TSP file** and pick a problem from `TSP_Problems/` (`berlin52.tsp` is a quick start).
2. Choose a mode, **shuffle** (random tours) or **elitism** (half nearest-neighbour tours),
   and a population size, then **Create initial population**.
3. **Create children** to run the first generation.
4. Choose the number of rounds and the crossover probability, then **Start genetic algorithm**.
   **Stop** ends the run after the current round and keeps the best tour found.

## Problems

`TSP_Problems/` holds TSPLIB instances; the `.opt.tour` files are the known optimal tours.

| Problem  | Cities | Optimal distance |
|----------|-------:|-----------------:|
| berlin52 |     52 |             7542 |
| eil101   |    101 |              629 |
| bier127  |    127 |           118282 |
| a280     |    280 |             2579 |
| d18512   |  18512 |           645238 |

Only `EUC_2D` problems are supported. The number in the file name must match the
problem's `DIMENSION` (for example `eil101.tsp` has 101 cities).

## Files

| File                 | Purpose                                                     |
|----------------------|-------------------------------------------------------------|
| `tsp_gui.py`         | Tkinter GUI and the main GA loop                            |
| `tsp_parser.py`      | Reads TSPLIB `.tsp` files                                   |
| `tsp_distance.py`    | TSPLIB rounded Euclidean distance and tour length           |
| `tsp_ga_init_pop.py` | Initial population (shuffle or nearest-neighbour elitism)   |
| `tsp_ga.py`          | Selection, one-point and PMX crossover, mutation operators  |

## License

Apache 2.0, see `LICENSE`.
