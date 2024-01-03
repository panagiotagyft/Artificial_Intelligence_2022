# multiAgents.py
# --------------
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


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent
from pacman import GameState



class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState: GameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState: GameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]
        
        curPos = currentGameState.getPacmanPosition()       # the current pacman position
        
        # FOOD
        newFood_list = newFood.asList()     # the new list of food locations
        powerPills_list = currentGameState.getCapsules()     # the list of power pills

        # Find the current scared and strong ghosts!
        strongGhosts = []
        scaredGhosts = []
        
        for ghostState in newGhostStates:       # Examine all ghosts!
            # if the current ghost's scaredtimer is 0  -- then -->>  the ghost is possible 
            # otherwise the ghost is scared
            if ghostState.scaredTimer == 0:
                strongGhosts.append(ghostState.getPosition())
            else:
                scaredGhosts.append(ghostState.getPosition())
        
        current_score = 0.0     # initialize counter
        
        # if the manhattan distance between the pacman and any powerful ghost is less than or equal to the unit 
        # -- then -->> return the lowest value of the system so that the pacman goes away from the ghost.
        for ghost in strongGhosts:
            if manhattanDistance( newPos , ghost) <= 1:
                return float("-inf") 

        # If the pacman's direction is stop then reduce the score because the delay has a negative effect for pacman.
        # newPos == curPos  -->> the direction is stop
        if newPos == curPos:
             current_score = -10
        
        # Check all scared ghosts
        for ghost in scaredGhosts:
            dist = manhattanDistance( newPos , ghost)
            
            # if the manhattan distance between pacman and a scared ghost is 0  -- then -->>  pacman receives 100-bonus points
            # else if manhattan distance is 1  -- then -->>  pacman receives 20-bonus points (minus 80% of best bonus due to position)
            if dist == 0:
                current_score = current_score + 100
            elif dist == 1:
                current_score = current_score + 20

        for pill in powerPills_list:
            dist = manhattanDistance(newPos , pill)

            # if the manhattan distance between pacman and a power pill is 0  -- then -->>  pacman receives 50-bonus points
            # else if manhattan distance is 1  -- then -->>  pacman receives 10-bonus points (minus 80% of best bonus due to position)
            if dist == 0:
                current_score = current_score + 50
            elif dist == 1:
                current_score = current_score + 10
        
        # If the shortest distance from a food is from the previous position of pacman -- then -->> the score is reduced,
        # because the new position is not the best, otherwise if the shortest distance from a food is from the current location 
        # -- then -->> we add a small bonus depending on the distance of the nearest food.
        if newFood_list:
            # The distance from pacman's new location to the nearest food.
            nearest_distance1 = min(manhattanDistance( newPos , foodPos) for foodPos in newFood_list)

            # The distance from pacman's previous location to the nearest food
            nearest_distance2 = min(manhattanDistance( curPos , foodPos) for foodPos in newFood_list)
            
            if nearest_distance1 <= nearest_distance2:
                current_score = current_score + 1.0/nearest_distance1
            else:
                 current_score -= 10

        # Returned the sum of the successor's score and the score counter of the current status.
        return successorGameState.getScore() + current_score    


def scoreEvaluationFunction(currentGameState: GameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)
        self.Agents = []


