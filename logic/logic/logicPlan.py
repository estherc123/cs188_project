# logicPlan.py
# ------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


"""
In logicPlan.py, you will implement logic planning methods which are called by
Pacman agents (in logicAgents.py).
"""

import util
import sys
import logic
import game

from logic import conjoin, disjoin
from logic import PropSymbolExpr, Expr, to_cnf, pycoSAT, parseExpr

import itertools
import copy

pacman_str = 'P'
food_str = 'FOOD'
wall_str = 'WALL'
pacman_wall_str = pacman_str + wall_str
ghost_pos_str = 'G'
ghost_east_str = 'GE'
pacman_alive_str = 'PA'
DIRECTIONS = ['North', 'South', 'East', 'West']
blocked_str_map = dict([(direction, (direction + "_blocked").upper()) for direction in DIRECTIONS])
geq_num_adj_wall_str_map = dict([(num, "GEQ_{}_adj_walls".format(num)) for num in range(1, 4)])
DIR_TO_DXDY_MAP = {'North':(0, 1), 'South':(0, -1), 'East':(1, 0), 'West':(-1, 0)}

class PlanningProblem:
    """
    This class outlines the structure of a planning problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the planning problem.
        """
        util.raiseNotDefined()

    def getGhostStartStates(self):
        """
        Returns a list containing the start state for each ghost.
        Only used in problems that use ghosts (FoodGhostPlanningProblem)
        """
        util.raiseNotDefined()

    def getGoalState(self):
        """
        Returns goal state for problem. Note only defined for problems that have
        a unique goal state such as PositionPlanningProblem
        """
        util.raiseNotDefined()


def tinyMazePlan(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s, s, w, s, w, w, s, w]


def sentence1():
    """Returns a Expr instance that encodes that the following expressions are all true.

    A or B
    (not A) if and only if ((not B) or C)
    (not A) or (not B) or C
    A ∨ B
    ¬ A ↔ (¬ B ∨ C)
    ¬ A ∨ ¬ B ∨ C
    """
    "*** BEGIN YOUR CODE HERE ***"
    a = Expr('A')
    b = Expr('B')
    c = Expr('C')
    expr_1 = a | b
    not_a = ~a
    not_b = ~b
    expr_2 = not_a % disjoin(not_b, c)
    expr_3 = disjoin(not_a, not_b, c)

    return conjoin(expr_1, expr_2, expr_3)
    "*** END YOUR CODE HERE ***"


def sentence2():
    """Returns a Expr instance that encodes that the following expressions are all true.

    C if and only if (B or D)
    A implies ((not B) and (not D))
    (not (B and (not C))) implies A
    (not D) implies C
    C ↔ (B ∨ D)

    A → (¬ B ∧ ¬ D)

    ¬ (B ∧ ¬ C) → A

    ¬ D → C
    """
    "*** BEGIN YOUR CODE HERE ***"
    a = Expr('A')
    b = Expr('B')
    c = Expr('C')
    d = Expr('D')
    not_b = ~b
    not_d = ~d
    not_c = ~c
    expression_1 = c % disjoin(b, d)
    expression_2 = a >> conjoin(not_b, not_d)
    expression_3 = ~ conjoin(b, not_c) >> a
    expression_4 = not_d >> c

    return conjoin(expression_1, expression_2, expression_3, expression_4)
    "*** END YOUR CODE HERE ***"


def sentence3():
    """Using the symbols PacmanAlive[1], PacmanAlive[0], PacmanBorn[0], and PacmanKilled[0],
    created using the PropSymbolExpr constructor, return a PropSymbolExpr
    instance that encodes the following English sentences (in this order):

    Pacman is alive at time 1 if and only if Pacman was alive at time 0 and it was
    not killed at time 0 or it was not alive at time 0 and it was born at time 0.
    PacmanAlive[1] <=> (PacmanAlive[0] & not PacmanKilled[0]) V (not PacmanAlive[0] & PacmanBorn[0])
    Pacman cannot both be alive at time 0 and be born at time 0.
    not (PacmanAlive[0] & PacmanBorn[0])
    Pacman is born at time 0.
    PacmanBorn[0]
    """
    "*** BEGIN YOUR CODE HERE ***"
    pa1 = PropSymbolExpr("PacmanAlive", 1)
    pa0 = PropSymbolExpr("PacmanAlive", 0)
    pb0 = PropSymbolExpr("PacmanBorn", 0)
    pk0 = PropSymbolExpr("PacmanKilled", 0)

    expression_1 = pa1 % disjoin(conjoin(pa0, ~ pk0),conjoin(~ pa0, pb0))
    expression_2 = ~ conjoin(pa0, pb0)
    expression_3 = pb0

    return conjoin(expression_1, expression_2, expression_3)
    "*** END YOUR CODE HERE ***"


