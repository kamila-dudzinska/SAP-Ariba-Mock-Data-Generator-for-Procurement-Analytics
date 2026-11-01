# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 18:02:37 2026
Extended on Sat Oct 31 20:11:59 2026
Extended on Sun Nov 01 10:35:11 2026

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
    
    total = sum([w for _, _, w in choices])
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

    # extended* - the last version has constant data frame - January - May 2026
    # now user defines the data frame - the function changed to avoide the 
    # invoice with date in the future - logic conflict
    if delivery_date > today:
        return None, 0

    payment_terms = random.randint(10, 90)
    invoice_date = delivery_date + timedelta(days=payment_terms)

    #if invoice_date > today, new loop with random 
    if invoice_date > today:
        invoice_date = delivery_date + timedelta(days=random.randint(0, (today - delivery_date).days))
        payment_terms = (invoice_date - delivery_date).days
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

    # empty delivery date - then status 'ordered' or 'confirmed'
    if delivery_date is None or delivery_date == "" or str(delivery_date).lower() == "nan":
        return random.choices(
            population=["ordered", "confirmed"],
            weights=[91, 9],
            k=1
        )[0]

    # str --> datetime
    if isinstance(delivery_date, str):
        delivery_date = datetime.strptime(delivery_date, "%d-%m-%Y")

    # Max 10 days ago
    ten_days_ago = today - timedelta(days=10)

    # Delivery date >= CURRENT_DATE - INTERVAL '10 day' 
    # AND delivery_date <= CURRENT_DATE (let's love SQL)
    if ten_days_ago <= delivery_date <= today:
        return random.choices(
            population=["received", "invoiced"],
            weights=[51, 49],
            k=1
        )[0]

    # Delivery date < CURRENT_DATE - INTERVAL '10 day' ;)
    if delivery_date < ten_days_ago:
        return random.choices(
            population=["received", "confirmed", "invoiced"],
            weights=[70, 8, 21],
            k=1
        )[0]

    # Delivery_date in the future*
    return "ordered"


def generate_invoice_number(existing_inv:str, invoice_date:str | None = None) ->str:
    '''
    Generates unique invoice number in the specified format.

    Args:
        existing_inv (list[str]): 
            A list of already generated invoice numbers to avoid duplicates.
        invoice_date (str | None):
            Invoice date in format "%d.%m.%Y". Year and month of the invoice
            number are taken from this date. If None - current year, random month.

    Returns:
        str: 
            A unique invoice number formatted as `FV/YYYY/MM/NNNNN`.

    Example:
        >>> existing_inv = ["FV/2026/03/00914", "FV/2026/07/00452"]
        >>> generate_invoice_number(existing_inv, "15.03.2025")
        'FV/2025/03/08310'
    '''

    # year and month in the invoice basis on the invoice_date* (01.11.2026)
    if invoice_date:
        invoice_dt = datetime.strptime(invoice_date, "%d.%m.%Y")
        year = str(invoice_dt.year)
        month = f"{invoice_dt.month:02d}"
    else:
        # no invoice_date - then random month + year 2026
        year = str(datetime.today().year)                   
        month = f"{random.randint(1,12):02d}"

    while True:
        random_num = f'{random.randint(1,99999):05d}'
        random_inv = f'FV/{year}/{month}/{random_num}' 
        if random_inv not in existing_inv:
            return random_inv
    
    

# %%
# MAIN
# IMPORT MODULES

# GENERATED DATA FOR FURTHER ACTIONS
# company codes - created manually basing on my work expierience
company_codes = ["A001", "A002", 
                 "B001", "B002", 
                 "CH01", "CH02", 
                 "D001", "D002", "D003", "D004", 
                 "N001", 
                 "F001", "F002", "F003", 
                 "S001", "S002"]

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


#created by copilot +  @example.com - test domain (31.10.2026)
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


