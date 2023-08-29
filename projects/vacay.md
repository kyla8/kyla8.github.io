---
layout: project
type: project
image: img/vacay/vacay-square.png
title: "Enhancing Laser Astronomy Insights through PAM Analysis"
date: 2023
published: true
labels:
  - Python
  - Matplotlib
  - Jupyter notebook
summary: "A responsive web application for travel planning that my team developed in ICS 415."
---

<img class="img-fluid" src="../img/vacay/vacay-home-page.png">

Robo-AO (https://www2.ifa.hawaii.edu/Robo-AO/)operational information presents an opportunity to assess the potential negative impacts of the growing population of satellites, especially the new mega-constellations, on laser astronomy and the ability to observe the sky. The Robo-AO systems are autonomous laser adaptive-optics instruments designed for high resolution astronomy with few-meter class telescopes. Robo-AO-2 is currently being commissioned at the University of Hawaii 2.2 meter telescope (UH88) on Maunakea. These systems fire a laser into the sky as a reference to understand how to correct for atmospheric disturbance. Predictive Avoidance Messages (PAMs) from US Space Command provide guidance, in the form of open/closure windows, on when and where it is safe to utilize lasers, i.e. to avoid damaging satellites. However, the plain text format of PAMs is difficult to directly comprehend, as it describes information in both spatial and temporal domains.

We are developing a python program that will leverage historical and newly received PAM files to understand satellite patterns and assist with operational decision-making. This visualization and analysis tool will analyze the percentage each area is open and how long until the next closure. 

<hr>

This experience provided me with a valuable opportunity to delve deeper into the realm of computer science and its profound implications within the field of astronomy. Furthermore, it allowed me to cultivate and refine my technical skill set, culminating in the organization and execution of a culminating symposium.

Here is some example code to illustrate Simple Schema use:

{% gist 9defa1fb3f4eb593ba5fa9eacedca960 %}
 
Source: <a href="https://github.com/theVacay/vacay">theVacay/vacay</a>
