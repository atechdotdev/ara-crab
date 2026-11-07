// Two MG90S servos on one Atech port, on jumper wires.
// Each servo uses one of the chip's 8 LEDC channels at 50 Hz: 8 servos per project at most.
#pragma once
#include <Arduino.h>

// MG90S (TowerPro, metal gear, 180 deg): 0..180 deg = 500..2400 us at 50 Hz. Pulses outside
// that drive it into its end stop, where it stalls and pulls its stall current from the 5 V supply.
#define MG90S_MIN_US 500
#define MG90S_MAX_US 2400

class Mg90sPair {
 public:
  Mg90sPair(int pinA, int pinB);
  void begin();
  void write(int which, float deg);       // 0..180
  void writeUs(int which, int us);        // clamped to MG90S_MIN_US..MG90S_MAX_US
  void detach(int which);
  float read(int which) const;

 private:
  int pin_[2];
  int ch_[2];
  float deg_[2];
};
