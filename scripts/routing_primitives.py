import pcbnew
import math

def route_pin_to_pin(board, pt1, pt2, net_code, layer=pcbnew.F_Cu, width=0.25):
    """Adds 45-degree or orthogonal track segments between pt1 and pt2"""
    x1, y1 = pt1
    x2, y2 = pt2
    
    # If points are identical, nothing to route
    if abs(x1 - x2) < 0.01 and abs(y1 - y2) < 0.01:
        return
        
    # Route with 45-degree corner
    dx = x2 - x1
    dy = y2 - y1
    
    # Intermediate point
    if abs(dx) > abs(dy):
        # Move horizontally first, then 45 deg, then horizontal
        corner_x = x2 - (abs(dy) if dx > 0 else -abs(dy))
        corner_y = y1
        mid_x = x2
        mid_y = y2
        pts = [(x1, y1), (corner_x, corner_y), (mid_x, mid_y)]
    else:
        corner_x = x1
        corner_y = y2 - (abs(dx) if dy > 0 else -abs(dx))
        mid_x = x2
        mid_y = y2
        pts = [(x1, y1), (corner_x, corner_y), (mid_x, mid_y)]
        
    for i in range(len(pts) - 1):
        p_start = pts[i]
        p_end = pts[i+1]
        if abs(p_start[0] - p_end[0]) < 0.01 and abs(p_start[1] - p_end[1]) < 0.01:
            continue
        track = pcbnew.PCB_TRACK(board)
        track.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(p_start[0]), pcbnew.FromMM(p_start[1])))
        track.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(p_end[0]), pcbnew.FromMM(p_end[1])))
        track.SetWidth(pcbnew.FromMM(width))
        track.SetLayer(layer)
        track.SetNetCode(net_code)
        board.Add(track)

def add_via(board, x, y, net_code, width=0.8, drill=0.4):
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
    via.SetWidth(pcbnew.FromMM(width))
    via.SetDrill(pcbnew.FromMM(drill))
    via.SetNetCode(net_code)
    board.Add(via)
    return via

print("Routing primitives defined successfully.")