def modelToString(model):
    """Converts the model to a string for printing purposes. The keys of a model are
    sorted before converting the model to a string.

    model: Either a boolean False or a dictionary of Expr symbols (keys)
    and a corresponding assignment of True or False (values). This model is the output of
    a call to pycoSAT.
    """
    if model == False:
        return "False"
    else:
        # Dictionary
        modelList = sorted(model.items(), key=lambda item: str(item[0]))
        return str(modelList)


def findModel(sentence):
    """Given a propositional logic sentence (i.e. a Expr instance), returns a satisfying
    model if one exists. Otherwise, returns False.
    """
    "*** BEGIN YOUR CODE HERE ***"
    return pycoSAT(to_cnf(sentence))
    "*** END YOUR CODE HERE ***"


def atLeastOne(literals):
    """
    Given a list of Expr literals (i.e. in the form A or ~A), return a single
    Expr instance in CNF (conjunctive normal form) that represents the logic
    that at least one of the literals in the list is true.
    >>> A = PropSymbolExpr('A');
    >>> B = PropSymbolExpr('B');
    >>> symbols = [A, B]
    >>> atleast1 = atLeastOne(symbols)
    >>> model1 = {A:False, B:False}
    >>> print(pl_true(atleast1,model1))
    False
    >>> model2 = {A:False, B:True}
    >>> print(pl_true(atleast1,model2))
    True
    >>> model3 = {A:True, B:True}
    >>> print(pl_true(atleast1,model2))
    True
    """
    "*** BEGIN YOUR CODE HERE ***"
    return disjoin(literals)
    "*** END YOUR CODE HERE ***"


def atMostOne(literals):
    """
    Given a list of Expr literals, return a single Expr instance in
    CNF (conjunctive normal form) that represents the logic that at most one of
    the expressions in the list is true.
    """
    "*** BEGIN YOUR CODE HERE ***"
    combinations = list(itertools.combinations(literals, 2))
    result = []
    for x in combinations:
        temp = disjoin(~x[0], ~x[1])
        result += [temp]

    return conjoin(result)
    "*** END YOUR CODE HERE ***"


def exactlyOne(literals):
    """
    Given a list of Expr literals, return a single Expr instance in
    CNF (conjunctive normal form)that represents the logic that exactly one of
    the expressions in the list is true.
    """
    "*** BEGIN YOUR CODE HERE ***"
    atleast = atLeastOne(literals)
    atMost = atMostOne(literals)
    return conjoin(atleast, atMost)
    "*** END YOUR CODE HERE ***"


def extractActionSequence(model, actions):
    """
    Convert a model in to an ordered list of actions.
    model: Propositional logic model stored as a dictionary with keys being
    the symbol strings and values being Boolean: True or False
    Example:
    >>> model = {"North[2]":True, "P[3,4,0]":True, "P[3,3,0]":False, "West[0]":True, "GhostScary":True, "West[2]":False, "South[1]":True, "East[0]":False}
    >>> actions = ['North', 'South', 'East', 'West']
    >>> plan = extractActionSequence(model, actions)
    >>> print(plan)
    ['West', 'South', 'North']
    """
    plan = [None for _ in range(len(model))]
    for sym, val in model.items():
        parsed = parseExpr(sym)
        if type(parsed) == tuple and parsed[0] in actions and val:
            action, time = parsed
            plan[int(time)] = action
    #return list(filter(lambda x: x is not None, plan))
    return [x for x in plan if x is not None]


