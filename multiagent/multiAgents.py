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

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and child states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed child
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        childGameState = currentGameState.getPacmanNextState(action)
        newPos = childGameState.getPacmanPosition()
        newFood = childGameState.getFood()
        newGhostStates = childGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]
        foodList = newFood.asList()
        flst = []
        for food in newFood.asList():
            flst +=  [manhattanDistance(food, newPos)]
        if len(flst) == 0:
            fmin = 0.001
        else:
            fmin = min(flst)

        glst = []
        for ghost in newGhostStates:
            glst +=  [manhattanDistance(ghost.getPosition(), newPos)]

        gmin = min(glst)
        if gmin == 0:
            gmin = 0.001
        "*** YOUR CODE HERE ***"
        return childGameState.getScore() + 1/fmin - 2/gmin

def scoreEvaluationFunction(currentGameState):
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

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.getNextState(agentIndex, action):
        Returns the child game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        actionList = gameState.getLegalActions(0)
        stateDic = {}
        for action in actionList:
            score = miniMax(self, gameState.getNextState(0, action), 1, 0)
            stateDic[action] = score

        return max(stateDic, key = stateDic.get)

"""
returns a score
"""
def miniMax(agent, gameState, index, depth):
    index = index % gameState.getNumAgents()
    if index == 0:
        depth += 1
    if depth == agent.depth or gameState.isWin() or gameState.isLose():
        return agent.evaluationFunction(gameState)
    actionList = gameState.getLegalActions(index)
    nextStateList = []
    for action in actionList:
        nextState = gameState.getNextState(index, action)
        nextStateList += [miniMax(agent, nextState, index + 1, depth)]
    if index == 0:
        return max(nextStateList)
    else:
        return min(nextStateList)


import math
class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """
    def getAction(self, gameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        actionList = gameState.getLegalActions(0)
        stateDic = {}
        alpha = -math.inf
        beta = math.inf
        score = alpha
        for action in actionList:
            nextScore = alphaBetaMiniMax(self, gameState.getNextState(0, action), 1, 0, alpha, beta)
            score = max(score, nextScore)
            alpha = max(alpha, score)
            stateDic[action] = nextScore
        return max(stateDic, key = stateDic.get)
"""
returns a score
"""
def alphaBetaMiniMax(agent, gameState, index, depth, alpha, beta):
    index = index % gameState.getNumAgents()
    v = 0
    if index == 0:
        v = -math.inf
    else:
        v = math.inf
    if index == 0:
        depth += 1
    if depth == agent.depth or gameState.isWin() or gameState.isLose():
        return agent.evaluationFunction(gameState)
    actionList = gameState.getLegalActions(index)
    nextStateList = []
    for action in actionList:
        nextState = gameState.getNextState(index, action)
        if index == 0 :
            v = max(v, alphaBetaMiniMax(agent, nextState, index + 1, depth, alpha, beta))
            if v > beta:
                return v
            alpha = max(alpha, v)
        else:
            v = min(v, alphaBetaMiniMax(agent, nextState, index + 1, depth, alpha, beta))

            if v < alpha:

                return v
            beta = min(beta, v)
    return v

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """
    def getAction(self, gameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        actionList = gameState.getLegalActions(0)
        stateDic = {}
        for action in actionList:
            score = expectiMax(self, gameState.getNextState(0, action), 1, 0)
            stateDic[action] = score

        return max(stateDic, key = stateDic.get)
import random
"""
returns a score
"""
def expectiMax(agent, gameState, index, depth):
    index = index % gameState.getNumAgents()
    if index == 0:
        depth += 1
    if depth == agent.depth or gameState.isWin() or gameState.isLose():
        return agent.evaluationFunction(gameState)
    actionList = gameState.getLegalActions(index)
    nextStateList = []
    for action in actionList:
        nextState = gameState.getNextState(index, action)
        nextStateList += [expectiMax(agent, nextState, index + 1, depth)]

    if index == 0:
        return max(nextStateList)
    else:
        return sum(nextStateList)/len(nextStateList)


def betterEvaluationFunction(currentGameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    # Useful information you can extract from a GameState (pacman.py)
    newPos = currentGameState.getPacmanPosition()
    newFood = currentGameState.getFood()
    pelletList = currentGameState.getCapsules()
    newGhostStates = currentGameState.getGhostStates()
    newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]
    foodList = newFood.asList()
    flst = []
    clst = []


    glst = []
    for ghost in newGhostStates:
        glst +=  [manhattanDistance(ghost.getPosition(), newPos)]
    gmin = min(glst)
    if gmin == 1:
        gmin = 0.0001
    if gmin == 2:
        gmin = 0.001
    if currentGameState.isLose():
        return -math.inf
    if len(pelletList) == 0:
        cNum = 0.01
    else:
        cNum = len(pelletList)


    for food in newFood.asList():
        flst +=  [manhattanDistance(food, newPos)]

    if len(flst) == 0:
        fmin = 0.001
        foodNum = 0.01
    else:
        foodNum = len(foodList)
        fmin = min(flst)

    if len(newScaredTimes) is not 0 and newScaredTimes[0] > 0:
        return currentGameState.getScore() + 1.3/foodNum + 2/gmin + 1/cNum + 1/fmin
    return currentGameState.getScore() + 1.3/foodNum - 2/gmin + 1/cNum + 1/fmin

# Abbreviation
better = betterEvaluationFunction
