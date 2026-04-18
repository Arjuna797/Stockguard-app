

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

RAW_DATA = """
Piezoelectric Accelerometer: Measures how much a car part vibrates.
K-Type Thermocouple: A heavy-duty wire that measures extreme heat, like inside an exhaust pipe.
Dynamic Strain Gauge: A sticker that detects if metal is bending or stretching.
Pitot Tube: A small pipe used to measure the speed of air flowing over the car.
NOx Sensor: Measures the amount of harmful nitrogen oxide in the exhaust.
O2 Oxygen Sensor: Checks if the fuel is burning efficiently.
Rotary Encoder: Measures the exact angle and speed of a spinning wheel.
Load Cell: An electronic scale that measures weight or heavy crushing forces.
Hall Effect Sensor: Uses magnets to measure how fast a gear or shaft is spinning.
Microphone (Free Field): Records engine and wind noise inside a quiet room.
Acoustic Emission Sensor: "Hears" microscopic cracks forming in metal before it breaks.
Optical RPM Sensor: Uses a laser to count engine revolutions.
Crash Test Dummy Decal: High-contrast stickers used as targets for high-speed cameras.
LVDT (Linear Transducer): Measures tiny, microscopic physical movements in suspension.
Mass Air Flow Sensor: Measures how much air the engine is "breathing" in.
Torque Transducer: Measures the twisting force of the engine or drive shaft.
Laser Displacement Sensor: Measures distance to a part without physically touching it.
Pressure Transducer: Measures the pressure of fluids or gases, like inside a brake line.
Humidity Sensor: Monitors the moisture in the air inside climate-controlled test chambers.
Proximity Sensor: Detects when a moving metal object gets too close.
Standardized Unleaded Gasoline: Very pure, consistent fuel used to get baseline test results.
Reference Diesel Fuel: Standardized diesel used specifically for emission testing.
E85 Ethanol Blend: Used to test cars running on alternative fuels.
5W-30 Synthetic Engine Oil: Standard lubrication for general engine running tests.
DOT 4 Brake Fluid: Used to test hydraulic braking systems.
Premixed Radiator Coolant: Keeps engines at the exact right temperature during testing.
Windshield Washer Fluid: Used for testing wiper blade durability and spray nozzles.
Dynamometer Calibration Oil: Special oil that keeps the large testing machines running smoothly.
Isopropyl Alcohol 99%: Used to clean electronic contacts and sensors without leaving residue.
Span Gas Cylinder (CO2): A tank of pure gas used to calibrate emission-reading machines.
Zero Gas Cylinder (Nitrogen): A tank of pure gas used to reset emission machines to zero.
Thread Locker (Blue): Liquid glue that keeps bolts from vibrating loose during tests.
Anti-Seize Compound: Paste that prevents hot metal parts from rusting together.
Dielectric Grease: Protects electrical connections from water and dirt.
Penetrating Fluid: Spray used to loosen rusted or stuck test parts.
BNC Coaxial Cable: The standard black cable used to plug sensors into computers.
CAN Bus Connector: Plugs directly into the car's brain to read its internal data.
OBD-II Extension Cable: Lengthens the reach of the car's diagnostic port.
Banana Plugs: Quick-connect pins for multimeters and electrical testers.
Ethernet Cable (Cat6): Connects the various testing computers in the lab.
Fiber Optic Cable: Sends massive amounts of sensor data instantly without electrical interference.
Heat Shrink Tubing: Rubber tubes that shrink with heat to seal wire connections.
12V Automotive Relay: An electrical switch that handles heavy power loads safely.
Blade Fuse (10A): Protects testing equipment from electrical surges.
Copper Grounding Strap: Prevents dangerous static electricity buildup on test rigs.
Multicore Shielded Cable: A thick wire that blocks outside electrical noise from ruining data.
Alligator Clips: Spring-loaded clamps for making temporary electrical connections.
USB to RS232 Adapter: Lets old testing sensors plug into modern laptops.
Thermocouple Extension Wire: Extra wire to reach from a hot exhaust pipe back to the computer.
High-Temp Zip Ties: Plastic ties that won't melt when organizing wires near a hot engine.
10mm Hex Bolt: The most common bolt used to bolt things together in the lab.
12mm Nylon Lock Nut: A nut with a plastic ring inside so it won't vibrate off.
Stainless Steel Flat Washer: Spreads the pressure of a bolt so it doesn't crush the metal.
Adjustable Hose Clamp: A metal band tightened with a screwdriver to secure fluid hoses.
Deep Groove Ball Bearing: A metal ring with balls inside that lets shafts spin perfectly smoothly.
V-Belt: A rubber belt that drives engine accessories like the alternator.
Serpentine Belt: The main, long rubber drive belt for modern engines.
Engine Mount Isolator: A heavy rubber block that absorbs engine shaking so the rig doesn't rattle.
Quick Release Pneumatic Fitting: Plugs in air hoses instantly, like a garden hose attachment.
Aluminum T-Slot Extrusion: Long metal bars used like adult Legos to build custom test frames.
T-Slot Nuts: Special nuts that slide into the aluminum framing to attach sensors.
Dynamometer Drive Shaft: The heavy metal pole connecting the car's wheels to the testing machine.
Universal Joint (U-Joint): A flexible metal joint that lets drive shafts bend while spinning.
Shock Absorber Spring: Used in rigs that test suspension bouncing.
Brake Rotor Blank: A standard, generic brake disc used purely for testing brake pads.
Sintered Brake Pad Set: A heavy-duty set of brake pads used for baseline stopping tests.
Exhaust Manifold Gasket: A heat-proof seal between the engine block and the exhaust pipe.
Rubber O-Ring Kit: Small rubber circles used to seal fluid connections tight.
High-Pressure Hydraulic Hose: Carries pressurized fluid for heavy-lifting test rigs.
Steel Mounting Bracket: A simple metal elbow used to hold a sensor to a car frame.
Particulate Filter Paper: Special paper that catches exhaust soot so it can be weighed.
Exhaust Extraction Hose: A giant vacuum hose that sucks toxic fumes out of the lab.
Charcoal Canister: A trap filled with carbon that captures evaporating fuel vapors.
Tedlar Gas Sampling Bag: A sterile bag used to capture exhaust gas to analyze later.
Heated Sample Line: A warm tube that stops water from condensing inside exhaust gas samples.
Silica Gel Packets: Put inside sealed test boxes to suck out all the moisture.
Weatherometer UV Lamp: A super-bright bulb that simulates years of damaging sunlight in weeks.
Salt Spray Testing Brine: A specific saltwater mix used to see how fast a car part rusts.
Arizona Dust (Standardized): Real desert dust used to test how quickly air filters clog.
Defrosting Element: A heater that keeps cold-test chambers from turning into solid ice.
Ozone Generator Bulb: Creates smog-like gas to test how quickly rubber tires rot.
Acoustic Foam Panel: Spiky foam squares that line the walls of quiet rooms to kill echoes.
Exhaust Tailpipe Adapter: A rubber cone that connects any car's tailpipe to the lab's exhaust system.
Catalytic Converter Core: The honeycomb-like center of an exhaust cleaner.
Diesel Exhaust Fluid (DEF): A fluid injected into diesel exhausts to break down bad emissions.
High-Visibility Safety Vest: Neon vests so testers aren't hit by moving vehicles in the lab.
Nitrile Lab Gloves: Disposable gloves that protect hands from fuel and oil.
Kevlar Heat Gloves: Thick gloves worn when handling piping hot exhaust parts.
Ear Protection Muffs: Heavy headphones that block out the deafening roar of engine testing.
Anti-Fog Safety Goggles: Glasses that protect eyes from flying metal and don't fog up when sweating.
Fire Extinguisher (Class B/C): Specifically designed to put out gas, oil, and electrical fires.
Oil Spill Absorbent Pad: A sponge-like mat thrown on the floor to soak up leaked test fluids.
Lockout/Tagout Padlock: A lock put on a machine's power switch so nobody turns it on during repairs.
Calibration Due Label: Small stickers put on tools so engineers know when they are too old to trust.
First Aid Burn Dressing: Special gel bandages for accidental burns from hot engines.
Hazardous Waste Disposal Bag: Special bags for throwing away toxic rags and leftover chemicals.
Antistatic Wrist Strap: Worn by engineers so they don't accidentally shock and break delicate electronics.
Yellow/Black Caution Tape: Used on the floor to mark dangerous zones around spinning testing rigs.
Lithium-Ion Battery Fire Blanket: A massive fireproof blanket used to smother electric vehicle battery fires.
Eye Wash Station Saline: Sterile saltwater used to flush chemicals out of an engineer's eyes
"""

