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

# IMPORT MODULES
import random
from datetime import datetime, timedelta
import procurement_mock_functions


# FUNCTIONS
# calculate weights for data choices for amount_ranges
def weighted_choice(choices):
    '''
    Calculates the order amount taking business weights into account. 
    Most orders are low-budget orders (tactical sourcing).
    '''
    
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
    within a range of up to 60 days.
    '''
    random_days = random.randint(1, 60)
    delivery_date = creation_date + timedelta(days=random_days)
    delivery_date.strftime("%d-%m-%Y")
    if delivery_date == delivery_date + timedelta(days=42):
        return None
    return delivery_date
    

# generate delivery date
def generate_invoice_date(delivery_date:datetime, today:datetime) -> tuple[str | None, int]:
    '''
    Randomly generates an invoice date based on the delivery date and PT 
    within a range of up to 90 days.
    '''
    if delivery_date is None: 
        return None, 0
    
    if isinstance(delivery_date, str):
        delivery_date = datetime.strptime(delivery_date, "%d.%m.%Y")
              
    payment_terms = random.randint(10, 90)
    invoice_date = delivery_date + timedelta(days=payment_terms)
    invoice_date: str  = invoice_date.strftime("%d.%m.%Y")
    
    return invoice_date, payment_terms


def calculate_invoice_amount(amount:float, order_status:str, invoice_status:str) -> float:
    '''
    Return the invoice amount. In 80% it is the same as PO amount (2 way match)
    and in 20% there is a small variation, which needs further clarification.
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
    '''

    while True:
        year = '2026'
        month = f"{random.randint(1,12):02d}"
        random_num = f'{random.randint(1,999):04d}'
        random_inv = f'FV/{year}/{month}/{random_num}' 
        if random_inv not in existing_inv:
            return random_inv
    
    
                























