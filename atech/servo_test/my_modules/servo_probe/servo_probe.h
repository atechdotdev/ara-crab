#pragma once
#include <Arduino.h>

class ServoProbe {
 public:
  ServoProbe(int pinA, int pinB);
  int pin(int line) const;   // 0 = Line A, 1 = Line B
 private:
  int pin_[2];
};
