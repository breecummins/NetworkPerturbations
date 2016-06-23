import sys
from copy import deepcopy
from numpy import matrix,copy
import intervalgraph as ig
import heapq
import fileparsers


# # Checks to see if the epsilon nbhd of value of t2 intersects the epsilon nbhd of value of t2
# def BoolIntersect(t1,t2,ts,epsilon):
# 	if (ts[t2] + epsilon) >= (ts[t1] - epsilon) and (ts[t2] - epsilon) <= (ts[t1] + epsilon):
# 		return True


# # Grows epsilon components for a given time t. It does this by simultaneiously checking both neighboring points,
# # if they exist, and only adding them if they intersect time t and all other times in the component, as well as
# # intersecting eachother.
# def GrowComponent(t,ts,epsilon,compList):
# 	index = 1
# 	if t == 0:
# 		while not(t+index > len(ts) - 1):
# 			for time in compList[t]:
# 				if not(BoolIntersect(t+index,time,ts,epsilon)):
# 					return compList
# 			compList[t].append(t+index)
# 			index += 1
# 	elif t == len(ts) - 1:
# 		while not(t-index < 0):
# 			for time in compList[t]:
# 				if not(BoolIntersect(t-index,time,ts,epsilon)):
# 					return compList
# 			compList[t].insert(0, t-index)
# 			index += 1
# 	elif not(BoolIntersect(t,t-index,ts,epsilon)) and BoolIntersect(t,t+index,ts,epsilon):
# 		while not(t+index > len(ts) - 1):
# 			for time in compList[t]:
# 				if not(BoolIntersect(t+index,time,ts,epsilon)):
# 					return compList
# 			compList[t].append(t+index)
# 			index += 1
# 	elif BoolIntersect(t,t-index,ts,epsilon) and not(BoolIntersect(t,t+index,ts,epsilon)):
# 		while not(t-index < 0):
# 			for time in compList[t]:
# 				if not(BoolIntersect(t-index,time,ts,epsilon)):
# 					return compList
# 			compList[t].insert(0, t-index)
# 			index += 1
# 	else:
# 		while BoolIntersect(t,t-index,ts,epsilon) and BoolIntersect(t,t+index,ts,epsilon):
# 			if BoolIntersect(t+index,t-index,ts,epsilon):
# 				for time in compList[t]:
# 					if not(BoolIntersect(t-index,time,ts,epsilon) and BoolIntersect(t+index,time,ts,epsilon)):
# 						return compList
# 				compList[t].append(t+index)
# 				compList[t].insert(0, t-index)
# 				if t+index == len(ts) - 1:
# 					index += 1
# 					while not(t-index < 0):
# 						for time in compList[t]:
# 							if not(BoolIntersect(t-index,time,ts,epsilon)):
# 								return compList
# 						compList[t].insert(0, t-index)
# 						index += 1
# 					return compList
# 				if t-index == 0:
# 					index += 1
# 					while not(t+index > len(ts) - 1):
# 						for time in compList[t]:
# 							if not(BoolIntersect(t+index,time,ts,epsilon)):
# 								return compList
# 						compList[t].append(t+index)
# 						index += 1
# 					return compList
# 				index += 1
# 				if not(BoolIntersect(t,t-index,ts,epsilon)) and BoolIntersect(t,t+index,ts,epsilon):
# 					while not(t+index > len(ts) - 1):
# 						for time in compList[t]:
# 							if not(BoolIntersect(t+index,time,ts,epsilon)):
# 								return compList
# 						compList[t].append(t+index)
# 						index += 1
# 					return compList
# 				if BoolIntersect(t,t-index,ts,epsilon) and not(BoolIntersect(t,t+index,ts,epsilon)):
# 					while not(t-index < 0):
# 						for time in compList[t]:
# 							if not(BoolIntersect(t-index,time,ts,epsilon)):
# 								return compList
# 						compList[t].insert(0, t-index)
# 						index += 1
# 					return compList
# 			else:
# 				return compList

# # For a given epsilon, build component list for each t
# # Inputs: ts = time series, epsilon
# # Outputs: compList = list of components indexed by time
# def BuildCompList(ts,epsilon):
# 	compList = []
# 	for t in range(0,len(ts)):
# 		compList.append([t])
# 		GrowComponent(t,ts,epsilon,compList)
# 	return compList

# # Build epsilon indexed list whose entries are lists of components generated at that epsilon
# # Inputs: ts = time series, step = user defined parameter that specifies the increase in epsilon 
# # Outputs: eiList = epsilon indexed list
# def BuildEIList(ts,step):
# 	newts,minVal,maxVal = Normalize(ts)
# 	eiList = []
# 	epsilon = 0
# 	while epsilon <= 0.55:
# 		eiList.append(BuildCompList(newts,epsilon))
# 		epsilon += step
# 	return eiList

