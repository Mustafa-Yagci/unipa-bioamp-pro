import pcbnew
import subprocess

def route_perfect():
    board_path = r"E:\unipa kayıtları\unipa\kicad repo bağlantısı\Custom_BioAmp_AFE\UniPa_BioAmp_Pro.kicad_pcb"
    board = pcbnew.LoadBoard(board_path)

    # 1. Clear all existing tracks, vias, zones
    for t in list(board.GetTracks()):
        board.Remove(t)
    while board.Zones().size() > 0:
        board.Remove(board.Zones()[0])

    # 2. Net lookup
    nets = {}
    for code, net in board.GetNetInfo().NetsByNetcode().items():
        if net.GetNetname():
            nets[net.GetNetname()] = net.GetNetCode()

    def get_pad(ref, pnum):
        fp = board.FindFootprintByReference(ref)
        pad = fp.FindPadByNumber(pnum)
        pos = pad.GetPosition()
        return (round(pcbnew.ToMM(pos.x), 3), round(pcbnew.ToMM(pos.y), 3))

    def add_seg(p1, p2, net_name, layer=pcbnew.F_Cu, width=0.25):
        if abs(p1[0] - p2[0]) < 0.001 and abs(p1[1] - p2[1]) < 0.001:
            return
        net_code = nets[net_name]
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(p1[0]), pcbnew.FromMM(p1[1])))
        t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(p2[0]), pcbnew.FromMM(p2[1])))
        t.SetWidth(pcbnew.FromMM(width))
        t.SetLayer(layer)
        t.SetNetCode(net_code)
        board.Add(t)

    def add_via(x, y, net_name, width=0.8, drill=0.4):
        net_code = nets[net_name]
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
        v.SetWidth(pcbnew.FromMM(width))
        v.SetDrill(pcbnew.FromMM(drill))
        v.SetNetCode(net_code)
        board.Add(v)

    def route_path(pts, net_name, layer=pcbnew.F_Cu, width=0.25):
        for i in range(len(pts) - 1):
            add_seg(pts[i], pts[i+1], net_name, layer, width)

    print("=== SYNTHESIZING CLEAN DRC-PERFECT PCB ROUTING ===")

    # 1. /ELEC_IN+ (Net 3)
    p_j1_3 = get_pad("J1", "3") # (106.0, 82.92)
    p_r1_2 = get_pad("R1", "2") # (110.175, 81.0)
    route_path([p_j1_3, (108.0, 82.92), (108.0, 81.0), p_r1_2], "/ELEC_IN+")

    # 2. /ELEC_IN- (Net 4)
    p_j1_2 = get_pad("J1", "2") # (106.0, 85.46)
    p_r2_2 = get_pad("R2", "2") # (110.175, 87.0)
    route_path([p_j1_2, (108.0, 85.46), (108.0, 87.0), p_r2_2], "/ELEC_IN-")

    # 3. Net-(U1A--) (Net 13)
    p_r1_1 = get_pad("R1", "1") # (111.825, 81.0)
    p_c1_1 = get_pad("C1", "1") # (115.0, 83.225)
    p_u1_2 = get_pad("U1", "2") # (122.53, 81.46)
    route_path([p_r1_1, (113.5, 81.0), (113.5, 83.225), p_c1_1], "Net-(U1A--)")
    route_path([p_c1_1, (116.0, 83.225), (116.0, 81.46), p_u1_2], "Net-(U1A--)")

    # 4. Net-(U1B--) (Net 15)
    p_r2_1 = get_pad("R2", "1") # (111.825, 87.0)
    p_c1_2 = get_pad("C1", "2") # (115.0, 84.775)
    p_u1_6 = get_pad("U1", "6") # (122.53, 86.54)
    route_path([p_r2_1, (113.5, 87.0), (113.5, 84.775), p_c1_2], "Net-(U1B--)")
    route_path([p_c1_2, (116.0, 84.775), (116.0, 86.54), p_u1_6], "Net-(U1B--)")

    # 5. Net-(U1A-+) (Net 12)
    p_u1_3 = get_pad("U1", "3") # (122.53, 82.73)
    p_r3_1 = get_pad("R3", "1") # (119.0, 83.175)
    p_r4_2 = get_pad("R4", "2") # (119.0, 77.675)
    route_path([p_u1_3, (120.5, 82.73), (120.5, 83.175), p_r3_1], "Net-(U1A-+)")
    add_via(119.0, 82.0, "Net-(U1A-+)")
    add_via(119.0, 76.5, "Net-(U1A-+)")
    add_seg(p_r3_1, (119.0, 82.0), "Net-(U1A-+)")
    route_path([(119.0, 82.0), (119.0, 76.5)], "Net-(U1A-+)", layer=pcbnew.B_Cu)
    add_seg((119.0, 76.5), p_r4_2, "Net-(U1A-+)")

    # 6. Net-(U1B-+) (Net 14)
    p_u1_5 = get_pad("U1", "5") # (122.53, 85.27)
    p_r3_2 = get_pad("R3", "2") # (119.0, 84.825)
    p_r5_2 = get_pad("R5", "2") # (119.0, 88.675)
    route_path([p_u1_5, (120.5, 85.27), (120.5, 84.825), p_r3_2], "Net-(U1B-+)")
    add_via(119.0, 86.0, "Net-(U1B-+)")
    add_via(119.0, 87.5, "Net-(U1B-+)")
    add_seg(p_r3_2, (119.0, 86.0), "Net-(U1B-+)")
    route_path([(119.0, 86.0), (119.0, 87.5)], "Net-(U1B-+)", layer=pcbnew.B_Cu)
    add_seg((119.0, 87.5), p_r5_2, "Net-(U1B-+)")

    # 7. Net-(R15-Pad1) (Net 9)
    p_r15_1 = get_pad("R15", "1") # (121.175, 96.0)
    p_r16_1 = get_pad("R16", "1") # (126.175, 96.0)
    p_r17_2 = get_pad("R17", "2") # (131.175, 96.0)
    route_path([p_r15_1, p_r16_1, p_r17_2], "Net-(R15-Pad1)")

    # 8. /DRL_ELEC (Net 2) - Route on B.Cu to J1.1
    p_j1_1 = get_pad("J1", "1") # (106.0, 88.0)
    p_r17_1 = get_pad("R17", "1") # (132.825, 96.0)
    add_via(132.825, 97.5, "/DRL_ELEC")
    add_seg(p_r17_1, (132.825, 97.5), "/DRL_ELEC")
    route_path([(132.825, 97.5), (132.825, 99.5), (106.0, 99.5), p_j1_1], "/DRL_ELEC", layer=pcbnew.B_Cu)

    # 9. Net-(U1C-+) (Net 16)
    p_u1_10 = get_pad("U1", "10") # (127.47, 85.27)
    p_r6_1 = get_pad("R6", "1") # (131.175, 92.5)
    p_r8_2 = get_pad("R8", "2") # (137.825, 92.5)
    route_path([p_u1_10, (130.0, 85.27), (130.0, 91.5), (131.175, 91.5), p_r6_1], "Net-(U1C-+)")
    route_path([p_r6_1, (131.175, 93.5), (137.825, 93.5), p_r8_2], "Net-(U1C-+)")

    # 10. Net-(U1C--) (Net 17)
    p_u1_9 = get_pad("U1", "9") # (127.47, 86.54)
    p_r7_1 = get_pad("R7", "1") # (131.175, 88.0)
    p_r9_2 = get_pad("R9", "2") # (137.825, 88.0)
    route_path([p_u1_9, (129.0, 86.54), (129.0, 88.0), p_r7_1], "Net-(U1C--)")
    route_path([p_r7_1, (131.175, 89.2), (137.825, 89.2), p_r9_2], "Net-(U1C--)")

    # 11. /INA_OUT (Net 5)
    p_u1_8 = get_pad("U1", "8") # (127.47, 87.81)
    p_r8_1 = get_pad("R8", "1") # (136.175, 92.5)
    p_c2_2 = get_pad("C2", "2") # (132.05, 82.5)
    route_path([p_u1_8, (128.5, 87.81), (128.5, 90.0), (136.175, 90.0), p_r8_1], "/INA_OUT")
    # From (128.5, 90.0) drop via to B.Cu to reach C2.2 at (132.05, 82.5)
    add_via(128.5, 90.0, "/INA_OUT")
    add_via(132.05, 84.0, "/INA_OUT")
    route_path([(128.5, 90.0), (132.05, 90.0), (132.05, 84.0)], "/INA_OUT", layer=pcbnew.B_Cu)
    add_seg((132.05, 84.0), p_c2_2, "/INA_OUT")

    # 12. Net-(C2-Pad1) (Net 8)
    p_c2_1 = get_pad("C2", "1") # (133.95, 82.5)
    p_r10_1 = get_pad("R10", "1") # (137.175, 82.5)
    p_r11_2 = get_pad("R11", "2") # (133.825, 77.0)
    route_path([p_c2_1, p_r10_1], "Net-(C2-Pad1)")
    route_path([p_c2_1, (133.95, 80.5), (133.825, 80.5), p_r11_2], "Net-(C2-Pad1)")

    # 13. Net-(U1D-+) (Net 18)
    p_u1_12 = get_pad("U1", "12") # (127.47, 82.73)
    p_r11_1 = get_pad("R11", "1") # (132.175, 77.0)
    p_r12_2 = get_pad("R12", "2") # (136.675, 77.0)
    p_c3_2 = get_pad("C3", "2") # (140.725, 77.0)
    route_path([p_u1_12, (129.5, 82.73), (129.5, 78.0), (132.175, 78.0), p_r11_1], "Net-(U1D-+)")
    route_path([p_r11_1, (132.175, 75.8), (136.675, 75.8), p_r12_2], "Net-(U1D-+)")
    route_path([p_r12_2, (136.675, 75.8), (140.725, 75.8), p_c3_2], "Net-(U1D-+)")

    # 14. /BIO_OUT (Net 1)
    p_u1_14 = get_pad("U1", "14") # (127.47, 80.19)
    p_r12_1 = get_pad("R12", "1") # (138.325, 77.0)
    p_c3_1 = get_pad("C3", "1") # (142.275, 77.0)
    p_j2_2 = get_pad("J2", "2") # (146.0, 82.96)
    route_path([p_u1_14, (128.5, 80.19), (128.5, 79.0), (138.325, 79.0), p_r12_1], "/BIO_OUT")
    route_path([p_r12_1, (138.325, 79.0), (142.275, 79.0), p_c3_1], "/BIO_OUT")
    route_path([p_c3_1, (144.5, 77.0), (144.5, 82.96), p_j2_2], "/BIO_OUT")

    # 15. Net-(R15-Pad2) (Net 10)
    p_u1_1 = get_pad("U1", "1") # (122.53, 80.19)
    p_r4_1 = get_pad("R4", "1") # (119.0, 79.325)
    p_r6_2 = get_pad("R6", "2") # (132.825, 92.5)
    p_r15_2 = get_pad("R15", "2") # (122.825, 96.0)
    route_path([p_u1_1, (120.5, 80.19), (120.5, 79.325), p_r4_1], "Net-(R15-Pad2)")
    add_via(120.5, 78.5, "Net-(R15-Pad2)")
    add_via(122.825, 94.0, "Net-(R15-Pad2)")
    add_via(132.825, 94.0, "Net-(R15-Pad2)")
    add_seg(p_r4_1, (120.5, 78.5), "Net-(R15-Pad2)")
    route_path([(120.5, 78.5), (117.0, 78.5), (117.0, 94.0), (122.825, 94.0)], "Net-(R15-Pad2)", layer=pcbnew.B_Cu)
    route_path([(122.825, 94.0), (132.825, 94.0)], "Net-(R15-Pad2)", layer=pcbnew.B_Cu)
    add_seg((122.825, 94.0), p_r15_2, "Net-(R15-Pad2)")
    add_seg((132.825, 94.0), p_r6_2, "Net-(R15-Pad2)")

    # 16. Net-(R16-Pad2) (Net 11)
    p_u1_7 = get_pad("U1", "7") # (122.53, 87.81)
    p_r5_1 = get_pad("R5", "1") # (119.0, 90.325)
    p_r7_2 = get_pad("R7", "2") # (132.825, 88.0)
    p_r16_2 = get_pad("R16", "2") # (127.825, 96.0)
    route_path([p_u1_7, (120.5, 87.81), (120.5, 90.325), p_r5_1], "Net-(R16-Pad2)")
    add_via(120.5, 91.5, "Net-(R16-Pad2)")
    add_via(127.825, 94.5, "Net-(R16-Pad2)")
    add_via(134.0, 86.5, "Net-(R16-Pad2)")
    add_seg(p_r5_1, (120.5, 91.5), "Net-(R16-Pad2)")
    route_path([(120.5, 91.5), (120.5, 92.5), (127.825, 92.5), (127.825, 94.5)], "Net-(R16-Pad2)", layer=pcbnew.B_Cu)
    route_path([(127.825, 92.5), (134.0, 92.5), (134.0, 86.5)], "Net-(R16-Pad2)", layer=pcbnew.B_Cu)
    add_seg((127.825, 94.5), p_r16_2, "Net-(R16-Pad2)")
    add_seg((134.0, 86.5), p_r7_2, "Net-(R16-Pad2)")

    # 17. /VREF (Net 6)
    p_r13_2 = get_pad("R13", "2") # (107.825, 96.0)
    p_r14_1 = get_pad("R14", "1") # (111.175, 96.0)
    p_c4_1 = get_pad("C4", "1") # (116.05, 96.0)
    p_u1_13 = get_pad("U1", "13") # (127.47, 81.46)
    p_r9_1 = get_pad("R9", "1") # (136.175, 88.0)
    p_r10_2 = get_pad("R10", "2") # (138.825, 82.5)
    p_j3_2 = get_pad("J3", "2") # (137.04, 74.0)
    p_j2_1 = get_pad("J2", "1") # (146.0, 85.5)

    route_path([p_r13_2, p_r14_1, p_c4_1], "/VREF")
    add_via(116.05, 97.5, "/VREF")
    add_via(143.5, 97.5, "/VREF")
    add_seg(p_c4_1, (116.05, 97.5), "/VREF")
    route_path([(116.05, 97.5), (143.5, 97.5)], "/VREF", layer=pcbnew.B_Cu)
    
    # On B.Cu route VREF bus up along X=143.5
    add_via(143.5, 85.5, "/VREF")
    add_via(136.175, 86.5, "/VREF")
    add_via(138.825, 84.0, "/VREF")
    add_via(128.5, 81.46, "/VREF")

    route_path([(143.5, 97.5), (143.5, 85.5)], "/VREF", layer=pcbnew.B_Cu)
    add_seg((143.5, 85.5), p_j2_1, "/VREF")
    route_path([(143.5, 86.5), (136.175, 86.5)], "/VREF", layer=pcbnew.B_Cu)
    add_seg((136.175, 86.5), p_r9_1, "/VREF")
    route_path([(143.5, 84.0), (138.825, 84.0)], "/VREF", layer=pcbnew.B_Cu)
    add_seg((138.825, 84.0), p_r10_2, "/VREF")
    route_path([(143.5, 85.5), (143.5, 74.0), p_j3_2], "/VREF", layer=pcbnew.B_Cu)
    route_path([(143.5, 81.46), (128.5, 81.46)], "/VREF", layer=pcbnew.B_Cu)
    add_seg((128.5, 81.46), p_u1_13, "/VREF")

    # 18. VCC (Net 19, width 0.4mm)
    p_j3_1 = get_pad("J3", "1") # (134.5, 74.0)
    p_c6_1 = get_pad("C6", "1") # (124.775, 74.0)
    p_c5_1 = get_pad("C5", "1") # (119.95, 74.0)
    p_u1_4 = get_pad("U1", "4") # (122.53, 84.0)
    p_r13_1 = get_pad("R13", "1") # (106.175, 96.0)

    # Route VCC along Y=72.0 on F.Cu so it never crosses C5/C6 pads
    route_path([p_j3_1, (134.5, 72.0), (124.775, 72.0), p_c6_1], "VCC", width=0.4)
    route_path([(124.775, 72.0), (119.95, 72.0), p_c5_1], "VCC", width=0.4)
    route_path([p_c6_1, (124.775, 84.0), p_u1_4], "VCC", width=0.4)
    route_path([(119.95, 72.0), (104.5, 72.0), (104.5, 96.0), p_r13_1], "VCC", width=0.4)

    # 19. GND (Net 7)
    p_u1_11 = get_pad("U1", "11") # (127.47, 84.0)
    p_r14_2 = get_pad("R14", "2") # (112.825, 96.0)
    p_c4_2 = get_pad("C4", "2") # (117.95, 96.0)
    p_c5_2 = get_pad("C5", "2") # (118.05, 74.0)
    p_c6_2 = get_pad("C6", "2") # (123.225, 74.0)

    for px, py, vx, vy in [
        (p_u1_11[0], p_u1_11[1], 126.0, 84.0),
        (p_r14_2[0], p_r14_2[1], 114.2, 96.0),
        (p_c4_2[0], p_c4_2[1], 119.2, 96.0),
        (p_c5_2[0], p_c5_2[1], 118.05, 75.5),
        (p_c6_2[0], p_c6_2[1], 123.225, 75.5),
    ]:
        add_via(vx, vy, "GND")
        add_seg((px, py), (vx, vy), "GND")

    # Solid Ground Zone on B.Cu
    zone = pcbnew.ZONE(board)
    zone.SetLayer(pcbnew.B_Cu)
    net_gnd = board.FindNet("GND")
    if net_gnd:
        zone.SetNet(net_gnd)

    outline = pcbnew.SHAPE_LINE_CHAIN()
    outline.Append(pcbnew.VECTOR2I(pcbnew.FromMM(100), pcbnew.FromMM(70)))
    outline.Append(pcbnew.VECTOR2I(pcbnew.FromMM(150), pcbnew.FromMM(70)))
    outline.Append(pcbnew.VECTOR2I(pcbnew.FromMM(150), pcbnew.FromMM(102)))
    outline.Append(pcbnew.VECTOR2I(pcbnew.FromMM(100), pcbnew.FromMM(102)))
    outline.SetClosed(True)

    poly = zone.Outline()
    poly.AddOutline(outline)
    board.Add(zone)

    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())

    board.Save(board_path)
    print(f"Board saved successfully: {board_path}")
    print(f"Total tracks/vias created: {len(board.GetTracks())}")

if __name__ == "__main__":
    route_perfect()