#   DATA CREATION
#   2 sheets generated - extenden (31.10.2026)
#   - "Ariba"    -> dane zamówień (PO)
#   - "Invoices" -> te same zamówienia + dane faktur (PO + invoices)
def generate_mock_data(record_count: int, selected_company_codes: list[str], output_file: str,
                       start_date: datetime, end_date: datetime) -> str:
    '''
    Generates mock SAP Ariba data (POs + invoices) and saves it to an Excel file
    with two sheets: "Ariba" and "Invoices".

    Args:
        record_count (int): number of records chosen on the slider.
        selected_company_codes (list[str]): Company Codes ticked in the GUI.
        output_file (str): path of the .xlsx file to save.
        start_date (datetime): first possible PO create date (from GUI).
        end_date (datetime): last possible PO create date (from GUI).

    Returns:
        str: path of the saved file.
    '''
    
    existing_po = set()     #set to avoid duplicates
    existing_inv = set()
    records = []

    # PO datetime range - daty od/do przychodzą teraz z GUI (wcześniej na sztywno 01.01-31.05.2026)
    today = datetime.today()

    # number of PO records
    for _ in range(record_count):
        po_number = generate_po_number(existing_po)
        existing_po.add(po_number)

        # Company Code - one random from GUI
        company_code = random.choice(selected_company_codes)

        # losowy klucz dostawcy i nazwa (value) ze słownika
        supplier_number = random.choice(list(suppliers.keys()))
        supplier_name = suppliers[supplier_number]

        user = random.choice(users)

        # do daty początkowej dodajemy losową liczbę dni z przedziału (data końcowa - data początkowa)
        creation_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))

        # data dostawy: data utworzenia + 1 do 60 dni
        delivery_date = generate_delivery_date(creation_date, today)

        # status zamówienia zależy od daty dostawy (get_order_status)
        order_status = get_order_status(delivery_date, today)

        # data faktury: data dostawy + termin płatności (10 do 90 dni)
        invoice_date, payment_terms = generate_invoice_date(delivery_date, today)

        amount = weighted_choice(amount_ranges)

        if invoice_date is None:
            # dostawa jeszcze nie przyszła -> brak faktury: puste numer, status i kwota faktury
            invoice_number = None
            invoice_status = None
            invoice_amount = None
        else:
            # numer faktury dopiero PO dacie faktury - rok i miesiąc w numerze biorą się z tej daty
            invoice_number = generate_invoice_number(existing_inv, invoice_date)
            existing_inv.add(invoice_number)

            invoice_status = random.choice(invoice_choices)

            # kwota faktury: zwykle = kwota PO, przy statusie "hold" może się różnić (do +/- 20%)
            invoice_amount = calculate_invoice_amount(amount, order_status, invoice_status)
        currency = random.choice(currency_choices)

        # one row - one result
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
            "Invoice Date": invoice_date,
            "Invoice Status": invoice_status,
            "Amount": amount,
            "Invoice Amount": invoice_amount,
            "Currency": currency,
            "Payment Terms": payment_terms,
            "Invoice Number": invoice_number
        }
        records.append(record)

    # dict --> Data Frame
    df_all = pd.DataFrame(records)

    # columns
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

    # 2 excel sheets
    df_tab1 = df_all[columns_tab1]
    df_tab2 = df_all[columns_tab2]

    # save Excel - all sheets 
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df_tab1.to_excel(writer, sheet_name='Ariba', index=False)
        df_tab2.to_excel(writer, sheet_name='Invoices', index=False)

    return output_file

# %%
# GUI

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
from datetime import datetime

# KOLORY I CZCIONKA - extended 01.11.2026 - 
# Każdy projekt z serii ma swój kolor: 
#    --> Mobi - granat (#1F3A5F)
#    --> Invio - śliwka (#5B1A5B)
#    --> SAP Mock Generator - ciemna zieleń (#2E6B52)
# duże literki - to zmienne globalne PEP 8
GREEN = "#1F4D3A"          
GREEN_HOVER = "#2E6B52"    
MINT = "#D5EFE0"           
GREY = "#6B7280"           
LIGHT_GREY = "#E5E7EB"     
TEXT = "#293037"           
BG = "#EEF3EF"             # jasna szaro-zieleń zamiast bieli - mniej męczy wzrok (extended 01.11.2026)
FONT = "Calibri"           

