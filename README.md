Adaptive Activity & Load Monitor (AALM)

Author: Alireza Foulagar

This project, via analyzer.py, collects events, calculates the events,
and detects anomalies (here called Burst of Activities) using an adaptive threshold.
With Storing Events & Bursts and via a simple HTML, we visualize the real-time event activities in a line graph (js.Chart).

How to run
uvicorn AALM.main:app --reload