class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        
        
        ActionsValues = {}          # stores all values of possible initial pacman actions
        Pacman = 0                  # agentIndex = 0 (Pacman = 0)
        
        Actions = gameState.getLegalActions(Pacman)     #  Actions  -->> the list of pacman's initial actions
        numAgents=gameState.getNumAgents()              #  numAgents -->> the total number of agents
        
        self.Agents = [ agentIndex for agentIndex in range(numAgents)]      # list of agents
        
        depth = self.depth 
        ply = depth*numAgents       # the last ply of the game tree (the depth of the game tree)
        
        maxVal = float('-inf')      # Initialization of the variable representing the maximum value of a movement
                                    # with the lowest system value.

        # Save stop direction. Stop direction, is always legal action
        ActionsValues["stop"] = maxVal
        
        # find the values of pacman's initial actions
        for action in Actions:
            
            # stop -->> legal action, continue
            if action == "stop":
                continue
            
            # state -->> the new state of the game after moving pacman
            state = gameState.generateSuccessor(Pacman, action)

            # Find the value of the current action.Cross the tree retrospectively to find the value of action
            val = self.MiniMax_Search(state, Pacman, ply)

            # store the current action with its value in the dictionary ActionsValues
            if action not in ActionsValues:
                ActionsValues[action] = val
           
        
        # update maxVal   
        maxVal = max(ActionsValues.values())   

        # From pacman's initial actions find the one with the highest value (highest value -> maxVal)
        for action in ActionsValues.keys():

            actionVal = ActionsValues[action]
            
            # The action with the highest value is Pacman's best action at the beginning of the game.
            if maxVal == actionVal:
                bestAction = action

        return bestAction
        
        # util.raiseNotDefined()
    
    
    def Is_Terminal(self, gameState: GameState, ply: int)-> bool:
        """
        Checks whether the current situation for Pacman or for one of the ghosts is victory or defeat.
        In these cases the current agent is in the final state and the fuction returns True.
        Otherwise the game is not finished and a boolean value False is returned.
        """
        if gameState.isWin(): 
            return True
        elif gameState.isLose(): 
            return True
        else: 
            return False
            

    def MiniMax_Search(self, gameState: GameState, Agent: int, ply: int) -> int:
        """
        Returns the minimax action from the current gameState.
        Crosses the game tree retrospectively, selecting each time the appropriate next player to examine, 
        until the entire tree is checked.
        """
    
        if (Agent + 1) not in self.Agents:
            successorAgent = self.index
        else:
            successorAgent = Agent+1

        # if ply is not 0 -->> continue  -- else --  return -> evaluation
        if ply - 1 > 0:
            # if successorAgent > 0 (1 to numAgents-1) then agent is a ghost  -->> called the Min_Value method to return the minimum ghost value
            # else if successorAgent is 0 then agent is pacman -->> called the Max_Value method to return the maximum pacman value
            if successorAgent is not self.index:
                return self.Min_Value(gameState, successorAgent , ply-1)
            else:
                return self.Max_Value(gameState, successorAgent , ply-1)

        else:
            return self.evaluationFunction(gameState)


    def Max_Value(self, gameState: GameState, Agent: int, ply: int)->int:
        """
        Returns the maximum value of pacman's
        """
        # Check if the current state is the final 
        # If it is the final state  -- then -->> return evaluation
        if self.Is_Terminal(gameState, ply) == True : return self.evaluationFunction(gameState)
        
        # the cuurent agent is pacman!
        Pacman = Agent
        maxVal = float('-inf')      # initialize the maxVal variable with the lowest system value

        Actions = gameState.getLegalActions(Pacman)     #  Actions  -->> the list of pacman's current actions

        # find the values of pacman's current actions
        for action in Actions:

            # state -->> the new state of the game after moving pacman
            state = gameState.generateSuccessor(Pacman, action)

            # Find the value of the current action.Cross the tree retrospectively to find the value.
            val = self.MiniMax_Search(state, Pacman, ply)
            
            # update maxVal
            if val > maxVal:
                maxVal = val
        
        return maxVal  
    

    def Min_Value(self, gameState: GameState, Agent: int, ply: int) -> int:
        """
        Returns the minimum value of No. ghost
        """
        # Check if the current state is the final 
        # If it is the final state  -- then -->> return evaluation     
        if self.Is_Terminal(gameState, ply): return self.evaluationFunction(gameState)
        
        # the cuurent agent is No. ghost!
        Ghost = Agent
        minVal = float('inf')

        Actions = gameState.getLegalActions(Ghost)     #  Actions  -->> the list of No. ghost current actions

        # find the values of No. ghost current actions
        for action in Actions:

            # state -->> the new state of the game after moving ghost
            state = gameState.generateSuccessor(Ghost, action)

            # Find the value of the current action.Cross the tree retrospectively to find the value.
            val = self.MiniMax_Search(state, Ghost, ply)

            # update minVal
            if minVal > val:
                minVal = val

        return minVal 
    
            
