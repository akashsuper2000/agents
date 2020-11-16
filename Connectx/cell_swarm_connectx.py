def cell_swarm(obs, conf):
    def evaluate_cell(cell):
        """ evaluate qualities of the cell """
        cell = get_patterns(cell)
        cell = calculate_points(cell)
        cell = explore_cell_above(cell)
        return cell
    
    def get_patterns(cell):
        """ get swarm and opponent's patterns of each axis of the cell """
        ne = get_pattern(cell["x"], lambda z : z + 1, cell["y"], lambda z : z - 1, conf.inarow)
        sw = get_pattern(cell["x"], lambda z : z - 1, cell["y"], lambda z : z + 1, conf.inarow)[::-1]
        cell["swarm_patterns"]["NE_SW"] = sw + [{"mark": swarm_mark, "in_air": False}] + ne
        cell["opp_patterns"]["NE_SW"] = sw + [{"mark": opp_mark, "in_air": False}] + ne
        e = get_pattern(cell["x"], lambda z : z + 1, cell["y"], lambda z : z, conf.inarow)
        w = get_pattern(cell["x"], lambda z : z - 1, cell["y"], lambda z : z, conf.inarow)[::-1]
        cell["swarm_patterns"]["E_W"] = w + [{"mark": swarm_mark, "in_air": False}] + e
        cell["opp_patterns"]["E_W"] = w + [{"mark": opp_mark, "in_air": False}] + e
        se = get_pattern(cell["x"], lambda z : z + 1, cell["y"], lambda z : z + 1, conf.inarow)
        nw = get_pattern(cell["x"], lambda z : z - 1, cell["y"], lambda z : z - 1, conf.inarow)[::-1]
        cell["swarm_patterns"]["SE_NW"] = nw + [{"mark": swarm_mark, "in_air": False}] + se
        cell["opp_patterns"]["SE_NW"] = nw + [{"mark": opp_mark, "in_air": False}] + se
        s = get_pattern(cell["x"], lambda z : z, cell["y"], lambda z : z + 1, conf.inarow)
        n = get_pattern(cell["x"], lambda z : z, cell["y"], lambda z : z - 1, conf.inarow)[::-1]
        cell["swarm_patterns"]["S_N"] = n + [{"mark": swarm_mark, "in_air": False}] + s
        cell["opp_patterns"]["S_N"] = n + [{"mark": opp_mark, "in_air": False}] + s
        return cell
        
    def get_pattern(x, x_fun, y, y_fun, cells_remained):
        """ get pattern of marks in direction """
        pattern = []
        x = x_fun(x)
        y = y_fun(y)
        # if cell is inside swarm's borders
        if y >= 0 and y < conf.rows and x >= 0 and x < conf.columns:
            pattern.append({
                "mark": swarm[x][y]["mark"],
                "in_air": True if (y + 1) < conf.rows and swarm[x][y + 1]["mark"] == 0 else False
            })
            # amount of cells to explore in this direction
            cells_remained -= 1
            if cells_remained > 1:
                pattern.extend(get_pattern(x, x_fun, y, y_fun, cells_remained))
        return pattern
    
    def calculate_points(cell):
        """ calculate amounts of swarm's and opponent's correct patterns and add them to cell's points """
        for i in range(conf.inarow - 1):
            # inarow = amount of marks in pattern to consider that pattern as correct
            inarow = conf.inarow - i
            swarm_points = 0
            swarm_in_air = 0
            swarm_s_n = 0
            opp_points = 0
            opp_in_air = 0
            opp_s_n = 0
            # calculate swarm's points
            swarm_points, swarm_in_air = evaluate_pattern(
                swarm_points, swarm_in_air, cell["swarm_patterns"]["E_W"], swarm_mark, inarow)
            swarm_points, swarm_in_air = evaluate_pattern(
                swarm_points, swarm_in_air, cell["swarm_patterns"]["NE_SW"], swarm_mark, inarow)
            swarm_points, swarm_in_air = evaluate_pattern(
                swarm_points, swarm_in_air, cell["swarm_patterns"]["SE_NW"], swarm_mark, inarow)
            # S -> N has lower priority than any other axis
            swarm_s_n, _ = evaluate_pattern(0, 0, cell["swarm_patterns"]["S_N"], swarm_mark, inarow)
            if swarm_s_n > 0:
                swarm_points += 1
                swarm_in_air += i
            # calculate opponent's points
            opp_points, opp_in_air = evaluate_pattern(
                opp_points, opp_in_air, cell["opp_patterns"]["E_W"], opp_mark, inarow)
            opp_points, opp_in_air = evaluate_pattern(
                opp_points, opp_in_air, cell["opp_patterns"]["NE_SW"], opp_mark, inarow)
            opp_points, opp_in_air = evaluate_pattern(
                opp_points, opp_in_air, cell["opp_patterns"]["SE_NW"], opp_mark, inarow)
            # S -> N has lower priority than any other axis
            opp_s_n, _ = evaluate_pattern(0, 0, cell["opp_patterns"]["S_N"], opp_mark, inarow)
            if opp_s_n > 0:
                opp_points += 1
                opp_in_air += i
            # central column priority
            if i == 2:
                if cell["x"] == swarm_center:
                    cell["points"].append(1)
                else:
                    cell["points"].append(0)
                cell["in_air"].append(0)
            # if more than one mark required for victory
            if i > 0:
                # swarm_mark or opp_mark priority
                if swarm_points > opp_points:
                    cell["points"].append(swarm_points)
                    cell["in_air"].append(swarm_in_air)
                    cell["points"].append(opp_points)
                    cell["in_air"].append(opp_in_air)
                else:
                    cell["points"].append(opp_points)
                    cell["in_air"].append(opp_in_air)
                    cell["points"].append(swarm_points)
                    cell["in_air"].append(swarm_in_air)
            else:
                cell["points"].append(swarm_points)
                cell["in_air"].append(swarm_in_air)
                cell["points"].append(opp_points)
                cell["in_air"].append(opp_in_air)
        return cell
                    
    def evaluate_pattern(points, in_air, pattern, mark, inarow):
        """ get amounts of points and "in_air" cells, if pattern have required amounts of marks and zeros """
        # saving enough cells for required amounts of marks and zeros
        for i in range(len(pattern) - (conf.inarow - 1)):
            marks = 0
            zeros = 0
            this_pattern_in_air = 0
            # check part of pattern for required amounts of marks and zeros
            for j in range(conf.inarow):
                if pattern[i + j]["mark"] == mark:
                    marks += 1
                elif pattern[i + j]["mark"] == 0:
                    zeros += 1
                    if pattern[i + j]["in_air"] is True:
                        this_pattern_in_air += 1
            if marks >= inarow and (marks + zeros) == conf.inarow:
                return points + 1, in_air + this_pattern_in_air
        return points, in_air
    
    def explore_cell_above(cell):
        """ add negative points from cell above (if it exists) to points of current cell """
        if (cell["y"] - 1) >= 0:
            cell_above = swarm[cell["x"]][cell["y"] - 1]
            cell_above = get_patterns(cell_above)
            cell_above = calculate_points(cell_above)
            # add first 4 points of cell_above["points"] to cell["points"] as negative numbers
            # starting from index 2 in cell["points"]
            cell["points"][2:2] = [-cell_above["points"][1], -cell_above["points"][0]]
            cell["in_air"][2:2] = [cell_above["in_air"][1], cell_above["in_air"][0]]
            # and then at index 4
            # if it is not potential "seven" pattern in cell
            if cell["points"][4] < 2 and cell["points"][4] < cell_above["points"][2]:
                cell["points"][4:4] = [-cell_above["points"][2]]
                cell["in_air"][4:4] = [cell_above["in_air"][2]]
                # and then at index 5
                # if it is not potential "seven" pattern in cell
                if cell["points"][5] < 2 and cell["points"][5] < cell_above["points"][3]:
                    cell["points"][5:5] = [-cell_above["points"][3]]
                    cell["in_air"][5:5] = [cell_above["in_air"][3]]
                # otherwise at index 7 add zero
                else:
                    cell["points"][7:7] = [0]
                    cell["in_air"][7:7] = [0]
            # otherwise at index 6 add zero
            else:
                cell["points"][6:6] = [0, 0]
                cell["in_air"][6:6] = [0, 0]
        else:
            cell["points"][2:2] = [0, 0]
            cell["in_air"][2:2] = [0, 0]
            cell["points"][6:6] = [0, 0]
            cell["in_air"][6:6] = [0, 0]
        return cell
    
    def choose_best_cell(best_cell, current_cell):
        """ compare two cells and return the best one """
        if best_cell is not None:
            for i in range(len(best_cell["points"])):
                # compare amounts of points of two cells
                if best_cell["points"][i] < current_cell["points"][i]:
                    best_cell = current_cell
                    break
                if best_cell["points"][i] > current_cell["points"][i]:
                    break
                # if amounts of points are equal, compare amounts of "in_air" cells in patterns
                if best_cell["in_air"][i] > current_cell["in_air"][i]:
                    best_cell = current_cell
                    break
                if best_cell["in_air"][i] < current_cell["in_air"][i]:
                    break
        else:
            best_cell = current_cell
        return best_cell
        
    
