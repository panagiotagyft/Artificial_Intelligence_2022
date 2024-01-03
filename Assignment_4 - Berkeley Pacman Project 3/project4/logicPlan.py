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

from typing import Dict, List, Tuple, Callable, Generator, Any
import util
import sys
import logic
import game

from logic import conjoin, disjoin
from logic import PropSymbolExpr, Expr, to_cnf, pycoSAT, parseExpr, pl_true

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


#______________________________________________________________________________
# QUESTION 1

def sentence1() -> Expr:
    """Returns a Expr instance that encodes that the following expressions are all true.
    
    A or B
    (not A) if and only if ((not B) or C)
    (not A) or (not B) or C
    """
    "*** BEGIN YOUR CODE HERE ***"
    
    # Expr object definition
    A = Expr('A')
    B = Expr('B')
    C = Expr('C')

    # ( A | B )
    A__OR__B = disjoin(A , B)   # disjoin() return a chained (logical OR) expression

    # -A <-> (-B | C)
    notA = ~ A
    notB = ~ B
    notB__OR__C = disjoin(notB , C)
    notA__IFF__notB_OR_C = notA % notB__OR__C


    # -A | -B | C
    notA_OR_notB_OR_C = disjoin(notA , notB , C)

    # return the list conjoined
    returnExpr = conjoin(A__OR__B , notA__IFF__notB_OR_C , notA_OR_notB_OR_C)
   
    return returnExpr

    # util.raiseNotDefined()
    "*** END YOUR CODE HERE ***"


def sentence2() -> Expr:
    """Returns a Expr instance that encodes that the following expressions are all true.
    
    C if and only if (B or D)
    A implies ((not B) and (not D))
    (not (B and (not C))) implies A
    (not D) implies C
    """
    "*** BEGIN YOUR CODE HERE ***"
    
    # Expr object definition
    A = Expr('A')
    B = Expr('B')
    C = Expr('C')
    D = Expr('D')

    # C <-> (B | D)
    B_OR_D = disjoin(B, D)      # return (B | D)
    C__IFF__B_OR_D = C % B_OR_D     # return C <-> (B | D)

    # A -> (-B | -D)
    notB = ~ B
    notD = ~ D
    notB_AND_notD =  conjoin(notB , notD)
    A__IF__notB_AND_notD = A >> notB_AND_notD

    # -(B | -C) -> A
    notC = ~ C 
    B__AND__notC = conjoin(B , notC)
    IF__not_B_AND_notC__THEN__A =  ~ B__AND__notC >> A

    # -D -> C
    IF__notD__THEN__C = ~ D >> C

    # return the list conjoined
    returnExpr = conjoin(C__IFF__B_OR_D , A__IF__notB_AND_notD , IF__not_B_AND_notC__THEN__A , IF__notD__THEN__C)

    return returnExpr

    # util.raiseNotDefined()
    "*** END YOUR CODE HERE ***"


def sentence3() -> Expr:
    """Using the symbols PacmanAlive_1 PacmanAlive_0, PacmanBorn_0, and PacmanKilled_0,
    created using the PropSymbolExpr constructor, return a PropSymbolExpr
    instance that encodes the following English sentences (in this order):

    Pacman is alive at time 1 if and only if Pacman was alive at time 0 and it was
    not killed at time 0 or it was not alive at time 0 and it was born at time 0.

    Pacman cannot both be alive at time 0 and be born at time 0.

    Pacman is born at time 0.
    (Project update: for this question only, [0] and _t are both acceptable.)
    """
    "*** BEGIN YOUR CODE HERE ***"
    
    # Pacphysics symbols
    PacmanAlive_1 = PropSymbolExpr('PacmanAlive' , 1)
    PacmanAlive_0 = PropSymbolExpr('PacmanAlive' , 0)
    PacmanBorn_0 = PropSymbolExpr('PacmanBorn' , 0)
    PacmanKilled_0 = PropSymbolExpr('PacmanKilled' , 0)
   
    # -- Convertion of corresponding sentences as propositional logic --    
    # 1. Pacman is alive at time 1 if and only if he was alive at time 0 and he was not 
    # killed at time 0 or he was not alive at time 0 and he was born at time 0.
    sentence_one = PacmanAlive_1 % ( ( PacmanAlive_0 & (~ PacmanKilled_0) ) | ( (~  PacmanAlive_0) & PacmanBorn_0 ) )
    
    # 2. At time 0, Pacman cannot both be alive and be born.
    sentence_two = ~ ( PacmanAlive_0 & PacmanBorn_0)

    # 3. Pacman is born at time 0.
    sentence_three = PacmanBorn_0
    
    # return the list conjoined
    returnExpr = conjoin(sentence_one , sentence_two , sentence_three) 

    return returnExpr

    # util.raiseNotDefined()
    "*** END YOUR CODE HERE ***"

def findModel(sentence: Expr) -> Dict[Expr, bool]:
    """Given a propositional logic sentence (i.e. a Expr instance), returns a satisfying
    model if one exists. Otherwise, returns False.
    """
    cnf_sentence = to_cnf(sentence)
    return pycoSAT(cnf_sentence)

