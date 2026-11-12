// One MG90S servo on an Atech port's Line A, on jumper wires. One LEDC channel at 50 Hz.
#pragma once
#include <Arduino.h>

#define MG90S_ONE_MIN_US 500     // 0 deg
#define MG90S_ONE_MAX_US 2400    // 180 deg

class Mg90sOne {
 public:
  explicit Mg90sOne(int pin);
  void begin();
  void write(float deg);         // 0..180
  void writeUs(int us);          // clamped to 500..2400
  void detach();
  float read() const { return deg_; }

 private:
  int pin_, ch_;
  float deg_;
};