def generate_synthetic_data(output_path):
    np.random.seed(42)
    end_date = datetime.today().date()
    start_date = end_date - timedelta(days=730)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    plants = ['P100', 'P200', 'P300']
    materials = []
    
    # Parse the RAW_DATA
    import re
    lines = RAW_DATA.strip().split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        if ':' in line:
            parts = line.split(':', 1)
            name = parts[0].strip()
            desc = parts[1].strip()
        else:
            name = line
            desc = "Automotive lab testing material."
            
        mat_id = f"MAT-{(i+1):03d}"
        plant = plants[i % 3] # Distribute evenly
        
        # Simulate characteristics
        if "Bolt" in name or "Nut" in name or "Washer" in name or "Glove" in name or "Cable" in name or "Zip" in name:
            base_qty = np.random.randint(20, 100)
            safe_stock = np.random.randint(500, 2000)
            lead = np.random.randint(2, 7)
            stock = safe_stock + np.random.randint(100, 500)
        elif "Sensor" in name or "Transducer" in name or "Encoder" in name:
            base_qty = np.random.randint(1, 5)
            safe_stock = np.random.randint(10, 50)
            lead = np.random.randint(14, 45)
            stock = safe_stock + np.random.randint(0, 20)
        elif "Gasoline" in name or "Fluid" in name or "Oil" in name or "Brine" in name:
            base_qty = np.random.randint(10, 30) # Liters/Gallons
            safe_stock = np.random.randint(100, 300)
            lead = np.random.randint(7, 21)
            stock = safe_stock + np.random.randint(20, 100)
        else:
            base_qty = np.random.randint(2, 15)
            safe_stock = np.random.randint(20, 100)
            lead = np.random.randint(5, 30)
            stock = safe_stock + np.random.randint(10, 50)
            
        materials.append({
            'id': mat_id, 'name': name, 'desc': desc, 'plant': plant,
            'base_qty': base_qty, 'safe_stock': safe_stock, 'lead': lead, 'stock': float(stock)
        })
        
    records = []
    
    print(f"Generating 2 years of granular data for {len(materials)} materials... this may take 15-30 seconds.")
    
    for mat in materials:
        for date in date_range:
            month = date.month
            season_multiplier = 1.2 if month in [11, 12, 1, 2] else 1.0
            
            daily_qty = int(np.random.normal(loc=mat['base_qty'], scale=mat['base_qty']*0.3) * season_multiplier)
            
            if np.random.rand() < 0.2:
                daily_qty = 0
            daily_qty = max(0, daily_qty)
            
            records.append({
                'Posting_Date': date.strftime('%Y-%m-%d'),
                'Plant_Code': mat['plant'],
                'Material_ID': mat['id'],
                'Material_Name': mat['name'],
                'Material_Description': mat['desc'],
                'Quantity_Consumed': daily_qty,
                'Current_Stock': mat['stock'],
                'Safety_Stock': mat['safe_stock'],
                'Lead_Time_Days': mat['lead']
            })
            
    df = pd.DataFrame(records)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Completed dataset at {output_path} with {len(df)} records.")

if __name__ == "__main__":
    target_path = "data/synthetic_industrial_machine_data.csv"
    generate_synthetic_data(target_path)