def findModelCheck() -> Dict[Any, bool]:
    """Returns the cmbs of findModel(Expr('a')) if lower cased expressions were allowed.
    You should not use findModel or Expr in this method.
    This can be solved with a one-line return statement.
    """
    class dummyClass:
        """dummy('A') has representation A, unlike a string 'A' that has repr 'A'.
        Of note: Expr('Name') has representation Name, not 'Name'.
        """
        def __init__(self, variable_name: str = 'A'):
            self.variable_name = variable_name
        
        def __repr__(self):
            return self.variable_name
    "*** BEGIN YOUR CODE HERE ***"

    a = dummyClass('a')     # dummy('a') has representation a
    dict = {a: True}        # satisfying model
    
    return dict
    # util.raiseNotDefined()
    "*** END YOUR CODE HERE ***"

def entails(premise: Expr, conclusion: Expr) -> bool:
    """Returns True if the premise entails the conclusion and False otherwise.
    """
    "*** BEGIN YOUR CODE HERE ***"
    
    # p.258 AIMA   premise |= conclusion  
    expr = premise & (~ conclusion ) 
    
    # The premise satisfies conclusion ? 
    # If return item is False then yes ->> The premise satisfies conclusion!
    # else ->> The premise doesn't satisfy conclusion!!
    if findModel(expr) == False: return True
    else:
        return False

    # util.raiseNotDefined()
    "*** END YOUR CODE HERE ***"

def plTrueInverse(assignments: Dict[Expr, bool], inverse_statement: Expr) -> bool:
    """Returns True if the (not inverse_statement) is True given assignments and False otherwise.
    pl_true may be useful here; see logic.py for its description.
    """
    "*** BEGIN YOUR CODE HERE ***"
    
    if pl_true(~inverse_statement, assignments) == True: return True
    else: 
        return False
    
    # util.raiseNotDefined()
    "*** END YOUR CODE HERE ***"

#______________________________________________________________________________
# QUESTION 2

