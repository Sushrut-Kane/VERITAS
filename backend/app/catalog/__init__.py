"""Catalog-ingestion + Delivery-Format layer (stdlib-only, offline-capable).

Turns messy input catalog rows into the 252-column UniLog Delivery Format,
reusing the firewall's philosophy (constrained, evidenced, honest-about-gaps)
without requiring the LLM/DB/graph to be running.
"""