def pacmanSuccessorStateAxioms(x, y, t, walls_grid, var_str=pacman_str):
    """
    Successor state axiom for state (x,y,t) (from t-1), given the board (as a
    grid representing the wall locations).
    Current <==> (previous position at time t-1) & (took action to move to x, y)
    Available actions are ['North', 'East', 'South', 'West']
    Note that STOP is not an available action.
    """
    possibilities = []
    if not walls_grid[x][y+1]:
        possibilities.append( PropSymbolExpr(var_str, x, y+1, t-1)
                            & PropSymbolExpr('South', t-1))
    if not walls_grid[x][y-1]:
        possibilities.append( PropSymbolExpr(var_str, x, y-1, t-1)
                            & PropSymbolExpr('North', t-1))
    if not walls_grid[x+1][y]:
        possibilities.append( PropSymbolExpr(var_str, x+1, y, t-1)
                            & PropSymbolExpr('West', t-1))
    if not walls_grid[x-1][y]:
        possibilities.append( PropSymbolExpr(var_str, x-1, y, t-1)
                            & PropSymbolExpr('East', t-1))

    if not possibilities:
        return None

    return PropSymbolExpr(var_str, x, y, t) % disjoin(possibilities)


def pacmanSLAMSuccessorStateAxioms(x, y, t, walls_grid, var_str=pacman_str):
    """
    Similar to `pacmanSuccessorStateAxioms` but accounts for illegal actions
    where the pacman might not move timestep to timestep.
    Available actions are ['North', 'East', 'South', 'West']
    """
    moved_tm1_possibilities = []
    if not walls_grid[x][y+1]:
        moved_tm1_possibilities.append( PropSymbolExpr(var_str, x, y+1, t-1)
                            & PropSymbolExpr('South', t-1))
    if not walls_grid[x][y-1]:
        moved_tm1_possibilities.append( PropSymbolExpr(var_str, x, y-1, t-1)
                            & PropSymbolExpr('North', t-1))
    if not walls_grid[x+1][y]:
        moved_tm1_possibilities.append( PropSymbolExpr(var_str, x+1, y, t-1)
                            & PropSymbolExpr('West', t-1))
    if not walls_grid[x-1][y]:
        moved_tm1_possibilities.append( PropSymbolExpr(var_str, x-1, y, t-1)
                            & PropSymbolExpr('East', t-1))

    if not moved_tm1_possibilities:
        return None

    moved_tm1_sent = conjoin([~PropSymbolExpr(var_str, x, y, t-1) , ~PropSymbolExpr(wall_str, x, y), disjoin(moved_tm1_possibilities)])

    unmoved_tm1_possibilities_aux_exprs = [] # merged variables
    aux_expr_defs = []
    for direction in DIRECTIONS:
        dx, dy = DIR_TO_DXDY_MAP[direction]
        wall_dir_clause = PropSymbolExpr(wall_str, x + dx, y + dy) & PropSymbolExpr(direction, t - 1)
        wall_dir_combined_literal = PropSymbolExpr(wall_str + direction, x + dx, y + dy, t - 1)
        unmoved_tm1_possibilities_aux_exprs.append(wall_dir_combined_literal)
        aux_expr_defs.append(wall_dir_combined_literal % wall_dir_clause)

    unmoved_tm1_sent = conjoin([
        PropSymbolExpr(var_str, x, y, t-1),
        disjoin(unmoved_tm1_possibilities_aux_exprs)])

    return conjoin([PropSymbolExpr(var_str, x, y, t) % disjoin([moved_tm1_sent, unmoved_tm1_sent])] + aux_expr_defs)


