# -*- coding: utf-8 -*-
"""
Created on Sat Jun 20 20:00:27 2026
Extended on Thu Oct 22 19:05:20 2026
Extended on Sat Oct 31 20:11:59 2026

@author: Kamila Dudzińska

Dataset: Procurement Department 
Contain: Data from SAP Ariba - Material POs
Characteristics: 2500 records,
                 outliers 0,01%, 
                 null values: 0,02%
Goal:   script created for procurement specialist and expert, who want to train 
        data analysis skills in Python/Pandas. 

"""


# %%
# IMPORT MODULES
import csv
import random
from datetime import datetime, timedelta
from procurement_mock_functions import validate_records

# RANDOM SEED
random.seed(42)

# GENERATED DATA FOR FURTHER ACTIONS
# company codes - created manually basing on my work expierience
company_codes = ["A001", "A002", "B001", "B002", "CH01", "CH02", "D001", "D002", "D003", "D004", "N001", "F001", "F002", "F003", "S001", "S002"]

# created by copilot basing on --> regex - always 10 digits
suppliers = {
    2004839201: "Adecco sp. z o. o.",
    2001297744: "BluePrint SA",
    2005938472: "Lila",
    2002846619: "Pedro",
    2009183340: "Januszex sp. z o. o.",
    2007745128: "Tech Solutions",
    2006629183: "Green Energy",
    2003374920: "Fast Logistics",
    2008457712: "Alpha Systems",
    2001183499: "Blue Ocean",
    2009927344: "Silverline",
    2004412870: "NextGen",
    2007139044: "Bright Future",
    2005578219: "Global Trade",
    2006291180: "Sunrise Corp",
    2007740033: "Kraftwerk GmbH",
    2008894412: "Bauhaus AG",
    2003319077: "Müller & Söhne",
    2006674921: "Schmidt GmbH",
    2002245190: "Weber AG",
    2009910044: "Fischer GmbH",
    2001138455: "NovaTech",
    2007746621: "EcoSmart",
    2005591188: "Urban Solutions",
    2008823410: "Pioneer Co.",
    2006619923: "Summit Industries",
    2004477129: "Quantum Corp",
    2003390041: "Visionary Ltd.",
    2007745510: "Everest Supplies",
    2006620033: "BlueSky",
    2005579912: "Ironclad",
    2008890021: "Nimbus",
    2003317744: "Crescent",
    2006675519: "Falcon",
    2002246610: "Atlas",
    2009917711: "Vanguard",
    2001139922: "Harbor",
    2007748820: "Legacy",
    2005597741: "Summit",
    2008826612: "Zenith",
    2006614477: "Pinnacle",
    2004475510: "Stratus",
    2003398821: "Nimbus",
    2007741199: "Echo",
    2006627740: "Solstice",
    2005573311: "Aurora",
    2008896612: "Celestial",
    2003315510: "Nimbus",
    2006678821: "Helios",
    2002247744: "Lumen",
    2009915512: "Orion",
    2001137740: "Vortex",
    2007743319: "BlueWave sp. z o. o.",
    2005596610: "IronGate sp. z o. o.",
    2008827741: "ClearWater sp. z o. o.",
    2006615512: "NextLevel sp. z o. o.",
    2004477744: "BrightStar sp. z o. o.",
    2003396611: "Skyline sp. z o. o.",
    2007748822: "EverGreen sp. z o. o.",
    2006623310: "MountainPeak sp. z o. o.",
    2005577741: "Oceanic sp. z o. o.",
    2008895512: "SilverStone sp. z o. o.",
    2003317749: "CrystalClear sp. z o. o.",
    2006676611: "RapidFlow sp. z o. o.",
    2002248822: "TrueNorth sp. z o. o.",
    2009913310: "BlueHorizon sp. z o. o.",
    2001137741: "Sunset sp. z o. o.",
    2007745512: "IronClad sp. z o. o.",
    2005597744: "StormRider sp. z o. o.",
    2008826611: "CloudNine sp. z o. o.",
    2006618822: "BrightPath sp. z o. o.",
    2004473310: "GoldenGate sp. z o. o.",
    2003397741: "NordicTech GmbH",
    2007746612: "Bergmann AG",
    2006625510: "Schneider & Sohn",
    2005578822: "Fischer GmbH",
    2008893310: "Weiss AG",
    2003318821: "Albatros SA",
    2006677744: "Bison SA",
    2002246611: "Cobra SA",
    2009918822: "Delta SA",
    2001135510: "Eagle SA"
}

