====================================
Interface for ISystem boiler to MQTT 
====================================

.. image:: https://travis-ci.org/ngraziano/isystem-to-mqtt.svg?branch=master
    :target: https://travis-ci.org/ngraziano/isystem-to-mqtt
.. image:: https://coveralls.io/repos/github/ngraziano/isystem-to-mqtt/badge.svg?branch=master
    :target: https://coveralls.io/github/ngraziano/isystem-to-mqtt?branch=master

The poll_isystem_qtt.py poll the boiler and publish value to mqtt host.



Usage
-----

Installation 
::
    pip install --upgrade git+https://github.com/ngraziano/isystem-to-mqtt.git

Read all the value from boiler for testing
::
    dump_isystem.py --serial /dev/ttyUSB0 --deviceid 10 

Run the mqtt publish daemon
::
    poll_isystem_mqtt.py --user MQTTUSER --password MQTTPASSWORD --interval 60 --log DEBUG  mqtt.server.example.com

Mode Bimaitre (bimaster)
------------------------

Boiler may be configured in bismaster mode : it send query during 5s and wait query during 5s. 
If you have incorrect respond from the boiler you can try to add --bimaster flag to the command line to handle bimaster mode.

This mode is not well tested, ti may not work.


Hardware connection
-------------------

On my system there is two 4 pin mini DIN connectors for the connection (MODBUS RS-485).

For the connection I use an USB to RS485 adapter : USB-RS485-WE-1800-BT. I connected the Data- B Yellow wire on pin 3
(up right with connector in front of you and plastic pin a the bottom) and the Data+ A Orange wire on pin 4 (low right).

MQTT Topic
----------

Available mqtt topic can be found in isystem_to_mqtt/tables.py.

Variable ZONE_TABLE_MODULENS_O define zone to read.

Variable READ_TABLE_MODULENS_O define topic exported to MQTT.

Variable WRITE_TABLE_MODULENS_O define topic subcribed to send data to boiler.

On Diematic iSystem, the Modbus interface exposes the stored weekly P4
schedule for heating zones A, B and C. P1-P3 weekly schedules are not
available through the exposed iSystem register map. The domestic hot-water
(DHW/CWU) schedule is also available for reading. This project currently
does not implement writing heating or DHW schedules. Writing the DHW/CWU
schedule has been observed to work on the tested installation, but is not yet
supported by this project.

The schedule topics are:

* ``heating/zone-a/schedule-p4``
* ``heating/zone-b/schedule-p4``
* ``heating/zone-c/schedule-p4``
* ``heating/dhw/schedule``

The selected program is published separately as a read-only value on
``heating/zone-a/program``, ``heating/zone-b/program`` and
``heating/zone-c/program``. Values ``0`` through ``3`` represent P1 through
P4. Program selection is not changed by this project.

Main topic are:

=========================================== ======================================
TOPIC                                       Description
=========================================== ======================================
heating/zone-a/temperature                  Inside temperature
heating/outside/temperature                 Outsite temperature
heating/zone-a/day-target-temperature       Current day mode target temperature
heating/zone-a/day-target-temperature/SET   To set day mode target temperature
heating/zone-a/night-target-temperature     Currect night mode target temperature
heating/zone-a/night-target-temperature/SET To set night mode target temperature
=========================================== ======================================

