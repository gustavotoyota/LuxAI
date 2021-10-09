# Action list

action_list = []

action_list.append('BuildWorker')
action_list.append('BuildCart')

action_list.append('BuildCity')
action_list.append('Pillage')

action_list.append('TransferWood')
action_list.append('TransferCoal')
action_list.append('TransferUranium')

action_list.append('MoveNorth')
action_list.append('MoveWest')
action_list.append('MoveEast')
action_list.append('MoveSouth')
action_list.append('MoveCenter')




# Action map

action_map = {}
for i in range(len(action_list)):
  action_map[action_list[i]] = i




# Action count

ACTION_COUNT = len(action_list)