def atLeastOne(literals: List[Expr]) -> Expr:
    """
    Given a list of Expr literals (i.e. in the form A or ~A), return a single 
    Expr instance in CNF (conjunctive normal form) that represents the logic 
    that at least one of the literals  ist is true.
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
    
    # return a single expr in CNF that at least one of the literals is true
    CNF = disjoin(literals) 
    
    return CNF
    util.raiseNotDefined()
    "*** END YOUR CODE HERE ***"


def atMostOne(literals: List[Expr]) -> Expr:
    """
    Given a list of Expr literals, return a single Expr instance in 
    CNF (conjunctive normal form) that represents the logic that at most one of 
    the expressions in the list is true.
    itertools.combinations may be useful here.
    """
    "*** BEGIN YOUR CODE HERE ***"
 
    cmbs = list( itertools.combinations(literals , 2) )     # combination function generator
   
    # Goal:  ( (A | B) & (A | C) & (B | C) )  -->> we don't want any evidence to be true!
    CNF = [ disjoin(~cmbs[i][0], ~cmbs[i][1])  for i in range( len(cmbs) ) ]  # create disjoin pairs
    CNF = conjoin(CNF)  # conjoin this pairs
    
    return CNF

    # util.raiseNotDefined()
    "*** END YOUR CODE HERE ***"


def exactlyOne(literals: List[Expr]) -> Expr:
    """
    Given a list of Expr literals, return a single Expr instance in 
    CNF (conjunctive normal form)that represents the logic that exactly one of 
    the expressions in the list is true.
    """
    "*** BEGIN YOUR CODE HERE ***"

    # atLeastOne & atMostOne
    cmbs = list( itertools.combinations(literals , 2) )
    CNF = [ disjoin(~cmbs[i][0], ~cmbs[i][1])  for i in range( len(cmbs) ) ]
    CNF = conjoin( conjoin(CNF) , disjoin(literals) ) 

    return CNF

    # util.raiseNotDefined()
    "*** END YOUR CODE HERE ***"

#______________________________________________________________________________
# QUESTION 3

def pacmanSuccessorAxiomSingle(x: int, y: int, time: int, walls_grid: List[List[bool]]=None) -> Expr:
    """
    Successor state axiom for state (x,y,t) (from t-1), given the board (as a 
    grid representing the wall locations).
    Current <==> (previous position at time t-1) & (took action to move to x, y)
    Available actions are ['North', 'East', 'South', 'West']
    Note that STOP is not an available action.
    """
    now, last = time, time - 1
    possible_causes: List[Expr] = [] # enumerate all possible causes for P[x,y]_t
    # the if statements give a small performance boost and are required for q4 and q5 correctness
 
    if walls_grid[x][y+1] != 1:
        possible_causes.append( PropSymbolExpr(pacman_str, x, y+1, time=last)
                            & PropSymbolExpr('South', time=last))
    if walls_grid[x][y-1] != 1:
        possible_causes.append( PropSymbolExpr(pacman_str, x, y-1, time=last) 
                            & PropSymbolExpr('North', time=last))
    if walls_grid[x+1][y] != 1:
        possible_causes.append( PropSymbolExpr(pacman_str, x+1, y, time=last) 
                            & PropSymbolExpr('West', time=last))
    if walls_grid[x-1][y] != 1:
        possible_causes.append( PropSymbolExpr(pacman_str, x-1, y, time=last) 
                            & PropSymbolExpr('East', time=last))
    if not possible_causes:
        return None
    
    "*** BEGIN YOUR CODE HERE ***"

    # Pacman may be in position xy at time t if and only if the possible conditions apply
    # Pacman_xy_t <--> possible_causes
    returnExpr = PropSymbolExpr(pacman_str, x, y, time = now) % disjoin(possible_causes)

    return returnExpr
    
    # util.raiseNotDefined()
    "*** END YOUR CODE HERE ***"


def SLAMSuccessorAxiomSingle(x: int, y: int, time: int, walls_grid: List[List[bool]]) -> Expr:
    """
    Similar to `pacmanSuccessorStateAxioms` but accounts for illegal actions
    where the pacman might not move timestep to timestep.
    Available actions are ['North', 'East', 'South', 'West']
    """
    now, last = time, time - 1
    moved_causes: List[Expr] = [] # enumerate all possible causes for P[x,y]_t, assuming moved to having moved
    if walls_grid[x][y+1] != 1:
        moved_causes.append( PropSymbolExpr(pacman_str, x, y+1, time=last)
                            & PropSymbolExpr('South', time=last))
    if walls_grid[x][y-1] != 1:
        moved_causes.append( PropSymbolExpr(pacman_str, x, y-1, time=last) 
                            & PropSymbolExpr('North', time=last))
    if walls_grid[x+1][y] != 1:
        moved_causes.append( PropSymbolExpr(pacman_str, x+1, y, time=last) 
                            & PropSymbolExpr('West', time=last))
    if walls_grid[x-1][y] != 1:
        moved_causes.append( PropSymbolExpr(pacman_str, x-1, y, time=last) 
                            & PropSymbolExpr('East', time=last))
    if not moved_causes:
        return None

    moved_causes_sent: Expr = conjoin([~PropSymbolExpr(pacman_str, x, y, time=last) , ~PropSymbolExpr(wall_str, x, y), disjoin(moved_causes)])

    failed_move_causes: List[Expr] = [] # using merged variables, improves speed significantly
    auxilary_expression_definitions: List[Expr] = []
    for direction in DIRECTIONS:
        dx, dy = DIR_TO_DXDY_MAP[direction]
        wall_dir_clause = PropSymbolExpr(wall_str, x + dx, y + dy) & PropSymbolExpr(direction, time=last)
        wall_dir_combined_literal = PropSymbolExpr(wall_str + direction, x + dx, y + dy, time=last)
        failed_move_causes.append(wall_dir_combined_literal)
        auxilary_expression_definitions.append(wall_dir_combined_literal % wall_dir_clause)

    failed_move_causes_sent: Expr = conjoin([
        PropSymbolExpr(pacman_str, x, y, time=last),
        disjoin(failed_move_causes)])

    return conjoin([PropSymbolExpr(pacman_str, x, y, time=now) % disjoin([moved_causes_sent, failed_move_causes_sent])] + auxilary_expression_definitions)


def pacphysicsAxioms(t: int, all_coords: List[Tuple], non_outer_wall_coords: List[Tuple], walls_grid: List[List] = None, sensorModel: Callable = None, successorAxioms: Callable = None) -> Expr:
    """
    Given:
        t: timestep
        all_coords: list of (x, y) coordinates of the entire problem
        non_outer_wall_coords: list of (x, y) coordinates of the entire problem,
            excluding the outer border (these are the actual squares pacman can
            possibly be in)
        walls_grid: 2D array of either -1/0/1 or T/F. Used only for successorAxioms.
            Do NOT use this when making possible locations for pacman to be in.
        sensorModel(t, non_outer_wall_coords) -> Expr: function that generates
            the sensor model axioms. If None, it's not provided, so shouldn't be run.
        successorAxioms(t, walls_grid, non_outer_wall_coords) -> Expr: function that generates
            the sensor model axioms. If None, it's not provided, so shouldn't be run.
    Return a logic sentence containing all of the following:
        - for all (x, y) in all_coords:
            If a wall is at (x, y) --> Pacman is not at (x, y)
        - Pacman is at exactly one of the squares at timestep t.
        - Pacman takes exactly one action at timestep t.
        - cmbss of calling sensorModel(...), unless None.
        - cmbss of calling successorAxioms(...), describing how Pacman can end in various
            locations on this time step. Consider edge cases. Don't call if None.
    """
    pacphysics_sentences = []

    "*** BEGIN YOUR CODE HERE ***"
    
    # - for all (x, y) in all_coords:
    #       If a wall is at (x, y) --> Pacman is not at (x, y)
    Pacman_xy = [ PropSymbolExpr(wall_str, all_coords[i][0], all_coords[i][1])  >> ~ PropSymbolExpr(pacman_str, all_coords[i][0], all_coords[i][1], time=t) 
                  for i in range( len(all_coords) ) ]
    pacphysics_sentences.append( conjoin(Pacman_xy) )
    
    # - Pacman is at exactly one of the squares at timestep t.
    Pacman_t = [ PropSymbolExpr(pacman_str, non_outer_wall_coords[i][0], non_outer_wall_coords[i][1], time = t) 
                 for i in range( len(non_outer_wall_coords) ) ]
    pacphysics_sentences.append( exactlyOne(Pacman_t) )

    # Pacman takes exactly one of the four actions in DIRECTIONS at timestep t.
    Action_t = [ PropSymbolExpr(direction, time = t) for direction in DIRECTIONS ]
    pacphysics_sentences.append( exactlyOne(Action_t) )

    if sensorModel is not None:
        pacphysics_sentences.append( sensorModel(t, non_outer_wall_coords) )
    
    #  Transitions: append the result of successorAxioms.
    if successorAxioms is not None and t is not 0:
        pacphysics_sentences.append( successorAxioms(t, walls_grid, non_outer_wall_coords) )

    # util.raiseNotDefined()
    "*** END YOUR CODE HERE ***"

    return conjoin(pacphysics_sentences)


def checkLocationSatisfiability(x1_y1: Tuple[int, int], x0_y0: Tuple[int, int], action0, action1, problem):
    """
    Given:
        - x1_y1 = (x1, y1), a potential location at time t = 1
        - x0_y0 = (x0, y0), Pacman's location at time t = 0
        - action0 = one of the four items in DIRECTIONS, Pacman's action at time t = 0
        - action1 = to ensure match with autograder solution
        - problem = an instance of logicAgents.LocMapProblem
    Note:
        - there's no sensorModel because we know everything about the world
        - the successorAxioms should be allLegalSuccessorAxioms where needed
    Return:
        - a model where Pacman is at (x1, y1) at time t = 1
        - a model where Pacman is not at (x1, y1) at time t = 1
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

    "*** BEGIN YOUR CODE HERE ***"
    
    # representation of important information
    Pacman_x1y1_t1 = PropSymbolExpr(pacman_str, x1, y1, time = 1)
    Pacman_x0y0_t0 = PropSymbolExpr(pacman_str, x0, y0, time = 0)
    Action_t0 = PropSymbolExpr(action0, time = 0)
    Action_t1 = PropSymbolExpr(action1, time = 1)
    
    # Add to KB: Pacman's current location (x0, y0) -- AND --- Add to KB: Pacman takes action0 
    # -- AND --- Add to KB: Pacman takes action1
    KB.append( conjoin(Pacman_x0y0_t0, Action_t0, Action_t1) )

    # Add to KB: pacphysics_axioms(...) with the appropriate timesteps.
    KB.append( conjoin( pacphysicsAxioms(0, all_coords, non_outer_wall_coords, walls_grid), 
                        pacphysicsAxioms(1, all_coords, non_outer_wall_coords, walls_grid)  ) 
             )
    
    # Add to KB allLegalSuccessorAxioms 
    KB.append( allLegalSuccessorAxioms(1, walls_grid, non_outer_wall_coords) )
    
    KB = conjoin(KB)    
    
    # model1: In model1, Pacman is at (x1, y1) at time t = 1 given x0_y0, action0, action1, proving that it's possible that Pacman there.
    #         Notably, if model1 is False, we know Pacman is guaranteed to NOT be there.
    model1 =  findModel( conjoin(KB, Pacman_x1y1_t1) )

    # model2: In model2, Pacman is NOT at (x1, y1) at time t = 1 given x0_y0, action0, action1, proving that it's possible that Pacman is
    #         not there. Notably, if model2 is False, we know Pacman is guaranteed to be there.
    model2 =  findModel( conjoin(KB, ~Pacman_x1y1_t1) )

    return (model1, model2)

    # util.raiseNotDefined()
    "*** END YOUR CODE HERE ***"

