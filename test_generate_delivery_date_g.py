# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 21:18:36 2026

@author: @author: Kamila Dudzińska
Project: Tests for SAP-Ariba-Mock-Data-Generator-for-Procurement-Analytics script
Goal:   check, if the function works correctly
"""

import pytest
from datetime import datetime, timedelta
from procurement_mock_functions import generate_delivery_date

def test_generate_delivery_date_range():
    creation_date = datetime(2026, 3, 1)
    today = datetime(2026, 3, 25)

    delivery_date = generate_delivery_date(creation_date, today)

    #delivery_date has type datetime
    assert isinstance(delivery_date, datetime)

    #delivery_date > creation_date
    assert delivery_date > creation_date

    # delivery_date in range of 1–60 days
    delta_days = (delivery_date - creation_date).days
    assert 1 <= delta_days <= 60

print("Test generate_delivery_date passed successfully")