def pacphysics_axioms(t, all_coords, non_outer_wall_coords):
    """
    Given:
        t: timestep
        all_coords: list of (x, y) coordinates of the entire problem
        non_outer_wall_coords: list of (x, y) coordinates of the entire problem,
            excluding the outer border (these are the actual squares pacman can
            possibly be in)
    Return a logic sentence containing all of the following:
        - for all (x, y) in all_coords:
            If a wall is at (x, y) --> Pacman is not at (x, y)
        - Pacman is at exactly one of the squares at timestep t.
        - Pacman takes exactly one action at timestep t.
        PropSymbolExpr(pacman_str, x, y, t): whether or not Pacman is at (x, y) at time t
PropSymbolExpr(wall_str, x, y): whether or not a wall is at (x, y)
PropSymbolExpr(action, t): whether or not pacman takes action action at time t, where action is an element of DIRECTIONS

    """
    pacphysics_sentences = []
    expr_1_list = []
    "*** BEGIN YOUR CODE HERE ***"

    for coord in all_coords:
        x, y = coord[0], coord[1]
        expr_1_list += [PropSymbolExpr(wall_str,x,y) >> ~PropSymbolExpr(pacman_str, x, y, t)]
    expr_1 = conjoin(expr_1_list)
    expr_2_list = [PropSymbolExpr(pacman_str, coord[0], coord[1], t) for coord in non_outer_wall_coords]
    expr_2 = exactlyOne(expr_2_list)
    expr_3_list = [PropSymbolExpr(dir, t) for dir in DIRECTIONS]
    expr_3 = exactlyOne(expr_3_list)
    pacphysics_sentences = [expr_1, expr_2, expr_3]
    "*** END YOUR CODE HERE ***"
    return conjoin(pacphysics_sentences)


def check_location_satisfiability(x1_y1, x0_y0, action0, action1, problem):
    """
    Given:
        - x1_y1 = (x1, y1), a potential location at time t = 1
        - x0_y0 = (x0, y0), Pacman's location at time t = 0
        - action0 = one of the four items in DIRECTIONS, Pacman's action at time t = 0
        - problem = An instance of logicAgents.LocMapProblem
    Return:
        - a model proving whether Pacman is at (x1, y1) at time t = 1
        - a model proving whether Pacman is not at (x1, y1) at time t = 1
    """

    walls_grid = problem.walls
    walls_list = walls_grid.asList()
    all_coords = list(itertools.product(range(problem.getWidth()+2), range(problem.getHeight()+2)))
    non_outer_wall_coords = list(itertools.product(range(1, problem.getWidth()+1), range(1, problem.getHeight()+1)))
    KB = []
    x0, y0 = x0_y0
    x1, y1 = x1_y1

    # We know which coords are walls:
    map_sent = [PropSymbolExpr(wall_str, x, y) for x, y in walls_list]
    KB.append(conjoin(map_sent))
    KB.append(PropSymbolExpr(pacman_str, x0, y0, 0))
    KB.append(pacphysics_axioms(0, all_coords, non_outer_wall_coords))
    KB.append(PropSymbolExpr(action0, 0))
    KB.append(allLegalSuccessorAxioms(1, walls_grid, non_outer_wall_coords))
    KB.append(pacphysics_axioms(1, all_coords, non_outer_wall_coords))
    KB.append(PropSymbolExpr(action1, 1))
    "*** BEGIN YOUR CODE HERE ***"
    kb = conjoin(KB)
    result = [findModel(conjoin(kb, ~PropSymbolExpr(pacman_str, x1, y1, 1))), findModel(conjoin(kb, PropSymbolExpr(pacman_str, x1, y1, 1)))]
    return result
    "*** END YOUR CODE HERE ***"


def positionLogicPlan(problem):
    """
    Given an instance of a PositionPlanningProblem, return a list of actions that lead to the goal.
    Available actions are ['North', 'East', 'South', 'West']
    Note that STOP is not an available action.
    """
    walls = problem.walls
    width, height = problem.getWidth(), problem.getHeight()
    walls_list = walls.asList()
    x0, y0 = problem.startState
    xg, yg = problem.goal

    # Get lists of possible locations (i.e. without walls) and possible actions
    all_coords = list(itertools.product(range(width + 2),
            range(height + 2)))
    non_wall_coords = [loc for loc in all_coords if loc not in walls_list]
    actions = [ 'North', 'South', 'East', 'West' ]
    KB = []

    "*** BEGIN YOUR CODE HERE ***"
    KB.append(PropSymbolExpr(pacman_str, x0, y0, 0))
    for t in range(50):
        KB.append(exactlyOne([PropSymbolExpr(pacman_str, loc[0], loc[1], t) for loc in non_wall_coords]))
        kb = conjoin(KB)
        models = findModel(conjoin(kb, PropSymbolExpr(pacman_str, xg, yg, t)))
        if models:
            return extractActionSequence(models, actions)
        KB.append(exactlyOne([PropSymbolExpr(action, t) for action in actions]))
        for position in non_wall_coords:
            KB.append(pacmanSuccessorStateAxioms(position[0], position[1], t + 1, walls, var_str=pacman_str))
    "*** END YOUR CODE HERE ***"


