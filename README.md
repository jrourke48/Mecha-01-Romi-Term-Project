# Mecha-01-Romi-Term-Project

## Overview
Throughout this term, every lab and homework assignment has contributed to the development of our final project: assembling and programming a Pololu Romi robot. Our goal was to enable Romi to follow a line and autonomously navigate a predetermined course as quickly and efficiently as possible. This required integrating various sensors, implementing cascaded chassis and motor control, and designing a navigation algorithm for path planning and obstacle avoidance. To achieve this, we applied concepts from dynamics, control theory, embedded systems, and priority scheduling in task-oriented programming to ensure Romi could complete the challenge successfully.

## Hardware Components
We were supplied with a Romi chassis kit, a differential-drive platform with a 6.5-inch diameter and an integrated battery holder for six AA batteries. The two drive wheels, located on the outer edges of the chassis, use 70 mm Pololu wheels connected to Mini Plastic Gearmotors with quadrature encoders for position feedback. Two fixed ball casters at the front and rear provide additional stability. The chassis includes a motor driver and power distribution board that powers the motor encoders and our microcontroller.

Our microcontroller was a Nucleo board featuring an STM32 MCU with 76 pins available for powering and communicating with sensors. We used Python and the MicroPython library to program Romi, process sensor data, control the motors, and determine the robot’s path. Additionally, we incorporated a BNO055 Inertial Measurement Unit (IMU) to track orientation using an accelerometer, magnetometer, and gyroscope. Since Romi operates on a flat track, we were primarily concerned with its heading (rotation about the z-axis).

Beyond the supplied components, we purchased a Bluetooth module and infrared reflection line sensors to detect the black lines on the white track. Bump sensors were also integrated to detect collisions with walls or obstacles.

## Software Architecture
The majority of our work focused on designing, implementing, debugging, and fine-tuning the code that allowed Romi to navigate the maze quickly and reliably. Our code is structured into three levels of abstraction:

1. **High Level:** This includes the 'main' file, `cotask`, and `taskshare`. The main file runs the scheduler, determining which task executes next. `Cotask` implements the scheduler, defining priority and frequency for each task. `Taskshare` provides shared data structures, including shares and queues, to facilitate communication between tasks.
2. **Middle Level:** This consists of tasks that divide the robot's functionality into manageable sections. Our project runs five concurrent tasks: `navtask`, `usertask`, `sensortask`, `motortask`, and `controllertask`. Each task operates as a finite state machine, transitioning between states based on flags and shared variables.
3. **Low Level:** This consists of classes for individual components such as sensors, motors, and the grid representation of the track. These classes include methods for initializing attributes and modifying states to facilitate Romi’s movement and control.

## Shared Variables
To facilitate inter-task communication, we implemented ten shared variables:
- `calibrateb`, `calibratew`: Flags to trigger line sensor calibration for black and white backgrounds.
- `V`: Base effort input by the user.
- `L_eff`, `R_eff`: Motor efforts set based on sensor feedback.
- `Centroid`: Current center of the line reading (range: 1 to 13).
- `e`: Error value used for heading and straight-line control.
- `Psat`: Mean sensor reading from the line sensor array.
- `Run`: Flag determining whether Romi is active or idle.
- `Mode`: Determines the current drive mode (1 = line following, 2 = pivot, 3 = straight-line driving).

## Task Descriptions
### Navigation Task
The `nav` task is responsible for determining Romi’s path through the maze. It continuously updates the robot's desired heading based on its current position, the next target point, and the drive mode. The task ensures Romi follows the correct path using feedback from the IMU, encoders, and line sensors. It transitions between states such as line following, pivoting, and straight-line driving based on the current mode and environmental conditions.

## User Task
The user task handles user inputs and settings, allowing users to calibrate the line sensors, set the motor effort, and start or stop Romi. It processes commands sent via Bluetooth and consists of four states. First, it waits for the user to press Enter to calibrate the black background (calibrateb flag). The second state is similar but calibrates the white background. Once calibration is complete, the third state prompts the user to enter a base motor effort, setting Run to 1 and updating V with the user’s input. Finally, the fourth state checks if Run has been set back to 0 by the navtask, signifying that Romi has completed the maze. When this happens, the usertask returns to the third state, ready for new input.

## Sensor Task
The sensor task collects and processes data from the line and bump sensors, updating shared variables such as Centroid (line position), Psat (mean sensor reading), and bmp (bump sensor trigger flag). This task operates in three states. The first two states handle calibration of the line sensor array for black and white backgrounds, respectively. Once Run is set to 1, the task enters the third state, where it continuously updates Centroid, Psat, and bmp with real-time sensor readings. This ensures accurate tracking of Romi’s position on the track and detects any obstacles it may encounter.

## Motor Task
The motor task directly controls the speed and direction of Romi’s motors. It operates in two states: wait and run. In the wait state, the motors remain idle until Romi begins running. Once in the run state, the task adjusts the motor efforts (L_eff and R_eff) using a PID loop that ensures smooth and stable movement. The motor task receives the desired motor efforts from the controller task and compares them with the actual motor velocities measured by the encoders. It then applies PID control to correct any discrepancies, allowing Romi to follow lines accurately, execute precise pivots, and maintain a straight trajectory when needed.

## Controller Task
The controller task is responsible for closed-loop control of Romi’s movement. It uses a cascaded PID control system where the outer loop adjusts the chassis movement based on yaw, yaw rate, and centroid position, while the inner loop fine-tunes motor speeds by comparing the desired efforts with real-time encoder readings. This task operates in four states. The first state waits for Run to be set to 1. The other three states correspond to different drive modes: line following, pivoting, and straight driving. In line-following mode, the error is determined as Centroid - 7, where 7 represents the center of the line sensor array, and adjustments are made to keep Romi on track. In pivot mode, the error (e) is based on the difference between the desired heading from navtask and the actual heading from the IMU, allowing Romi to turn accurately. In straight-driving mode, the yaw rate is used as the error, ensuring Romi maintains a straight path without unintended deviations.

## Conclusion
The Mecha-01 Romi Term Project was a culmination of multiple engineering principles and hands-on development. By systematically designing the software and hardware, implementing robust control strategies, and fine-tuning our approach, we successfully created an autonomous Romi capable of navigating the maze efficiently. This project not only reinforced our understanding of embedded systems and robotics but also provided valuable experience in integrating sensors, real-time task scheduling, and control algorithms.

