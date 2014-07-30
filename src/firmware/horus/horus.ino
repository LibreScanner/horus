//--------------------------------------------------------------
//-- Horus Firmware. Compatible with ZUM Scan Shield V.1
//--------------------------------------------------------------
//-- Code based on (c) Juan Gonzalez-Gomez (Obijuan), May-2013
//-- (c) Jesus Arroyo Torrens, October/November-2013
//-- GPL license
//--------------------------------------------------------------

//----------------------------------------------------------------
//-- The communication with the PC is by the serial port (19200 bauds)
//-- The config frame contains ascii characters. The format is the 
//-- following:
//--
//--  bddddmmmmmq , where
//--
//--  b is the frame header
//--  q is the frame footer
//--  dddd is the degress in one step * 100
//--  mmmmm is the delay in microseconds
//--
//-- The frame should finish one of the following characters:
//--  lf
//--
//-- Example:  b004500100q   --> step = 0.45º delay = 100 us
//--
//-- The command frame is a byte. The format is the following:
//--
//-- 10 cc vv 01
//--
//--  10 is the header
//--  01 is the footer
//--  cc is the command: 00 motor, 01 laser right, 10 laser left, 11 laser right&left
//--  vv is the value: laser on/off X0/X1, motor NoOp/SCW/SCCW/NoOp 00/01/10/11
//--
//-- Example:   10 00 01 01   --> Motor Step CW
//--
//-- NOTE: the command 11 00 00 11 sets configuration mode (fals default)
//--
//-- A complete example is presented below:
//--
//--    -> b004500100q\n
//--    <- bq\n
//--    -> 0b10000101
//--    -> 0b10010101
//--    -> 0b11000011
//--    -> b010000800q\n
//--    <- bq\n
//--    -> 0b10000101
//--    ...
//--

//-----------------------------------------------------------------

//-- Definitions for the frames
#define FRAME_HEADER 'b'
#define FRAME_FOOTER 'q'

//-- Pinout
//
//  Laser 1: 2
//  Laser 2: 3
//  Laser 3: 4
//  Laser 4: 5
//
//  LDR 1: A0
//  LDR 2: A1
//
//  Motor 1:
//    - Enable: 9
//    - Step:  12
//    - Dir:   13 
//
//  Motor 2:
//    - Enable: 6
//    - Step:   7
//    - Dir:    8

#define LASER_LEFT_PIN    2
#define LASER_RIGHT_PIN   3

#define MOTOR_STEP_PIN   12
#define MOTOR_DIR_PIN    13

#define ENABLE_PIN        9

#define USTEP_RESOLUTION  16
#define STEP_DEGREES     1.8


//---------- Global variables

float step_value; //-- Motor step
int step_delay; // -- Motor delay

float uStep = USTEP_RESOLUTION / STEP_DEGREES;

//-- Buffer for storing the received commands
#define BUFSIZE 11
char buffer[BUFSIZE+1];
int buflen = 0;

//-- Binary commands
#define BIN_ACK          B10000001
#define BIN_CHK          B10000001
#define BIN_CHK_MASK     B11000011
#define BIN_CMD_MASK     B00110000
#define BIN_VALUE_MASK   B00001100
#define BIN_LL_MASK      B00100000
#define BIN_LR_MASK      B00010000
#define BIN_ONOFF_MASK   B00000100

#define BIN_CONFIG_MODE  B11000011

boolean config_mode = false;
boolean cmd_ready = false;

void setup()
{ 
  //-- Configure the serial port
  Serial.begin(19200);
  
  //-- Configure the lasers
  pinMode(LASER_LEFT_PIN, OUTPUT);
  pinMode(LASER_RIGHT_PIN, OUTPUT);
    
  //-- Turn off the lasers
  digitalWrite(LASER_LEFT_PIN, LOW);
  digitalWrite(LASER_RIGHT_PIN, LOW);
  
  //-- Configure motor
  pinMode(MOTOR_STEP_PIN, OUTPUT);
  pinMode(MOTOR_DIR_PIN, OUTPUT);
  
  digitalWrite(MOTOR_STEP_PIN, LOW);
  digitalWrite(MOTOR_DIR_PIN, HIGH);
  
  //-- Configure !enable
  pinMode(ENABLE_PIN, OUTPUT);
  
  //-- Turn on the !enable
  digitalWrite(ENABLE_PIN, LOW);
}

