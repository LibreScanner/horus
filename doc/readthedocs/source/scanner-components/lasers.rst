.. _sec-scanner-components-lasers:

Lasers
======

Supported lasers
----------------

Line laser
``````````

.. image:: ../_static/scanner-components/line-laser.png
   :width: 250 px

Red Class 1 line laser.

.. list-table::
   :widths: 50 25

   * - **Name**
     - **Value**
   * - Wavelength
     - 650 nm
   * - Voltage
     - 5 V
   * - Working distance
     - 300 mm
   * - Output aperture
     - 3 mm
   * - Output power
     - 2.5 mW
   * - Fan angle
     - > 60 º
   * - Body diameter
     - 8 mm
   * - Body length
     - 26 mm
   * - Wire length
     - 250 mm
   * - Security class
     - 1
   * - TÜV certificate
     - Yes

.. warning::

   Only **Class 1** lasers according to *IEC 60825-1:2014* are recommended to ensure eye safety. The emission limits for this wavelength must be less than 390 uW.

Gcodes
------

M70
````
Switch off the laser specified in the T command.

:Example: M70 T1

M71
````
Switch on the laser specified in the T command.

:Example: M71 T2

.. note::

    Lasers are switched off automatically after 255 seconds as a safety measure.

Troubleshooting
---------------

Laser not detected correctly
````````````````````````````

   If the laser is not detected correctly:

   1. Improve the environment light conditions.
   2. Adjust the camera settings in *Adjustment workbench*:

      * *Scan capture > Laser* for the laser over the scanning object.
      * *Calibration capture > Laser* for the laser over the pattern.
