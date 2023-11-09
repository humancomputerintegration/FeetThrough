// ----
// 2023/3/10 Keigo Ushiyama (ushiyama@kaji-lab.jp)
// code to drive shiftregisters with esp32 devkit c
// ---

// headers
const byte ELECTRO = 0xFF;

// for shift registers (optocoupler switching)
const int SR_SER = 32;
//const int SR_CLK = 33;
const int SR_CLK = 25;

//const int SR_RCLK = 25;
const int SR_RCLK = 33;

const int SR_CLR = 26;
const int SR_OE = 27;

const int STATE_OPEN = 0;
const int STATE_GND = 1;
const int STATE_HIGH = 2;

const int register_num_one_board = 8 * 4;
const int board_num = 4; // change this when you changed the number of boards!!
const int register_num = register_num_one_board * board_num;
int register_state[register_num] = { 0 };

const int channel_num = register_num / 2;
int channel_state[channel_num] = { STATE_OPEN };
// -----


// ------ switching for electrical stimulation -----
void set_all_channel() {
  digitalWrite(SR_CLK, LOW);
  digitalWrite(SR_RCLK, LOW);

  for (int i = channel_num - 1; i >= 0; i--) {
    if (channel_state[i] == STATE_OPEN) {
      // LOW
      digitalWrite(SR_SER, LOW);
      digitalWrite(SR_CLK, HIGH);
      digitalWrite(SR_CLK, LOW);
      // LOW
      digitalWrite(SR_SER, LOW);
      digitalWrite(SR_CLK, HIGH);
      digitalWrite(SR_CLK, LOW);
    } else if (channel_state[i] == STATE_HIGH) {
      // LOW
      digitalWrite(SR_SER, LOW);
      digitalWrite(SR_CLK, HIGH);
      digitalWrite(SR_CLK, LOW);
      // HIGH
      digitalWrite(SR_SER, HIGH);
      digitalWrite(SR_CLK, HIGH);
      digitalWrite(SR_CLK, LOW);
    } else if (channel_state[i] == STATE_GND) {
      // HIGH
      digitalWrite(SR_SER, HIGH);
      digitalWrite(SR_CLK, HIGH);
      digitalWrite(SR_CLK, LOW);
      // LOW
      digitalWrite(SR_SER, LOW);
      digitalWrite(SR_CLK, HIGH);
      digitalWrite(SR_CLK, LOW);
    }
  }

  digitalWrite(SR_SER, LOW);
  digitalWrite(SR_RCLK, HIGH);
  digitalWrite(SR_RCLK, LOW);
}

// ------

void setup() {
  // --- for shift registers
  pinMode(SR_SER, OUTPUT);
  pinMode(SR_CLK, OUTPUT);
  pinMode(SR_RCLK, OUTPUT);
  pinMode(SR_CLR, OUTPUT);
  pinMode(SR_OE, OUTPUT);

  digitalWrite(SR_OE, LOW);
  digitalWrite(SR_CLR, HIGH);

  for (int i = 0; i < channel_num; i++) {
    channel_state[i] = STATE_OPEN;
  }
  set_all_channel();

  Serial.begin(921600);

}

void loop() {
  // each channel (N byte) + header (1 byte)
  if (Serial.available() > 0) {
    char header = Serial.read();
    if (header == ELECTRO) {
      byte state = 0;
      for (int i = 0; i < channel_num; i++) {
        state = Serial.read();
        if (state < 0 || state > 2) {
          // out of range. something went wrong
          continue;
        }
        channel_state[i] = state;
      }
      set_all_channel();
    } 
  }



  // debug -- measurement
  //  int sleep = 200;
  //  channel_state[0] = STATE_HIGH;
  //  channel_state[1] = STATE_GND;
  //  channel_state[30] = STATE_HIGH;
  //  channel_state[31] = STATE_GND;
  //  set_all_channel();
  //  delayMicroseconds(sleep);
  //  channel_state[0] = STATE_GND;
  //  channel_state[1] = STATE_HIGH;
  //  channel_state[30] = STATE_GND;
  //  channel_state[31] = STATE_HIGH;
  ////  channel_state[32] = STATE_GND;
  //  set_all_channel();
  //  delayMicroseconds(sleep);
  // ----

}
