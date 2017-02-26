# AllMyServos - Fun with PWM

## Description

AllMyServos is a robotics app for Raspberry Pi, written in Python, to help it interface with:

	- Pi Camera
	- Adafruit PCA9685 16 Channel Servo Driver
	- Invensense MPU6050 or MPU9050 Accelerometer and Gyro
	- Motor Drivers: L298N, TB6612FNG and BTS7960

The app provides a user friendly interface for configuration, a command line version for running over SSH and now supports headless operation.

To get started, make sure the directory which contains this file is copied to the SD card of your Raspberry Pi, open a terminal, change to this directory and run 'sudo python GUI.py'

For more information visit:

http://allmyservos.co.uk
https://www.youtube.com/user/allmyservos

Technical documentation is available here:

http://allmyservos.github.io

## Supported Models and Operating Systems

AllMyServos has been tested with:

- Raspberry Pi Model B+
- Raspberry Pi 2
- Raspberry Pi 3
- Raspberry Pi Zero

OS Versions:

- Raspbian Wheezy
	- 2015-05-05
- Raspbian Jessie
	- 2015-11-21
	- 2016-05-10
	- 2016-09-23
	- 2016-11-25
	- 2017-01-11

## Functionality

### GUI.py

#### Specification

This section keeps track of everything required to reproduce a specific robot. After all, a set of instructions for servos only makes sense within the context of that specific servo configuration.
The specification contains all of the information required to recreate:

- Servos
- Motions
- Chains
- DC Motors
- Stepper Motors
- Keymaps
- IMU orientation

Create your own specification based on the way you want to connect your servos.
Specification packages can be created to make sharing and duplicating your robot easier. These are contained in a file using the naming convention: [ident].tar.gz
Specification packages contain JSON serialized data, a preview image and a blend file.

#### System

Menu: File -> System -> Information
Use this section to check various platform specific information.

Menu: File -> System -> Startup
Use this section to start AllMyServos with the Pi automatically.
This is useful for a Pi which is dedicated to a particular robot and should make the services available as soon as it boots.
Auto starting All My Servos is also useful for headless operation (without a monitor).
One example is making the Pi automatically start capturing timelapse footage when powered on.

#### Servos

These objects represent servos connected to the Adafruit 16 ch Servo Driver.

#### Motions

When the servo configuration is complete, motions can be created which orchestrate the angles of the servos over time.

#### Chains

A chain is a series of motions that can be triggered, loop until trigger is released and then end in a controlled fashion.

#### DC Motors

DC motors can be connected to the Raspberry Pi using motor driver boards. These boards interpret signals sent to it as a direction and speed, outputting the relevant current, with the relevant polarity.
Motor driver boards also allow a separate power supply to send more current to the motor(s) than a single board computer or microcontroller could provide.
The motor section enables motors with several different drive types to be configured. Each drive type reserves a set of pins on the Pi's GPIO connector to send signals to the motor driver.
Once a motor has been saved, controllers can be setup which control the speed and direction of the motor. USB and Bluetooth joysticks and gamepads are supported.

#### Stepper Motors

Stepper motors can also be connected to the Raspberry Pi using Dual H Bridge motor driver boards. These boards allow 4 input wires (from the Pi GPIO) and 4  output wires from a stepper motor to be connected.
Sending a HIGH signal from a GPIO pin will cause the motor driver to energize a coil in the stepper motor with a particulary polarity. This turns the stepper motor to align with that coil.
AllMyServos allows stepper motors to be configured by providing the steps per revolution and maximum revolutions per minute (normally available on the stepper motor datasheet).
As with DC motors, AllMyServos allows the speed and direction of the motor to be changed by setting the drive state (-1 to 1). When editing a stepper motor, this can be done using a slider.
The angle of the stepper motor is tracked by AllMyServos allowing the motor to turn to a given angle.
Once a stepper motor has been saved, it is possible to configure joystick / gamepad actions to control the stepper motor.

#### Keyboard

Motions and chains can be triggered using keys on the keyboard. This section of the application allows mappings to be setup between a keypress and a motion.

#### Joystick

AllMyServos now includes a joystick module which enables joysticks and gamepads to be connected to the Raspberry Pi via USB or Bluetooth. The module provides an interface for testing any connected joysticks.
This module has been integrated with the motor module to allow motors to be controlled using any axis or button on a connected joystick.

#### Metrics

Parts of the application require measurements to be taken. Metrics can be used like variables but they can retain previous values in memory and archive them according to the time the value was set.

#### RPC

Remote Procedure Calls allow a remote computer, with the correct settings, to communicate with AllMyServos.

#### IMU

This section of the app deals with the Gyro and Accelerometer provided by the MPU6050. The app allows you to specify how the IMU is mounted inside of your robot and illustrates how the output will be interpreted.
The IMU -> Sensor Data section demonstrates how IMU data is collected and processed.
The effect of gravity on the accelerometer is demonstrated with an artificial horizon. The complementary filter is demonstrated with orthographic images for Roll, Pitch and Yaw.

#### Camera

This section makes working with the Pi Camera super easy.

##### Manage
This section allows the camera service to be started and stopped.
The camera service, starts and stops the camera hardware and triggers capture and streaming events.
The viewfinder section shows the area of the screen which will be marshalled for previewing.
Below the viewfinder there are capture and stream buttons which. 
The capture button will either take a photo or begin shooting video.
The stream button enabled streaming.
Camera profiles are a collection of settings related to the camera.
These can be used to initialize the camera. The current camera profile is shown on the right.
Settings can be changed while the camera is previewing and they will be applied instantly.

##### Shortcuts

As long as the keyboard service is running the following keyboard shortcuts are available:
C (Shift + c) - Start / stop the camera service
S (Shift + s) - Toggle streaming
Space - Start / stop video capture or capture image (depending on the record mode of the active profile)

##### Timelapse

This section allows one or more timelapse tasks to be setup.
The camera can either record a still image every N seconds or N seconds of video every N seconds.
If a timelapse task is active and the camera service is running then the camera will be recording.
As the task runs, it takes a note of all the media it creates.
Use the 'media' button to view a list of media recorded by the task.

##### Media

This section provides basic file manager functionality to make finding the files the camera has created easier.
The camera saves files in '/files/camera/still' and '/files/camera/video'
Files are named using this format:
[Image|Clip]-[timestamp].[extension]

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

Python system paths are managed automatically by __bootstrap.py. Modules under the 'contrib' directory are added at startup.

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
