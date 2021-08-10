=============
Logging
=============

**********************
Current
**********************
the logging is done within the Event Handler. Every event triggers an entry in the log file. There are 37 columns but not all of them are relevant for each event. Only relevant data is logged as a number and other entries are saved as 'nan' to simplify reading of the log file.

0. time
1. global_pointer
2. period_idx
3. event_code
4. pPre_0
5. pDepre_0
6. pPre_after_0
7. pDiff_0
8. tSwitchDepressure_0
9. tSwitchDepressureEst_0
10. tSwitchPressure_0
11. tSwitchPressureEst_0
12. gradientPressure_0
13. gradientDepressure_0
14. gradientPressureEst_0
15. gradientDepressureEst_0
16. riseTime_0
17. fallTime_0
18. pPre_1
19. pDepre_1
20. pPre_after_1
21. pDiff_1
22. tSwitchDepressure_1
23. tSwitchPressure_1
24. gradientPressure_1
25. gradientDepressure_1
26. fallTime_1
27. riseTime_1
28. period
29. delay
30. pressure_pulse_width
31. depressure_pulse_width
32. pump_stroke
33. depressure_valve_counter
34. pressure_valve_counter
35. leak_value
36. meanbit3


Example of first few enties in the current implantation of the log file.

.. code-block:: python

    ####This experiment started at: 1627668487.4405897 and other information 'and other information'
    b'time' , b'global_pointer', b'period_idx', b'event_code' , b'pPre_0' , b'pDepre_0' , b'pPre_after_0' , b'pDiff_0' , b'tSwitchDepressure_0' , b'tSwitchDepressureEst_0' , b'tSwitchPressure_0' , b'tSwitchPressureEst_0' , b'gradientPressure_0' , b'gradientDepressure_0' , b'gradientPressureEst_0' , b'gradientDepressureEst_0' , b'riseTime_0' , b'fallTime_0' , b'pPre_1' , b'pDepre_1' , b'pPre_after_1$
    1627668489.8208976, 114030759416, 0, 20, 9.591156177712787, nan, nan, nan, nan, nan, 16.837499999999466, 21.607874999999463, 0.05554857700839955, nan, 0.02986482634860191, nan, 0.75, nan, 1.4903641129098288, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, 3686720.75, nan, nan, nan, nan, 83452, nan, nan
    1627668490.421642, 114030759416, 1, 200, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, 16.945, nan, nan, nan, nan, nan, nan, nan, nan
    1627668496.5032792, 114030788216, 1, 21, nan, nan, 2.4031492716982306, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, 0.32877287988655113, nan, nan, nan, nan, nan, nan, nan, nan, nan, 7200.0, nan, nan, nan, nan, nan, nan
    1627668519.4651134, 114030879416, 2, 200, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, 30.0, nan, nan, nan, nan, nan, nan, nan, nan

**********************
In future
**********************
The logging module is a separate Python process that uses Channel Access to subscribe to "logging" PVs hosted by other serves.

Rules of logging
TODO
