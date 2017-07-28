
private int ROBOT_X;
private int ROBOT_Y;
private float servoBaseAngle = 0.0f;
private float servoForearmAngle = 0.0f;
private float servoHandAngle = 0.0f;
private float servoEndpointAngle = 0.0f;
private char select = 'b';
private boolean pressed = false;
private float world_width = 200f;
private float world_height = 200f;
private float mX;
private float mY;


public void settings() {
  size(800, 600);
}

public void setup() {
  ROBOT_X = worldToScreen(50);
  ROBOT_Y = worldToScreen(50);

  smooth();
  frameRate(30);
  textSize(32);
}


public void draw() {
  background(255);

  pushMatrix();
  translate(0, 0);

  if (mousePressed) {
    if (!pressed) {
      pressed = true;
      mX = mouseX;
      mY = mouseY;

      if (mY < worldToScreen(50)) select = 'e';
      else if (mY < worldToScreen(100)) select = 'h';
      else if (mY < worldToScreen(150)) select = 'f';
      else if (mY < worldToScreen(200)) select = 'b';
    }

    ellipse(mX, mY, worldToScreen(10), worldToScreen(10));
    stroke(5);
    line(mX, mY, mouseX, mouseY);
  } else pressed = false;
  drawRobot();
  drawText();
  popMatrix();
  stroke(5);
  line(width/2,worldToScreen(50),width/2,worldToScreen(150));  
  line(width/2,worldToScreen(50),width,worldToScreen(50));
  text("Forearm",width/2,worldToScreen(50));
  line(width/2,worldToScreen(100),width,worldToScreen(100));
  text("Hand",width/2,worldToScreen(100));
  line(width/2,worldToScreen(150),width,worldToScreen(150));
}

private void drawRobot() {
  noStroke();
  fill(38, 38, 200);
  drawServoBase();
}

private void drawServoBase() {
  pushMatrix();
  translate(worldToScreen(50), worldToScreen(180));
  //rotate(servoBaseAngle);
  rect(worldToScreen(-24), 0, worldToScreen(24), worldToScreen(-15)); // left arm
  drawServoForearm();
  popMatrix();
}

void drawServoForearm() {
  pushMatrix();
  translate(worldToScreen(-6), worldToScreen(-15));
  rotate(servoForearmAngle);
  rect(worldToScreen(-12), 0, worldToScreen(12), worldToScreen(-40));
  drawServoHand();
  popMatrix();
}


void drawServoHand() {
  pushMatrix();
  translate(0, worldToScreen(-40));
  rotate(servoHandAngle);
  rect(worldToScreen(-12), 0, worldToScreen(12), worldToScreen(-30));
  drawServoEndPoint();
  popMatrix();
}


void drawServoEndPoint() {
  pushMatrix();
  translate(worldToScreen(-12), worldToScreen(-30));
  //rotate(servoEndpointAngle);
  triangle(worldToScreen(1), 0, worldToScreen(4), worldToScreen(-10), worldToScreen(4), 0);
  triangle(worldToScreen(8), worldToScreen(-10), worldToScreen(8), 0, worldToScreen(11), 0);
  popMatrix();
}
int worldToScreen(int value) {
  float dimension = min((float)width, (float)height);
  return (int)(value*(dimension/world_width));
}

void drawText() {
  fill(0);
  text("Forearm: "+(int)degrees(servoForearmAngle), 0, 32);
  text("Hand: "+(int)degrees(servoHandAngle)+"/"+(int)degrees(servoForearmAngle+servoHandAngle), 0, 64);
}

void mouseDragged() {
  if (dist(mX, mY, mouseX, mouseY)>50) {  
    switch(select) {
      // Base
    case 'b':
      servoBaseAngle = atan2(mouseY - mY, mouseX - mX) - HALF_PI;
      break;

      // Forearm
    case 'f':
      servoForearmAngle = atan2(mouseY - mY, mouseX - mX) + HALF_PI;
      servoForearmAngle = constrain(servoForearmAngle,0,radians(90));
      break;

      // Hand
    case 'h':
      servoHandAngle = atan2(mouseY - mY, mouseX - mX) + HALF_PI;
      servoHandAngle = constrain(servoHandAngle,0,radians(172));
      break;

      // End-point
    case 'e':
      servoEndpointAngle = atan2(mouseY - mY, mouseX - mX) - HALF_PI;
      break;
    }
  }
}