root = tk.Tk()
root.title("SAP Ariba Mock Data Generator")
root.geometry("700x650")          # size
root.minsize(600, 620)            # min. size 
root.configure(bg=BG)

# wdiget settings
root.option_add("*Background", BG)
root.option_add("*Font", (FONT, 11))
# master=root -> for Spyder - only active choice* (pamięta tylko aktywny wybór)
save_folder = tk.StringVar(master=root, 
                           value="")

# Spójny nagłówek
header = tk.Frame(root, 
                  bg=GREEN, 
                  height=70)
# fill="x" - pasek na całą szerokość okna - aby zachować styl z Mobi & Invio
header.pack(fill="x")                  
header.pack_propagate(False)           
tk.Label(header, 
         text="SAP Ariba Mock Data Generator",
         bg=GREEN, 
         fg="white", 
         font=(FONT, 18, "bold")).pack(pady=(10, 0))
tk.Label(header, 
         text="Procurement mock data  •  PO + Invoices",
         bg=GREEN, 
         fg=MINT, 
         font=(FONT, 10)).pack()

# Styl suwaka
style = ttk.Style(root)            
style.theme_use('clam')
style.configure("green.Horizontal.TScale", 
                troughcolor=LIGHT_GREY, 
                background=GREEN,
                bordercolor=LIGHT_GREY,
                lightcolor=GREEN,      # lightcolor/darkcolor - cieniowanie
                darkcolor=GREEN)

# suwak - wartosci
record_var = tk.IntVar(master=root, 
                       value=2500)

MIN_RECORDS = 100                  # zakres suwaka i pola do wpisania
MAX_RECORDS = 50000

def update_label(value):
    # update suwaczka
    record_var.set(int(float(value)))
    record_label.config(text=f"{record_var.get()} rekordów", 
                        fg=GREEN, 
                        font=(FONT, 12, "bold"))
    record_entry_var.set(str(record_var.get()))


def apply_entry(event=None):
    '''
    Liczba rekordów wpisana ręcznie (extended 01.11.2026).
    Sprawdza wpis i ustawia suwak. Zwraca True, jeśli liczba jest OK.
    event=None, bo funkcję wołamy z klawisza Enter (wtedy tkinter podaje event) i z run_generator (bez eventu).
    '''
    text = record_entry_var.get().strip().replace(" ", "")   # "10 000" -> "10000"
    if not text.isdigit():
        messagebox.showwarning("Zła liczba", f"Wpisz liczbę rekordów od {MIN_RECORDS} do {MAX_RECORDS}.")
        return False
    count = int(text)
    if not MIN_RECORDS <= count <= MAX_RECORDS:
        messagebox.showwarning("Zła liczba", f"Liczba rekordów musi być od {MIN_RECORDS} do {MAX_RECORDS}.")
        return False
    record_scale.set(count)        # przesuwa suwak -> suwak sam wywoła update_label i odświeży napis
    return True

# suwak - labelki
tk.Label(
         root, 
         text="Ilość rekordów do wygenerowania:", 
         font=(FONT, 12, "bold"), 
         fg=TEXT).pack(pady=(15, 5))

# wiersz: [pole do wpisania]  [napis "2500 rekordów"]
count_frame = tk.Frame(root)
count_frame.pack()

record_entry_var = tk.StringVar(master=root, 
                                value="2500")
record_entry = tk.Entry(count_frame, 
                        textvariable=record_entry_var, 
                        width=8, 
                        fg=TEXT,
                        justify="center", 
                        relief="flat", 
                        bg="white",
                        highlightthickness=1, 
                        highlightbackground=LIGHT_GREY, 
                        highlightcolor=GREEN)
record_entry.pack(side="left", padx=10)
record_entry.bind("<Return>", apply_entry)     # Enter w polu -> ustaw suwak na wpisaną liczbę

