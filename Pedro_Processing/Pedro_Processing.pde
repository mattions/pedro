
private float servoBaseAngle = 0.0f;
private float servoForearmAngle = 0.0f;
private float servoHandAngle = 0.0f;
private float servoEndpointAngle = 0.0f;
private char select = 'b';
private boolean pressed = false;
private float world_width = 200f; // virtual sketch size (used in Android)
private float world_height = 200f; // virtual sketch size (used in Android)
private int length_Base = 15;
private int length_Forearm = 40;
private int length_Hand = 30;
private int length_EndPoint = 10;
private float mX;
private float mY;


public void settings() {
	// Actual screen size in pixels.
  size(800, 600);
}

public void setup() {
  smooth();
  frameRate(30);
  textSize(worldToScreen(10));
}

public void draw() {
  background(255);
  pushMatrix();
  
  checkInput();
  drawRobot();
  drawText();
  drawControlZone();
  
  popMatrix();  
}

private void drawControlZone(){	
  stroke(5);
  line(width/2, worldToScreen(50), width/2, worldToScreen(150));  
  line(width/2, worldToScreen(50), width, worldToScreen(50));
  text("Forearm", width/2, worldToScreen(50));
  line(width/2, worldToScreen(100), width, worldToScreen(100));
  text("Hand", width/2, worldToScreen(100));
  line(width/2, worldToScreen(150), width, worldToScreen(150));
}
	
	// Start drawing robot, we set color and stroke mode here.
private void drawRobot() {
  noStroke();
  fill(38, 38, 200);
  drawServoBase();
}

	// Draw different parts of robot
	// Drawn in sequence so rotation is kept from base to end-point.
private void drawServoBase() {
  pushMatrix();
  translate(worldToScreen(50), worldToScreen(180));
  //rotate(servoBaseAngle);
  rect(worldToScreen(-24), 0, worldToScreen(24), worldToScreen(-length_Base)); // left arm
  drawServoForearm();
  popMatrix();
}

void drawServoForearm() {
  pushMatrix();
  translate(worldToScreen(-6), worldToScreen(-length_Base));
  rotate(-radians(servoForearmAngle) + HALF_PI);
  rect(worldToScreen(-12), 0, worldToScreen(12), worldToScreen(-length_Forearm));
  drawServoHand();
  popMatrix();
}

void drawServoHand() {
  pushMatrix();
  translate(0, worldToScreen(-length_Forearm));
  rotate(-radians(servoHandAngle)+PI);
  rect(worldToScreen(-12), 0, worldToScreen(12), worldToScreen(-length_Hand));
  drawServoEndPoint();
  popMatrix();
}

void drawServoEndPoint() {
  pushMatrix();
  translate(worldToScreen(-12), worldToScreen(-length_Hand));
  //rotate(servoEndpointAngle);
  triangle(worldToScreen(1), 0, worldToScreen(4), worldToScreen(-length_EndPoint), worldToScreen(4), 0);
  triangle(worldToScreen(8), worldToScreen(-length_EndPoint), worldToScreen(8), 0, worldToScreen(11), 0);
  popMatrix();
}

	// Draw Debug Text
void drawText() {
  fill(0);
  text("Forearm: "+(int)servoForearmAngle, 0, worldToScreen(10));
  text("Hand: "+(int)servoHandAngle+"/"
               +(int)(servoForearmAngle+servoHandAngle), 0, worldToScreen(20));
  text("Servos: "+(int)servoBaseAngle+"/"
                 +(int)servoForearmAngle+"/"
                 +(int)servoHandAngle
                 , 0, worldToScreen(30));
}

private void checkInput(){
	
  if (mousePressed){
		// We grab first-click-position here, and see if its inside control zone
	if (mouseX > width/2f && mouseY > worldToScreen(50) && mouseY < worldToScreen(150)){
		if (!pressed) {
		  pressed = true;
		  mX = mouseX;
		  mY = mouseY;

		  //if (mX > width/2f && mY < worldToScreen(50)) select = 'e';
		  //else 
		  
		  if (mX > width/2f && mY < worldToScreen(100)) select = 'f';
		  else if (mX > width/2f && mY < worldToScreen(150)) select = 'h';
		  
		  //else if (mX > width/2f && mY < worldToScreen(200)) select = 'b';
		}
    
      ellipse(mX, mY, worldToScreen(10), worldToScreen(10));
      stroke(worldToScreen(5));
      line(mX, mY, mouseX, mouseY);
    } // If mouse click is outside control zone, we use our IK system.
	else xyzToServoAngles(mouseX, mouseY, 0);
    
  } // clear pressed flag when mouse is released.
  else pressed = false;

}
	
	// When mouse dragged from inside control box, update angles
void mouseDragged() {
	// Make sure distance betwen first-click-position and current-mouse-position have a small offset
  if (mouseX > width/2 && (dist(mX, mY, mouseX, mouseY)>worldToScreen(15))) {  
    switch(select) {
      // Base
    case 'b':
      servoBaseAngle = degrees(atan2(mouseY - mY, mouseX - mX) - HALF_PI);
      break;

      // Forearm
    case 'f':
      servoForearmAngle = -degrees(atan2(mouseY - mY, mouseX - mX));
      servoForearmAngle = constrain(servoForearmAngle, 0, 90);
      break;

      // Hand
    case 'h':
      servoHandAngle = -degrees(atan2(mouseY - mY, mouseX - mX))+90;
      servoHandAngle = constrain(servoHandAngle, 0, 180);
      break;

      // End-point
    case 'e':
      servoEndpointAngle = atan2(mouseY - mY, mouseX - mX) - HALF_PI;
      break;
    }
  }
}
	
	// Helper method to convert sketch distances to actual screen distance in pixels (used in Android)
int worldToScreen(int value) {
  float dimension = min((float)width, (float)height);
  return (int)(value*(dimension/world_width));
}

	// Inverse Kinematics:
	// From Cartesian to Servo Angles
void xyzToServoAngles(int x, int y, int z){
  float a = worldToScreen(length_Forearm); // Lenght of Forearm
  float b = worldToScreen(length_Hand); // Length of Hand
  float r = constrain(sqrt(x*x + y*y), 0 ,a+b);
  float R = constrain(sqrt(r*r + z*z),0, a+b);
  
  servoBaseAngle = degrees(atan(y/((float)x)));
  servoForearmAngle = degrees(acos((a*a + R*R - b*b)/(2*a*R)) + acos(r/R));
  servoHandAngle = degrees(acos((a*a + b*b - R*R)/(2*a*b)));
}