#created by copilot +  @example.com - test domain (changed 31.10.2026)
users = [
    {"Requestor_ID": "PLANNMAC", "Name": "Anna Maciejewska", "Mail": "anna.maciejewska@example.com"},
    {"Requestor_ID": "PLJANNOW", "Name": "Jan Nowak", "Mail": "jan.nowak@example.com"},
    {"Requestor_ID": "PLEWAZIE", "Name": "Ewa Zielinska", "Mail": "ewa.zielinska@example.com"},
    {"Requestor_ID": "PLPIWONO", "Name": "Piotr Wozniak", "Mail": "piotr.wozniak@example.com"},
    {"Requestor_ID": "PLKAMAZU", "Name": "Katarzyna Mazur", "Mail": "katarzyna.mazur@example.com"},
    {"Requestor_ID": "PLMIWISI", "Name": "Michał Wiśniewski", "Mail": "michal.wisniewski@example.com"},
    {"Requestor_ID": "PLAGNNO", "Name": "Agnieszka Nowak", "Mail": "agnieszka.nowak@example.com"},
    {"Requestor_ID": "PLTOZIE", "Name": "Tomasz Zieliński", "Mail": "tomasz.zielinski@example.com"},
    {"Requestor_ID": "PLMOLEW", "Name": "Monika Lewandowska", "Mail": "monika.lewandowska@example.com"},
    {"Requestor_ID": "PLPAKAC", "Name": "Paweł Kaczmarek", "Mail": "pawel.kaczmarek@example.com"},
    {"Requestor_ID": "PLKIWOJ", "Name": "Kinga Wójcik", "Mail": "kinga.wojcik@example.com"},
    {"Requestor_ID": "PLLUKAM", "Name": "Łukasz Kamiński", "Mail": "lukasz.kaminski@example.com"},
    {"Requestor_ID": "PLNASZY", "Name": "Natalia Szymańska", "Mail": "natalia.szymanska@example.com"},
    {"Requestor_ID": "PLJADUD", "Name": "Jakub Duda", "Mail": "jakub.duda@example.com"},
    {"Requestor_ID": "PLMAPAW", "Name": "Magdalena Pawlak", "Mail": "magdalena.pawlak@example.com"},
    {"Requestor_ID": "PLMARKRA", "Name": "Marcin Krawczyk", "Mail": "marcin.krawczyk@example.com"},
    {"Requestor_ID": "PLBANO", "Name": "Barbara Nowicka", "Mail": "barbara.nowicka@example.com"},
    {"Requestor_ID": "PLGRWRO", "Name": "Grzegorz Wrona", "Mail": "grzegorz.wrona@example.com"},
    {"Requestor_ID": "PLJOLIS", "Name": "Joanna Lis", "Mail": "joanna.lis@example.com"},
    {"Requestor_ID": "PLDASZA", "Name": "Dariusz Zając", "Mail": "dariusz.zajac@example.com"},
]


# percentage of statuses in dataset - basing on my real life expierience
status_choices = ["ordered"] * 30 + ["confirmed"] * 8 + ["received"] * 22 + ["invoiced"] * 27 + ["canceled"] * 3

# percentage of cureency_codes - basing on my real life expierience
currency_choices = ["EUR"] * 60 + ["CHF"] * 12 + ["GBP"] * 8 + ["PLN"] * 20