#______________________________________________________________________________
# QUESTION 4

def positionLogicPlan(problem) -> List:
    """
    Given an instance of a PositionPlanningProblem, return a list of actions that lead to the goal.
    Available actions are ['North', 'East', 'South', 'West']
    Note that STOP is not an available action.
    Overview: add knowledge incrementally, and query for a model each timestep. Do NOT use pacphysicsAxioms.
    """
    walls_grid = problem.walls
    width, height = problem.getWidth(), problem.getHeight()
    walls_list = walls_grid.asList()
    x0, y0 = problem.startState
    xg, yg = problem.goal
    
    # Get lists of possible locations (i.e. without walls) and possible actions
    all_coords = list(itertools.product(range(width + 2), 
            range(height + 2)))
    non_wall_coords = [loc for loc in all_coords if loc not in walls_list]
    actions = [ 'North', 'South', 'East', 'West' ]
    KB = []

    "*** BEGIN YOUR CODE HERE ***"

    # Add to KB: Initial knowledge: Pacman's initial location at timestep 0 
    Pacman_x0y0_t0 = PropSymbolExpr(pacman_str, x0, y0, time = 0)
    KB.append(Pacman_x0y0_t0)

    for t in range(50):
        # 1.
        # print(t)

        # 2. Add to KB: Initial knowledge
        Pacman_t = [ PropSymbolExpr(pacman_str, coord[0], coord[1], time = t) for coord in non_wall_coords ]
        KB.append( exactlyOne(Pacman_t) )

        # 3. Use findModel and pass in the Goal Assertion and KB.
        Pacman_xygoal_t = PropSymbolExpr(pacman_str, xg, yg, time = t)

        exprList = KB.copy()
        exprList.append(Pacman_xygoal_t)
        
        satisfactoryModel = findModel( conjoin(exprList) )
        
        # If there is, return a sequence of actions from start to goal using extractActionSequence.
        if satisfactoryModel:
            return extractActionSequence(satisfactoryModel, actions)

        # 4. Add to KB: Pacman takes exactly one action per timestep.
        PacExactly1action = [ PropSymbolExpr(action, time = t) for action in actions ]
        KB.append( exactlyOne(PacExactly1action) )

        # 5. Add to KB: Transition Model sentences: call pacmanSuccessorAxiomSingle(...) 
        #    for all possible pacman positions in non_wall_coords.
        nt = t + 1
        for coord in non_wall_coords:
            KB.append( pacmanSuccessorAxiomSingle(coord[0], coord[1], nt, walls_grid) )


    return None
    # util.raiseNotDefined()
    "*** END YOUR CODE HERE ***"
#______________________________________________________________________________
# QUESTION 5

