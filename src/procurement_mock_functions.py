# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 18:02:37 2026
Extended on Thu Oct 22 20:05:20 2026
Extended on Sun Nov 01 11:14:38 2026

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
import re
from datetime import datetime, timedelta


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
    
    # lista [ ] zamiast samego generatora: działa i ze zwykłym sum(), i gdy Spyder podmieni sum
    # na numpy.sum (opcja "load Pylab and NumPy") - wtedy generator dawał TypeError (extended 01.11.2026)
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
def generate_po_number(existing:int) -> int:
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
        if num not in existing:
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
def generate_invoice_date(delivery_date:datetime, today:datetime) -> tuple[str | None, int]:
    '''
    Randomly generates an invoice date based on the delivery date and PT 
    within a range of up to 90 days.

    Args:
        delivery_date (datetime | str): 
            The delivery date as a datetime object or string in format "%d.%m.%Y".
        today (datetime): 
            The current date used for validation or reference.

    Returns:
        tuple[str | None, int]: 
            A tuple containing:
              - The invoice date formatted as "%d.%m.%Y" (or None if invalid
                or if the delivery date is in the future).
              - The payment term in days (between 10 and 90; shorter if the
                invoice date had to be moved back to today at the latest).

    Example:
        >>> generate_invoice_date(datetime(2026, 3, 25), datetime(2026, 8, 1))
        ('23.05.2026', 59)
    '''
  
    if delivery_date is None: 
        return None, 0
    
    if isinstance(delivery_date, str):
        delivery_date = datetime.strptime(delivery_date, "%d.%m.%Y")

    # FAKTURA MAKSYMALNIE DO DZISIAJ (extended 01.11.2026)
    # Przy sztywnych datach (styczeń-maj 2026) faktury zawsze wypadały w przeszłości.
    # Teraz daty są dynamiczne (do dzisiaj), więc trzeba pilnować, żeby faktura nie była z przyszłości.
    if delivery_date > today:
        return None, 0

    payment_terms = random.randint(10, 90)
    invoice_date = delivery_date + timedelta(days=payment_terms)

    # 2. data faktury wypadła po dzisiaj -> losujemy ją od nowa między dostawą a dzisiaj
    if invoice_date > today:
        invoice_date = delivery_date + timedelta(days=random.randint(0, (today - delivery_date).days))
        payment_terms = (invoice_date - delivery_date).days
    invoice_date: str  = invoice_date.strftime("%d.%m.%Y")
    
    return invoice_date, payment_terms


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

    # Pusta data dostawy -> tylko "ordered" lub "confirmed"
    if delivery_date is None or delivery_date == "" or str(delivery_date).lower() == "nan":
        return random.choices(
            population=["ordered", "confirmed"],
            weights=[91, 9],
            k=1
        )[0]

    # Jeśli mamy string, zamieniamy na datetime
    if isinstance(delivery_date, str):
        delivery_date = datetime.strptime(delivery_date, "%d-%m-%Y")

    # Granica 10 dni temu
    ten_days_ago = today - timedelta(days=10)

    # Delivery Date w ostatnich 10 dniach (do dziś)
    if ten_days_ago <= delivery_date <= today:
        return random.choices(
            population=["received", "invoiced"],
            weights=[51, 49],
            k=1
        )[0]

    # Delivery Date starsza niż 10 dni
    if delivery_date < ten_days_ago:
        return random.choices(
            population=["received", "confirmed", "invoiced"],
            weights=[70, 8, 21],
            k=1
        )[0]

    # Delivery Date w przyszłości (awaryjnie)
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

    # rok i miesiąc w numerze faktury bierzemy z daty faktury (wcześniej rok był na sztywno '2026',
    # więc faktura z 2024 dostawała numer FV/2026/... co było confused -  extended 01.11.2026)
    if invoice_date:
        invoice_dt = datetime.strptime(invoice_date, "%d.%m.%Y")
        year = str(invoice_dt.year)
        month = f"{invoice_dt.month:02d}"
    else:
        # brak daty faktury -> jak wcześniej: bieżący rok i losowy miesiąc
        year = str(datetime.today().year)
        month = f"{random.randint(1,12):02d}"

    while True:
        random_num = f'{random.randint(1,99999):05d}'
        random_inv = f'FV/{year}/{month}/{random_num}' 
        if random_inv not in existing_inv:
            return random_inv



# DATA VALIDATION - REGEX
# one rule per column, based on the rules in data/regex1.xlsx
REGEX_RULES = {
    "PO Number":      r"^6000\d{6}$",                 # 6000 + 6 digits
    "Company Code":   r"^[A-Z0-9]{4}$",               # e.g. A001, CH01
    "Supplier ID":    r"^200\d{7}$",                  # 200 + 7 digits
    "Requester ID":   r"^PL[A-Z]{4,6}$",              # PL + 4-6 letters. The same as in project Invio & Mobi.
    "Requester Mail": r"^[a-z]+\.[a-z]+@example\.com$", # domena testowa @example.com 
    "Create Date":    r"^(\d{4}-\d{2}-\d{2}|\d{2}\.\d{2}\.\d{4})$",  # 2026-03-25 or 25.03.2026
    "Delivery Date":  r"^(\d{4}-\d{2}-\d{2}|\d{2}\.\d{2}\.\d{4})$",
    "Amount":         r"^\d+(\.\d{1,2})?$",           # max 2 decimals
    "Currency":       r"^[A-Z]{3}$",                  # ISO 4217, e.g. EUR
    "Invoice Number": r"^FV/\d{4}/\d{2}/\d{5}$",      # FV/2026/03/00914 (5 cyfr od 01.11.2026)
    "Payment Terms":  r"^\d+$",                       # days
}

# empty values are allowed - exceptions:
OPTIONAL_FIELDS = {"Delivery Date", "Invoice Number", "Payment Terms"}


def validate_record(record: dict) -> list[str]:
    """
    Checks one generated record against REGEX_RULES.

    Only columns present in the record are checked, so the same function
    works for the PO report and for the invoice report.

    Args:
        record (dict): one row, e.g. {"PO Number": 6000123456, ...}

    Returns:
        list[str]: names of the columns that do not match their rule.
                   An empty list means the record is valid.

    Example:
        >>> validate_record({"PO Number": 6000123456, "Currency": "eur"})
        ['Currency']
    """
    errors = []
    for field, pattern in REGEX_RULES.items():
        if field not in record:
            continue
        value = record[field]
        if value is None or str(value) == "":
            if field not in OPTIONAL_FIELDS:
                errors.append(field)
            continue
        if not re.fullmatch(pattern, str(value)):
            errors.append(field)
    return errors


def validate_records(records: list[dict]) -> dict[str, int]:
    """
    Validates all records and counts errors per column.

    Returns:
        dict[str, int]: e.g. {"Supplier ID": 2500}. Empty dict = all valid.
    """
    summary = {}
    for record in records:
        for field in validate_record(record):
            summary[field] = summary.get(field, 0) + 1
    return summary