###############################################################################
    # define swarm's and opponent's marks
    swarm_mark = obs.mark
    opp_mark = 2 if swarm_mark == 1 else 1
    
    # define swarm as two dimensional array of cells
    swarm = []
    for column in range(conf.columns):
        swarm.append([])
        for row in range(conf.rows):
            cell = {
                        "x": column,
                        "y": row,
                        "mark": obs.board[conf.columns * row + column],
                        "swarm_patterns": {},
                        "opp_patterns": {},
                        "points": [],
                        "in_air": []
                    }
            swarm[column].append(cell)
    
    best_cell = None
    swarm_center = conf.columns // 2
    # start searching for best_cell from swarm center
    x = swarm_center
    # shift to right or left from swarm center
    shift = 0
    
    # searching for best_cell
    while x >= 0 and x < conf.columns:
        # find first empty cell starting from bottom of the column
        y = conf.rows - 1
        while y >= 0 and swarm[x][y]["mark"] != 0:
            y -= 1
        # if column is not full
        if y >= 0:
            # current cell evaluates its own qualities
            current_cell = evaluate_cell(swarm[x][y])
            # current cell compares itself against best cell
            best_cell = choose_best_cell(best_cell, current_cell)
                        
        # shift x to right or left from swarm center
        if shift >= 0:
            shift += 1
        shift *= -1
        x = swarm_center + shift

    # return index of the best cell column
    return best_cell["x"]
