import math
import json
from collections import deque, defaultdict

NODE_GAP = 22
LABEL_HEIGHT = 24
STANDARD_HEIGHT = 57
HORIZONTAL_SPACING = 240

finalJSON = {}

#this function will create the nodes array for reactflow to generate a winner's bracket of size `entrants``
def bracketToJSON(entrants: int):
    
    #linear search who cares itworks iguess
    def getWRNodes(nodes_array: list, round: int):
       result = []
       for node in nodes_array:
            if round > 9 and node["id"][:4] == f'WR{round}':
                result.append(node)
            elif round < 10 and node["id"][:3] == f'WR{round}':
                result.append(node)
        
       return result
    
    def getLRNodes(nodes_array: list, round: int):
       result = []
       for node in nodes_array:
            if round > 9 and node["id"][:4] == f'LR{round}':
                result.append(node)
            elif round < 10 and node["id"][:3] == f'LR{round}':
                result.append(node)
       
       return result
   
    data = defaultdict(list)
    totalRounds = math.ceil(math.log2(entrants)) + 1

    nextPower = 2**(totalRounds-1)

    #add all the label nodes first
    for r in range(1, totalRounds+1):
        label = ""
        if r == totalRounds:
            label = "Grand Finals"
        elif r == totalRounds - 1:
            label = "Winners Finals"
        elif r == totalRounds - 2:
            label = "Winners Semifinals"
        else:
            label = f'Winners Round {r}'

        data["nodes"].append({
                        'id': f'LABEL-WR{r}',
                        'type': 'roundLabelNode',
                        'position': { 'x': (r-1)*HORIZONTAL_SPACING, 'y': 0 }, 
                        'data': {'roundLabel': label, }
                    })
    

    startUpperBound, startLowerBound = LABEL_HEIGHT, LABEL_HEIGHT + NODE_GAP + (nextPower/2 * (STANDARD_HEIGHT+NODE_GAP)) - NODE_GAP
    data["nodes"].append({
                        'id': f'WR{totalRounds}N0',
                        'type': 'bracketNode',
                        'position': { 'x': (totalRounds-1)*HORIZONTAL_SPACING, 'y': (startLowerBound + startUpperBound)/2}, 
                        'data': {'roundLabel': "Grand Finals", 'bracketNodeType': 'end'}
                    })
    

    #BFS to generate winners bracket from grand finals node (in this case would be root node of binary tree)
    nodeIDTracker = [0]* totalRounds
    q = deque([(totalRounds-1, (1,2), (startUpperBound, startLowerBound))])
    
    while len(q) > 0:
        currentRound, seeds, bounds = q.popleft()
        prevRoundCompetitors = nextPower/(2**(currentRound-2))

        bracketNodeType = "intermediate"
        if currentRound == 1:
            bracketNodeType = "start"
        yCoord = (bounds[0] + bounds[1])/2
        
        nodeData = { 
            'bracketNodeType': bracketNodeType
        }
        
        #bye case, only high seed exists
        if currentRound == 1 and seeds[1] > entrants:
            nodeData['highSeed'] = seeds[0]
        else: 
            nodeData['highSeed'] = seeds[0]
            nodeData['lowSeed'] = seeds[1]
        
        #add to json array, along with the edge to my parent
        data["nodes"].append({
            'id': f'WR{currentRound}N{nodeIDTracker[currentRound]}',
            'type': "bracketNode",
            'position': {'x': (currentRound-1)*HORIZONTAL_SPACING, 'y': yCoord },
            'data' : nodeData
        })
        

        parentNodeID = nodeIDTracker[currentRound]//2
        data["edges"].append({
            'id': f'eWR{currentRound}N{nodeIDTracker[currentRound]}-WR{currentRound+1}N{parentNodeID}',
            'type': 'smoothstep',
            'source': f'WR{currentRound}N{nodeIDTracker[currentRound]}',
            'target': f'WR{currentRound+1}N{parentNodeID}',
            'style' : { 'strokeDasharray': '5 5' }
        })
        
        nodeIDTracker[currentRound] += 1
        
        if currentRound - 1 > 0:
            q.append((currentRound-1, (seeds[0], prevRoundCompetitors - seeds[0] + 1), (bounds[0], yCoord)))
            q.append((currentRound-1, (seeds[1], prevRoundCompetitors - seeds[1] + 1), (yCoord, bounds[1])))     

   
   
    #NOW FOR LOSER NODES
    wr2_nodes = nextPower/4
    wr1_nonbye_nodes = nextPower/2 - (nextPower-entrants)

    losersYCoordBase = LABEL_HEIGHT + NODE_GAP + (STANDARD_HEIGHT + NODE_GAP)*(nextPower/2) + STANDARD_HEIGHT + NODE_GAP
    
    if entrants > 3:
        data["nodes"].append({
                    'id': f'LABEL-LR1',
                    'type': "roundLabelNode",
                    'position': {'x': 0, 'y': losersYCoordBase  },
                    'data' : {'roundLabel': f'Losers Round 1' }
                })
            
        data["nodes"].append({
            'id': f'LABEL-LR2',
            'type': "roundLabelNode",
            'position': {'x': HORIZONTAL_SPACING, 'y': losersYCoordBase },
            'data': {'roundLabel': f'Losers Round 2' }
        })

    currNodes = getWRNodes(data["nodes"], 1)
    if wr1_nonbye_nodes > wr2_nodes:
        
        for i in range(int(len(currNodes)/2)):
            node1 = currNodes[i*2]
            node2 = currNodes[i*2 + 1]

            if 'highSeed' in node1["data"] and 'lowSeed' in node1["data"] and 'highSeed' in node2["data"] and 'lowSeed' in node2["data"]:
                yCoord = label
                data["nodes"].append({
                    'id': f'LR1N{i}',
                    'type': "bracketNode",
                    'position': {'x': 0, 'y': losersYCoordBase +LABEL_HEIGHT + NODE_GAP + (STANDARD_HEIGHT + NODE_GAP)*i  },
                    'data' : {'bracketNodeType': 'start', 'winnerSourceTop': f"{node1['id']}", 'winnerSourceBottom': f"{node2['id']}"}
                })
                data["nodes"].append({
                    'id': f'LR2N{i}',
                    'type': "bracketNode",
                    'position': {'x': HORIZONTAL_SPACING, 'y': losersYCoordBase + LABEL_HEIGHT + NODE_GAP + (STANDARD_HEIGHT + NODE_GAP)*i  },
                    'data' : {'bracketNodeType': "intermediate" if nextPower/4 > 1 else "end", 'winnerSourceTop': f'WR2N{int(nextPower/4 - i - 1)}'}
                })
                
                data["edges"].append({
                    'id': f'eLR1N{i}-LR2N{i}',
                    'type': 'smoothstep',
                    'source': f'LR1N{i}',
                    'target': f'LR2N{i}',
                    'style' :  { 'strokeDasharray': '5 5' }
                })
            else:
                bottom = ""
                if 'highSeed' in node1["data"] and 'lowSeed' not in node1["data"]:
                    bottom = f"{node2['id']}"
                else:
                    bottom = f"{node1['id']}"

                data["nodes"].append({
                    'id': f'LR2N{i}',
                    'type': "bracketNode",
                    'position': {'x': HORIZONTAL_SPACING, 'y': losersYCoordBase + LABEL_HEIGHT + NODE_GAP + (STANDARD_HEIGHT + NODE_GAP)*i  },
                    'data' : {'bracketNodeType': "start", 'winnerSourceTop': f'WR2N{int(nextPower/4 - i - 1)}', 'winnerSourceBottom': bottom }
                })
        if nextPower/4 > 1:

            data["nodes"].append({
                'id': f'LABEL-LR3',
                'type': "roundLabelNode",
                'position': {'x': 2*HORIZONTAL_SPACING, 'y': losersYCoordBase },
                'data': {'roundLabel': f'Losers Round 3' }
            })
            #now for nodes that 
            for i in range(int(len(currNodes)/4)):
                t, b = losersYCoordBase + LABEL_HEIGHT + NODE_GAP + (STANDARD_HEIGHT + NODE_GAP)*(i*2), losersYCoordBase + LABEL_HEIGHT + NODE_GAP + (STANDARD_HEIGHT + NODE_GAP)*(i*2+1)
                data["nodes"].append({
                        'id': f'LR3N{i}',
                        'type': "bracketNode",
                        'position': {'x': 2*HORIZONTAL_SPACING, 'y': (t+b)/2 },
                        'data' : {'bracketNodeType': "intermediate"}
                })
                
                data["edges"].append({
                    'id': f'eLR2N{i*2}-LR3{i}',
                    'type': 'smoothstep',
                    'source': f'LR2N{i*2}',
                    'target': f'LR3N{i}',
                    'style' :  { 'strokeDasharray': '5 5' }
                })
                
                data["edges"].append({
                    'id': f'eLR2N{i*2 + 1}-LR3{i}',
                    'type': 'smoothstep',
                    'source': f'LR2N{i*2 + 1}',
                    'target': f'LR3N{i}',
                    'style' :  { 'strokeDasharray': '5 5' }
                })
    else:
        for i in range(int(len(currNodes)/4)):
            pair1 = (currNodes[i*4], currNodes[i*4 + 1])
            pair2 = (currNodes[i*4 + 2], currNodes[i*4 + 3])
            
            p1BothByes = True if ('lowSeed' not in pair1[0]['data'] and 'lowSeed' not in pair1[1]["data"]) else False
            p2BothByes = True if ('lowSeed' not in pair2[0]['data'] and 'lowSeed' not in pair2[1]["data"]) else False
            t,b = losersYCoordBase + LABEL_HEIGHT + NODE_GAP + (STANDARD_HEIGHT + NODE_GAP)*(i*2), losersYCoordBase + LABEL_HEIGHT + NODE_GAP + (STANDARD_HEIGHT + NODE_GAP)*(i*2+1)
            if p1BothByes and p2BothByes:
                #WAHT THE FK CONFUSING INDEXING BRUHhh
                 data["nodes"].append({
                        'id': f'LR2N{(i*2)}',
                        'type': "bracketNode",
                        'position': {'x': HORIZONTAL_SPACING, 'y': (t+b)/2 },
                        'data' : {'bracketNodeType': "start", 'winnerSourceTop': f'WR2N{int(nextPower/4 - (i*2) - 1)}', 'winnerSourceBottom': f'WR2N{int(nextPower/4 - (i*2+1) - 1)}'}
                })
            
            elif not p1BothByes and p2BothByes:
                data["nodes"].append({
                        'id': f'LR1N{(i*2)}',
                        'type': "bracketNode",
                        'position': {'x': 0, 'y': (t+b)/2 },
                        'data' : {'bracketNodeType': "start", 'winnerSourceTop': f'WR2N{int(nextPower/4 - (i*2) - 1)}', 'winnerSourceBottom': pair1[1]['id']}
                })

                data["nodes"].append({
                        'id': f'LR2N{(i*2)}',
                        'type': "bracketNode",
                        'position': {'x': HORIZONTAL_SPACING, 'y': (t+b)/2 },
                        'data' : {'bracketNodeType': "intermediate", 'winnerSourceTop': f'WR2N{int(nextPower/4 - (i*2+1) - 1)}'}
                })

                data["edges"].append({
                        'id': f'eLR1N{(i*2)}-LR2N{(i*2)}',
                        'type': 'smoothstep',
                        'source': f'LR1N{(i*2)}',
                        'target': f'LR2N{(i*2)}',
                        'style' :  { 'strokeDasharray': '5 5' }
                })
                
            else:
                data["nodes"].append({
                        'id': f'LR1N{(i*2)}',
                        'type': "bracketNode",
                        'position': {'x': 0, 'y': t },
                        'data' : {'bracketNodeType': "start", 'winnerSourceTop': f'WR2N{int(nextPower/4 - (i*2) - 1)}', 'winnerSourceBottom': pair1[1]['id']}
                })
                
                data["nodes"].append({
                        'id': f'LR1N{(i*2 + 1)}',
                        'type': "bracketNode",
                        'position': {'x': 0, 'y': b },
                        'data' : {'bracketNodeType': "start", 'winnerSourceTop': f'WR2N{int(nextPower/4 - (i*2+1) - 1)}', 'winnerSourceBottom': pair2[1]['id']}
                })

                data["edges"].append({
                        'id': f'eLR1N{(i*2)}-LR2N{i}',
                        'type': 'smoothstep',
                        'source': f"LR1N{(i*2)}",
                        'target': f'LR2N{i}',
                        'style' :  { 'strokeDasharray': '5 5' }
                })

                data["edges"].append({
                        'id': f'eLR1N{(i*2 + 1)}-LR2N{i}',
                        'type': 'smoothstep',
                        'source': f"LR1N{(i*2 + 1)}",
                        'target': f'LR2N{i}',
                        'style' :  { 'strokeDasharray': '5 5' }
                })

                data["nodes"].append({
                        'id': f'LR2N{i}',
                        'type': "bracketNode",
                        'position': {'x': HORIZONTAL_SPACING, 'y': (t+b)/2 },
                        'data' : {'bracketNodeType': "intermediate"}
                })

    #now that inital 2-3 round edge cases are setup, rest of losers bracket follows straightforward formula
    connection = 0
    
    #if entrants == 4 we are just done
    #if not, we need to build rest of losers bracket
    if nextPower > 4:
        
        currRound = 3
        if wr1_nonbye_nodes > wr2_nodes:
            currRound = 4
        associatedWinnerRound = 3
        populationType = 0
        while True:

            #label first
            data["nodes"].append({
                        'id': f'LABEL-LR{currRound}',
                        'type': 'roundLabelNode',
                        'position': { 'x': (currRound-1)*HORIZONTAL_SPACING, 'y': losersYCoordBase }, 
                        'data': {'roundLabel': f"Losers Round {currRound}", }
            })
            
            #direct edges from previous round, make nods that pull a winner for top 
            prevNodes = getLRNodes(data["nodes"], currRound-1)
            if connection == 0:
                #every node from previous round gets directly connected to a current node
                #this current node takes 
                for i, prevNode in enumerate(prevNodes):
                    
                    #weird algorithm for mixing up the nodes that take in a new batch of winners
                    winnerNodes = getWRNodes(data["nodes"], associatedWinnerRound)
                    N = len(winnerNodes)
                    winnerNodeNumber = -1
                    if populationType == 0:
                        winnerNodeNumber = N//2 - 1 - i
                        if i >= N//2:
                            winnerNodeNumber = N - 1 - (i - N//2)
                    elif populationType == 1:
                        winnerNodeNumber = (i+N//2) % (N)
                    elif populationType == 2:
                        winnerNodeNumber = i
                    else:
                        winnerNodeNumber = N - i - 1
                    
                    
                        

                    
                    data["nodes"].append({
                        'id': f'LR{currRound}N{i}',
                        'type': "bracketNode",
                        'position': {'x': prevNode['position']['x'] + HORIZONTAL_SPACING, 'y': prevNode['position']['y']},
                        'data' : {'bracketNodeType': "end" if len(prevNodes) == 1 else "intermediate", 'winnerSourceTop': f'WR{associatedWinnerRound}N{winnerNodeNumber}'}
                    })
                    
                    data["edges"].append({
                        'id': f"e{prevNode['id']}-LR{currRound}N{i}",
                        'type': 'smoothstep',
                        'source': f"{prevNode['id']}",
                        'target': f'LR{currRound}N{i}',
                        'style' :  { 'strokeDasharray': '5 5' }
                    })
                associatedWinnerRound +=1
                populationType = (populationType + 1) % 4
            #simply make filtering nodes
            else:
                for i in range(int(len(prevNodes)/2)):
                    node1 = prevNodes[(i*2)]
                    node2 = prevNodes[(i*2)+1]

                    data["nodes"].append({
                        'id': f'LR{currRound}N{i}',
                        'type': 'bracketNode',
                        'position': { 'x': node1['position']['x'] + HORIZONTAL_SPACING, 'y': (node1['position']['y'] + node2['position']['y'])/2},
                        'data' : {'bracketNodeType': "intermediate"}
                    })

                    data["edges"].append({
                        'id': f"e{node1['id']}-LR{currRound}N{i}",
                        'type': 'smoothstep',
                        'source': f"{node1['id']}",
                        'target': f'LR{currRound}N{i}',
                        'style' : { 'strokeDasharray': '5 5' }
                    })

                    data["edges"].append({
                        'id': f"e{node2['id']}-LR{currRound}N{i}",
                        'type': 'smoothstep',
                        'source': f"{node2['id']}",
                        'target': f'LR{currRound}N{i}',
                        'style' : { 'strokeDasharray': '5 5' }
                    })
            
            connection = 1 - connection
            currRound+=1
            if len(prevNodes) == 1:
                break
    
    #hard losers bracket for entrants = 3
    if entrants == 3:
        data["nodes"].append({
                        'id': f'LABEL-LR{r}',
                        'type': 'roundLabelNode',
                        'position': { 'x': 0, 'y': losersYCoordBase }, 
                        'data': {'roundLabel': 'Losers Round 1', }
                    })
        
        data["nodes"].append({
                        'id': f'LR1N0',
                        'type': 'bracketNode',
                        'position': { 'x': 0 ,'y':losersYCoordBase + LABEL_HEIGHT +NODE_GAP},
                        'data' : {"winnerSourceTop": "WR2N0", "winnerSourceBottom": "WR1N0"}
        })


    #lastly... add a lone, true finals column
    data["nodes"].append({
                        'id': f'LABEL-TF',
                        'type': 'roundLabelNode',
                        'position': { 'x': (totalRounds)*HORIZONTAL_SPACING, 'y': 0 }, 
                        'data': {'roundLabel': "True Finals", }
                    })

    data["nodes"].append({
                        'id': f'WR{totalRounds+1}N0',
                        'type': 'bracketNode',
                        'position': { 'x': (totalRounds)*HORIZONTAL_SPACING, 'y': (startLowerBound + startUpperBound)/2}, 
                        'data': {'roundLabel': "True Finals"}
                    })
    
    
    
    data["size"] = str(entrants)
    




    return data












for i in range(2,129):
    finalJSON[str(i)] = bracketToJSON(i)

with open(f'src/app/SerializedBrackets.json', 'w') as fp:
    json.dump(finalJSON, fp)  
