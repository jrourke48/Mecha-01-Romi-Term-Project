# Mecha-01 Romi Term Project

## Overview

Throughout this term, every lab and homework assignment contributed to the development of our final project: assembling and programming a Pololu Romi robot. Our goal was to enable Romi to follow a line and autonomously navigate a predetermined course as quickly and efficiently as possible. This required integrating various sensors, implementing cascaded chassis and motor control, and designing a navigation algorithm for path planning and obstacle avoidance. To achieve this, we integrated concepts from dynamics, control theory, embedded systems, and task-oriented programming with priority scheduling, ensuring Romi could complete the challenge. Below is a video showing our Romi completing this term's game track.

https://github.com/user-attachments/assets/5a8826ec-0096-449b-a98e-756b12be9f72

## The Course
The course consists of a black line on a white background containing 5 main checkpoints 2 cups that each deduct your overall time by 5 seconds as well as some other notable obstacles see the state transition diagrams branch for the PDF of the track. There are five main obstructions in the line: the  "diamond" is the first where the path divides into two and back then to one forming a diamond pattern. Shortly after the diamond the line becomes dashed and then in between CP3 and 4 there are perpendicular lines running along the path as well. After checkpoint four the line is lost altogether and is replaced with a faint grid pattern engulfed by an 80-20 cage requiring precise control of Romi through it to not hit the cage. After the cage, the line returns at CP5 and Romi thinks it's smooth sailing to the finish but the last obstruction is a wall between the line and the finish/start. Our Romi navigates these checkpoints using a combination of line-following, pivoting, and straight-line driving. Some sections demand quick transitions between drive modes, and others require precise control testing Romi’s ability to adjust its driving based on sensor feedback.
[Game_Track.pdf](https://github.com/user-attachments/files/19256793/Game_Track.pdf)

## Hardware Components

We were supplied with a Romi chassis kit, a differential-drive platform with a 6.5-inch diameter, and an integrated battery holder for six AA batteries. The two drive wheels, located on the outer edges of the chassis, use 70 mm Pololu wheels connected to Mini Plastic Gearmotors with quadrature encoders for position feedback. Two fixed ball casters at the front and rear provide additional stability. The chassis includes a motor driver and power distribution board that powers the motor encoders and our microcontroller.

We used a Nucleo board with an STM32 MCU, which provides 76 pins for power distribution and sensor communication. We used Python and the MicroPython library to program Romi, process sensor data, control the motors, and determine the robot’s path. Additionally, we incorporated a BNO055 Inertial Measurement Unit (IMU) to track orientation using an accelerometer, magnetometer, and gyroscope. Since Romi operates on a flat track, we were primarily concerned with its heading (rotation about the z-axis).


Beyond the supplied components, we integrated a Bluetooth module for wireless control and infrared reflection line sensors to detect the black lines on the white track. Bump sensors were also included to detect collisions with walls or obstacles. We made the mistake of buying too large of a line sensor which made it impossible to mount the sensor on Romi so we had to 3D print a mount to make the line sensors fit see the state transition diagrams branch for the CAD files of Romi.
![image](https://github.com/user-attachments/assets/2402c3d5-ea50-4bbb-9848-50a96701016f)

## Software Architecture

Our software design follows a structured hierarchy with three levels of abstraction:

1. **High Level:** Includes the 'main' file, `cotask`, and `taskshare`. The main file runs the scheduler, determining which task executes next. `Cotask` implements the scheduler, defining priority and frequency for each task. `Taskshare` provides shared data structures, including shares and queues, to facilitate communication between tasks.
2. **Middle Level:** Consists of tasks that divide Romi’s functionality into manageable sections. Our project runs five concurrent tasks: `navtask`, `usertask`, `sensortask`, `motortask`, and `controllertask`. Each operates as a finite state machine, transitioning between states based on flags and shared variables.
3. **Low Level:** Comprises classes for individual components such as sensors, motors, and the grid representation of the track. These classes define methods for initializing attributes and modifying states to facilitate Romi’s movement and control.

## Shared Variables

To facilitate inter-task communication, we implemented ten shared variables:

- `calibrateb`, `calibratew`: Flags to trigger line sensor calibration.
- `V`: Base effort input by the user.
- `L_eff`, `R_eff`: Motor efforts set based on sensor feedback.
- `Centroid`: Current center of the line reading (range: 1 to 13).
- `e`: Error value used for heading and straight-line control.
- `Psat`: Mean sensor reading from the line sensor array.
- `Run`: Flag determining whether Romi is active or idle.
- `Mode`: Determines the current drive mode (1 = line following, 2 = pivot, 3 = straight-line driving).
- `bmp`: Flag determining if any bump sensors are currently triggered.

## Navigation Task

The `navtask` determines Romi’s path through the maze using feedback from the IMU, encoders, bump sensors, and line sensors. It follows a series of sequential states, each representing a checkpoint on the grid. The navigation system is built around two primary classes. The `Grid` class defines the track’s boundaries and checkpoints, utilizing a nested `Point` class. The `Nav` class manages movement and tracking, featuring a nested `Line` class for calculating distances and headings between points.

Key methods in `navtask` include `update_yaw()`, which determines Romi’s heading relative to its starting position; `update_all()`, which tracks the average encoder position change to measure movement; `check_target()`, which verifies if Romi has reached its designated checkpoint; and `new_target()`, which updates Romi’s next target upon reaching the current one.

The navigation system consists of the following states:

- **S0 Wait:** Stationary, waiting for calibration, a base effort, and `Run` to be set.
- **S1 Start:** Establishes an absolute heading reference and checks `Psat` to see if Romi has reached CP0.
- **S2 CP0:** Pivots toward checkpoint 1 and then drives the distance determined between the points set in the navigation.
- **S3 CP1:** Line follows to checkpoint 2, checking `Psat` and the heading.
- **S4 CP2:** Pivots toward an arbitrary point on the line between CP2 and CP3 and drives forward, hitting the first cup.
- **S5 -5s1:** Line follows to checkpoint 3, checking for a rise in `Psat`.
- **S6 CP3:** Adjusts heading and drives straight toward checkpoint 4.
- **S7 CP4:** Adjusts heading and drives straight toward the intermediate point.
- **S8 INT:** Adjusts heading and drives straight toward checkpoint 5.
- **S9 CP5:** Returns to line following, checking `bmp` to detect wall impact.
- **S10 BMP:** Adjusts heading and drives straight toward the second cup.
- **S11 -5s2:** Adjusts heading and drives straight toward the final checkpoint before the finish line.
- **S12 Finish:** Completes the final segment of the maze and returns to the finish line.

### User Task

The `usertask` manages user input, allowing calibration, effort setting, and start/stop commands via Bluetooth. It consists of four states: calibrating black, calibrating white, setting motor effort, and waiting for task completion.

### Sensor Task

The `sensortask` continuously updates shared variables for the line and bump sensors. It has three states: calibration for black and white backgrounds and real-time sensor monitoring when `Run` is activated.

### Motor Task

The `motortask` controls Romi’s motors with a PID loop, ensuring accurate movement and smooth transitions. It has two states: idle and active, adjusting motor efforts based on encoder feedback.

### Controller Task

The `controllertask` implements cascaded PID control for chassis movement. It operates in four states: idle, line following, pivot, and straight-driving. Each mode adjusts Romi’s movement based on sensor feedback to maintain accurate navigation.

## Conclusion

The Mecha-01 Romi Term Project integrated multiple engineering and computer science disciplines, including dynamics, embedded systems, and control theory. As well as strengthening our skills in the mechanical side of the project like mounting all the sensors properly within the space constraints Romi poses. Through hard work and endless hours spent on hardware and software development, we successfully created an autonomous Romi capable of navigating as quickly and efficiently as possible. This project reinforced our understanding of robotics and provided valuable experience in time management, project planning, software and sensor integration, task scheduling, and control as well as countless other things. Future enhancements for Romi could focus on improving obstacle avoidance especially in the 80-20, fine-tuning the PID controller, and optimizing Romi’s navigation speed for different portions of the track instead of using a base speed for the entire course.


