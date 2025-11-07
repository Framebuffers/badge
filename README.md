# 🪪 badge

![](https://github.com/user-attachments/assets/b880e606-48bb-42b3-b6e2-5abcf55ab245)

Code for my furcon badge. Built for [SAFE2026](https://www.furcrew.cl/).


## 🖥️ Specs
  - Raspberry Pi 2 Zero W
    <img width="999" height="572" alt="image" src="https://github.com/user-attachments/assets/c1c99383-7074-4048-a446-fab4f8cc33db" />
  - [Waveshare 2.13" e-ink display hat for the Pi.](https://www.waveshare.com/product/displays/e-paper/epaper-3/2.13inch-e-paper-hat-plus.htm)


## ⚙️How does it work?

- `EPD` holds all the code to drive the display itself.
- `DisplayRoutines` extends `EPD` adding all the fun features. It has features to:
    - Add text
    - Create QRs from strings
    - Load bitmaps
    - Draw lines, curves
- `main.py` runs through a couple tests to go through several of these features.


## ℹ️ Things to know

It's gonna go on top of a laser, CNC-cut cardboard base. Probably going to print a base + integrated case for the Pi.
