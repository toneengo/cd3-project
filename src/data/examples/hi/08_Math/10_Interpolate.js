/*
  * @name रैखिक इंटरपोलेशन
  * @frame 720, 400
  * @description माउस को स्क्रीन पर ले जाएँ और सिंबल उसके पीछे आ जाएगा।
  * एनीमेशन के प्रत्येक फ्रेम को खींचने के बीच, दीर्घवृत्त भाग जाता है
  * दूरी (0.05) की वर्तमान स्थिति से कर्सर की ओर का उपयोग कर
  * lerp () फ़ंक्शन।
  * यह केवल lerp() के साथ इनपुट के तहत ईजिंग जैसा ही है ..
  */

let x = 0;
let y = 0;

function setup() {
  createCanvas(720, 400);
  noStroke();
}

function draw() {
  background(51);

   // lerp () एक विशिष्ट वेतन वृद्धि पर दो संख्याओं के बीच की संख्या की गणना करता है।
   // एएमटी पैरामीटर दो मानों के बीच प्रक्षेपित करने की राशि है
   // जहां 0.0 पहले बिंदु के बराबर है, 0.1 पहले बिंदु के बहुत करीब है, 0.5
   // बीच में आधा रास्ता है, आदि।

   // यहां हम प्रत्येक फ्रेम में 5% रास्ते को माउस स्थान पर ले जा रहे हैं
  x = lerp(x, mouseX, 0.05);
  y = lerp(y, mouseY, 0.05);

  fill(255);
  stroke(255);
  ellipse(x, y, 66, 66);
}
