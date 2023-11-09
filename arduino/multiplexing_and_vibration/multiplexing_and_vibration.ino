// ----
// esp32 devkit c
// ---
#include <SPI.h>

// headers
const int ELECTRO = 0xFF;
const int VIBRO = 0xFE;

// for shift registers (optocoupler switching)
const int SR_SER = 32;
const int SR_CLK = 33;
const int SR_RCLK = 25;
const int SR_CLR = 26;
const int SR_OE = 27;

const int STATE_OPEN = 0;
const int STATE_GND = 1;
const int STATE_HIGH = 2;

// change this when you changed the number of boards!!
const int register_num = (8 * 4) * 4;
int register_state[register_num] = { 0 };

const int channel_num = register_num / 2;
int channel_state[channel_num] = { STATE_OPEN };
// -----


// for DACs and LRAs
// HSPI
const int m_HSCK = 14;
const int m_HMISO = 12;
const int m_HMOSI = 13;
const int m_HCS = 15;

// VSPI
const int m_VSCK = 18;
const int m_VMISO = 19;
const int m_VMOSI = 23;
const int m_VCS = 5;

// chip select by myself
const int m_CS1 = 16;
const int m_CS2 = 17;
const int SPI_FREQ = 10 * 1000 * 1000;

const int MAX_AMP = 1023;  // LTC1660 - 10bit
const int BASE_OFFSET = (1.0 / 5.0) * MAX_AMP;
const int BASE_AMP = 1023 - BASE_OFFSET;

const int CHANNELS = 16;  //10;


const int VIBRATION = 0xFF;
const int CALIBRATION = 0xFE;

const int TABLE_LEN = 10000;
int table_index = 0;
const int sampling_rate = 10000;
int vibration_intensities[CHANNELS];
//float sin_table[TABLE_LEN];
float square_table[TABLE_LEN];
hw_timer_t *counter_timer;


// stimulation parameters
int frequency = 175;  // Hz
int vibrate_flags[CHANNELS];

void IRAM_ATTR increment_index() {
  int increment = (int)(frequency * ((double)TABLE_LEN / (double)sampling_rate));
  table_index = (table_index + increment) % TABLE_LEN;
}

