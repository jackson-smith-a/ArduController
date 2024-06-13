#include <QuadratureEncoder.h>
#include "motor.h"
#include "pid.h"

#define ENCODER_PIN_A 50
#define ENCODER_PIN_B 52

#define MOTOR_RPWM_PIN 2
#define MOTOR_LPWM_PIN 3

// stop all motors after this long without communication
#define TIMEOUT_MS 500

#define CYCLE_DELAY_MS 5

Encoders encoder(ENCODER_PIN_A, ENCODER_PIN_B);
PID pid{0, 0, 0, 0, 0, 0, 0, 0};

Motor motor(MOTOR_LPWM_PIN, MOTOR_RPWM_PIN, -1, &encoder, &pid);

typedef size_t (*EventFn)(uint8_t *, uint8_t *);

enum Command {
  SET_SPEED = 1,
  ENCODER_REQUEST = 2,
  SET_PID = 3,
  SET_POSITION = 4
};

struct EventHandler
{
  Command command;
  EventFn callback;
};

#define MAX_EVENTS 100

size_t events = 0;
EventHandler event_handlers[MAX_EVENTS];

long int time_of_last_heartbeat = 0;

void setup()
{
  register_event(SET_SPEED, handle_speed_change);
  register_event(ENCODER_REQUEST, handle_encoder_request);
  register_event(SET_PID, handle_set_pid);
  register_event(SET_POSITION, handle_set_position);
  motor.setup();
  Serial.begin(115200);
  delay(500);

  time_of_last_heartbeat = millis();
}

void register_event(Command instruction, EventFn callback)
{
  EventHandler event_handler;
  event_handler.command = instruction;
  event_handler.callback = callback;

  event_handlers[events++] = event_handler;

  events %= MAX_EVENTS; // overwriting is better than writing to random memory
}

size_t handle_set_pid(uint8_t *reply, uint8_t *data)
{
  pid.KP = read_float(data, 0);
  pid.KI = read_float(data, 4);
  pid.KD = read_float(data, 8);

  pid.zero_output = read_float(data, 12);
  pid.min_output = read_float(data, 16);
  pid.max_output = read_float(data, 20);

  pid.I_region = read_float(data, 24);
  pid.I_max = read_float(data, 28);

  return 0;
}

size_t handle_set_position(uint8_t *reply, uint8_t *data)
{
  long int pos = read_int(data, 0);
  motor.set_position_mode();
  motor.set_position(pos);

  return write_int(reply, pos, 0);
}

size_t handle_speed_change(uint8_t *reply, uint8_t *data)
{
  int speed = (int)read_int(data, 0);
  motor.set_analog(speed);
  motor.set_analog_mode();
  return 0;
}

size_t handle_encoder_request(uint8_t *reply, uint8_t *data)
{
  long int enc = motor.get_enc();

  size_t written_length = write_int(reply, enc, 0);

  return written_length;
}

void loop()
{
  motor.update();
  while (Serial.available())
  {
    read_serial();
  }

  long int time_since_heartbeat = millis() - time_of_last_heartbeat;

  if (time_since_heartbeat > TIMEOUT_MS)
  {
    stop_motors();
  }

  delay(CYCLE_DELAY_MS);
}

void stop_motors()
{
  motor.stop();
}

#define INCOMING_BUFFER 200
int buffer_index = 0;
uint8_t msg_buffer[INCOMING_BUFFER];

void read_serial()
{
  int new_byte = Serial.read();

  // no byte to read
  if (new_byte == -1)
  {
    return;
  }

  time_of_last_heartbeat = millis();

  msg_buffer[buffer_index++] = (uint8_t)new_byte;

  if (new_byte != 0)
  {
    // wait until full, 0-delimited message is sent
    return;
  }

  uint8_t decoded[INCOMING_BUFFER];

  size_t len = cobs_decode(decoded, msg_buffer, buffer_index);

  Command command = (Command)decoded[0];
  uint8_t *data = &decoded[1];

  dispatch(command, data);

  buffer_index = 0;
}

#define REPLY_LENGTH 200
uint8_t reply[REPLY_LENGTH];

uint8_t encoded_reply[REPLY_LENGTH + 2];

void dispatch(Command command, uint8_t *data)
{
  for (size_t i = 0; i < events; ++i)
  {
    EventHandler handler = event_handlers[i];

    if (handler.command == command)
    {
      size_t reply_len = handler.callback(reply, data);

      if (reply_len)
      {
        size_t enc_reply_len = cobs_encode(encoded_reply, reply, reply_len);
        Serial.write(encoded_reply, enc_reply_len);
      }
    }
  }
}

size_t cobs_encode(uint8_t *dst, const uint8_t *src, size_t len)
{
  uint8_t next_zero = 1;

  size_t write_index = 1;
  size_t next_zero_index = 0;

  for (size_t i = 0; i < len; ++i)
  {
    uint8_t val = src[i];
    if (val == 0)
    {
      // encoder proper zero offset
      dst[next_zero_index] = next_zero;
      next_zero = 1;
      next_zero_index = write_index++;
    }
    else
    {
      dst[write_index++] = val;
      next_zero++;
      // if we've hit max, encode placeholder
      if (next_zero == 0xFF)
      {
        dst[next_zero_index] = next_zero;
        next_zero = 1;
        next_zero_index = write_index++;
      }
    }
  }

  // patch in final zero location
  dst[next_zero_index] = next_zero;

  // add trailing zero
  dst[write_index++] = 0;

  return write_index;
}

size_t cobs_decode(uint8_t *dst, const uint8_t *src, size_t len)
{
  size_t dst_idx = 0;
  // don't increment i here so we can do it inside differently depending on data
  for (size_t i = 0; i < len;)
  {
    uint8_t next_zero = src[i++];

    // go until we've hit the next zero
    for (size_t j = 1; j < next_zero && i < len; ++j)
    {
      // copy over bytes normally
      dst[dst_idx++] = src[i++];
    }

    // add in the zero unlesss it was a placeholder
    if (next_zero != 0xFF && i < len - 1)
    {
      dst[dst_idx++] = 0;
    }
  }

  return dst_idx;
}

float read_float(uint8_t *buffer, int index)
{
  uint8_t byte0 = buffer[index];
  uint8_t byte1 = buffer[index + 1];
  uint8_t byte2 = buffer[index + 2];
  uint8_t byte3 = buffer[index + 3];

  uint8_t byte_array[] = {byte0, byte1, byte2, byte3};
  float float_value;
  memcpy(&float_value, &byte_array, sizeof(float_value));

  return float_value;
}

long int read_int(uint8_t *buffer, int index)
{
  uint8_t byte0 = buffer[index];
  uint8_t byte1 = buffer[index + 1];
  uint8_t byte2 = buffer[index + 2];
  uint8_t byte3 = buffer[index + 3];

  uint8_t byte_array[] = {byte0, byte1, byte2, byte3};
  long int value;
  memcpy(&value, byte_array, sizeof(value));

  return value;
}

size_t write_int(uint8_t *buffer, long int val, size_t index)
{
  memcpy(buffer + index, &val, sizeof(val));
  return sizeof(val) + index;
}

size_t write_float(uint8_t *buffer, float val, size_t index)
{
  memcpy(buffer + index, &val, sizeof(val));
  return sizeof(val) + index;
}
