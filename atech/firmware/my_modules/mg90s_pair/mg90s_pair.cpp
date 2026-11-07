#include "mg90s_pair.h"

// Each servo gets one of the ESP32-S3's 8 LEDC channels at 50 Hz, 14-bit: a 20 ms
// period in 16384 steps, 1.22 us per step. So a project takes at most 8 servos (4 pairs);
// the 9th is refused with a message.
namespace {
constexpr int kFreq = 50, kBits = 14;
constexpr int kMinUs = MG90S_MIN_US, kMaxUs = MG90S_MAX_US;   // 0..180 deg, and the writeUs() limits
int nextChannel = 0;
}  // namespace

Mg90sPair::Mg90sPair(int pinA, int pinB) : pin_{pinA, pinB}, ch_{-1, -1}, deg_{90, 90} {}

void Mg90sPair::begin() {
  for (int i = 0; i < 2; i++) {
    if (nextChannel >= 8) {
      Serial.printf("mg90s_pair: no LEDC channel left for the servo on GPIO %d (8 servos at most)\n", pin_[i]);
      continue;
    }
    ch_[i] = nextChannel++;
    ledcSetup(ch_[i], kFreq, kBits);
    ledcWrite(ch_[i], 0);                 // no pulse until the first write: the servo stays limp
    ledcAttachPin(pin_[i], ch_[i]);
  }
}

void Mg90sPair::writeUs(int which, int us) {
  if (which < 0 || which > 1 || ch_[which] < 0) return;
  us = constrain(us, kMinUs, kMaxUs);
  ledcWrite(ch_[which], (uint32_t)((uint64_t)us * ((1 << kBits) - 1) / 20000));
}

void Mg90sPair::write(int which, float deg) {
  if (which < 0 || which > 1) return;
  deg = constrain(deg, 0.0f, 180.0f);
  deg_[which] = deg;
  writeUs(which, kMinUs + (int)(deg * (kMaxUs - kMinUs) / 180.0f + 0.5f));
}

void Mg90sPair::detach(int which) {
  if (which < 0 || which > 1 || ch_[which] < 0) return;
  ledcWrite(ch_[which], 0);
}

float Mg90sPair::read(int which) const { return (which == 0 || which == 1) ? deg_[which] : 0.0f; }
