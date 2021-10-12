# Unit action list

cell_action_list = []




cell_action_list.append('BuildWorker')
cell_action_list.append('BuildCart')

cell_action_list.append('Research')




cell_action_list.append('DoNothing')

cell_action_list.append('MoveNorth')
cell_action_list.append('MoveWest')
cell_action_list.append('MoveEast')
cell_action_list.append('MoveSouth')

cell_action_list.append('SmartTransfer')




cell_action_list.append('BuildCity')
cell_action_list.append('Pillage')




# Unit action map

cell_action_map = {}
for i in range(len(cell_action_list)):
  cell_action_map[cell_action_list[i]] = i




# Unit action count

UNIT_ACTION_COUNT = len(cell_action_list)