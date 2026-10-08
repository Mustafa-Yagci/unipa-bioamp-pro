import re

sch_path = r"E:\unipa kayıtları\unipa\kicad repo bağlantısı\Custom_BioAmp_AFE\UniPa_BioAmp_Pro.kicad_sch"
with open(sch_path, 'r', encoding='utf-8') as f:
    text = f.read()

wires = re.findall(r'\(wire\s+\(pts\s+\(xy\s+([-\d.]+)\s+([-\d.]+)\)\s+\(xy\s+([-\d.]+)\s+([-\d.]+)\)\)', text)
print(f"Total wires in generated schematic: {len(wires)}")

junctions = re.findall(r'\(junction\s+\(at\s+([-\d.]+)\s+([-\d.]+)\)', text)
print(f"Total junctions in generated schematic: {len(junctions)}")

symbols = re.findall(r'\(symbol\s+\(lib_id\s+"([^"]+)"\)\s+\(at\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\)', text)
print(f"Total symbols in generated schematic: {len(symbols)}")

# Collect all wire endpoints
endpoints = set()
for w in wires:
    endpoints.add((float(w[0]), float(w[1])))
    endpoints.add((float(w[2]), float(w[3])))

print(f"Total unique wire vertices: {len(endpoints)}")

# Let's verify that opamp pins touch endpoints
from build_clean_bioamp import calc_pin

# TL074 pins
tl074_units = [
    (1, 105.0, 68.0, 0, 'x', [("1", 7.62, 0), ("2", -7.62, -2.54), ("3", -7.62, 2.54)]),
    (2, 105.0, 102.0, 0, None, [("7", 7.62, 0), ("6", -7.62, -2.54), ("5", -7.62, 2.54)]),
    (3, 150.0, 85.0, 0, None, [("8", 7.62, 0), ("9", -7.62, -2.54), ("10", -7.62, 2.54)]),
    (4, 222.0, 85.0, 0, None, [("14", 7.62, 0), ("13", -7.62, -2.54), ("12", -7.62, 2.54)]),
    (5, 225.0, 165.0, 0, None, [("4", -2.54, 7.62), ("11", -2.54, -7.62)])
]

print("\n--- TL074 PIN CONNECTIVITY CHECK ---")
all_connected = True
for unit, x, y, rot, mirror, pins in tl074_units:
    for pnum, dx, dy in pins:
        ppos = calc_pin(x, y, dx, dy, rot, mirror)
        # Check if ppos in endpoints
        touch = any(abs(ep[0] - ppos[0]) < 0.05 and abs(ep[1] - ppos[1]) < 0.05 for ep in endpoints)
        status = "CONNECTED" if touch else "NOT CONNECTED"
        if not touch: all_connected = False
        print(f"Unit {unit} Pin {pnum} at {ppos}: {status}")

print("\nAll op-amp pins connected?", all_connected)

# Check all symbols
sym_data = re.findall(r'\(symbol\s+\(lib_id\s+"([^"]+)"\)\s+\(at\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\)(?:\s+\(mirror\s+([xy])\))?\s+\(unit\s+(\d+)\).*?\(property\s+"Reference"\s+"([^"]+)".*?\(property\s+"Value"\s+"([^"]+)"', text, re.DOTALL)

print(f"\n--- ALL SYMBOLS PIN CHECK ({len(sym_data)} symbols) ---")
all_syms_ok = True
for lib, x, y, rot, mirror, unit, ref, val in sym_data:
    x, y, rot, unit = float(x), float(y), float(rot), int(unit)
    if "Device:R" in lib or "Device:C" in lib:
        p1 = calc_pin(x, y, 0, 3.81, rot, mirror)
        p2 = calc_pin(x, y, 0, -3.81, rot, mirror)
        t1 = any(abs(ep[0] - p1[0]) < 0.05 and abs(ep[1] - p1[1]) < 0.05 for ep in endpoints)
        t2 = any(abs(ep[0] - p2[0]) < 0.05 and abs(ep[1] - p2[1]) < 0.05 for ep in endpoints)
        if not (t1 and t2):
            print(f"FAILED PASSIVE: {ref} ({val}): Pin 1={t1}, Pin 2={t2}")
            all_syms_ok = False
        else:
            print(f"PASSIVE OK: {ref:<6} ({val:<15}) -> P1={p1}, P2={p2}")
    elif "Conn" in lib:
        # 3 pins
        for i, dy in [(1, 2.54), (2, 0), (3, -2.54)]:
            p = calc_pin(x, y, -5.08, dy, rot, mirror)
            t = any(abs(ep[0] - p[0]) < 0.05 and abs(ep[1] - p[1]) < 0.05 for ep in endpoints)
            if not t:
                print(f"FAILED CONN: {ref} Pin {i} at {p}")
                all_syms_ok = False
            else:
                print(f"CONN OK:    {ref} Pin {i} at {p}")

print("\nAll passives & connectors 100% connected?", all_syms_ok)

