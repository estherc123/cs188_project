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

    def expand(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (child,
        action, stepCost), where 'child' is a child to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that child.
        """
        util.raiseNotDefined()

    def getActions(self, state):
        """
          state: Search state

        For a given state, this should return a list of possible actions.
        """
        util.raiseNotDefined()

    def getActionCost(self, state, action, next_state):
        """
          state: Search state
          action: action taken at state.
          next_state: next Search state after taking action.

        For a given state, this should return the cost of the (s, a, s') transition.
        """
        util.raiseNotDefined()

    def getNextState(self, state, action):
        """
          state: Search state
          action: action taken at state

        For a given state, this should return the next state after taking action from state.
        """
        util.raiseNotDefined()

    def getCostOfActionSequence(self, actions):
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

def depthFirstSearch(problem):
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches the
    goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print("Start:", problem.getStartState())
    print("Is the start a goal?", problem.isGoalState(problem.getStartState()))
    """
    "*** YOUR CODE HERE ***"
    from util import Stack
    curr_state = problem.getStartState()
    stk = Stack()
    paths = {curr_state:[]}
    former = {}
    stk.push(curr_state)
    while(not stk.isEmpty()):
        state = stk.pop()
        if state in former:
            paths[state] = paths[former[state][1]] + [former[state][0]]
        if problem.isGoalState(state):
            return paths[state]
        for x in problem.expand(state):
            if x[0] not in former:
                stk.push(x[0])
            former[x[0]] = (x[1], state)









def breadthFirstSearch(problem):
    """Search the shallowest nodes in the search tree first."""
    "*** YOUR CODE HERE ***"
    from util import Queue
    curr_state = problem.getStartState()
    stk = Queue()
    paths = {curr_state:[]}
    stk.push(curr_state)
    while(not stk.isEmpty()):
        state = stk.pop()
        if problem.isGoalState(state):
            #print("goal state reached!")
            return paths[state]
        for x in problem.expand(state):
            if x[0] not in paths:
                stk.push(x[0])
                paths[x[0]] = paths[state] + [x[1]]
                #print("path so far", paths[x[0]])



def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

def aStarSearch(problem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    "*** YOUR CODE HERE ***"
    from util import PriorityQueue
    curr_state = problem.getStartState()
    pq = PriorityQueue()
    paths = {curr_state:[]}
    cost_so_far = {curr_state:0}
    pq.push(curr_state, heuristic(curr_state, problem))
    former = {curr_state: (curr_state, None, 0)}
    while(not pq.isEmpty()):
        state = pq.pop()
        if state in former:
            if former[state][1] is not None:
                paths[state] = paths[former[state][0]] + [former[state][1]]
        cost_so_far[state] = cost_so_far[former[state][0]] + former[state][2]
        if problem.isGoalState(state):
            return paths[state]
        for x in problem.expand(state):
            new_cost = cost_so_far[state] + x[2] + heuristic(x[0], problem)
            if x[0] not in cost_so_far or new_cost < cost_so_far[x[0]] + heuristic(x[0], problem):
                pq.update(x[0], new_cost)
                if x[0] not in former or cost_so_far[state] + x[2] < cost_so_far[former[x[0]][0]] + former[x[0]][2]:
                    former[x[0]] = (state, x[1], x[2])



        #print("csf updated", state)


# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
