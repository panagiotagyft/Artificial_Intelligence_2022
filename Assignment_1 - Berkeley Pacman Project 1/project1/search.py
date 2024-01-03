# search.py
# ---------
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
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

from sys import path_hooks
import util

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s, s, w, s, w, w, s, w]

def pathConstruction(problem: SearchProblem, parentKids: dict, node: str, pathConstr: list, i: int) -> list:
    """
    Construct the path followed to the target node. 
    """

    start = problem.getStartState()

    while node!=start:
        parent, sourcePath = parentKids[i]
        if node in sourcePath.keys():
            pathConstr.append(sourcePath[node])
            node = parent 
        i+=1 
    
    return pathConstr[::-1]
    

def depthFirstSearch(problem: SearchProblem):
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches the
    goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print("Start:", problem.getStartState())
    print("Is the start a goal?", problem.isGoalState(problem.getStartState()))
    print("Start's successors:", problem.getSuccessors(problem.getStartState()))
    """
    
    frontier = util.Stack()

    requestedRoute = [] 
    expanded = set()
    
    parentKids = []
    pathConstr = []

    node = problem.getStartState() # initial state node
    
    # if the first node is the target --then-->> return an empty list of actions - else - push the first node 
    if  problem.isGoalState( node ) == True:
        return requestedRoute
    else:
        frontier.push( node )

   # while the stack is not empty, i.e. there are nodes to search 
    while frontier:
        node = frontier.pop()  # remove the topmost element in the stack

        # if the current node removed from the stack is the target node --then-->> call the pathConstruction() function
        # to construct the path followed to the target node. Return this path
        # else continue searching.
        if  problem.isGoalState( node ) == True:
            requestedRoute = pathConstruction(problem, parentKids[::-1], node, pathConstr, 0)
            return requestedRoute
            
        # add the current node to the list of visitors to avoid a second future visit
        if node not in expanded:
            expanded.add( node )

        # receive valid successors
        listSuccessors = problem.getSuccessors( node )

        i = 0   
        sourcePath = {}          
        while i < len( listSuccessors )  :
            # If the current successor has not visited --then-->> add it to the stack (frontier) and
            # add to the dictionary the current successor with the source motion action
            if listSuccessors[i][0] not in expanded :
                frontier.push( listSuccessors[i][0] )
                    
                sourcePath[listSuccessors[i][0]] = listSuccessors[i][1]
            i += 1
        
        # save the successors of the current node with their traffic information
        parentKids.append( (node, sourcePath) ) 
  
    return None
    util.raiseNotDefined()

def breadthFirstSearch(problem: SearchProblem):
    """Search the shallowest nodes in the search tree first."""
    
    frontier = util.Queue()

    requestedRoute = []
    expanded = set()
    parentKids = []
    pathConstr = []

    node = problem.getStartState() # initial state node

    # if the first node is the target --then-->> return an empty list of actions - else - push the first node 
    if  problem.isGoalState( node ) == True:
        return requestedRoute
    else:
        frontier.push( node )

    # while the queue is not empty, i.e. there are nodes to search 
    while frontier:
        node = frontier.pop() # remove an element from the front of the queue

        # if the current node removed from the queue is the target node --then-->> call the pathConstruction() function
        # to construct the path followed to the target node. Return this path
        # else continue searching.
        if  problem.isGoalState( node ) == True:
            requestedRoute = pathConstruction(problem, parentKids[::-1], node, pathConstr, 0)
            return requestedRoute
        
        # add the current node to the list of visitors to avoid a second future visit
        if node not in expanded:
            expanded.add( node ) 

        listSuccessors = problem.getSuccessors( node )

        i = 0   
        sourcePath = {}            
        while i < len( listSuccessors )  :
            # If the current successor has not visited and frontier does not contains the successor --then-->> add it to the frontier
            # and add to the dictionary the current successor with the source motion action
            if listSuccessors[i][0] not in expanded and listSuccessors[i][0] not in frontier.list:
                frontier.push( listSuccessors[i][0] )

                sourcePath[listSuccessors[i][0]] = listSuccessors[i][1]
            i += 1

        # save the successors of the current node with their traffic information
        parentKids.append( (node, sourcePath) )
  
    return None 

    util.raiseNotDefined()

def uniformCostSearch(problem: SearchProblem):
    """Search the node of least total cost first."""
    
    frontier = util.PriorityQueue()               

    requestedRoute = []
    expanded = set()
    path = {}
    new_path = []

    node = problem.getStartState() # initial state node
    
    # if the first node is the target --then-->> return an empty list of actions - else - push the first node 
    if  problem.isGoalState( node ) == True:
        return requestedRoute
    else:
        frontier.push( node, 0 )

    # while the priority queue is not empty, i.e. there are nodes to search 
    while not frontier.isEmpty():
        node = frontier.pop()


        if len(path) == 0:
            current_path = []
        else:
            current_path = path[node]

        if  problem.isGoalState( node ) == True:
            requestedRoute = path[node]
            return requestedRoute
        
        if node not in expanded:
            expanded.add( node )

        listSuccessors = problem.getSuccessors( node )

        i = 0          
        while i < len( listSuccessors )  :
            if listSuccessors[i][0] not in expanded:

                # initialize the new_path with the path of the current node and and add to it action of the successor
                new_path = [ x for x in current_path] 
                new_path.append(listSuccessors[i][1]) 
                    

                item_exists = False
                for element in frontier.heap: 
                    # if the successor exists at the frontier then update the path
                    if listSuccessors[i][0] in element:
                        item_exists = True
                        # comparison of new and old cost path
                        previous_path = path[listSuccessors[i][0]]
                        previous_cost = problem.getCostOfActions(previous_path)
                        new_cost = problem.getCostOfActions(new_path)

                        if new_cost < previous_cost:
                            path[listSuccessors[i][0]] = new_path
                            break
                # if the successor does not exists at the frontier add path in dictionary
                if item_exists == False:
                    path[listSuccessors[i][0]] = new_path
        
                frontier.update( listSuccessors[i][0], problem.getCostOfActions(new_path) )

            i += 1
  
    return None

    util.raiseNotDefined()

def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

def aStarSearch(problem: SearchProblem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""

    frontier = util.PriorityQueue()               

    requestedRoute = []
    expanded = set()
    path = {}
    new_path = []

    node = problem.getStartState() # initial state node
    
    # if the first node is the target --then-->> return an empty list of actions - else - push the first node 
    if  problem.isGoalState( node ) == True:
        return requestedRoute
    else:
        frontier.push( node, 0 )

    # while the priority queue is not empty, i.e. there are nodes to search 
    while not frontier.isEmpty():
        node = frontier.pop()

        if len(path) == 0:
            current_path = []
        else:
            current_path = path[node]

        if  problem.isGoalState( node ) == True:
            requestedRoute = path[node]
            return requestedRoute
        
        if node not in expanded:
            expanded.add( node )

            listSuccessors = problem.getSuccessors( node )

            i = 0          
            while i < len( listSuccessors )  :
                if listSuccessors[i][0] not in expanded:
                    
                    # initialize the new_path with the path of the current node and and add to it action of the successor
                    new_path = [ x for x in current_path]
                    new_path.append(listSuccessors[i][1])
                    

                    item_exists = False
                    for element in frontier.heap:

                        # if the successor exists at the frontier then update the path 
                        if listSuccessors[i][0] in element:
                            item_exists = True
                            
                            previous_path = path[listSuccessors[i][0]]
                            previous_cost = problem.getCostOfActions(previous_path) + heuristic(listSuccessors[i][0], problem)
                            new_cost = problem.getCostOfActions(new_path) + heuristic(listSuccessors[i][0], problem)

                            if new_cost < previous_cost:
                                path[listSuccessors[i][0]] = new_path
                                break
                    
                    # if the successor does not exists at the frontier add path in dictionary
                    if item_exists == False:
                        path[listSuccessors[i][0]] = new_path
            
                    frontier.update( listSuccessors[i][0], problem.getCostOfActions(new_path)+heuristic(listSuccessors[i][0], problem) )

                i += 1
  
    return None
    
    util.raiseNotDefined()


# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