class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        ActionsValues = {}          # stores all values of possible initial pacman actions
        Pacman = 0 
        
        Actions = gameState.getLegalActions(Pacman)
        numAgents=gameState.getNumAgents()

        self.Agents = [ agentIndex for agentIndex in range(numAgents)]

        depth = self.depth
        ply = depth*numAgents

        # Initialize variables.
        maxVal = float('-inf')
        alpha = -float('inf')
        beta = float('inf')
        
        # Save stop direction. Stop direction, is always legal action
        ActionsValues["stop"] = maxVal
        
        # find the values of pacman's initial actions
        for action in Actions:
            
            if action == "stop":
                continue
            
            state = gameState.generateSuccessor(Pacman, action)
            val = self.Alpha_Beta_Search(state, Pacman, ply, alpha, beta)
                
            if action not in ActionsValues:
                ActionsValues[action] = val
                
            # update maxVal   
            maxVal = max(ActionsValues.values())  
            
            # update alpha
            alpha = max(alpha,maxVal)
        
        # From pacman's initial actions find the one with the alpha item
        for action in ActionsValues.keys():

            actionVal = ActionsValues[action]

            if alpha == actionVal:
                bestAction = action
 
        return bestAction
        
        # util.raiseNotDefined()
    
    
    def Is_Terminal(self, gameState: GameState, ply: int)-> bool:
        """
        Checks whether the current situation for Pacman or for one of the ghosts is victory or defeat.
        In these cases the current agent is in the final state and the fuction returns True.
        Otherwise the game is not finished and a boolean value False is returned.
        """
        if gameState.isWin(): 
            return True
        elif gameState.isLose(): 
            return True
        else: 
            return False
            

    def Alpha_Beta_Search(self, gameState: GameState, Agent: int, ply: int, alpha, beta)-> int:
        """
        Returns the minimax action from the current gameState.
        Crosses the game tree retrospectively, selecting each time the appropriate next player to examine, 
        until the entire tree is checked.
        """

        if (Agent + 1) not in self.Agents:
            successorAgent = self.index
        else:
            successorAgent = Agent+1

        # if ply is not 0 -->> continue  -- else --  return -> evaluation
        if ply - 1 > 0: 
            if successorAgent is not self.index:
                return self.Min_Value(gameState, successorAgent , ply-1, alpha, beta)
            else:
                return self.Max_Value(gameState, successorAgent , ply-1, alpha, beta)
        else:
            return self.evaluationFunction(gameState)


    def Max_Value(self, gameState: GameState, Agent: int, ply: int, alpha, beta)->int:
        """
        Returns the maximum value of pacman's
        """
        
        # Check if the current state is the final 
        # If it is the final state  -- then -->> return evaluation
        if self.Is_Terminal(gameState, ply) == True : return self.evaluationFunction(gameState)
        
        Pacman = Agent
        maxVal = float('-inf')

        Actions = gameState.getLegalActions(Pacman)

        # find the values of pacman's current actions
        for action in Actions:
            state = gameState.generateSuccessor(Pacman, action)

            val = self.Alpha_Beta_Search(state, Pacman, ply, alpha, beta)

            # update alpha and maxVal
            if val > maxVal:
                maxVal = val
                alpha = max(alpha, maxVal)

            if maxVal > beta:
                return maxVal
            
        
        return maxVal
    

    def Min_Value(self, gameState: GameState, Agent: int, ply: int, alpha, beta)-> int:
        """
        Returns the minimum value of No. ghost
        """

        # Check if the current state is the final 
        # If it is the final state  -- then -->> return evaluation
        if self.Is_Terminal(gameState, ply): return self.evaluationFunction(gameState)
            
        Ghost = Agent
        minVal = float('inf')

        Actions = gameState.getLegalActions(Ghost)

        # find the values of No. ghost current actions
        for action in Actions:
            state = gameState.generateSuccessor(Ghost, action)

            val = self.Alpha_Beta_Search(state, Ghost, ply, alpha, beta)

            # update beta and maxVal
            if val < minVal:
                minVal = val
                beta = min(beta, minVal)
            
            if minVal < alpha:
                return minVal
                   
        return minVal 

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"

        ActionsValues = {}          # stores all values of possible initial pacman actions
        Pacman = 0 
        
        Actions = gameState.getLegalActions(Pacman)
        numAgents=gameState.getNumAgents()

        self.Agents = [ agentIndex for agentIndex in range(numAgents)]

        depth = self.depth
        ply = depth*numAgents
        
        maxVal = float('-inf')

        ActionsValues["stop"] = maxVal

        # find the values of pacman's initial actions
        for action in Actions:
            
            if action == "stop":
                continue

            state = gameState.generateSuccessor(Pacman, action)
            val = self.ExpectiMiniMax_Search(state, Pacman, ply)

        
            if action not in ActionsValues:
                ActionsValues[action] = val
                    

        # update maxVal   
        maxVal = max(ActionsValues.values())  

        # From pacman's initial actions find the one with the highest value (highest value -> maxVal)
        for action in ActionsValues.keys():

            actionVal = ActionsValues[action]

            if maxVal == actionVal:
                bestAction = action
 
        return bestAction
        
        # util.raiseNotDefined()
    
    
    def Is_Terminal(self, gameState: GameState, ply: int)-> bool:
        """
        Checks whether the current situation for Pacman or for one of the ghosts is victory or defeat.
        In these cases the current agent is in the final state and the fuction returns True.
        Otherwise the game is not finished and a boolean value False is returned.
        """

        if gameState.isWin(): 
            return True
        elif gameState.isLose(): 
            return True
        else: 
            return False
            

    def ExpectiMiniMax_Search(self, gameState: GameState, Agent: int, ply: int)-> int:
        """
        Returns the minimax action from the current gameState.
        Crosses the game tree retrospectively, selecting each time the appropriate next player to examine, 
        until the entire tree is checked.
        """

        if (Agent + 1) not in self.Agents:
            successorAgent = self.index
        else:
            successorAgent = Agent+1

        # if ply is not 0 -->> continue  -- else --  return -> evaluation
        if ply - 1 > 0:
            if successorAgent is not self.index:
                return self.Expected_Value(gameState, successorAgent , ply-1)
            else:
                return self.Max_Value(gameState, successorAgent , ply-1)
        else:
            return self.evaluationFunction(gameState)


    def Max_Value(self, gameState: GameState, Agent: int, ply: int) -> int:
        """
        Returns the maximum value of pacman's
        """
        
        # Check if the current state is the final 
        # If it is the final state  -- then -->> return evaluation
        if self.Is_Terminal(gameState, ply) == True : return self.evaluationFunction(gameState)
        
        Pacman = Agent
        maxVal = float('-inf')

        Actions = gameState.getLegalActions(Pacman)

        for action in Actions:
            state = gameState.generateSuccessor(Pacman, action)

            val = self.ExpectiMiniMax_Search(state, Pacman, ply)

            # update maxVal
            if val > maxVal:
                maxVal = val
        
        return maxVal
    

    def Expected_Value(self, gameState: GameState, Agent: int, ply: int) -> int:
        """
        Returns average prices
        """
        
        if self.Is_Terminal(gameState, ply): return self.evaluationFunction(gameState)
            
        Ghost = Agent
        expectedVal = 0.0
        
        Actions = gameState.getLegalActions(Ghost)
        numofActions = len(Actions)
        for action in Actions:
            state = gameState.generateSuccessor(Ghost, action)

            val = self.ExpectiMiniMax_Search(state, Ghost, ply)

             # update expectedVal
            expectedVal += val
        
        # expectedVal = expected_value * current successor's probability
        expectedVal /= numofActions

        return expectedVal  