record_label = tk.Label(count_frame, 
                        text=f"{record_var.get()} rekordów", 
                        fg=GREEN,                               #zielony - wybrana liczba
                        font=(FONT, 12, "bold"))
record_label.pack(side="left")

record_scale = ttk.Scale(root, 
                         from_=MIN_RECORDS, 
                         to=MAX_RECORDS, 
                         orient="horizontal", 
                         length=400,
                         style="green.Horizontal.TScale", 
                         command=update_label)
record_scale.set(2500)
record_scale.pack(pady=10)          #margines

#zakres dat wprowadza user - extended 31.10.2026
DATE_FORMAT = "%d.%m.%Y"            # format daty w polach (np. 31.10.2026)
years_back_max = 5                  # "Data od" nie może być starsza niż 5 lat

tk.Label(root,
         text="Zakres dat utworzenia PO (dd.mm.rrrr):",
         font=(FONT, 12, "bold"),
         fg=TEXT).pack(pady=5)

date_frame = tk.Frame(root)         # ramka, żeby oba pola były w jednym wierszu
date_frame.pack()

# StringVar + default values - last 12 months
date_from_var = tk.StringVar(master=root, 
                             value=(datetime.today() - timedelta(days=365)).strftime(DATE_FORMAT))
date_to_var = tk.StringVar(master=root, 
                           value=datetime.today().strftime(DATE_FORMAT))

# pola z datami: jasnoszara ramka, a po kliknięciu w pole - zielona (highlightcolor)
tk.Label(date_frame, 
         text="Data od:", 
         fg=GREY).pack(side="left", padx=5)
tk.Entry(date_frame, 
         textvariable=date_from_var, 
         width=12, 
         fg=TEXT, 
         relief="flat", 
         bg="white",
         highlightthickness=1, 
         highlightbackground=LIGHT_GREY, 
         highlightcolor=GREEN).pack(side="left", padx=5)
tk.Label(date_frame, 
         text="Data do:", 
         fg=GREY).pack(side="left", padx=5)
tk.Entry(date_frame, 
         textvariable=date_to_var, 
         width=12, 
         fg=TEXT, 
         relief="flat", 
         bg="white",
         highlightthickness=1, 
         highlightbackground=LIGHT_GREY, 
         highlightcolor=GREEN).pack(side="left", padx=5)


def read_dates():
    '''
    Czyta daty z pól i sprawdza je.
    Zwraca (start_date, end_date), a jeśli coś jest nie tak - pokazuje okienko i zwraca None.
    '''
    # str-->datetime
    try:
        start_date = datetime.strptime(date_from_var.get().strip(), DATE_FORMAT)    
        end_date = datetime.strptime(date_to_var.get().strip(), DATE_FORMAT)        
    except ValueError:
        messagebox.showwarning("Zła data", "Wpisz daty w formacie dd.mm.rrrr, np. 31.10.2026.")
        return None

    today = datetime.today()
    # date- not older than 5 years (years_back_max)
    if start_date < today - timedelta(days=years_back_max * 365):
        messagebox.showwarning("Zła data", f"Data od nie może być starsza niż {years_back_max} lat.")
        return None
    # 3. date cannot be in the future!
    if end_date > today:
        messagebox.showwarning("Zła data", "Data do nie może być w przyszłości.")
        return None
    # 'data od' cannot be bigger than 'data to'
    if start_date >= end_date:
        messagebox.showwarning("Zła data", "Data od musi być wcześniejsza niż Data do.")
        return None

    return start_date, end_date

# Company codes - 3 kolumny (extended 01.11.2026 - wcześniej 2 kolumny, okno było za długie)
tk.Label(root, 
         text="Wybierz Company Codes:", 
         font=(FONT, 12, "bold"), 
         fg=TEXT).pack(pady=(15, 5))

# słownik wybranych wartoci
checkbox_vars = {}
checkbox_frame = tk.Frame(root)
checkbox_frame.pack()