def GrowComponent(ts,epsilon,comp):
	# Grows epsilon components for a given time t. It does this by simultaneously checking both neighboring points,
	# if they exist, and only adding them if they intersect time t and all other times in the component, as well as
	# intersecting each other.

	def BoolIntersect(t1,t2,ts,epsilon):
		# Checks to see if the epsilon nbhd of value of t2 intersects the epsilon nbhd of value of t2
		if abs(ts[t2] - ts[t1]) <= 2*epsilon: 
			return True

	def isgoodcandidate(ts,epsilon,candidate,comp):
		for time in comp:
			if not BoolIntersect(candidate,time,ts,epsilon):
				return False
		return True

	def checkleft(ts,epsilon,comp):
		# Proceed to check interval overlap to the left of the component only
		candidate = comp[0] - 1
		while candidate > -1:
			if not isgoodcandidate(ts,epsilon,candidate,comp): 
				return comp
			comp.insert(0, candidate)
			candidate -= 1
		return comp

	def checkright(ts,epsilon,comp):
		# Proceed to check interval overlap to the right of the component only
		candidate = comp[-1] + 1
		N = len(ts)
		while candidate < N:
			if not isgoodcandidate(ts,epsilon,candidate,comp): 
				return comp
			comp.append(candidate)
			candidate += 1
		return comp

	t_beg = comp[0]
	t_end = comp[-1]
	N = len(ts)
	if t_beg == 0:
		return checkright(ts,epsilon,comp)
	elif t_end == N-1:
		return checkleft(ts,epsilon,comp)
	else:
		candidate_beg = t_beg-1
		candidate_end = t_end+1

		while True:
			beg_good = isgoodcandidate(ts,epsilon,candidate_beg,comp)
			end_good = isgoodcandidate(ts,epsilon,candidate_end,comp)
			if (not beg_good) and (not end_good):
				return comp
			elif beg_good and (not end_good):
				comp.insert(0, candidate_beg)			
				return checkleft(ts,epsilon,comp)
			elif (not beg_good) and end_good:
				comp.append(candidate_end)
				return checkright(ts,epsilon,comp)
			else:
				if not BoolIntersect(candidate_beg,candidate_end,ts,epsilon):
					return comp
				else:
					comp.insert(0,candidate_beg)
					comp.append(candidate_end)
					candidate_beg -= 1
					candidate_end += 1
					if candidate_beg == -1:
						if candidate_end < N:
							return checkright(ts,epsilon,comp)
						else:
							return comp
					elif candidate_end == N:
						return checkleft(ts,epsilon,comp)
					else:
						continue

# Build epsilon indexed list whose entries are lists of components generated at that epsilon
# Inputs: ts = time series, step = user defined parameter that specifies the increase in epsilon 
# Outputs: eiList = epsilon indexed list
def BuildEIList(ts,step):
	newts,minVal,maxVal = Normalize(ts)
	compList=[[t] for t in range(len(ts))] # compList at epsilon=0
	eiList = [deepcopy(compList)]
	epsilon = step
	while epsilon <= 0.55:
		compList = [ GrowComponent(newts,epsilon,comp) for comp in compList ] # grow compList from previous calculation
		eiList.append(deepcopy(compList)) # want snapshots of compList at each epsilon
		epsilon += step
	return eiList

# Normalize time series and find global min/max
# Inputs: ts
# Outputs: newts = normalized time series, minVal = global min, maxVal = global max
def Normalize(ts):
	maxVal = ts[0]
	minVal = ts[0]
	for value in ts:
		if value > maxVal:
			maxVal = value
		if value < minVal:
			minVal = value
	newts = []
	for value in ts:
		newValue = float((value - minVal)) / (maxVal - minVal)
		newts.append(newValue)
	return newts,minVal,maxVal

# Concatenate a list of lists
def Concatenate(lists):
	newList = []
	for l in lists:
		newList += l
	return newList

# Uniqify a list, i.e. turn it into a set
def Uniqify(inputList):
 	for item1 in inputList:
 		tempList = list(inputList)
 		tempList.remove(item1)
 		for item2 in tempList:
 			if item1 == item2:
 				inputList.remove(item1)
 	return inputList

# Sorts the unique components grown into two lists, minList and maxList
# Inputs: eiList, ts
# Outputs: minList = list containing all components that are minima, maxList = similar
def MinMaxLabel(eiList,ts):
	compList = Uniqify(Concatenate(eiList))  
	minList = []
	maxList = []
	for comp in compList:
		if 0 in comp:
			if not(len(ts)-1 in comp):
				if ts[comp[-1]+1] > ts[comp[-1]]:
					minList.append(comp)
				else:
					maxList.append(comp)
		elif len(ts)-1 in comp:
			if not(0 in comp):
				if ts[comp[0]-1] > ts[comp[0]]:
					minList.append(comp)
				else:
					maxList.append(comp)
		else:
			if (ts[comp[0]-1] > ts[comp[0]]) and (ts[comp[-1]+1] > ts[comp[-1]]):
				minList.append(comp)
			if (ts[comp[0]-1] < ts[comp[0]]) and (ts[comp[-1]+1] < ts[comp[-1]]):
				maxList.append(comp)
	return minList,maxList

