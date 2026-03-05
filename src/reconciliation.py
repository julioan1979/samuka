"""Reconciliation calculations for CashCheck.

This module is responsible for:
- Aggregating cash movements per closing
- Calculating expected_total and settled_total
- Evaluating the difference and status
"""

import logging
from typing import List

import pandas as pd

from .models.closing import Closing
from .models.movement import Movement

logger = logging.getLogger(__name__)


def aggregate_movements(movements: List[Movement]) -> pd.DataFrame:
    """Return a DataFrame with movements aggregated by payment method and type."""
    if not movements:
        return pd.DataFrame(
            columns=["movement_type", "payment_method", "amount", "signed_amount"]
        )
    rows = [
        {
            "movement_type": m.movement_type,
            "payment_method": m.payment_method,
            "amount": m.amount,
            "signed_amount": m.signed_amount(),
        }
        for m in movements
    ]
    df = pd.DataFrame(rows)
    return df


def calculate_settled_total(movements: List[Movement]) -> float:
    """
    Sum all signed amounts across movements to produce the settled total.

    Sales are positive; Expenses, Sangria, and Courier Payments are negative.
    Adjustments use their raw amount (positive means add, negative means subtract).
    """
    total = sum(m.signed_amount() for m in movements)
    return round(total, 2)


def reconcile(closing: Closing, movements: List[Movement]) -> Closing:
    """
    Perform full reconciliation for a closing.

    Steps:
    1. Calculate settled_total from movements.
    2. Use pos_total as expected_total (can be overridden externally).
    3. Compute difference = expected_total - settled_total.
    4. Set status to OK or Discrepancy.

    Args:
        closing: The Closing record to update.
        movements: All movements linked to this closing.

    Returns:
        The updated Closing record.
    """
    closing.settled_total = calculate_settled_total(movements)

    if closing.expected_total == 0.0:
        closing.expected_total = closing.pos_total

    closing.evaluate_status()

    logger.info(
        "Reconciled closing %s | expected=%.2f settled=%.2f diff=%.2f status=%s",
        closing.id or "(new)",
        closing.expected_total,
        closing.settled_total,
        closing.difference,
        closing.status,
    )
    return closing


def summary_by_payment_method(movements: List[Movement]) -> pd.DataFrame:
    """Return a pivot table: payment method vs. movement type with totals."""
    df = aggregate_movements(movements)
    if df.empty:
        return df
    pivot = df.pivot_table(
        index="payment_method",
        columns="movement_type",
        values="signed_amount",
        aggfunc="sum",
        fill_value=0.0,
    )
    pivot["Total"] = pivot.sum(axis=1)
    return pivot.reset_index()
