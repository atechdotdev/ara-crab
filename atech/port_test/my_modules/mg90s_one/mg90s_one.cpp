#include "mg90s_one.h"

namespace {
constexpr int kFreq = 50, kBits = 14;    // 20 ms in 16384 steps, 1.22 us each
int nextChannel = 0;
}  // namespace

Mg90sOne::Mg90sOne(int pin) : pin_(pin), ch_(-1), deg_(90) {}

void Mg90sOne::begin() {
  if (nextChannel >= 8) {
    Serial.printf("mg90s_one: no LEDC channel left for the servo on GPIO %d (8 servos at most)\n", pin_);
    return;
  }
  ch_ = nextChannel++;
  ledcSetup(ch_, kFreq, kBits);
  ledcWrite(ch_, 0);                     // no pulse until the first write: limp
  ledcAttachPin(pin_, ch_);
}

void Mg90sOne::writeUs(int us) {
  if (ch_ < 0) return;
  us = constrain(us, MG90S_ONE_MIN_US, MG90S_ONE_MAX_US);
  ledcWrite(ch_, (uint32_t)((uint64_t)us * ((1 << kBits) - 1) / 20000));
}

void Mg90sOne::write(float deg) {
  deg = constrain(deg, 0.0f, 180.0f);
  deg_ = deg;
  writeUs(MG90S_ONE_MIN_US + (int)(deg * (MG90S_ONE_MAX_US - MG90S_ONE_MIN_US) / 180.0f + 0.5f));
}

void Mg90sOne::detach() {
  if (ch_ >= 0) ledcWrite(ch_, 0);
}