# Return component-chain list indexed by time and a labeled(min/max/n/a) chain list
# Creates list indexed by time where each entry is an epsilon indexed list of components grown at that
# time. This is called chainList. Then I assign each component a label, 'min'/'max'/'n/a' and record
# this as labeledChains.
def BuildChains(eiList,ts,step):
	minList,maxList = MinMaxLabel(BuildEIList(ts,step),ts)
	chainList = []
	labeledChains = []
	for i in range(0,len(eiList[0])):
		chainList.append([])
		labeledChains.append([])
	for list in eiList:
		ndx = 0
		for item in list:
			chainList[ndx].append(item)
			if item in minList:
				labeledChains[ndx].append('min')
			elif item in maxList:
				labeledChains[ndx].append('max')
			else:
				labeledChains[ndx].append('n/a')
			ndx+=1
	return chainList,labeledChains

# Count number of epsilon steps that mins/maxes persisted and return list of min/max lifetimes.
# Note, only considers those that are local mins/maxes at epsilon = 0. 
# Outputs: minLife = time indexed list initialized to all 0's, time's entry is # of consecutive 
# epsilon steps that time was a min, maxLife = similar
def EpsLife(labeledChains):
	minLife = [0] * len(labeledChains)
	maxLife = [0] * len(labeledChains)
	for t in range(0,len(labeledChains)):
		if labeledChains[t][0] == 'min':
			s = 0
			while labeledChains[t][s] == labeledChains[t][0]:
				minLife[t] += 1
				s+=1
		elif labeledChains[t][0] == 'max':
			s = 0
			while labeledChains[t][s] == labeledChains[t][0]:
				maxLife[t] += 1
				s+=1
	return minLife,maxLife

# Extract the n deepest lifetime mins and maxes. If there are ties, the sequentially first one is chosen
# return list of 2n events, ordered by highest min, highest max, second highest min, ...
def DeepLife(minLife,maxLife,ts,n):
	minLifeCopy = list(minLife)
	maxLifeCopy = list(maxLife)
	deepEventList = []
	for ndx in range(0,n):
		minimum = max(minLifeCopy)
		maximum = max(maxLifeCopy)
		minIndex = minLifeCopy.index(minimum)
		maxIndex = maxLifeCopy.index(maximum)
		deepEventList.append(minIndex)
		deepEventList.append(maxIndex)
		minLifeCopy[minIndex] = 0
		maxLifeCopy[maxIndex] = 0
	return deepEventList

# Given a min and max, find the maximum epsilon step where their components are disjoint
def FindEps(eiList, deepEventList):
	value = 0
	epsilon = 0
	maxEps = -1
	while value == 0:
		for ndx1 in range(0,len(deepEventList)):
			for ndx2 in range(0,len(deepEventList)):
				if len(set(eiList[epsilon][deepEventList[ndx1]]).intersection(eiList[epsilon][deepEventList[ndx2]])) != 0 and ndx1 != ndx2:
					value = 1
		if value == 0:
			maxEps = epsilon
		epsilon += 1
	return maxEps

# Process a list of time series and output a list of time series info. Each item in the list will correspond to time series
# and will be a list of the form [eiList, minTime, maxTime, eps]
# eiList = epsilon-indexed list of components, deepMin/MaxList = list of times of first n mins/maxes
# eps = highest step of epsilon at which the min component and max component are disjoint
def ProcessTS(tsList, n, step):
	sumList = []
	for ts in tsList:
		eiList = BuildEIList(ts,step)
		chainList, labeledChains = BuildChains(eiList,ts,step)
		minLife,maxLife = EpsLife(labeledChains)
		deepEventList = DeepLife(minLife,maxLife,ts,n)
		eps = FindEps(eiList,deepEventList)
		sumList.append([eiList,deepEventList,eps])
	return sumList

# Find the minimum value of eps such that min/max interval of every time series being processed
# is disjoint. So take min of all eps
def FindMaxEps(sumList):
	epsilon = sumList[0][2]
	for ts in sumList:
		if ts[2] < epsilon:
			epsilon = ts[2]
	return epsilon

