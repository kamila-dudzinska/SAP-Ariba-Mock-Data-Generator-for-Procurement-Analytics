# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 21:18:36 2026

@author: @author: Kamila Dudzińska
Project: Tests for SAP-Ariba-Mock-Data-Generator-for-Procurement-Analytics script
Goal:   check, if the function works correctly
"""

#import modules
import datetime
from procurement_mock_functions import generate_po_number


def test_generate_po_number_unique():
    existing = [6000000001, 6000000002]
    new_po = generate_po_number(existing)
    assert new_po not in existing
    assert str(new_po).startswith("6000")

print("Test completed successfully")
