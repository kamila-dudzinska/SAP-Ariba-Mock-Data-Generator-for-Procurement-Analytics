# -*- coding: utf-8 -*-
"""
Created on Sat Jun 20 20:00:27 2026

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

# RANDOM SEED
random.seed(42)

# GENERATED DATA FOR FURTHER ACTIONS
# company codes - created manually basing on my work expierience
company_codes = ["A001", "A002", "B001", "B002", "CH01", "CH02", "D001", "D002", "D003", "D004", "N001", "F001", "F002", "F003", "S001", "S002"]

#created by copilot basing on the rules in attched excel file
suppliers = {
    20401: "Adecco sp. z o. o.",
    20402: "BluePrint SA",
    20403: "Lila",
    20404: "Pedro",
    20405: "Januszex sp. z o. o.",
    20406: "Tech Solutions",
    20407: "Green Energy",
    20408: "Fast Logistics",
    20409: "Alpha Systems",
    20410: "Blue Ocean",
    20411: "Silverline",
    20412: "NextGen",
    20413: "Bright Future",
    20414: "Global Trade",
    20415: "Sunrise Corp",
    20416: "Kraftwerk GmbH",
    20417: "Bauhaus AG",
    20418: "Müller & Söhne",
    20419: "Schmidt GmbH",
    20420: "Weber AG",
    20421: "Fischer GmbH",
    20422: "NovaTech",
    20423: "EcoSmart",
    20424: "Urban Solutions",
    20425: "Pioneer Co.",
    20426: "Summit Industries",
    20427: "Quantum Corp",
    20428: "Visionary Ltd.",
    20429: "Everest Supplies",
    20430: "BlueSky",
    20431: "Ironclad",
    20432: "Nimbus",
    20433: "Crescent",
    20434: "Falcon",
    20435: "Atlas",
    20436: "Vanguard",
    20437: "Harbor",
    20438: "Legacy",
    20439: "Summit",
    20440: "Zenith",
    20441: "Pinnacle",
    20442: "Stratus",
    20443: "Nimbus",
    20444: "Echo",
    20445: "Solstice",
    20446: "Aurora",
    20447: "Celestial",
    20448: "Nimbus",
    20449: "Helios",
    20450: "Lumen",
    20451: "Orion",
    20452: "Vortex",
    20453: "BlueWave sp. z o. o.",
    20454: "IronGate sp. z o. o.",
    20455: "ClearWater sp. z o. o.",
    20456: "NextLevel sp. z o. o.",
    20457: "BrightStar sp. z o. o.",
    20458: "Skyline sp. z o. o.",
    20459: "EverGreen sp. z o. o.",
    20460: "MountainPeak sp. z o. o.",
    20461: "Oceanic sp. z o. o.",
    20462: "SilverStone sp. z o. o.",
    20463: "CrystalClear sp. z o. o.",
    20464: "RapidFlow sp. z o. o.",
    20465: "TrueNorth sp. z o. o.",
    20466: "BlueHorizon sp. z o. o.",
    20467: "Sunset sp. z o. o.",
    20468: "IronClad sp. z o. o.",
    20469: "StormRider sp. z o. o.",
    20470: "CloudNine sp. z o. o.",
    20471: "BrightPath sp. z o. o.",
    20472: "GoldenGate sp. z o. o.",
    20473: "NordicTech GmbH",
    20474: "Bergmann AG",
    20475: "Schneider & Sohn",
    20476: "Fischer GmbH",
    20477: "Weiss AG",
    20478: "Albatros SA",
    20479: "Bison SA",
    20480: "Cobra SA",
    20481: "Delta SA",
    20482: "Eagle SA"
}

#created by copilot basing on the rules in attched excel file (module re)
users = [
    {"Requestor_ID": "PLANNMAC", "Name": "Anna Maciejewska", "Mail": "anna.maciejewska@firma.com"},
    {"Requestor_ID": "PLJANNOW", "Name": "Jan Nowak", "Mail": "jan.nowak@firma.com"},
    {"Requestor_ID": "PLEWAZIE", "Name": "Ewa Zielinska", "Mail": "ewa.zielinska@firma.com"},
    {"Requestor_ID": "PLPIWONO", "Name": "Piotr Wozniak", "Mail": "piotr.wozniak@firma.com"},
    {"Requestor_ID": "PLKAMAZU", "Name": "Katarzyna Mazur", "Mail": "katarzyna.mazur@firma.com"},
    {"Requestor_ID": "PLMIWISI", "Name": "Michał Wiśniewski", "Mail": "michal.wisniewski@firma.com"},
    {"Requestor_ID": "PLAGNNO", "Name": "Agnieszka Nowak", "Mail": "agnieszka.nowak@firma.com"},
    {"Requestor_ID": "PLTOZIE", "Name": "Tomasz Zieliński", "Mail": "tomasz.zielinski@firma.com"},
    {"Requestor_ID": "PLMOLEW", "Name": "Monika Lewandowska", "Mail": "monika.lewandowska@firma.com"},
    {"Requestor_ID": "PLPAKAC", "Name": "Paweł Kaczmarek", "Mail": "pawel.kaczmarek@firma.com"},
    {"Requestor_ID": "PLKIWOJ", "Name": "Kinga Wójcik", "Mail": "kinga.wojcik@firma.com"},
    {"Requestor_ID": "PLLUKAM", "Name": "Łukasz Kamiński", "Mail": "lukasz.kaminski@firma.com"},
    {"Requestor_ID": "PLNASZY", "Name": "Natalia Szymańska", "Mail": "natalia.szymanska@firma.com"},
    {"Requestor_ID": "PLJADUD", "Name": "Jakub Duda", "Mail": "jakub.duda@firma.com"},
    {"Requestor_ID": "PLMAPAW", "Name": "Magdalena Pawlak", "Mail": "magdalena.pawlak@firma.com"},
    {"Requestor_ID": "PLMARKRA", "Name": "Marcin Krawczyk", "Mail": "marcin.krawczyk@firma.com"},
    {"Requestor_ID": "PLBANO", "Name": "Barbara Nowicka", "Mail": "barbara.nowicka@firma.com"},
    {"Requestor_ID": "PLGRWRO", "Name": "Grzegorz Wrona", "Mail": "grzegorz.wrona@firma.com"},
    {"Requestor_ID": "PLJOLIS", "Name": "Joanna Lis", "Mail": "joanna.lis@firma.com"},
    {"Requestor_ID": "PLDASZA", "Name": "Dariusz Zając", "Mail": "dariusz.zajac@firma.com"},
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

start_date = datetime.strptime("2026-01-01", "%Y-%m-%d")
end_date = datetime.strptime("2026-04-30", "%Y-%m-%d")
today = datetime.today()
# do daty początkowej dodajemy randomową liczbę dni z przedziału (data końcowa -data początkowa)
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