def foodLogicPlan(problem) -> List:
    """
    Given an instance of a FoodPlanningProblem, return a list of actions that help Pacman
    eat all of the food.
    Available actions are ['North', 'East', 'South', 'West']
    Note that STOP is not an available action.
    Overview: add knowledge incrementally, and query for a model each timestep. Do NOT use pacphysicsAxioms.
    """
    walls = problem.walls
    width, height = problem.getWidth(), problem.getHeight()
    walls_list = walls.asList()
    (x0, y0), food = problem.start
    food = food.asList()

    # Get lists of possible locations (i.e. without walls) and possible actions
    all_coords = list(itertools.product(range(width + 2), range(height + 2)))

    non_wall_coords = [loc for loc in all_coords if loc not in walls_list]
    actions = [ 'North', 'South', 'East', 'West' ]

    KB = []

    "*** BEGIN YOUR CODE HERE ***"
   

    # Add to KB: Initial knowledge: Pacman's initial location at timestep 0 
    Pacman_x0y0_t0 = PropSymbolExpr(pacman_str, x0, y0, time = 0)
    KB.append( Pacman_x0y0_t0 )

    # Initialize Food[x,y]_t variables with the code PropSymbolExpr(food_str, x, y, time=t), 
    # where each variable is true if and only if there is a food at (x, y) at time t.
    food_t = [ PropSymbolExpr(food_str, food_coord[0], food_coord[1], time = 0) for food_coord in food ]
    KB = KB + food_t

    for t in range(50):
        
        # print(t)
 
        Pacman_t = [ PropSymbolExpr(pacman_str, coord[0], coord[1], time = t) for coord in non_wall_coords ]
        KB.append( exactlyOne(Pacman_t) )


        # Change the goal assertion: Your goal assertion sentence must be true if and only if all of the food have been eaten. 
        # This happens when all Food[x,y]_t are false.
        Pacman_foodGoal_t = [ ~ PropSymbolExpr(food_str, food_coord[0], food_coord[1], time = t) for food_coord in food ]

        exprList = KB + Pacman_foodGoal_t

        satisfactoryModel = findModel( conjoin(exprList) )
        
        if satisfactoryModel:
            return extractActionSequence(satisfactoryModel, actions)

        
        PacExactly1action = [ PropSymbolExpr(action, time = t) for action in actions ]
        KB.append( exactlyOne(PacExactly1action) )

        
        nt = t + 1
        [ KB.append( pacmanSuccessorAxiomSingle(coord[0], coord[1], nt, walls) ) for coord in non_wall_coords ]

        # Add a food successor axiom:
        # if pac_xy_t and  food_x1y1_t  then the time = t+1 exists food in x(1,y1)
        [KB.append( ( PropSymbolExpr(food_str, food_coord[0], food_coord[1], time=t) & 
                      ~ PropSymbolExpr(pacman_str, food_coord[0], food_coord[1], time=t) 
                    ) >> PropSymbolExpr(food_str, food_coord[0], food_coord[1], time=t+1)
                ) for food_coord in food 
        ]

        # if eat food at time t then no food the time = t+1 in this possition 
        [KB.append( ( PropSymbolExpr(food_str, food_coord[0], food_coord[1], time=t) & 
                      PropSymbolExpr(pacman_str, food_coord[0], food_coord[1], time=t) 
                    ) >> ~ PropSymbolExpr(food_str, food_coord[0], food_coord[1], time=t+1)
                ) for food_coord in food 
        ]

        food_t = [ PropSymbolExpr(food_str, food_coord[0], food_coord[1], time = t) for food_coord in food ]


    return None

    # util.raiseNotDefined()
    "*** END YOUR CODE HERE ***"

#______________________________________________________________________________
# QUESTION 6

def localization(problem, agent) -> Generator:
    '''
    problem: a LocalizationProblem instance
    agent: a LocalizationLogicAgent instance
    '''
    walls_grid = problem.walls
    walls_list = walls_grid.asList()
    all_coords = list(itertools.product(range(problem.getWidth()+2), range(problem.getHeight()+2)))
    non_outer_wall_coords = list(itertools.product(range(1, problem.getWidth()+1), range(1, problem.getHeight()+1)))

    KB = []

    "*** BEGIN YOUR CODE HERE ***"
    
    # Add to KB: where the walls are (walls_list) and aren't (not in walls_list).
    #  coord[0] -->> x
    #  coord[1] -->> y
    auxiliaryList = [   PropSymbolExpr(wall_str, coord[0], coord[1]) if coord in walls_list 
                        else  ~ PropSymbolExpr(wall_str, coord[0], coord[1])
                        for coord in all_coords
                    ]

    KB.append( conjoin(auxiliaryList) )

    
    # util.raiseNotDefined()

    for t in range(agent.num_timesteps):

        # Add pacphysics, action, and percept information to KB.
        pacAxioms = pacphysicsAxioms(t, all_coords, non_outer_wall_coords, walls_grid, sensorAxioms, allLegalSuccessorAxioms)
        KB.append( pacAxioms )

        pacAction_t = PropSymbolExpr(agent.actions[t], time = t)
        KB.append( pacAction_t )

        percepts = agent.getPercepts()
        percept_rules = fourBitPerceptRules(t, percepts)
        KB.append( percept_rules )

        # Find possible pacman locations with updated KB.
        # 1.
        possible_locations = []

        # 2.
        for coord in non_outer_wall_coords:
            
            premise = conjoin(KB)
            
            # locations where Pacman is provably at, at time t.
            PacmanISat_xy = PropSymbolExpr(pacman_str, coord[0], coord[1], time = t)   # conclusion = PacmanISat_xy
            
            # locations where Pacman is provably not at, at time t.
            PacmanISNTat_xy = ~ PropSymbolExpr(pacman_str, coord[0], coord[1], time = t) # conclusion = PacmanISNTat_xy
            
            
            FlagPacmanISat_xy = False
            FlagPacmanISNTat_xy = False
            
            # prove whether Pacman is at (x, y) -- And --  prove whether Pacman is not at (x, y)
            if entails(premise, PacmanISat_xy)== True:  # Pacman is at (x,y)
                FlagPacmanISat_xy = True

            if entails(premise, PacmanISNTat_xy) == True:  # Pacman isn't at (x,y)
                FlagPacmanISNTat_xy = True
            
            if FlagPacmanISat_xy == True and FlagPacmanISNTat_xy == False:  # Pacman is at (x,y) and -(Pacman isn't at (x,y))
                KB.append( PacmanISat_xy ) 
                possible_locations.append( coord )
            elif FlagPacmanISat_xy == False and FlagPacmanISNTat_xy == True:   # -(Pacman is at (x,y))  and Pacman isn't at (x,y)
                KB.append( PacmanISNTat_xy )
            elif FlagPacmanISat_xy == False and FlagPacmanISNTat_xy == False:  # -(Pacman is at (x,y))  and  -(Pacman isn't at (x,y))
                possible_locations.append( coord )
            else:
                print("Error the results of entails contradict each other!\n")   # Pacman is at (x,y) and Pacman isn't at (x,y)
     
        agent.moveToNextState(agent.actions[t])    

        "*** END YOUR CODE HERE ***"
        
        yield possible_locations