def foodLogicPlan(problem):
    """
    Given an instance of a FoodPlanningProblem, return a list of actions that help Pacman
    eat all of the food.
    Available actions are ['North', 'East', 'South', 'West']
    Note that STOP is not an available action.
    """
    walls = problem.walls
    width, height = problem.getWidth(), problem.getHeight()
    walls_list = walls.asList()
    (x0, y0), food = problem.start
    food = food.asList()

    # Get lists of possible locations (i.e. without walls) and possible actions
    all_coords = list(itertools.product(range(width + 2), range(height + 2)))

    #locations = list(filter(lambda loc : loc not in walls_list, all_coords))
    non_wall_coords = [loc for loc in all_coords if loc not in walls_list]
    actions = [ 'North', 'South', 'East', 'West' ]

    KB = []

    "*** BEGIN YOUR CODE HERE ***"
    KB.append(PropSymbolExpr(pacman_str, x0, y0, 0))
    foods2 = []
    for f in food:
        foods2.append(PropSymbolExpr(food_str, f[0], f[1], 0))
    foods2_conjoined = conjoin(foods2)
    KB.append(foods2_conjoined)
    for t in range(50):
        KB.append(exactlyOne([PropSymbolExpr(pacman_str, loc[0], loc[1], t) for loc in non_wall_coords]))
        kb = conjoin(KB)
        foods = []
        for f in food:
            foods.append(PropSymbolExpr(food_str, f[0], f[1], t))
        goal_assert = conjoin([~food for food in foods])
        models = findModel(conjoin(kb, goal_assert))
        if models:
            return extractActionSequence(models, actions)
        KB.append(exactlyOne([PropSymbolExpr(action, t) for action in actions]))
        for position in non_wall_coords:
            KB.append(pacmanSuccessorStateAxioms(position[0], position[1], t + 1, walls, var_str=pacman_str))
            food_successor_axiom = conjoin(PropSymbolExpr(food_str, position[0], position[1], t), PropSymbolExpr(pacman_str, position[0], position[1], t)) | ~PropSymbolExpr(food_str, position[0], position[1], t) %  ~PropSymbolExpr(food_str, position[0], position[1], t+1)

            KB.append(food_successor_axiom)
    "*** END YOUR CODE HERE ***"


# Helpful Debug Method
def visualize_coords(coords_list, problem):
    wallGrid = game.Grid(problem.walls.width, problem.walls.height, initialValue=False)
    for (x, y) in itertools.product(range(problem.getWidth()+2), range(problem.getHeight()+2)):
        if (x, y) in coords_list:
            wallGrid.data[x][y] = True
    print(wallGrid)


# Helpful Debug Method
def visualize_bool_array(bool_arr, problem):
    wallGrid = game.Grid(problem.walls.width, problem.walls.height, initialValue=False)
    wallGrid.data = copy.deepcopy(bool_arr)
    print(wallGrid)


def sensorAxioms(t, non_outer_wall_coords):
    all_percept_exprs = []
    combo_var_def_exprs = []
    for direction in DIRECTIONS:
        percept_exprs = []
        dx, dy = DIR_TO_DXDY_MAP[direction]
        for x, y in non_outer_wall_coords:
            combo_var = PropSymbolExpr(pacman_wall_str, x, y, t, x + dx, y + dy)
            percept_exprs.append(combo_var)
            combo_var_def_exprs.append(combo_var % (
                PropSymbolExpr(pacman_str, x, y, t) & PropSymbolExpr(wall_str, x + dx, y + dy)))

        percept_unit_clause = PropSymbolExpr(blocked_str_map[direction], t)
        all_percept_exprs.append(percept_unit_clause % disjoin(percept_exprs))

    return conjoin(all_percept_exprs + combo_var_def_exprs)