codes = company_codes
COLUMNS = 4                                   # liczba kolumn z checkboxami (16 kodów = 4 x 4, równe kolumny)
rows = -(-len(codes) // COLUMNS)              # dzielenie z zaokrągleniem w górę: 16 kodów / 4 = 4 wiersze

# Checkboxy - grid() układa je w siatce: wiersz i kolumna
# kolejność "w dół kolumnami": A001, A002... w 1. kolumnie, potem 2. kolumna itd.
for i, code in enumerate(codes):
    var = tk.BooleanVar(master=root)          # wartosć logiczna, True zaznaczony obiekt
    checkbox_vars[code] = var
    tk.Checkbutton(checkbox_frame, 
                   text=code, 
                   variable=var, 
                   fg=TEXT,
                   activebackground=MINT,     # tło po najechaniu myszką
                   highlightthickness=0,      
                   selectcolor=MINT            # selectcolor = tło kwadracika, gdy zaznaczony
                   ).grid(row=i % rows, column=i // rows, sticky="w", padx=15)


# Przyciski zaznacz/odznacz - obok siebie w jednym rzędzie (oszczędza miejsce w pionie)
def select_all():
    for var in checkbox_vars.values():
        var.set(True)

def deselect_all():
    for var in checkbox_vars.values():
        var.set(False)

buttons_frame = tk.Frame(root)
buttons_frame.pack(pady=10)

tk.Button(
          buttons_frame, 
          text="Zaznacz wszystko", 
          command=select_all,
          bg=GREEN, 
          fg="white", 
          activebackground=GREEN_HOVER,   # kolor w momencie kliknięcia
          activeforeground="white",
          relief="flat",        # płaski - nowocześniej, tak jak pozostałe przyciski
          padx=10, 
          pady=5).pack(side="left", padx=5)

tk.Button(buttons_frame, text="Odznacz wszystko", command=deselect_all,
          bg=LIGHT_GREY, fg=TEXT, activebackground=MINT, relief="flat", padx=10, pady=5).pack(side="left", padx=5)


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
          bg=MINT,              # miętowy - przycisk "pomocniczy", żeby nie konkurował z Generuj dane
          fg=GREEN, 
          activebackground=LIGHT_GREY,
          relief="flat", 
          padx=10, 
          pady=5).pack(pady=10)

folder_label = tk.Label(
                        root, 
                        text="Nie wybrano folderu", 
                        font=(FONT, 10), 
                        fg=GREY)
folder_label.pack()


# Generator danych
def run_generator():
    # najpierw liczba z pola - ktoś mógł ją wpisać i od razu kliknąć "Generuj dane" bez Entera
    if not apply_entry():
        return
    record_count = record_var.get()
    selected = [code for code, var in checkbox_vars.items() if var.get()]

    if not selected:
        messagebox.showwarning("Brak wyboru", "Musisz wybrać przynajmniej jeden Company Code.")
        return

    # dates check
    dates = read_dates()
    if dates is None:
        return
    start_date, end_date = dates

    # excel file save
    if save_folder.get():
        output_file = save_folder.get() + "/generated_procurement_mock.xlsx"
    else:
        output_file = "generated_procurement_mock.xlsx"

    try:
        generate_mock_data(record_count, selected, output_file, start_date, end_date)
        messagebox.showinfo("Sukces", f"Wygenerowano {record_count} rekordów.\n"
                            f"Plik zapisano jako:\n{output_file}")   # f-string, żeby pokazać prawdziwą ścieżkę
    except Exception as e:
        import traceback
        messagebox.showerror("Błąd", f"{e}\n\n{traceback.format_exc()}")

# Generuj dane Button - najważniejszy przycisk w kolorach spójnych
tk.Button(root, 
          text="Generuj dane", 
          command=run_generator,
          bg=GREEN, 
          fg="white", 
          activebackground=GREEN_HOVER, 
          activeforeground="white",
          font=(FONT, 13, "bold"), 
          relief="flat", 
          padx=30, pady=8).pack(pady=20)          # cursor="hand2" -> rączka po najechaniu








root.mainloop()