#pragma once
#include <QuadratureEncoder.h>
#include "pid.h"

enum MotorMode
{
  ANALOG,
  POSITION_PID,
  STOPPED
};

class Motor
{
public:
  Motor(int LPWM_pin, int RPWM_pin, int polarity, Encoders *encoder, PID *pid)
      : LPWM_pin(LPWM_pin), RPWM_pin(RPWM_pin), polarity(polarity), encoder(encoder), pid(pid) {}

  void setup()
  {
    pinMode(RPWM_pin, OUTPUT);
    pinMode(LPWM_pin, OUTPUT);

    stop();
  }

  void stop()
  {
    mode = STOPPED;
    write_analog(0);
  }

  void update()
  {
    switch (mode)
    {
    case ANALOG:
      write_analog(speed);
      break;
    case POSITION_PID:
    {
      double output = pid->calculate((double)get_enc(), (double)setpoint);
      write_analog((int)output);
      break;
    }
    case STOPPED:
      stop();
      break;
    }
  }

  void set_position(long int pos)
  {
    setpoint = pos;
  }

  void set_analog_mode()
  {
    mode = ANALOG;
  }

  void set_position_mode()
  {
    mode = POSITION_PID;
  }

  void set_analog(int speed)
  {
    this->speed = speed;
  }

  // 0 < speeds <= 255 forwards, -255 <= speed < 0 backwards
  void write_analog(int speed)
  {
    // clamp to proper range
    speed = max(min(speed, 255), -255) * polarity;

    if (speed < 0)
    {
      analogWrite(RPWM_pin, -speed);
      analogWrite(LPWM_pin, 0);
    }

    else
    {
      analogWrite(RPWM_pin, 0);
      analogWrite(LPWM_pin, speed);
    }
  }

  long int get_enc()
  {
    return encoder->getEncoderCount();
  }

  void set_enc(long int count)
  {
    encoder->setEncoderCount(count);
  }

private:
  long int setpoint;
  int speed;

  int polarity = 1;

  int LPWM_pin;
  int RPWM_pin;

  Encoders *encoder;
  PID *pid;

  MotorMode mode = ANALOG;
};