# For each ts, pull min/max components for each step up to eps indexed by ts
# then highest min, highest max, second highest min, ...
def PullEventComps(sumList,maxEps,step,n):
	eventCompList = []
	ndx = 0
	for tsList in sumList:
		eventCompList.append([])
		for event in range(0,2*n):
			eventCompList[ndx].append(tsList[0][maxEps][tsList[1][event]])
		ndx += 1
	return eventCompList

# Build partial order list indexed by epsilon. Each PO is a list indexed by 1st ts highest min, 1st ts highest max, 
# 1st ts second highest min, 1st ts second highst max, ..., last ts nth highest min, last ts nth highest max
# Each entry is a list of all mins/maxes that occur before the given min/max. 
def BuildPO(eventCompList,step,n):
	PO = []
	for ts in range(0,len(eventCompList)):
		for event in range(0,2*n):
			PO.append([])
			for ndx in range(0,len(eventCompList)):
				for ndx1 in range(0,2*n):
					fixed = eventCompList[ts][event]
					checker = eventCompList[ndx][ndx1]
					intSize = len(set(fixed).intersection(checker))
					if intSize == 0:
						if fixed[0] < checker[0]:
							PO[2*n*ts + event].append(2*n*ndx + ndx1)
	return PO

# Convert PO's to graph class
def POToGraph(PO,TSLabels,n):
	G = ig.Graph()
	for value in range(0,len(PO)):
		G.add_vertex(value,TSLabels[value/(2*n)])
	for i in range(0,len(PO)):
		for j in PO[i]:
			G.add_edge(i,j)
	G = G.transitive_reduction()
	return G

# Convert graphs to digraphs
def GraphToDigraph(G):
	DG = Digraph(comment = 'PO')
	for v in G.vertices():
		DG.node(str(v),G.vertex_label(v))
	for e in G.edges():
		DG.edge(str(e[0]),str(e[1]))
	DG.render('graph.gv',view=True)

# Labeling function for the genes
def CreateLabel(sumList):
	d = len(sumList)
	label = [0]*(2*d)
	for ndx in range(0,d):
		lastEvent = max(sumList[ndx][1])
		indexOfLE = sumList[ndx][1].index(lastEvent)
		if indexOfLE%2 == 1:   # last event was max, since ordered min,max,min,max,...
			label[2*d - 1 - ndx] = 1
			label[d - 1 - ndx] = 0
		else:
			label[2*d - 1 - ndx] = 0
			label[d - 1 - ndx] = 1
	label = '0b' + ''.join([str(x) for x in label])	#Cast to binary
	label = int(label,2)
	return label

# Create JSON string for each graph
def ConvertToJSON(graph,sumList,TSLabels):
	G = graph
	output = {}
	output["poset"] = [ list(G.adjacencies(i)) for i in G.vertices() ]
	output["events"] = [ TSLabels.index(G.vertex_label(i)) for i in G.vertices() ]
	output["label"] = CreateLabel(sumList)
	output["dimension"] = len(TSLabels)
	return output

def makeJSONstring(TSList,TSLabels,n=1,scalingFactor=1,step=0.01):
	# TSList is a list of time series, each of which is a list of floats
	# Each time series has a label in the corresponding index of TSLabels
	# n = number of mins/maxes to pull
	# scalingFactor = a scaling factor of maxEps (Must be in [0,1]), step (default to 0.01)
	if step <=0:
		print "Changing step size to 0.01."
		step = 0.01

	sumList = ProcessTS(TSList,n,step)

	maxEps = FindMaxEps(sumList)
	if scalingFactor >= 0 and scalingFactor < 1:
		maxEps = int(scalingFactor*maxEps)
	eventCompList = PullEventComps(sumList,maxEps,step,n)
	PO = BuildPO(eventCompList,step,n)
	graph = POToGraph(PO,TSLabels,n)
	return ConvertToJSON(graph,sumList,TSLabels)

def testme():
	# import fileparsers
	# import matplotlib.pyplot as plt
	TSList,TSLabels,timeStepList = fileparsers.parseTimeSeriesFileRow('testtimeseries.txt')
	# desiredlabels = ['PF3D7_0100100','PF3D7_0100200','PF3D7_0100300','PF3D7_0100400','PF3D7_0100900','PF3D7_0101000']
	desiredlabels = ['PF3D7_0100100','PF3D7_0100200','PF3D7_0100300']
	ind = timeStepList.index(42)
	labels,data = zip(*[(node,TSList[TSLabels.index(node)][:ind+1]) for node in TSLabels if node in desiredlabels])
	print makeJSONstring(data,labels,n=1,scalingFactor=0.05,step=0.01)
	ts=timeStepList[:ind+1]
	# plt.figure()
	# plt.hold('on')
	# for d in data:
	# 	nd,_,_ = Normalize(d)
	# 	plt.plot(ts,nd)
	# plt.legend(desiredlabels)
	# plt.show()



if __name__ == "__main__":	
	testme()