def betterEvaluationFunction(currentGameState: GameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    
    # Setup information to be used as arguments in evaluation function
    pacman_position = currentGameState.getPacmanPosition()
    ghostStates = currentGameState.getGhostStates()
    scaredTimes = [ghostState.scaredTimer for ghostState in ghostStates]

    nearest_distance = 1.0

    # FOOD
    food_list = currentGameState.getFood().asList()     # the new list of food locations
    powerPills_list = currentGameState.getCapsules()        # the list of power pills

    # Find the current scared and strong ghosts!
    strongGhosts = []
    scaredGhosts = []
        
    for ghostState in ghostStates:       # Examine all ghosts!
        # if the current ghost's scaredtimer is 0  -- then -->>  the ghost is possible 
        # otherwise the ghost is scared
        if ghostState.scaredTimer == 0:
            strongGhosts.append(ghostState.getPosition())
        else:
            scaredGhosts.append(ghostState.getPosition())
        
    current_score = 0.0     # initialize counter

    # if the manhattan distance between the pacman and any powerful ghost is less than or equal to the unit 
    # -- then -->> set nearest_distance = big val, so pacman can get away from the ghost and eat closer food.
    for ghost in strongGhosts:
        if manhattanDistance( pacman_position , ghost) <= 1:
           nearest_distance = 1000


    # Check all scared ghosts
    for ghost in scaredGhosts:
        dist = manhattanDistance( pacman_position , ghost)
            
        # if the manhattan distance between pacman and a scared ghost is 0  -- then -->>  pacman receives 100-bonus points
        # else if manhattan distance is 1  -- then -->>  pacman receives 20-bonus points (minus 80% of best bonus due to position)
        if dist == 0:
            current_score = current_score + 100
        elif dist == 1:
            current_score = current_score + 20

    for pill in powerPills_list:
        dist = manhattanDistance(pacman_position , pill)

        # if the manhattan distance between pacman and a power pill is 0  -- then -->>  pacman receives 50-bonus points
        # else if manhattan distance is 1  -- then -->>  pacman receives 10-bonus points (minus 80% of best bonus due to position)
        if dist == 0:
            current_score = current_score + 50
        elif dist == 1:
            current_score = current_score + 10

    
    if food_list:
        # The distance from pacman's new location to the nearest food.
        nearest_distance = min(manhattanDistance(pacman_position, food_position) for food_position in food_list)


    current_score += 1.0 / nearest_distance

    return currentGameState.getScore() + current_score

# Abbreviation
better = betterEvaluationFunction
