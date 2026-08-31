# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 18:02:37 2026

@author: Kamila Dudzińska

Supporting module with functions

Dataset: Procurement Department 
Contain: Data from SAP Ariba - Material POs
Characteristics: 2500 records,
                 outliers 0,04%, 
                 null values < 0,02%
Goal:   script created for procurement specialist and expert, who want to train 
        data analysis skills in Python/Pandas. The dataset reflects the SAP
        Ariba architecture. 
        
Module with functions
        
"""
# %%
# FUNCTIONS
# IMPORT MODULES
import random
from datetime import datetime, timedelta
import openpyxl
import csv
import pandas as pd

# FUNCTIONS 


def weighted_choice(choices):
    """
    Selects a random value from weighted ranges.
    
    This function calculates the order amount by taking business-defined
    weights into account. It ensures that most orders fall into low-budget
    categories (tactical sourcing), reflecting realistic procurement behavior.
    
    Args:
        choices (list[tuple[int, int, float]]): 
            A list of tuples in the form (low, high, weight), where:
              - low: lower bound of the range
              - high: upper bound of the range
              - weight: probability weight for that range
    
    Returns:
        int: A randomly selected integer within the chosen range.
    
    Example:
        >>> weighted_choice([(100, 500, 0.6), (501, 2000, 0.3), (2001, 10000, 0.1)])
        347
    """
    
    total = sum(w for _, _, w in choices)
    r = random.uniform(0, total)                #floating-point number from zero to total 0.87
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
def generate_po_number(existing_po:int) -> int:
    '''
    Generates an order number in the range 6000000000 - 6000999999, 
    according to the SAP ARIBA standard.

    This function genertes a random PO number from the mentioned range.

    Args:
        existing (list[int]): 
            A list of already generated PO numbers to avoid duplicates.

    Returns:
        int: A unique PO number within the specified range.

    Example:
        >>> existing = [6000000001, 6000000002]
        >>> generate_po_number(existing)
        6000000347
    '''
  
    while True:
        num = random.randint(6000000000, 6000999999)
        if num not in existing_po:
            return num


# generate delivery date
def generate_delivery_date(creation_date:datetime, today:datetime) -> datetime:
    '''
    Randomly generates a delivery date based on the create date and PT 
    within a range of up to 60 days.

    This function randomly selects a delivery date within a range of up to 60 days
    from the creation date. It ensures that the generated date is realistic for
    procurement processes and avoids invalid edge cases.

    Args:
        creation_date (datetime): 
            The date when the purchase order was created.
        today (datetime): 
            The current date used as a reference point for validation.

    Returns:
        datetime | None: 
            A randomly generated delivery date within the allowed range.
            Returns None if the generated date is invalid.

    Example:
        >>> generate_delivery_date(datetime(2026, 3, 1), datetime(2026, 3, 25))
        datetime.datetime(2026, 3, 19, 0, 0)
    '''
    random_days = random.randint(1, 60)
    delivery_date = creation_date + timedelta(days=random_days)
    delivery_date.strftime("%d-%m-%Y")
    if delivery_date == delivery_date + timedelta(days=42):
        return None
    return delivery_date
    

# generate delivery date
def generate_invoice_date(delivery_date: datetime, today: datetime) -> tuple[str | None, int]:
    """
    Randomly generates an invoice date based on the delivery date and PT
    within a range of up to 90 days.
    """
    if delivery_date is None:
        return None, 0

    if isinstance(delivery_date, str):
        delivery_date = datetime.strptime(delivery_date, "%d.%m.%Y")

    payment_terms = random.randint(10, 90)
    invoice_date = delivery_date + timedelta(days=payment_terms)
    invoice_date_str = invoice_date.strftime("%d.%m.%Y")

    return invoice_date_str, payment_terms


def calculate_invoice_amount(amount:float, order_status:str, invoice_status:str) -> float:
    '''
    Return the invoice amount. In 80% it is the same as PO amount (2 way match)
    and in 20% there is a small variation, which needs further clarification.

    Args:
        delivery_date (datetime | str): 
            The delivery date as a datetime object or string in format "%d.%m.%Y".
        today (datetime): 
            The current date used for validation or reference.

    Returns:
        tuple[str | None, int]: 
            A tuple containing:
              - The invoice date formatted as "%d.%m.%Y" (or None if invalid).
              - The payment term in days (integer between 10 and 90).

    Example:
        >>> generate_invoice_date(datetime(2026, 3, 25), datetime(2026, 4, 1))
        ('23.05.2026', 59)
        
    '''
  
    if amount is None or amount <=0:
        return None
    
    #80% zgodne z amount
    if invoice_status != 'hold' and random.random() > 0.20:
        return round(amount, 2)
    elif invoice_status == 'hold' and order_status in ['received', 'ordered']:
        variation = random.uniform(0.80, 1.20)
        return round(amount * variation, 2)
    else:
        return amount
    

def get_order_status(delivery_date: datetime | str | None, today: datetime) -> str:
    """
    Returns order status based on delivery date logic.

    This function evaluates the delivery date and returns a realistic order status
    according to procurement workflow rules. It handles missing, string, and datetime
    inputs, and applies weighted probabilities to simulate real-world status distribution.

    Logic overview:
        1. If delivery date is missing or invalid, returns either "ordered" or "confirmed".
        2. If delivery date is within the last 10 days, returns either "received" or "invoiced".
        3. Otherwise, defaults to "confirmed" or "ordered" based on weighted random choice.

    Args:
        delivery_date (datetime | str | None): 
            The delivery date of the purchase order. Can be a datetime object, 
            a string in format "%d-%m-%Y", or None.
        today (datetime): 
            The current date used as a reference point for comparison.

    Returns:
        str: 
            The simulated order status ("ordered", "confirmed", "received", or "invoiced").

    Example:
        >>> get_order_status(datetime(2026, 8, 10), datetime(2026, 8, 14))
        'received'
        >>> get_order_status(None, datetime(2026, 8, 14))
        'ordered'
    """

    # --- 1. Pusta data dostawy -> tylko "ordered" lub "confirmed"
    if delivery_date is None or delivery_date == "" or str(delivery_date).lower() == "nan":
        return random.choices(
            population=["ordered", "confirmed"],
            weights=[91, 9],
            k=1
        )[0]

    # --- 2. Jeśli mamy string, zamieniamy na datetime
    if isinstance(delivery_date, str):
        delivery_date = datetime.strptime(delivery_date, "%d-%m-%Y")

    # --- 3. Granica 10 dni temu
    ten_days_ago = today - timedelta(days=10)

    # --- 4. Delivery Date w ostatnich 10 dniach (do dziś)
    if ten_days_ago <= delivery_date <= today:
        return random.choices(
            population=["received", "invoiced"],
            weights=[51, 49],
            k=1
        )[0]

    # --- 5. Delivery Date starsza niż 10 dni
    if delivery_date < ten_days_ago:
        return random.choices(
            population=["received", "confirmed", "invoiced"],
            weights=[70, 8, 21],
            k=1
        )[0]

    # --- 6. Delivery Date w przyszłości (awaryjnie)
    return "ordered"


def generate_invoice_number(existing_inv:str) ->str:
    '''
    Generates unique invoice number in the specified format.

    Args:
        existing_inv (list[str]): 
            A list of already generated invoice numbers to avoid duplicates.

    Returns:
        str: 
            A unique invoice number formatted as `FV/YYYY/MM/NNNN`.

    Example:
        >>> existing_inv = ["FV/2026/03/0914", "FV/2026/07/0452"]
        >>> generate_invoice_number(existing_inv)
        'FV/2026/12/0831'
    '''

    while True:
        year = '2026'
        month = f"{random.randint(1,12):02d}"
        random_num = f'{random.randint(1,999):04d}'
        random_inv = f'FV/{year}/{month}/{random_num}' 
        if random_inv not in existing_inv:
            return random_inv
    
    

# %%
# MAIN
# IMPORT MODULES

# GENERATED DATA FOR FURTHER ACTIONS
# company codes - created manually basing on my work expierience
company_codes = ["A001", "A002", "B001", "B002", "CH01", "CH02", "D001", "D002", "D003", "D004", "N001", "F001", "F002", "F003", "S001", "S002"]

#created by copilot basing on the rules in attched excel file
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

# percentage of invoice statuses in dataset:
invoice_choices =['entered']*15 + ['vouched']*18 +['hold']*12 + ['pending approval']*6 + ['approved']*8 + ['selected']*5 +['paid']*30 + ['canceled']*2


#amount range % percentage in dataset
amount_ranges = [
    (0, 990, 40),
    (1000, 10000, 26),
    (10001, 20000, 13),
    (20001, 50000, 5),
    (50001, 70000, 9),
    (70001, 80000, 3.02),
    (80001, 1000000, 0.06),  
    (250001, 250001, 0.02)  
]


# DATA CREATION
existing_po = set()             #emoty set
records = []                    #empty lists
existing_inv = set()

start_date = datetime.strptime("01.01.2026", "%d.%m.%Y")
end_date = datetime.strptime("31.05.2026", "%d.%m.%Y")
today = datetime.today()
# do daty początkowej dodajemy randomową liczbę dni z przedziału (data końcowa -data początkowa)
creation_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))

def generate_mock_data(record_count: int, selected_company_codes: list[str], output_file: str):
    existing_po = set()
    records = []
    start_date = datetime.strptime("2026-01-01", "%Y-%m-%d")
    end_date = datetime.strptime("2026-04-30", "%Y-%m-%d")
    today = datetime.today()

    for _ in range(record_count):
        po_number = generate_po_number(existing_po)
        existing_po.add(po_number)

        company_code = random.choice(selected_company_codes)
        supplier_number = random.choice(list(suppliers.keys()))
        supplier_name = suppliers[supplier_number]
        user = random.choice(users)

        creation_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
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

    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, 
                                fieldnames=list(records[0].keys()), 
                                delimiter=';')
        writer.writeheader()
        for rec in records:
            writer.writerow(rec)

    return output_file





#MAIN LOOP
if __name__ =="__main__":
    print("I'm starting to generate data for the SAP Ariba report")
    
    for _ in range(100):
        po_number = generate_po_number(existing_po)
        existing_po.add(po_number)

        company_code = random.choice(company_codes)
        
        #choose a random.choice() from keys()
        supplier_number = random.choice(list(suppliers.keys()))
        supplier_name = suppliers[supplier_number]
    
        user = random.choice(users)
        
        #from starting date we add the date from range(end_date - start_date)
        creation_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
        
        # to creation_date add a number of days from range (1,30)
        delivery_date = generate_delivery_date(creation_date, today)
        
        order_status = get_order_status(delivery_date, today)
        
        invoice_number = generate_invoice_number(existing_inv)
        existing_inv.add(invoice_number)
        
        #invoice_date add a number of days from range(10,90)
        invoice_date, payment_terms = generate_invoice_date(delivery_date, today)
    
        invoice_status = random.choice(invoice_choices)
        amount = weighted_choice(amount_ranges)
        
        invoice_amount = calculate_invoice_amount(amount, order_status, invoice_status)
        currency = random.choice(currency_choices)
        
        
    
        record = {
            "PO Number": po_number,
            "Company Code": company_code,
            "Supplier ID": supplier_number,
            "Supplier Name": supplier_name,
            "Requester ID": user["Requestor_ID"],
            "Requester Name": user["Name"],
            "Requester Mail": user["Mail"],
            "Order Status": order_status,
            "Create Date": creation_date.strftime("%d.%m.%Y"),
            "Delivery Date": delivery_date.strftime("%d.%m.%Y"),
            'Invoice Date': invoice_date,
            "Invoice Status": invoice_status,
            "Amount": amount,
            "Invoice Amount": invoice_amount,
            "Currency": currency,
            "Payment Terms": payment_terms,
            "Invoice Number": invoice_number 
        }
        records.append(record)
        
    #konwersja listy na obiekt DataFrame
    df_all = pd.DataFrame(records)    
    
    #definiujemy, które kolumny mają ić do której zakładki
    columns_tab1 = ['PO Number', 
                          'Company Code', 
                          'Supplier ID',
                          'Supplier Name',
                          'Requester ID',
                          'Requester Name',
                          'Requester Mail',
                          'Create Date',
                          'Delivery Date',
                          'Order Status',
                          'Amount',
                          'Currency']
    
    
    columns_tab2 = ['PO Number', 
                          'Company Code', 
                          'Supplier ID',
                          'Supplier Name',
                          'Requester ID',
                          'Requester Name',
                          'Requester Mail',
                          'Delivery Date',
                          'Order Status',
                          'Amount',
                          'Invoice Number',
                          'Invoice Date',
                          'Invoice Status',
                          'Invoice Amount',
                          'Currency',
                          'Payment Terms']
    
    #filtrowanie tabeli na 2 podzbiory:
    df_tab1 = df_all[columns_tab1]
    df_tab2 = df_all[columns_tab2]

    # write excel
    with pd.ExcelWriter("procurement_mock_dataset_inv.xlsx", 
                        engine='openpyxl') as writer:
        df_tab1.to_excel(writer,
                         sheet_name='Ariba',
                         index=False)
        df_tab2.to_excel(writer,
                         sheet_name='Invoices',
                         index=False)
    

    
    print("Generated the file procurement_mock_dataset_inv with 2 sheets.")

# %%
# GUI

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
from datetime import datetime

root = tk.Tk()
root.title("SAP Ariba Mock Data Generator")
root.geometry("700x700")
save_folder = tk.StringVar(value="")

# Styl suwaka
style = ttk.Style()
style.theme_use('clam')
style.configure("green.Horizontal.TScale", 
                troughcolor="#e0e0e0", 
                background="#4CAF50")

# suwak - wartosci
record_var = tk.IntVar(value=2500)

def update_label(value):
    record_var.set(int(float(value)))
    record_label.config(text=f"{record_var.get()} rekordów", 
                        fg="black", 
                        font=("Arial", 12))

# suwak - labelki
tk.Label(
         root, 
         text="Ilość rekordów do wygenerowania:", 
         font=("Arial", 12), 
         fg="#293037").pack(pady=10)

record_label = tk.Label(
                        root, 
                        text=f"{record_var.get()} rekordów", 
                        fg="#293037",                           #ciemny szary
                        font=("Arial", 12, "bold"))
record_label.pack()

record_scale = ttk.Scale(
                         root, 
                         from_=100, 
                         to=50000, 
                         orient="horizontal", 
                         length=400,
                         style="green.Horizontal.TScale", 
                         command=update_label)
record_scale.set(2500)
record_scale.pack(pady=10)          #margines

# Company codes - 2 kolumny
tk.Label(
          root, 
          text="Wybierz Company Codes:", 
          font=("Arial", 12, "bold"), 
          fg="#293037").pack(pady=10)

# słownik wybranych wartoci
checkbox_vars = {}
checkbox_frame = tk.Frame(root)
checkbox_frame.pack()

# pobieramy listę company codes z pliku głównego
codes = company_codes
# dzielimy listę company codes na 2 częci
half = len(codes) // 2

left_frame = tk.Frame(checkbox_frame)
right_frame = tk.Frame(checkbox_frame)
left_frame.pack(side="left", padx=20)
right_frame.pack(side="left", padx=20)

# Checkboxy
for code in codes[:half]:           # od początku: do połowy*
    var = tk.BooleanVar()           # wartosć logiczna, True zaznaczony obiekt
    checkbox_vars[code] = var
    tk.Checkbutton(left_frame, 
                   text=code, 
                   variable=var, 
                   font=("Arial", 11), 
                   fg="#293037").pack(anchor="w")


for code in codes[half:]:           
    var = tk.BooleanVar()
    checkbox_vars[code] = var
    tk.Checkbutton(
                   right_frame, 
                   text=code, 
                   variable=var, 
                   font=("Arial", 11), 
                   fg="#293037").pack(anchor="w")


# Przyciski zaznacz/odznacz
def select_all():
    for var in checkbox_vars.values():
        var.set(True)

def deselect_all():
    for var in checkbox_vars.values():
        var.set(False)

tk.Button(
          root, 
          text="Zaznacz wszystko", 
          command=select_all,
          bg="#4CAF50", 
          fg="white", 
          relief="raised",      # wypukły
          padx=10, 
          pady=5).pack(pady=5)

tk.Button(root, text="Odznacz wszystko", command=deselect_all,
          bg="#e0e0e0", fg="black", relief="flat", padx=10, pady=5).pack(pady=5)


#wybór folderu do zapisu
def choose_folder():
    folder = filedialog.askdirectory()
    if folder:
        save_folder.set(folder)
        folder_label.config(text=f"Wybrany folder: {folder}")

tk.Button(
          root, 
          text="Wybierz folder zapisu", 
          command = choose_folder,
          bg="#4CAF50", 
          fg="white", 
          relief="flat", 
          padx=10, 
          pady=5).pack(pady=10)

folder_label = tk.Label(
                        root, 
                        text="Nie wybrano folderu", 
                        font=("Arial", 10), 
                        fg="#293037")
folder_label.pack()


# Generator danych
def run_generator():
    record_count = record_var.get()
    selected = [code for code, var in checkbox_vars.items() if var.get()]

    if not selected:
        messagebox.showwarning("Brak wyboru", "Musisz wybrać przynajmniej jeden Company Code.")
        return

    if save_folder.get():
        output_file = save_folder.get() + "/generated_procurement_mock.csv"
    else:
        output_file = "generated_procurement_mock.csv"

    try:
        generate_mock_data(record_count, selected, output_file)
        messagebox.showinfo("Sukces", f"Wygenerowano {record_count} rekordów.\n"
                            "Plik zapisano jako:\n{output_file}")
    except Exception as e:
        import traceback
        messagebox.showerror("Błąd", f"{e}\n\n{traceback.format_exc()}")

# Generuj dane Button
ttk.Button(root, text="Generuj dane", command=run_generator).pack(pady=20)

root.mainloop()