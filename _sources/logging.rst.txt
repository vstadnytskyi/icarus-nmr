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
      1627668520.1073966, 114030879416, 2, 999, nan, 2.4178070472506836, 2.4178070472506836, 0.014657775552453067, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, 0.43448508330832186, 0.43448508330832186, 0.10571220342177073, nan, nan, nan, nan, nan, nan, 46.945, nan, nan, nan, nan, nan, nan, -0.010800629768072528, nan
      1627668530.5746562, 114030923507, 2, 10, nan, 2.4173441424422806, nan, -0.0004629048084030529, 26.69249999999664, 29.672492499996643, nan, nan, nan, 0.6194507981542737, nan, 0.30972539907713686, nan, 3.954999999996403, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, 61597, nan, 0.02805216980419478, nan
      1627668530.942101, 114030923615, 2, 11, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, 27.0, nan, nan, nan, nan, nan
      1627668549.3881385, 114030999416, 3, 200, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, 30.0, nan, nan, nan, nan, nan, nan, nan, nan
      1627668549.965775, 114030999416, 3, 999, nan, -0.021991660596497726, -0.021991660596497726, -2.4397987078471814, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, 0.20536929633271125, 0.20536929633271125, -0.2291157869756106, nan, nan, nan, nan, nan, nan, 30.0, nan, nan, nan, nan, nan, nan, 0.02805216980419478, nan
      1627668579.4214935, 114031119416, 4, 200, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, 30.0, nan, nan, nan, nan, nan, nan, nan, nan
      1627668580.0285552, 114031119416, 4, 999, nan, -0.020763910797846168, -0.020763910797846168, 0.0012277497986515583, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, 0.20590847522886285, 0.20590847522886285, 0.0005391788961515986, nan, nan, nan, nan, nan, nan, 30.0, nan, nan, nan, nan, nan, nan, 0.02037844448831602, nan
      1627668609.392286, 114031239416, 5, 200, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, 30.0, nan, nan, nan, nan, nan, nan, nan, nan
      1627668610.0279021, 114031239416, 5, 999, nan, -0.02071078195051806, -0.02071078195051806, 5.312884732810649e-05, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, 0.20551448011352866, 0.20551448011352866, -0.00039399511533419473, nan, nan, nan, nan, nan, nan, 30.0, nan, nan, nan, nan, nan, nan, 0.005351025488889449, nan
      1627668611.7973204, 114031249151, 5, 20, 9.132122936797922, nan, nan, nan, nan, nan, 22.022499999994523, 26.79287499999452, 2.1466158433321674, nan, 1.1540945394258963, nan, 1.25, nan, 1.3795194524248862, nan, nan, nan, nan, 26.352499999999225, 0.4767919526554294, nan, nan, 6.0, nan, 81411.0, nan, nan, nan, nan, 83453, nan, nan
      1627668612.2706754, 114031249151, 6, 200, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, 2.43375, nan, nan, nan, nan, nan, nan, nan, nan
      1627668613.8257473, 114031256465, 6, 100, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, 26574, nan, nan, nan, nan
      1627668619.2385705, 114031279348, 6, 21, nan, nan, 2.3990672929332195, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, 0.49857478005995426, nan, nan, nan, nan, nan, nan, nan, nan, nan, 7549.25, nan, nan, nan, nan, nan, nan

**********************
In future
**********************
The logging module is a separate Python process that uses Channel Access to subscribe to "logging" PVs hosted by other serves.

Rules of logging
TODO
