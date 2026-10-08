# UniPa BioAmp Pro — Precision Biopotential Analog Front-End (AFE)

<div align="center">

![Header Banner](https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=2,12,30,48&height=200&section=header&text=UniPa%20BioAmp%20Pro&fontSize=48&fontColor=ffffff&animation=fadeIn&subtext=Precision%20Biopotential%20AFE%20%7C%20CMRR%20%3E100%20dB%20%E2%80%A2%20DRL%20Active%20Suppression%20%E2%80%A2%20KiCad%208&subfontSize=17&subfontColor=d8ecf8)

[![KiCad 8.0](https://img.shields.io/badge/EDA-KiCad_8.0-314CB0?style=for-the-badge&logo=kicad&logoColor=white)](https://kicad.org)
[![CMRR](https://img.shields.io/badge/CMRR-%3E100_dB_@_50Hz-darkgreen?style=for-the-badge)](https://github.com/yotova/unipa-bioamp-pro)
[![DRL](https://img.shields.io/badge/DRL-Active_Common--Mode_Drive-blue?style=for-the-badge)](https://github.com/yotova/unipa-bioamp-pro)
[![Fabrication](https://img.shields.io/badge/Gerbers-RS--274X_Verified-008080?style=for-the-badge)](https://github.com/yotova/unipa-bioamp-pro/tree/main/gerbers)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

<p align="center">
  <b>Engineered by Mustafa Yağcı (<a href="https://github.com/yotova">@yotova</a>)</b><br/>
  <i>M.Sc. Electronic Engineering — Università degli Studi di Palermo (UniPa)</i>
</p>

</div>

---

## 📌 Executive Overview

**UniPa BioAmp Pro** is an open-source, laboratory-grade, low-noise **Biopotential Analog Front-End (AFE)** engineered in **KiCad 8**. Designed for recording electrophysiological biopotentials (**ECG, EMG, EEG, EOG**), it resolves the primary physical challenge of biological measurements: extracting microvolt-level differential biosignals ($\sim 10\,\mu	ext{V} - 5\,	ext{mV}$) in the presence of severe common-mode environmental interference (up to several volts of 50/60 Hz mains displacement current).

Compared to conventional single-ended educational boards, **UniPa BioAmp Pro** implements an industrial-grade **Driven Right Leg (DRL)** active feedback loop, a high-order active bandpass filtering chain, a tunable Twin-T notch filter, and a low-impedance ADC-driver stage.

```
+----------------------------------------------------------------------------------------------------+
|                                      SIGNAL CHAIN ARCHITECTURE                                     |
+----------------------------------------------------------------------------------------------------+

   [ VIN+ (IN1) ] ──> [ R-C RF Filter ] ──┐
                                          ├──> [ Instrumentation Amp ] ──> [ Active HPF ] ──┐
   [ VIN- (IN2) ] ──> [ R-C RF Filter ] ──┘          (INA128 / AD620)         (fc = 0.5 Hz)  │
                                                            │                               │
                                                     [ CM Sense ]                           ▼
                                                            │                         [ Active LPF ]
                                                            ▼                         (fc = 150 Hz)
   [ REF (DRL)  ] <── [ Phase-Lead Loop ] <── [ DRL Inverting Amp ]                         │
                                                                                            ▼
                                                                                   [ Twin-T Notch ]
                                                                                     (50 Hz / Q=10)
                                                                                            │
                                                                                            ▼
   [ ADC_OUT    ] <────────────────────────────────────────────────────── [ Rail-to-Rail Buffer ]
```

---

## ⚡ Technical Specifications

| Parameter | Specification | Notes / Operating Condition |
| :--- | :--- | :--- |
| **Target Biosignals** | ECG, EMG, EEG, EOG | Selectable filter corner frequencies via passive networks |
| **Common-Mode Rejection (CMRR)** | **> 100 dB** @ 50/60 Hz | Laser-trimmed internal thin-film resistor matching |
| **Active Noise Suppression** | **Driven Right Leg (DRL)** | Active phase-inverted common-mode return electrode |
| **Input Impedance ($Z_{in}$)** | **$10^{10}\,\Omega \parallel 3\,	ext{pF}$** | Minimizes electrode-skin impedance mismatch degradation |
| **Bandpass Bandwidth** | **0.5 Hz – 150 Hz** (ECG Mode) | 2nd-order active high-pass + 2nd-order active low-pass |
| **Mains Notch Attenuation** | **> -40 dB** @ 50 Hz | Active Twin-T notch with feedback Q-enhancement |
| **Overall Voltage Gain ($A_v$)** | **$1000	imes$ (60 dB)** | $A_{v1} = 10	imes$ (In-Amp) + $A_{v2} = 100	imes$ (Active Filter) |
| **Supply Voltage ($V_{DD} / V_{SS}$)** | $\pm 3.3	ext{V}$ to $\pm 5.0	ext{V}$ (or single 5V via rail splitter) | Ultra-low ripple LDO regulation recommended |
| **Output Dynamic Range** | 0 to $V_{ref}$ (0 – 3.3V / 0 – 5V) | DC-biased to $V_{DD}/2$ for unipolar microcontroller ADCs |
| **Form Factor & PCB Layout** | 2-Layer / 4-Layer Mixed Signal | Solid ground return plane, guarded high-impedance input traces |

---

## 🔬 Circuit Theory & Engineering Innovations

### 1. High-CMRR Instrumentation Stage
The frontend employs a three-op-amp instrumentation amplifier topology:
$$V_{out1} = \left( 1 + rac{2 R_1}{R_G} ight) (V_{IN+} - V_{IN-})$$
By keeping first-stage gain modest ($A_{v1} pprox 10$), the circuit preserves large common-mode headroom without saturating the rails under large DC half-cell electrode potentials ($\pm 300\,	ext{mV}$).

### 2. Driven Right Leg (DRL) Active Feedback
Mains power displacement currents ($i_{disp}$) capacitively couple from 230V/110V room wiring into the human body, inducing common-mode voltage $V_{cm} = i_{disp} \cdot Z_{body}$. Instead of grounding the patient directly:
1. The common-mode signal is sensed from the center tap of the differential input buffer.
2. An auxiliary op-amp inverts and amplifies this common-mode error:
   $$V_{DRL} = - A_{DRL} \cdot V_{cm}$$
3. The signal is injected back to the body via the reference electrode, actively suppressing common-mode potential by a factor of $(1 + A_{DRL})$ (typically 30 dB to 40 dB additional attenuation).

### 3. Sallen-Key 4-Pole Filtering
- **High-Pass Cutoff ($f_{HP} = 0.5\,	ext{Hz}$):** Rejects electrode half-cell polarization potential and patient respiration baseline drift.
- **Low-Pass Cutoff ($f_{LP} = 150\,	ext{Hz}$):** Suppresses electrosurgical noise and high-frequency RF interference beyond the diagnostic ECG bandwidth.

---

## 📂 Repository Structure

```
unipa-bioamp-pro/
├── hardware/                                # Complete KiCad 8 Project Suite
│   ├── UniPa_BioAmp_Pro.kicad_pro           # KiCad project master
│   ├── UniPa_BioAmp_Pro.kicad_sch           # Complete schematic design
│   ├── UniPa_BioAmp_Pro.kicad_pcb           # PCB layout & routing
│   ├── UniPa_BioAmp_Pro.net                 # Generated netlist
│   ├── UniPa_BioAmp_Pro.step                # 3D CAD mechanical model
│   └── UniPa_BioAmp_Pro.rpt                 # Design Rule Check (DRC) report
├── gerbers/                                 # Manufacturing Package (RS-274X)
│   ├── UniPa_BioAmp_Pro-F_Cu.gtl            # Top Copper Layer
│   ├── UniPa_BioAmp_Pro-B_Cu.gbl            # Bottom Copper Layer
│   ├── UniPa_BioAmp_Pro-F_Mask.gts          # Top Solder Mask
│   ├── UniPa_BioAmp_Pro-B_Mask.gbs          # Bottom Solder Mask
│   ├── UniPa_BioAmp_Pro-F_Silkscreen.gto    # Top Silkscreen Legend
│   ├── UniPa_BioAmp_Pro-Edge_Cuts.gm1       # Board Outline & Edge Cuts
│   └── UniPa_BioAmp_Pro.drl                 # Excellon NC Drill File
├── docs/                                    # Technical Reports & Design Guides (PDF)
│   ├── UniPa_BioAmp_Pro_Sifirdan_AFE_Muhendislik_Rehberi.pdf
│   ├── UniPa_BioAmp_Pro_Komponent_Secimi_ve_Hesaplamalari.pdf
│   ├── UniPa_BioAmp_Pro_vs_BioAmp_EXG_Pill_Karsilastirma_Raporu.pdf
│   ├── UniPa_BioAmp_Pro_Schematic.pdf
│   └── UniPa_BioAmp_Pro_PCB.pdf
├── assets/                                  # Visualizations & SVG Circuit Diagrams
│   ├── UniPa_BioAmp_Pro_PCB.svg
│   └── UniPa_BioAmp_Pro_Schematic.svg
└── scripts/                                 # Verification & Geometric Checking Scripts
    ├── build_schematic.py
    ├── build_full_pcb.py
    ├── clean_router.py
    └── verify_wiring.py
```

---

## 🛠️ Fabrication & Assembly (JLCPCB / PCBWay)

The manufacturing files in `gerbers/` are 100% production-ready:
1. Download or clone this repository:
   ```bash
   git clone https://github.com/yotova/unipa-bioamp-pro.git
   ```
2. Compress the contents of the `gerbers/` folder into `UniPa_BioAmp_Pro_Gerber.zip`.
3. Upload to your preferred PCB fabricator (**JLCPCB**, **PCBWay**, **OSH Park**).
4. Recommended PCB specs:
   - **Layers:** 2 or 4 Layers
   - **PCB Thickness:** 1.6 mm
   - **Copper Weight:** 1 oz (35 µm)
   - **Surface Finish:** ENIG (Electroless Nickel Immersion Gold) recommended for biopotential signal integrity.

---

## 📊 Comprehensive Comparison: UniPa BioAmp Pro vs Commercial Educational Kits

| Feature | Generic Educational Boards (e.g., BioAmp EXG Pill) | **UniPa BioAmp Pro** (This Project) |
| :--- | :--- | :--- |
| **Frontend Architecture** | Quad Op-Amp (TL074) Discrete Differential | **Precision Laser-Trimmed In-Amp (INA128 / AD620)** |
| **Guaranteed CMRR** | $\sim 60 - 70\,	ext{dB}$ (Resistor tolerance limited) | **$\mathbf{> 100\,	ext{dB}}$** (High-precision differential rejection) |
| **Mains Suppression** | Passive ground reference only | **Active Driven Right Leg (DRL) closed loop** |
| **Notch Filtering** | Digital DSP post-processing required | **On-board Active Twin-T 50/60 Hz Notch Stage** |
| **Input Guarding** | Standard trace routing | **Guarded input rings preventing surface leakage** |
| **Dynamic Range** | Prone to rail saturation on electrode motion | **Multi-stage AC coupling prevents DC drift** |

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for full details. Open for academic research, medical instrumentation development, and educational applications.

---

## 📬 Contact & Inquiries

- **Author:** Mustafa Yağcı ([@yotova](https://github.com/yotova))
- **Email:** [mrmustafayagci@gmail.com](mailto:mrmustafayagci@gmail.com)
- **Institution:** Università degli Studi di Palermo (UniPa), Palermo, Italy