// ------ electrical stimulation -----
void set_all_channel() {
  digitalWrite(SR_CLK, LOW);
  digitalWrite(SR_RCLK, LOW);

  for (int i = 0; i < channel_num; i++) {
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
  // --- for DACs + Vibrators
  pinMode(m_CS1, OUTPUT);
  pinMode(m_CS2, OUTPUT);
  // chip select
  digitalWrite(m_CS1, HIGH);  // dac1
  digitalWrite(m_CS2, HIGH);  // dac2

  // prepare table for square wave
  for (int i = 0; i < TABLE_LEN; i++) {
    if (i < TABLE_LEN / 2.0) {
      square_table[i] = 0;
    } else {
      square_table[i] = 1;
    }
  }

  for (int i = 0; i < CHANNELS; i++) {
    vibration_intensities[i] = MAX_AMP;
    vibrate_flags[i] = 0;
  }

  SPI.begin(m_VSCK, m_VMISO, m_VMOSI, m_VCS);
  SPI.setHwCs(false);  // manage cs by myself


  // there was noise on signals. I quitted using hw_timer
  //  counter_timer = timerBegin(0, 80, true);
  //  timerAttachInterrupt(counter_timer, &increment_index, true);
  //  timerAlarmWrite(counter_timer, 1000000 / sampling_rate, true);
  //  timerAlarmEnable(counter_timer);

  Serial.begin(921600);
  // Serial.begin(1500000);

  LTC1660_clear();
}

void LTC1660_clear() {
  int channel = 0x0F;
  int transfer_data = ((channel & 0x0F) << 12) | ((0 & 0x03FF) << 2);
  digitalWrite(m_CS1, LOW);
  digitalWrite(m_CS2, LOW);
  SPI.beginTransaction(SPISettings(SPI_FREQ, MSBFIRST, SPI_MODE0));
  SPI.write16(transfer_data);
  SPI.endTransaction();
  digitalWrite(m_CS1, HIGH);
  digitalWrite(m_CS2, HIGH);
}

void LTC1660_transfer(int channel, int d) {
  // if channel is larger than 8, change CS pin
  int CSpin = m_CS1;
  if (channel > 8) {
    channel -= 8;
    CSpin = m_CS2;
  }

  int transfer_data = ((channel & 0x0F) << 12) | ((d & 0x03FF) << 2);
  digitalWrite(CSpin, LOW);
  SPI.beginTransaction(SPISettings(SPI_FREQ, MSBFIRST, SPI_MODE0));
  SPI.write16(transfer_data);
  SPI.endTransaction();
  digitalWrite(CSpin, HIGH);
}


void vibrate_by_flags(int duration) {
  double timer = 0;
  // if frequency = 175 Hz, 175 pulses in 1 sec.
  int pulse_count = round((duration / 1000.0) / (1.0 / frequency));

  int counter = 0;
  int pulse = 0;
  while (counter <= pulse_count) {
    double delay_us = (1000000.0 / (double)frequency) / 2.0;
    double st = micros();
    for (int i = 0; i < CHANNELS; i++) {
      if (vibrate_flags[i] == 1) {
        // VIBRATE (send a signal)
        int amp = vibration_intensities[i] * 1;  //* square_table[table_index];
        int channel = i + 1;
        LTC1660_transfer(channel, amp);
      }
    }

    delay_us -= micros() - st;
    delayMicroseconds(delay_us);  // delay microseconds

    st = micros();
    delay_us = (1000000.0 / (double)frequency) / 2.0;
    LTC1660_clear();
    delay_us -= (micros() - st);
    delayMicroseconds(delay_us);
    counter++;
  }
  LTC1660_clear();
}

void vibrate(int channel, int duration) {
  // channel: 1 ~ 8, 9, 10
  // duration: ms
  //  int u_tick = 1; // 1 us
  // 250 ms -> 250 * 1000 us
  //  int vib_len = (int)(duration * 1000.0 / (double) u_tick);
  // due to latency of SPI, this may not work well.

  int pulse_count = round((duration / 1000.0) / (1.0 / frequency));
  int index = channel - 1;
  int counter = 0;
  int pulse = 0;
  while (counter <= pulse_count) {
    double delay_us = (1000000.0 / (double)frequency) / 2.0;
    double st = micros();

    // VIBRATE (send a signal)
    int amp = vibration_intensities[index] * 1;  //* square_table[table_index];
    LTC1660_transfer(channel, amp);


    delay_us -= micros() - st;
    delayMicroseconds(delay_us);  // delay microseconds

    st = micros();
    delay_us = (1000000.0 / (double)frequency) / 2.0;
    LTC1660_clear();
    delay_us -= (micros() - st);
    delayMicroseconds(delay_us);

    counter++;
  }
  LTC1660_clear();
}


int vib_index = 0;
void loop() {


  // each channel (N byte) + header (1 byte)
  if (Serial.available() >= CHANNELS) {
    int header = Serial.read();
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
    } else if (header == VIBRO) {
      for (int i = 0; i < CHANNELS; i++) {
        int amplitude = Serial.read();  // 0 ~ 255
        if (amplitude > 0) {
          vibrate_flags[i] = 1;
        } else {
          vibrate_flags[i] = 0;
        }
        vibration_intensities[i] = amplitude << 2;  // 2bit shift -> 0 ~ 1023;
      }

      int duration = Serial.read() * 100;  // changed from pulses to duration
      vibrate_by_flags(duration);

      for (int i = 0; i < CHANNELS; i++) {
        vibrate_flags[i] = 0;
      }
    }
  }


  // debug -- vibration
  //  int duration = 500;
  //  vibrate_flags[vib_index] = 1;
  //  vibrate_by_flags(duration);
  //  vibrate_flags[vib_index] = 0;
  //  vib_index = (vib_index + 1) % CHANNELS;
  //  delay(500);

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