#______________________________________________________________________________
# QUESTION 7

def mapping(problem, agent) -> Generator:
    '''
    problem: a MappingProblem instance
    agent: a MappingLogicAgent instance
    '''
    pac_x_0, pac_y_0 = problem.startState
    KB = []
    all_coords = list(itertools.product(range(problem.getWidth()+2), range(problem.getHeight()+2)))
    non_outer_wall_coords = list(itertools.product(range(1, problem.getWidth()+1), range(1, problem.getHeight()+1)))

    # map describes what we know, for GUI rendering purposes. -1 is unknown, 0 is open, 1 is wall
    known_map = [[-1 for y in range(problem.getHeight()+2)] for x in range(problem.getWidth()+2)]

    # Pacman knows that the outer border of squares are all walls
    outer_wall_sent = []
    for x, y in all_coords:
        if ((x == 0 or x == problem.getWidth() + 1)
                or (y == 0 or y == problem.getHeight() + 1)):
            known_map[x][y] = 1
            outer_wall_sent.append(PropSymbolExpr(wall_str, x, y))
    KB.append(conjoin(outer_wall_sent))

    "*** BEGIN YOUR CODE HERE ***"
    # util.raiseNotDefined()

    # Add to KB: Initial knowledge: Pacman's initial location at timestep 0 
    Pacman_x0y0_t0 = PropSymbolExpr(pacman_str, pac_x_0, pac_y_0, time = 0)
    KB.append( Pacman_x0y0_t0 )

    for t in range(agent.num_timesteps):
        
        # Add pacphysics, action, and percept information to KB.
        pacAxioms = pacphysicsAxioms(t, all_coords, non_outer_wall_coords, known_map, sensorAxioms, allLegalSuccessorAxioms)
        KB.append( pacAxioms )

        pacAction_t = PropSymbolExpr(agent.actions[t], time = t)
        KB.append( pacAction_t )

        percepts = agent.getPercepts()
        percept_rules = fourBitPerceptRules(t, percepts)
        KB.append( percept_rules )

        # Find provable wall locations with updated KB.
        # 1.
        provable_walls = []

        # 2.
        for coord in non_outer_wall_coords:
            
            premise = conjoin(KB)
            
            # Location with wall
            WallISat_xy = PropSymbolExpr(wall_str, coord[0], coord[1])   # conclusion WallISat_xy

            # Location where there is no wall
            WallISNTat_xy = ~ PropSymbolExpr(wall_str, coord[0], coord[1]) # conclusion = WallISNTat_xy

            FlagWallISat_xy = False
            FlagWallISNTat_xy = False

            if entails(premise, WallISat_xy)== True:  #  Wall is at (x,y)
                FlagWallISat_xy = True

            if entails(premise, WallISNTat_xy) == True:  #  Wall isn't at (x,y)
                FlagWallISNTat_xy = True
             
            if FlagWallISat_xy == True and FlagWallISNTat_xy == False:      # Wall is at (x,y) and -(Wall is at (x,y))
                KB.append( WallISat_xy ) 
                known_map[coord[0]][coord[1]] = 1
            elif FlagWallISat_xy == False and FlagWallISNTat_xy == True:    # -( Wall is at (x,y)) and Wall is at (x,y)
                KB.append( WallISNTat_xy ) 
                known_map[coord[0]][coord[1]] = 0
            elif FlagWallISat_xy == False and FlagWallISNTat_xy == False:   # -( Wall is at (x,y)) and -(Wall is at (x,y))
                known_map[coord[0]][coord[1]] = -1
            else:
                print("Error the results of entails contradict each other!\n")

     
        agent.moveToNextState(agent.actions[t])  

        "*** END YOUR CODE HERE ***"
        yield known_map

#______________________________________________________________________________
# QUESTION 8

