## Project Goal
The goal of this project is to improve traffic flow at intersection.

## Fuzzy Controller Utilization
We are using a fuzzy controller that analyzes two key parameters:
1. The waiting time at a red light.
2. The number of vehicles waiting to cross.

Based on these data, the controller determines the priority, deciding which direction will get the green light.
## Launching
The intersection should be triggered by the following command:
```python
python main.py a b c d e
```
where:
- `a`, `b`, `c`, `d` - is probability of drawing a car in a specified direction
- `e` - the number of cars generated per second

## Inspiration
Our pygame visualization was inspired by the work presented in [Basic-Traffic-Intersection-Simulation](https://github.com/mihir-m-gandhi/Basic-Traffic-Intersection-Simulation/tree/main).