#amount range % percentage in dataset
amount_ranges = [
    (0, 999, 40),
    (1000, 10000, 26),
    (10001, 20000, 13),
    (20001, 50000, 5),
    (50001, 70000, 9),
    (70001, 80000, 3.079),
    (80001, 1000000, 0.001),  
    (250001, 250001, 0.02)  
]

# FUNCTIONS
# calculate weights for data choices for amount_ranges
def weighted_choice(choices):
    '''
    Calculates the order amount taking business weights into account. 
    Most orders are low-budget orders (tactical sourcing).
    '''
    
    total = sum(w for _, _, w in choices)
    r = random.uniform(0, total)                #floating-point number from zero to total
    upto = 0                                    #upto = counter
    #  dolny zakres, górny zakres, waga
    for low, high, weight in choices:           
        if upto + weight >= r:                  #check the range for weight
            if low == high:                     
                return low                      
            return random.randint(low, high)    #return low and high
        upto += weight
    return choices[-1][1]


# generate PO number
def generate_po_number(existing:int) -> int:
    '''
    Generates an order number in the range 6000000000 - 6000999999, 
    according to the SAP ARIBA standard.
    '''
    while True:
        num = random.randint(6000000000, 6000999999)
        if num not in existing:
            return num
        
# generate delivery date
def generate_delivery_date(creation_date:datetime, today:datetime) -> datetime:
    '''
    Randomly generates a delivery date based on the create date and PT 
    within a range of up to 90 days.
    '''
    random_days = random.randint(1, 90)
    delivery_date = creation_date + timedelta(days=random_days)
    if delivery_date >today:
        return None
    return delivery_date.strftime("%Y-%m-%d")
    

# DATA CREATION
existing_po = set()             #emoty set
records = []                    #empty lists

# date range - today() - shows default and fresh data
today = datetime.today()
start_date = today - timedelta(days=365)
end_date = today
# random date 
creation_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))

#MAIN LOOP
if __name__ =="__main__":
    print("I'm starting to generate data for the SAP Ariba report")
    
    for _ in range(2500):
        po_number = generate_po_number(existing_po)
        existing_po.add(po_number)

        company_code = random.choice(company_codes)
        
        #choose a random.choice() from keys()
        supplier_number = random.choice(list(suppliers.keys()))
        supplier_name = suppliers[supplier_number]
    
        user = random.choice(users)
        
        #from starting date we add the date from range(end_date - start_date)
        creation_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
        
        # to creation_date add a number of days from range (1,90)
        delivery_date = generate_delivery_date(creation_date, today)
        
    
        status = random.choice(status_choices)
        amount = weighted_choice(amount_ranges)
        currency = random.choice(currency_choices)
    
        record = {
            "PO Number": po_number,
            "Company Code": company_code,
            "Supplier ID": supplier_number,
            "Supplier Name": supplier_name,
            "Requester ID": user["Requestor_ID"],
            "Requester Name": user["Name"],
            "Requester Mail": user["Mail"],
            "Create Date": creation_date.strftime("%Y-%m-%d"),
            "Delivery Date": delivery_date,
            "Order Status": status,
            "Amount": amount,
            "Currency": currency
        }
        records.append(record)

    # DATA VALIDATION - every record checked with regex
    validation_errors = validate_records(records)
    if validation_errors:
        print("Validation: some values do not match the rules:")
        for field, count in validation_errors.items():
            print(f"  {field}: {count} record(s)")
    else:
        print(f"Validation OK: all {len(records)} records match the regex rules.")

    # write csv
    with open("procurement_mock_2500.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["PO Number", 
                                                  "Company Code", 
                                                  "Supplier ID", 
                                                  "Supplier Name", 
                                                  "Requester ID", 
                                                  "Requester Name", 
                                                  "Requester Mail", 
                                                  "Create Date", 
                                                  "Delivery Date", 
                                                  "Order Status", 
                                                  "Amount", 
                                                  "Currency"], delimiter=';')
        writer.writeheader()
        for rec in records:
            writer.writerow(rec)            #write for a row
    
    print("Generated the file procurement_mock_2500.csv with 2500 records.")