def slam(problem, agent) -> Generator:
    '''
    problem: a SLAMProblem instance
    agent: a SLAMLogicAgent instance
    '''
    pac_x_0, pac_y_0 = problem.startState
    KB = []
    all_coords = list(itertools.product(range(problem.getWidth()+2), range(problem.getHeight()+2)))
    non_outer_wall_coords = list(itertools.product(range(1, problem.getWidth()+1), range(1, problem.getHeight()+1)))

    # map describes what we know, for GUI rendering purposes. -1 is unknown, 0 is open, 1 is wall
    known_map = [[-1 for y in range(problem.getHeight()+2)] for x in range(problem.getWidth()+2)]

    # We know that the outer_coords are all walls.
    outer_wall_sent = []
    for x, y in all_coords:
        if ((x == 0 or x == problem.getWidth() + 1)
                or (y == 0 or y == problem.getHeight() + 1)):
            known_map[x][y] = 1
            outer_wall_sent.append(PropSymbolExpr(wall_str, x, y))
    KB.append(conjoin(outer_wall_sent))

    "*** BEGIN YOUR CODE HERE ***"
   
    # Add to KB: Initial knowledge: Pacman's initial location at timestep 0 
    Pacman_x0y0_t0 = PropSymbolExpr(pacman_str, pac_x_0, pac_y_0, time = 0)
    KB.append( Pacman_x0y0_t0 )

    # Add to KB: where the walls are (walls_list) and aren't (not in walls_list).
    #  coord[0] -->> x
    #  coord[1] -->> y
    known_map[pac_x_0][pac_y_0] = 0 
    KB.append(~PropSymbolExpr(wall_str, pac_x_0, pac_y_0))

    # util.raiseNotDefined()

    for t in range(agent.num_timesteps):

        pacAxioms = pacphysicsAxioms(t, all_coords, non_outer_wall_coords, known_map, SLAMSensorAxioms, SLAMSuccessorAxioms)
        KB.append( pacAxioms )

        pacAction_t = PropSymbolExpr(agent.actions[t], time = t)
        KB.append( pacAction_t )

        percepts = agent.getPercepts()
        percept_rules = numAdjWallsPerceptRules(t, percepts)
        KB.append( percept_rules )

        # Find provable wall locations with updated KB
        # 1.
        possible_locations = []

        # 2.
        for coord in non_outer_wall_coords:
            
            premise = conjoin(KB)
            
            PacmanISat_xy = PropSymbolExpr(pacman_str, coord[0], coord[1], time = t)   # conclusion = PacmanISat_xy
            PacmanISNTat_xy = ~ PropSymbolExpr(pacman_str, coord[0], coord[1], time = t) # conclusion = PacmanISat_xy
            
            
            FlagPacmanISat_xy = False
            FlagPacmanISNTat_xy = False

            if entails(premise, PacmanISat_xy)== True: 
                FlagPacmanISat_xy = True

            if entails(premise, PacmanISNTat_xy) == True: 
                FlagPacmanISNTat_xy = True
            
            if FlagPacmanISat_xy == True and FlagPacmanISNTat_xy == False:
                KB.append( PacmanISat_xy ) 
                possible_locations.append( coord )
            elif FlagPacmanISat_xy == False and FlagPacmanISNTat_xy == True:
                KB.append( PacmanISNTat_xy )
            elif FlagPacmanISat_xy == False and FlagPacmanISNTat_xy == False:
                possible_locations.append( coord )
            else:
                print("Error the results of entails contradict each other!\n")

            WallISat_xy = PropSymbolExpr(wall_str, coord[0], coord[1])   # conclusion WallISat_xy
            WallISNTat_xy = ~ PropSymbolExpr(wall_str, coord[0], coord[1]) # conclusion = WallISNTat_xy

            FlagWallISat_xy = False
            FlagWallISNTat_xy = False

            if entails(premise, WallISat_xy)== True: 
                FlagWallISat_xy = True

            if entails(premise, WallISNTat_xy) == True: 
                FlagWallISNTat_xy = True
             
            if FlagWallISat_xy == True and FlagWallISNTat_xy == False:
                KB.append( WallISat_xy ) 
                known_map[coord[0]][coord[1]] = 1
            elif FlagWallISat_xy == False and FlagWallISNTat_xy == True:
                KB.append( WallISNTat_xy ) 
                known_map[coord[0]][coord[1]] = 0
            elif FlagWallISat_xy == False and FlagWallISNTat_xy == False:
                known_map[coord[0]][coord[1]] = -1
            else:
                print("Error the results of entails contradict each other!\n")
     
        agent.moveToNextState(agent.actions[t])    

        "*** END YOUR CODE HERE ***"
        yield (known_map, possible_locations)


# Abbreviations
plp = positionLogicPlan
loc = localization
mp = mapping
flp = foodLogicPlan
# Sometimes the logic module uses pretty deep recursion on long expressions
sys.setrecursionlimit(100000)

#______________________________________________________________________________
# Important expression generating functions, useful to read for understanding of this project.


def sensorAxioms(t: int, non_outer_wall_coords: List[Tuple[int, int]]) -> Expr:
    all_percept_exprs = []
    combo_var_def_exprs = []
    for direction in DIRECTIONS:
        percept_exprs = []
        dx, dy = DIR_TO_DXDY_MAP[direction]
        for x, y in non_outer_wall_coords:
            combo_var = PropSymbolExpr(pacman_wall_str, x, y, x + dx, y + dy, time=t)
            percept_exprs.append(combo_var)
            combo_var_def_exprs.append(combo_var % (
                PropSymbolExpr(pacman_str, x, y, time=t) & PropSymbolExpr(wall_str, x + dx, y + dy)))

        percept_unit_clause = PropSymbolExpr(blocked_str_map[direction], time = t)
        all_percept_exprs.append(percept_unit_clause % disjoin(percept_exprs))

    return conjoin(all_percept_exprs + combo_var_def_exprs)