void read_frame()
{
  //-- For reading the serial input
  char serial_char;

  if (Serial.available() && buflen < BUFSIZE) {
    
    //-- Read the char
    serial_char = Serial.read();
    
    //-- Detect blank caracters. They are interpreted as the end of a command    
    if (serial_char == '\n') {

      //-- Store the end of string
      buffer[buflen]=0;
      
      //-- Now there is a command ready to be processed!
      if (buflen>0)
        cmd_ready = true;
    }
    //-- Normal character: store it in the buffer  
    else {
      buffer[buflen]=serial_char;
      buflen++;
    }
  }
}

boolean process_config()
{  
  //-- Parse the command
  //-- First check if the header is ok
  if (buffer[0] != FRAME_HEADER)
    return false;
    
  //-- Check if the footer is ok
  if (buffer[10] != FRAME_FOOTER)
    return false;

  //-- Read step value
  if ((step_value = read_value(1, 4, 10)) == -1)
    return false;

  //-- Read step delay
  if ((step_delay = read_value(5, 9, 10000)) == -1)
    return false;

  return true;
}

float read_value(int b, int e, float factor)
{
  float ret = 0;
  
  for (int i = b; i <= e; i++)
  {
    //-- Check if the character is a number
    if (is_not_number(buffer[i]))
      return -1;
    ret += (buffer[i] - '0') * factor;
    factor /= 10;
  }
  
  return ret;
}

boolean is_not_number(char c)
{
  return (c < 48) && (c > 57);
}

boolean process_cmd(byte cmd)
{
  //-- Check command type
  if ((cmd & BIN_CHK_MASK) != BIN_CHK)
    return false;
  
  //-- Get value
  int value = ((cmd & BIN_ONOFF_MASK) == BIN_ONOFF_MASK) ? HIGH : LOW;
  
  //-- Check Laser commands
  if ((cmd & BIN_LL_MASK) == BIN_LL_MASK)
      digitalWrite(LASER_LEFT_PIN, value);
  if ((cmd & BIN_LR_MASK) == BIN_LR_MASK)
      digitalWrite(LASER_RIGHT_PIN, value);
     
  //-- Check Motor commands
  if ((cmd & BIN_CMD_MASK) == 0)
  {
    switch((cmd & BIN_VALUE_MASK) >> 2)
    {
      //-- Disable
      case 0:
        digitalWrite(ENABLE_PIN, HIGH);
        
      //-- Motor CW
      case 1:
        digitalWrite(MOTOR_DIR_PIN, HIGH);
        Step(MOTOR_STEP_PIN, step_value);
        break;
        
      //-- Motor CCW
      case 2:
        digitalWrite(MOTOR_DIR_PIN, LOW);
        Step(MOTOR_STEP_PIN, step_value);
        break;
        
      //-- Enable
      case 3:
        digitalWrite(ENABLE_PIN, LOW);
  
      default:
         break;
    }
  }
  
  return true;
}

void Pulse(int step_pin)
{  
  digitalWrite(step_pin, LOW);
  delayMicroseconds(step_delay);
  digitalWrite(step_pin, HIGH);
  delayMicroseconds(step_delay);
}

void Step(int step_pin, float deg)
{
  int limit = uStep * deg;
  for (int i = 0; i < limit; i++)
    Pulse(step_pin);
}

void loop() 
{
  if (Serial.available()) {
    if (config_mode) {
      //-- Configuration Frame
      boolean handshake = false;
     
      do {
        //-- Task: Read the information from the serial port
        read_frame();
        
        //-- If there is a command ready or the buffer is full
        //-- process the command!!
        if (cmd_ready || buflen==BUFSIZE) {
        
          //-- Process the command
          handshake = process_config();
          
          //-- Command processed!
          cmd_ready=false;
          buflen=0;
        }
      }
      while(!handshake);
      
      Serial.print("bq\n");
  
      config_mode = false;
    }
    else {
      //-- Read command
      byte cmd = Serial.read();
      
      config_mode = cmd == BIN_CONFIG_MODE;
      
      if (!config_mode) {
        //-- Process the command
        process_cmd(cmd);
        //if (process_cmd(cmd))
        //-- If success send acknowledge
        //Serial.print(BIN_ACK); TODO
      } 
    }
  }
  
  delay(1);
}