def four_bit_percept_rules(t, percepts):
    """
    Localization and Mapping both use the 4 bit sensor, which tells us True/False whether
    a wall is to pacman's north, south, east, and west.
    """
    assert isinstance(percepts, list), "Percepts must be a list."
    assert len(percepts) == 4, "Percepts must be a length 4 list."

    percept_unit_clauses = []
    for wall_present, direction in zip(percepts, DIRECTIONS):
        percept_unit_clause = PropSymbolExpr(blocked_str_map[direction], t)
        if not wall_present:
            percept_unit_clause = ~PropSymbolExpr(blocked_str_map[direction], t)
        percept_unit_clauses.append(percept_unit_clause) # The actual sensor readings
    return conjoin(percept_unit_clauses)


def num_adj_walls_percept_rules(t, percepts):
    """
    SLAM uses a weaker num_adj_walls sensor, which tells us how many walls pacman is adjacent to
    in its four directions.
        000 = 0 adj walls.
        100 = 1 adj wall.
        110 = 2 adj walls.
        111 = 3 adj walls.
    """
    assert isinstance(percepts, list), "Percepts must be a list."
    assert len(percepts) == 3, "Percepts must be a length 3 list."

    percept_unit_clauses = []
    num_adj_walls = sum(percepts)
    for i, percept in enumerate(percepts):
        n = i + 1
        percept_literal_n = PropSymbolExpr(geq_num_adj_wall_str_map[n], t)
        if not percept:
            percept_literal_n = ~percept_literal_n
        percept_unit_clauses.append(percept_literal_n)
    return conjoin(percept_unit_clauses)


def SLAMSensorAxioms(t, non_outer_wall_coords):
    all_percept_exprs = []
    combo_var_def_exprs = []
    for direction in DIRECTIONS:
        percept_exprs = []
        dx, dy = DIR_TO_DXDY_MAP[direction]
        for x, y in non_outer_wall_coords:
            combo_var = PropSymbolExpr(pacman_wall_str, x, y, t, x + dx, y + dy)
            percept_exprs.append(combo_var)
            combo_var_def_exprs.append(combo_var % (PropSymbolExpr(pacman_str, x, y, t) & PropSymbolExpr(wall_str, x + dx, y + dy)))

        blocked_dir_clause = PropSymbolExpr(blocked_str_map[direction], t)
        all_percept_exprs.append(blocked_dir_clause % disjoin(percept_exprs))

    percept_to_blocked_sent = []
    for n in range(1, 4):
        wall_combos_size_n = itertools.combinations(blocked_str_map.values(), n)
        n_walls_blocked_sent = disjoin([
            conjoin([PropSymbolExpr(blocked_str, t) for blocked_str in wall_combo])
            for wall_combo in wall_combos_size_n])
        # n_walls_blocked_sent is of form: (N & S) | (N & E) | ...
        percept_to_blocked_sent.append(
            PropSymbolExpr(geq_num_adj_wall_str_map[n], t) % n_walls_blocked_sent)
    return conjoin(all_percept_exprs + combo_var_def_exprs + percept_to_blocked_sent)


def allLegalSuccessorAxioms(t, walls_grid, non_outer_wall_coords):
    all_xy_succ_axioms = []
    for x, y in non_outer_wall_coords:
        xy_succ_axiom = pacmanSuccessorStateAxioms(
            x, y, t, walls_grid, var_str=pacman_str)
        if xy_succ_axiom:
            all_xy_succ_axioms.append(xy_succ_axiom)
    return conjoin(all_xy_succ_axioms)


def SLAMSuccessorAxioms(t, walls_grid, non_outer_wall_coords):
    all_xy_succ_axioms = []
    for x, y in non_outer_wall_coords:
        xy_succ_axiom = pacmanSLAMSuccessorStateAxioms(
            x, y, t, walls_grid, var_str=pacman_str)
        if xy_succ_axiom:
            all_xy_succ_axioms.append(xy_succ_axiom)
    return conjoin(all_xy_succ_axioms)