def fourBitPerceptRules(t: int, percepts: List) -> Expr:
    """
    Localization and Mapping both use the 4 bit sensor, which tells us True/False whether
    a wall is to pacman's north, south, east, and west.
    """
    assert isinstance(percepts, list), "Percepts must be a list."
    assert len(percepts) == 4, "Percepts must be a length 4 list."

    percept_unit_clauses = []
    for wall_present, direction in zip(percepts, DIRECTIONS):
        percept_unit_clause = PropSymbolExpr(blocked_str_map[direction], time=t)
        if not wall_present:
            percept_unit_clause = ~PropSymbolExpr(blocked_str_map[direction], time=t)
        percept_unit_clauses.append(percept_unit_clause) # The actual sensor readings
    return conjoin(percept_unit_clauses)


def numAdjWallsPerceptRules(t: int, percepts: List) -> Expr:
    """
    SLAM uses a weaker numAdjWallsPerceptRules sensor, which tells us how many walls pacman is adjacent to
    in its four directions.
        000 = 0 adj walls.
        100 = 1 adj wall.
        110 = 2 adj walls.
        111 = 3 adj walls.
    """
    assert isinstance(percepts, list), "Percepts must be a list."
    assert len(percepts) == 3, "Percepts must be a length 3 list."

    percept_unit_clauses = []
    for i, percept in enumerate(percepts):
        n = i + 1
        percept_literal_n = PropSymbolExpr(geq_num_adj_wall_str_map[n], time=t)
        if not percept:
            percept_literal_n = ~percept_literal_n
        percept_unit_clauses.append(percept_literal_n)
    return conjoin(percept_unit_clauses)


def SLAMSensorAxioms(t: int, non_outer_wall_coords: List[Tuple[int, int]]) -> Expr:
    all_percept_exprs = []
    combo_var_def_exprs = []
    for direction in DIRECTIONS:
        percept_exprs = []
        dx, dy = DIR_TO_DXDY_MAP[direction]
        for x, y in non_outer_wall_coords:
            combo_var = PropSymbolExpr(pacman_wall_str, x, y, x + dx, y + dy, time=t)
            percept_exprs.append(combo_var)
            combo_var_def_exprs.append(combo_var % (PropSymbolExpr(pacman_str, x, y, time=t) & PropSymbolExpr(wall_str, x + dx, y + dy)))

        blocked_dir_clause = PropSymbolExpr(blocked_str_map[direction], time=t)
        all_percept_exprs.append(blocked_dir_clause % disjoin(percept_exprs))

    percept_to_blocked_sent = []
    for n in range(1, 4):
        wall_combos_size_n = itertools.combinations(blocked_str_map.values(), n)
        n_walls_blocked_sent = disjoin([
            conjoin([PropSymbolExpr(blocked_str, time=t) for blocked_str in wall_combo])
            for wall_combo in wall_combos_size_n])
        # n_walls_blocked_sent is of form: (N & S) | (N & E) | ...
        percept_to_blocked_sent.append(
            PropSymbolExpr(geq_num_adj_wall_str_map[n], time=t) % n_walls_blocked_sent)

    return conjoin(all_percept_exprs + combo_var_def_exprs + percept_to_blocked_sent)


def allLegalSuccessorAxioms(t: int, walls_grid: List[List], non_outer_wall_coords: List[Tuple[int, int]]) -> Expr:
    """walls_grid can be a 2D array of ints or bools."""
    all_xy_succ_axioms = []
    for x, y in non_outer_wall_coords:
        xy_succ_axiom = pacmanSuccessorAxiomSingle(
            x, y, t, walls_grid)
        if xy_succ_axiom:
            all_xy_succ_axioms.append(xy_succ_axiom)
    return conjoin(all_xy_succ_axioms)


def SLAMSuccessorAxioms(t: int, walls_grid: List[List], non_outer_wall_coords: List[Tuple[int, int]]) -> Expr:
    """walls_grid can be a 2D array of ints or bools."""
    all_xy_succ_axioms = []
    for x, y in non_outer_wall_coords:
        xy_succ_axiom = SLAMSuccessorAxiomSingle(
            x, y, t, walls_grid)
        if xy_succ_axiom:
            all_xy_succ_axioms.append(xy_succ_axiom)
    return conjoin(all_xy_succ_axioms)

#______________________________________________________________________________
# Various useful functions, are not needed for completing the project but may be useful for debugging


def modelToString(model: Dict[Expr, bool]) -> str:
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


def extractActionSequence(model: Dict[Expr, bool], actions: List) -> List:
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
            action, _, time = parsed
            plan[time] = action
    #return list(filter(lambda x: x is not None, plan))
    return [x for x in plan if x is not None]


# Helpful Debug Method
def visualizeCoords(coords_list, problem) -> None:
    wallGrid = game.Grid(problem.walls.width, problem.walls.height, initialValue=False)
    for (x, y) in itertools.product(range(problem.getWidth()+2), range(problem.getHeight()+2)):
        if (x, y) in coords_list:
            wallGrid.data[x][y] = True
    print(wallGrid)


# Helpful Debug Method
def visualizeBoolArray(bool_arr, problem) -> None:
    wallGrid = game.Grid(problem.walls.width, problem.walls.height, initialValue=False)
    wallGrid.data = copy.deepcopy(bool_arr)
    print(wallGrid)

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
