'''
    Class gameProblem, implements simpleai.search.SearchProblem
'''


from simpleai.search import SearchProblem
# from simpleai.search import breadth_first,depth_first,astar,greedy
import simpleai.search

class GameProblem(SearchProblem):

    # Object attributes, can be accessed in the methods below

	MAP=None
	POSITIONS=None
	INITIAL_STATE=None
	GOAL=None
	CONFIG=None
	AGENT_START=None
	SHOPS=None
	CUSTOMERS=None
	MAXBAGS = 0

	MOVES = ('West','North','East','South')

   # --------------- Common functions to a SearchProblem -----------------

	def actions(self, state):
		'''Returns a LIST of the actions that may be executed in this state'''
		
		action = []

		if (state[0],state[1]) in self.POSITIONS['pizza'] and state[2]<self.MAXBAGS:
			action.append('Load')

		elif len(state)>3 and state[2]>0:	
			for position in state[3]:
				if position[0]==state[0] and position[1]==state[1]:
					action.append('Unload')
					
		if state[1]!=0:
			if (state[0],state[1]-1) not in self.POSITIONS['building']:
				action.append('North')
			
		if state[1]!=self.CONFIG['map_size'][1]-1:
			if (state[0],state[1]+1) not in self.POSITIONS['building']:		
				action.append('South')

		if state[0]!=0:
			if (state[0]-1,state[1]) not in self.POSITIONS['building']:
				action.append('West')

		if state[0]!=self.CONFIG['map_size'][0]-1:
			if (state[0]+1,state[1]) not in self.POSITIONS['building']:		
				action.append('East')
	
		return action


	def result(self, state, action):
		'''Returns the state reached from this state when the given action is executed'''
		if action == 'Load':
			next_state = (state[0],state[1],state[2]+1, state[3])

		if action == 'Unload':
			positions = ()
			for position in state[3]:
				if (position[0],position[1])==(state[0],state[1]):
					left = position[2]-1
					if left!=0:
						positions += ((position[0], position[1], left) ,)
				else:
					positions += ((position[0], position[1], position[2]) ,)
			next_state = (state[0], state[1], state[2]-1, positions)
				
		if action == 'North':
			next_state = (state[0], state[1]-1, state[2], state[3])

		if action == 'East':
			next_state = (state[0]+1, state[1], state[2], state[3])

		if action == 'South':
			next_state = (state[0], state[1]+1, state[2], state[3])

		if action == 'West':
			next_state = (state[0]-1, state[1], state[2], state[3])

		return next_state

	def delivered(self, state):
		'''Return the number of pizzas you would deliver at a customer's house'''
		for pl in state[3]:
			if (state[0],state[1])==(pl[0],pl[1]):
				if pl[2]>state[2]:
					return state[2]
				else:
					return pl[2]
		return 0

	def pick(self, state):
		'''Returns the number of pizzas you would load at the pizza place'''
		if self.MAXBAGS > self.getTotalRequests(state):
			return self.getTotalRequests(state)
		else:
			return self.MAXBAGS
	

	def is_goal(self, state):
		'''
		Returns true if state is the final state
	    final_state= (self.AGENT_START[0], self.AGENT_START[1], 0, ())
        '''
		return state==self.GOAL

	def cost(self, state, action, state2):
    	#Returns the cost of applying 'action' from 'state' to 'state2'
		#The returned value is a number (integer or floating point)
		#By default this function returns '1'
        
		cost = self.getAttribute((state[0], state[1]), 'cost') + state[2]
	
		for pizz in self.SHOPS:
			if action == 'Load' and (state2[0],state2[1])==(pizz[0],pizz[1]):
				if self.pick(state2) > 0:
					cost += 2 * self.pick(state2)	
		 
		if action == 'Unload':
			for cus in state2[3]:
				if (state2[0],state2[1])==(cus[0],cus[1]):
					cost += 3 * self.delivered(state2)
		return cost

	def manhattan(self, pos1, pos2):
		return abs(pos1[0]-pos2[0]) + abs(pos1[1]-pos2[1])

	def goal_distance (self, state):
		return self.manhattan((state[0],state[1]), (self.GOAL[0],self.GOAL[1]))
	
	def nearestShop (self, state):
		#This function returns the coordinates of the nearest shop from the position you are at
		nearests = None
		distance = self.CONFIG['map_size'][0] + self.CONFIG['map_size'][1]
		for shop in self.SHOPS:
			new_distance = self.manhattan((state[0],state[1]), shop)
			if new_distance<distance:
				distance = new_distance
				nearests = shop
		return nearests

	def distanceNearShop(self, state):
		#This function calculates the distance from the driver's current position to the nearest shop
		distance = self.CONFIG['map_size'][0] + self.CONFIG['map_size'][1]
		for shop in self.SHOPS:
			distance = min(self.manhattan((state[0],state[1]), self.nearestShop(state)), distance)
		return distance

	def farthestShop (self, state):
		#This function returns the coordinates of the farthest shop from the position you are at
		farthests = 0
		distance = 0
		for shop in self.SHOPS:
			new_distance = self.manhattan((state[0],state[1]), shop)
			if distance<new_distance:
				distance = new_distance
				farthest = shop
		return farthests

	def distanceFarShop (self, state):
		distance = 0
		for shop in self.SHOPS:
			distance = max(self.manhattan((state[0],state[1]), shop), distance)
		return distance

	def nearestClient (self, state):
		if len(state)>3:
			distance = self.CONFIG['map_size'][0] + self.CONFIG['map_size'][1]
			nearestc = None 
			for clients in state[3]:
				new_distance = self.manhattan((state[0],state[1]), (clients[0],clients[1]))
				if new_distance<distance:
					distance = new_distance
					nearestc = (clients[0], clients[1])
		return nearestc

	def distanceNearClient (self, state):
		if len(state)<3:
			return 0
		distance = self.CONFIG['map_size'][0] + self.CONFIG['map_size'][1]
		for cust in state[3]:
			distance = min(self.manhattan((state[0],state[1]), (cust[0],cust[1])), distance)
		return distance
	
	def farthestClient (self, state):
		if len(state)>3:	
			distance = 0
			farthestc = None
			for clients in state[3]:
				new_distance = self.manhattan((state[0],state[1]), (clients[0],clients[1]))
				if new_distance>distance:
					distance = new_distance
					farthestc = (clients[0], clients[1])
		return farthestc

	def distanceFarClient (self, state):
		if len(state)<3:
			return 0
		distance = 0
		for cust in state[3]:
			distance = max(self.manhattan((state[0],state[1]), (cust[0],cust[1])), distance)
		return distance

	def distanceMostOrders (self, state):
		#Return distance to the client that has ordered the most pizzas
	
		for order in state[3]:
			if 'customer3' in self.POSITIONS.keys():
				for cust in self.POSITIONS['customer3']:
					if (cust[0], cust[1])==(order[0],order[1]):
						return self.manhattan((cust[0],cust[1]),(order[0],order[1]))
			if 'customer2' in self.POSITIONS.keys():
				for cust in self.POSITIONS['customer2']:
					if (cust[0], cust[1])==(order[0],order[1]):
						return self.manhattan((cust[0],cust[1]),(order[0],order[1]))	
			if 'customer1' in self.POSITIONS.keys():
				for cust in self.POSITIONS['customer1']:
					if (cust[0], cust[1])==(order[0],order[1]):
						return self.manhattan((cust[0],cust[1]),(order[0],order[1]))	
		return 0
		
	def heuristic(self, state):
		#Returns the heuristic for `state`

		def heuristic0(self, state):
			return 0

		def heuristic1(self, state):
			if len(state)>3:
				if state[2]>0:
					return self.distanceNearClient(state)
				else:
					return self.distanceNearShop(state)
			else:
				return self.goal_distance(state)
		
		def heuristic2(self, state):
			if len(state)>3:
				if state[2]>0:
					return self.distanceFarClient(state)
				else:
					return self.distanceFarShop(state)
			else:
				return self.goal_distance(state)
		
		def heuristic3 (self, state):
			if len(state)>3:
				if state[2]>0:
					return self.distanceMostOrders(state)
				else:
					return self.distanceNearShop(state)
			else:
				return self.goal_distance(state)
	
		return heuristic0(self, state)
		#return heuristic1(self, state)
		#return heuristic2(self, state)
		#return heuristic3(self, state)

	def setup (self):
			#This method must create the initial state, final state (if desired) and specify the algorithm to be used
			#This values are later stored as globals that are used when calling the search algorithm.
			#final state is optional because it is only used inside the is_goal() method
			#It also must set the values of the object attributes that the methods need, as for example, self.SHOPS or self.MAXBAGS

		print ('\nMAP: ', self.MAP, '\n')
		print ('POSITIONS: ', self.POSITIONS, '\n')
		print ('CONFIG: ', self.CONFIG, '\n')

		self.CUSTOMERS = ()

		if 'customer1' in self.POSITIONS.keys():
			for location in self.POSITIONS['customer1']:
				self.CUSTOMERS += ( (location[0],location[1],self.getAttribute(location, 'objects')) ,)
		if 'customer2' in self.POSITIONS.keys():
			for location in self.POSITIONS['customer2']:
				self.CUSTOMERS += ( (location[0], location[1],self.getAttribute(location, 'objects')) ,)
		if 'customer3' in self.POSITIONS.keys():
			for location in self.POSITIONS['customer3']:
				self.CUSTOMERS += ( (location[0], location[1],self.getAttribute(location, 'objects')) ,)

			initial_state = (self.AGENT_START[0], self.AGENT_START[1], 0, self.CUSTOMERS)
			'''final_state= (self.AGENT_START[0], self.AGENT_START[1], 0, ())'''
		final_state = (0, 0, 0, ())

		self.SHOPS = list(self.POSITIONS['pizza'])
		self.MAXBAGS = self.CONFIG["maxBags"]

		#algorithm= simpleai.search.astar
		#algorithm= simpleai.search.breadth_first
		algorithm= simpleai.search.depth_first
		#algorithm= simpleai.search.limited_depth_first

		return initial_state,final_state,algorithm


	def printState (self,state):
		#Return a string to pretty-print the state

		pps='Delivery boy is at position ({0}, {1}), he is carrying {2} pizzas and there are {3} remaining orders\n'.format(state[0], state[1], state[2], self.getPendingRequests(state))
		print (pps)
		return (pps)


	def getPendingRequests (self,state):
		#Return the number of pending requests in the given position (0-N)
		#MUST return None if the position is not a customer.
		#This information is used to show the proper customer image.

		if len(state)>3:
			for element in state[3]:
				if (element[0], element[1])==(state[0],state[1]):
					return element[2]

		if 'customer1' in self.POSITIONS.keys():
			for customer in self.POSITIONS['customer1']:
				if (customer[0], customer[1])==(state[0],state[1]):
					return 0
		if 'customer2' in self.POSITIONS.keys():
			for customer in self.POSITIONS['customer2']:
				if (customer[0], customer[1])==(state[0],state[1]):
					return 0
		if 'customer3' in self.POSITIONS.keys():
			for customer in self.POSITIONS['customer3']:
				if (customer[0], customer[1])==(state[0],state[1]):
					return 0
		return None
		

	def getTotalRequests (self, state):
		tot= 0
		if len(state)>3:
			for customer in state[3]:
				tot += customer[2]
		return tot	

    # -------------------------------------------------------------- #
    # --------------- DO NOT EDIT BELOW THIS LINE  ----------------- #
    # -------------------------------------------------------------- #

	def getAttribute (self, position, attributeName):
		#Returns an attribute value for a given position of the map
		#position is a tuple(x,y)
		#attributeName is a string

		#Returns:
		#None if the attribute does not exist
		#Value of the attribute otherwise

		tileAttributes=self.MAP[position[0]][position[1]][2]

		if attributeName in tileAttributes.keys():
			return tileAttributes[attributeName]
		else:
			return None

	def getStateData (self,state):
		stateData={}
		pendingItems=self.getPendingRequests(state)
		if pendingItems >= 0:
			stateData['newType']='customer{}'.format(pendingItems)
		return stateData

    # THIS INITIALIZATION FUNCTION HAS TO BE CALLED BEFORE THE SEARCH
	def initializeProblem(self,map,positions,conf,aiBaseName):
		self.MAP=map
		self.POSITIONS=positions
		self.CONFIG=conf
		self.AGENT_START = tuple(conf['agent']['start'])

		initial_state,final_state,algorithm = self.setup()
		if initial_state == False:
			print ('-- INITIALIZATION FAILED')
			return True

		self.INITIAL_STATE=initial_state
		self.GOAL=final_state
		self.ALGORITHM=algorithm
		super(GameProblem,self).__init__(self.INITIAL_STATE)

		print ('-- INITIALIZATION OK')
		return True

    # END initializeProblem
