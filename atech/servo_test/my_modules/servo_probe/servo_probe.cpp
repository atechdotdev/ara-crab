#include "servo_probe.h"

ServoProbe::ServoProbe(int pinA, int pinB) : pin_{pinA, pinB} {}
int ServoProbe::pin(int line) const { return (line == 0 || line == 1) ? pin_[line] : -1; }
