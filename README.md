# AllMyServos - Fun with PWM

## Description

AllMyServos is a robotics app for Raspberry Pi, written in Python, to help it interface with:

	- Adafruit 16 Channel Servo Driver
	- Invensense MPU6050 Accelerometer and Gyro

All three of these pieces of hardware are low cost and widely available. Using AllMyServos makes them a great platform for experimenting with robots.

To get started, make sure the directory which contains this file is copied to the SD card of your Raspberry Pi, open a terminal, change to this directory and run 'sudo python GUI.py'

For more information visit:

http://allmyservos.co.uk
https://www.youtube.com/user/allmyservos

## Supported Operating Systems

AllMyServos has been tested with:

- Raspbian Wheezy
	- 2015-05-05
- Raspbian Jessie
	- 2015-11-21

## Functionality

### GUI.py

#### Specification

This section keeps track of everything required to reproduce a specific robot. After all, a set of instructions for servos only makes sense within the context of that specific servo configuration.
The specification contains all of the information required to recreate:

- Servos
- Motions
- Chains
- Keymaps
- IMU orientation

Create your own specification based on the way you want to connect your servos.
Specification packages can be created to make sharing and duplicating your robot easier. These are contained in a file using the naming convention: [ident].tar.gz
Specification packages contain JSON serialized data, a preview image and a blend file.

#### System

This section of the app lists system information and provides shortcuts for reboot / poweroff.

#### Servos

These objects represent servos connected to the Adafruit 16 ch Servo Driver.

#### Motions

When the servo configuration is complete, motions can be created which orchestrate the angles of the servos over time.

#### Chains

A chain is a series of motions that can be triggered, loop until trigger is released and then end in a controlled fashion.

#### Keyboard

Motions and chains can be triggered using keys on the keyboard. This section of the application allows mappings to be setup between a keypress and a motion.

#### Metrics

Parts of the application require measurements to be taken. Metrics can be used like variables but they can retain previous values in memory and archive them according to the time the value was set.

#### RPC

Remote Procedure Calls allow a remote computer, with the correct settings, to communicate with AllMyServos.

#### IMU

This section of the app deals with the Gyro and Accelerometer provided by the MPU6050. The app allows you to specify how the IMU is mounted inside of your robot and illustrates how the output will be interpreted.
The IMU -> Sensor Data section demonstrates how IMU data is collected and processed.
The effect of gravity on the accelerometer is demonstrated with an artificial horizon. The complementary filter is demonstrated with orthographic images for Roll, Pitch and Yaw.

#### Settings

The Setting object can be referred to anywhere a script imports it. Settings are accessed statically (using Setting.get() and Setting.set('setting_name',default), the class uses SQLite to check if a value exists, if not the default value is saved.
Use the menu: 'Settings' -> 'List Settings' to see any stored settings and modify their values. For example: 'motion_slow_factor' is an integer which controls how many times slower to play slow motions.
Simply delete a setting to restore its default value.

#### Themes

These are stored in: /themes
They contain an XML file and any images (in gif format) which comprise the theme. The XML file contains the data needed for TkInter to initialise, colours, images and fonts.
The GUI provides an interface where you can edit and clone themes.

#### Help

This section of the app contains information about how to use the app.

### CLI.py

Using the GUI, you can configure services to auto-start when either GUI.py or CLI.py is executed. GUI.py requires the LXDE desktop to be displayed on a monitor whereas CLI.py can be run from the terminal or via SSH.

For best results, set the motion scheduler, keyboard and RPC services to autostart before running CLI.py. 

## Dependencies

AllMyServos includes a built-in dependency manager which will notify you if any third party libraries (from apt-get or pip) are required and allow you to install them with a single click (provided the Raspberry Pi has an internet connection).
After a dependency has been installed the app will require a restart. The next time the app runs, it will be able to make use of that dependency.

## Blender

AllMyServos includes an addon for Blender which enables you to perform the following over RPC:

- Download the servo config from the current specification
- Send live commands to servos from Blender
- Upload keyframed armature movements as motions

see: Help -> Blender for more information.

## Structure

The files which comprise AllMyServos are organised to conform with a few basic criteria:

- The root directory remains the same as development continues
- The 'contrib' directory contains all modules, divided by vendor name and sub divided by type.
- All files generated by modules are contained in the '/files' directory. Modules should assume this folder to be empty in the first instance.
- All themes and specifications are contained in sub folders of the root directory

## Development

Python system paths are managed automatically by __bootstrap.py. Modules using the 'contrib' directory are added at startup.

File -> System -> Information lists the current system paths.

Modules which extend the TkBlock or TkPage classes are instantiated according to the theme profile. Import statements for these modules are also handled automatically.

Themes may contain multiple profiles which adapt the layout for different sized displays.

see: Settings -> Themes

## Code Contribution

Scripts containing the notice below were created specifically for AllMyServos. Scripts created by third parties are listed below:

/contrib/AllMyServos/IMU/lowpassfilter.py
/contrib/AllMyServos/IMU/MPU6050.py
/contrib/AllMyServos/Servos/Adafruit_I2C.py
/contrib/AllMyServos/Adafruit_PWM_Servo_Driver.py

## Notice

Please leave the following notice intact at the top of scripts which contain it:

AllMyServos - Fun with PWM
Copyright (C) 2015  Donate BTC:14rVTppdYQzLrqay5fp2FwP3AXvn3VSZxQ

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see http://www.gnu.org/licenses/.