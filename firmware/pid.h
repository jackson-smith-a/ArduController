#pragma once

class PID
{
public:
  PID(double KP, double KI, double KD, double zero_output, double min_output, double max_output, double I_region, double I_max)
      : KP(KP), KI(KI), KD(KD), zero_output(zero_output), min_output(min_output), max_output(max_output), I_region(I_region), I_max(I_max)
  {
    prev_time = micros() / 1000.0;
  }

  double calculate(double measurement, double setpoint)
  {
    double current_time = micros() / 1000.0;
    double dt = current_time - prev_time;
    prev_time = current_time;

    double deriv = (measurement - prev_measurement) / dt;

    prev_measurement = measurement;

    double error = measurement - setpoint;
    // integrate if within region
    if (fabs(error) < I_region)
    {
      integrator += error * KI * dt;

      // make sure integrator stays within bounds
      if (fabs(integrator) > I_max)
      {
        integrator *= I_max / fabs(integrator);
      }
    }

    double output = KP * error + integrator + KD * deriv;

    if (fabs(output) > max_output)
    {
      output *= max_output / fabs(output);
    }

    if (fabs(output) < zero_output)
    {
      output = 0;
    }
    else if (fabs(output) < min_output)
    {
      output *= max_output / fabs(output);
    }

    return output;
  }

  double KP, KI, KD;
  double zero_output, min_output, max_output;
  double I_region, I_max;

  // private:
  double prev_time = 0;
  double prev_measurement = 0;
  double integrator = 0;
};
