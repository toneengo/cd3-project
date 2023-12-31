/*
 * @name Setup and Draw
 * @arialabel Animated horizontal white line on a black background that moves from the bottom to the top of the screen
 * @description The code inside the draw() function runs continuously from top
 * to bottom until the program is stopped. The
 * code in setup() is run once when the program starts.
 */
let y = 100;

// The statements in the setup() function
// execute once when the program begins
function setup() {
  // createCanvas must be the first statement
  createCanvas(720, 400);
  stroke(255); // Set line drawing color to white
  frameRate(30);
}
// The statements in draw() are executed until the
// program is stopped. Each statement is executed in
// sequence and after the last line is read, the first
// line is executed again.
function draw() {
  background(0); // Set the background to black
  y = y - 1;
  if (y < 0) {
    y = height;
  }
  line(0, y, width, y);
}