def localization(problem, agent):
    '''
    problem: a LocalizationProblem instance
    agent: a LocalizationLogicAgent instance
    '''
    debug = False

    walls_grid = problem.walls
    walls_list = walls_grid.asList()
    all_coords = list(itertools.product(range(problem.getWidth()+2), range(problem.getHeight()+2)))
    non_outer_wall_coords = list(itertools.product(range(1, problem.getWidth()+1), range(1, problem.getHeight()+1)))

    possible_locs_by_timestep = []
    KB = []

    "*** BEGIN YOUR CODE HERE ***"
    for coord in all_coords:
        x,y = coord[0], coord[1]
        if coord in walls_list:
            KB.append(PropSymbolExpr(wall_str,x,y))
        else:
            KB.append(~PropSymbolExpr(wall_str,x,y))

    for t in range(agent.num_timesteps):
        KB.append(pacphysics_axioms(t, all_coords, non_outer_wall_coords))
        KB.append(PropSymbolExpr(agent.actions[t], t))
        sensor = sensorAxioms(t, non_outer_wall_coords)
        KB.append(sensor)
        KB.append(four_bit_percept_rules(t, agent.getPercepts()))

        possible_locations_t = []
        for coord in non_outer_wall_coords:
            kb = conjoin(KB)
            x,y = coord[0], coord[1]
            at_here = findModel(conjoin(kb, PropSymbolExpr(pacman_str,x,y,t)))
            not_here = findModel(conjoin(kb, ~PropSymbolExpr(pacman_str,x,y,t)))
            if not not_here:
                KB.append(PropSymbolExpr(pacman_str,x,y,t))
            if not at_here:
                KB.append(~PropSymbolExpr(pacman_str,x,y,t))
            if at_here:
                possible_locations_t.append(coord)

        possible_locs_by_timestep.append(possible_locations_t)

        agent.moveToNextState(agent.actions[t])
        KB.append(allLegalSuccessorAxioms(t + 1, walls_grid, non_outer_wall_coords))



    "*** END YOUR CODE HERE ***"
    return possible_locs_by_timestep


def mapping(problem, agent):
    '''
    problem: a MappingProblem instance
    agent: a MappingLogicAgent instance
    '''
    debug = False

    pac_x_0, pac_y_0 = problem.startState
    KB = []
    all_coords = list(itertools.product(range(problem.getWidth()+2), range(problem.getHeight()+2)))
    non_outer_wall_coords = list(itertools.product(range(1, problem.getWidth()+1), range(1, problem.getHeight()+1)))

    #map describes what we know, for GUI rendering purposes. -1 is unknown, 0 is open, 1 is wall
    known_map = [[-1 for y in range(problem.getHeight()+2)] for x in range(problem.getWidth()+2)]
    known_map_by_timestep = []

    # Pacman knows that the outer border of squares are all walls
    outer_wall_sent = []
    for x, y in all_coords:
        if ((x == 0 or x == problem.getWidth() + 1)
                or (y == 0 or y == problem.getHeight() + 1)):
            known_map[x][y] = 1
            outer_wall_sent.append(PropSymbolExpr(wall_str, x, y))
    KB.append(conjoin(outer_wall_sent))

    "*** BEGIN YOUR CODE HERE ***"
    KB.append(PropSymbolExpr(pacman_str,pac_x_0, pac_y_0,0))
    for t in range(agent.num_timesteps):
        KB.append(pacphysics_axioms(t, all_coords, non_outer_wall_coords))
        KB.append(PropSymbolExpr(agent.actions[t], t))
        sensor = sensorAxioms(t, non_outer_wall_coords)
        KB.append(sensor)
        KB.append(four_bit_percept_rules(t, agent.getPercepts()))

        for coord in non_outer_wall_coords:
            kb = conjoin(KB)
            x,y = coord[0], coord[1]
            at_here = findModel(conjoin(kb, PropSymbolExpr(wall_str,x,y)))
            not_here = findModel(conjoin(kb, ~PropSymbolExpr(wall_str,x,y)))
            if not not_here:
                KB.append(PropSymbolExpr(wall_str,x,y))
                known_map[x][y] = 1
            if not at_here:
                KB.append(~PropSymbolExpr(wall_str,x,y))
                known_map[x][y] = 0
        known_map_by_timestep.append(copy.deepcopy(known_map))

        agent.moveToNextState(agent.actions[t])
        KB.append(allLegalSuccessorAxioms(t + 1, known_map, non_outer_wall_coords))


    "*** END YOUR CODE HERE ***"
    return known_map_by_timestep


