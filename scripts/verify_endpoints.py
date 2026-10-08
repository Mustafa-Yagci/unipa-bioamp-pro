import re
import math

sch_path = r"E:\unipa kayıtları\unipa\kicad repo bağlantısı\BioAmp-EXG-Pill\hardware\BioAmp-EXG-Pill.kicad_sch"
with open(sch_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Load all wires
wires = re.findall(r'\(wire\s+\(pts\s+\(xy\s+([-\d.]+)\s+([-\d.]+)\)\s+\(xy\s+([-\d.]+)\s+([-\d.]+)\)\)', text)
wire_endpoints = set()
for w in wires:
    wire_endpoints.add((round(float(w[0]), 2), round(float(w[1]), 2)))
    wire_endpoints.add((round(float(w[2]), 2), round(float(w[3]), 2)))

print(f"Total unique wire endpoints: {len(wire_endpoints)}")

# Find symbols in file
sym_matches = re.finditer(r'\(symbol\s+\(lib_id\s+"([^"]+)"\)\s+\(at\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\)(?:\s+\(mirror\s+([xy])\))?\s+\(unit\s+(\d+)\).*?\(property\s+"Reference"\s+"([^"]+)".*?\(property\s+"Value"\s+"([^"]+)"', text, re.DOTALL)

for sm in sym_matches:
    lib_id = sm.group(1)
    sx = float(sm.group(2))
    sy = float(sm.group(3))
    rot = float(sm.group(4))
    mirror = sm.group(5)
    unit = int(sm.group(6))
    ref = sm.group(7)
    val = sm.group(8)
    
    # Check if any wire endpoint is within 1mm of the symbol center or expected pins
    nearby = [ep for ep in wire_endpoints if abs(ep[0] - sx) < 15 and abs(ep[1] - sy) < 15]
    print(f"Symbol {ref} ({val}, unit {unit}) at ({sx}, {sy}, rot={rot}, mirror={mirror}): {len(nearby)} wire endpoints nearby")
    for ep in nearby[:5]:
        dx = ep[0] - sx
        dy = ep[1] - sy
        print(f"   nearby wire endpoint: ({ep[0]}, {ep[1]}), relative: ({dx:.2f}, {dy:.2f})")
    print()
    if ref in ['U1', 'R7', 'R2', 'R6', 'J1']:
        pass
    else:
        continue