def slam(problem, agent):
    '''
    problem: a SLAMProblem instance
    agent: a SLAMLogicAgent instance
    '''
    debug = False

    pac_x_0, pac_y_0 = problem.startState
    KB = []
    all_coords = list(itertools.product(range(problem.getWidth()+2), range(problem.getHeight()+2)))
    non_outer_wall_coords = list(itertools.product(range(1, problem.getWidth()+1), range(1, problem.getHeight()+1)))

    # map describes what we know, for GUI rendering purposes. -1 is unknown, 0 is open, 1 is wall
    known_map = [[-1 for y in range(problem.getHeight()+2)] for x in range(problem.getWidth()+2)]
    known_map_by_timestep = []
    possible_locs_by_timestep = []

    # We know that the outer_coords are all walls.
    outer_wall_sent = []
    for x, y in all_coords:
        if ((x == 0 or x == problem.getWidth() + 1)
                or (y == 0 or y == problem.getHeight() + 1)):
            known_map[x][y] = 1
            outer_wall_sent.append(PropSymbolExpr(wall_str, x, y))
    KB.append(conjoin(outer_wall_sent))

    "*** BEGIN YOUR CODE HERE ***"
    KB.append(PropSymbolExpr(pacman_str,pac_x_0, pac_y_0,0))
    for t in range(agent.num_timesteps):
        KB.append(pacphysics_axioms(t, all_coords, non_outer_wall_coords))
        KB.append(PropSymbolExpr(agent.actions[t], t))
        sensor = SLAMSensorAxioms(t, non_outer_wall_coords)
        KB.append(sensor)
        KB.append(num_adj_walls_percept_rules(t, agent.getPercepts()))

        for coord in non_outer_wall_coords:
            kb = conjoin(KB)
            x,y = coord[0], coord[1]
            at_here = findModel(conjoin(kb, PropSymbolExpr(wall_str,x,y)))
            not_here = findModel(conjoin(kb, ~PropSymbolExpr(wall_str,x,y)))
            if not not_here:
                KB.append(PropSymbolExpr(wall_str,x,y))
                known_map[x][y] = 1
            if not at_here:
                KB.append(~PropSymbolExpr(wall_str,x,y))
                known_map[x][y] = 0
        known_map_by_timestep.append(copy.deepcopy(known_map))

        possible_locations_t = []
        for coord in non_outer_wall_coords:
            kb = conjoin(KB)
            x,y = coord[0], coord[1]
            at_here = findModel(conjoin(kb, PropSymbolExpr(pacman_str,x,y,t)))
            not_here = findModel(conjoin(kb, ~PropSymbolExpr(pacman_str,x,y,t)))
            if not not_here:
                KB.append(PropSymbolExpr(pacman_str,x,y,t))
            if not at_here:
                KB.append(~PropSymbolExpr(pacman_str,x,y,t))
            if at_here:
                possible_locations_t.append(coord)

        possible_locs_by_timestep.append(possible_locations_t)

        agent.moveToNextState(agent.actions[t])

        sure_map = [[False for y in range(problem.getHeight()+2)] for x in range(problem.getWidth()+2)]
        for x in range(problem.getWidth()+2):
            for y in range(problem.getHeight()+2):
                if known_map[x][y] == 1:
                    sure_map[x][y] = True
        KB.append(SLAMSuccessorAxioms(t + 1, sure_map, non_outer_wall_coords))

    "*** END YOUR CODE HERE ***"
    return known_map_by_timestep, possible_locs_by_timestep

# Abbreviations
plp = positionLogicPlan
loc = localization
mp = mapping
flp = foodLogicPlan
# Sometimes the logic module uses pretty deep recursion on long expressions
sys.setrecursionlimit(100000)
