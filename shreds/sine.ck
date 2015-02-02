
// one-shot sine spork
fun void sine(float freq, float gain, int a, int d, int sus, int r)
{
	SinOsc s => ADSR e => dac;
	gain => s.gain;
	freq => s.freq;
	
	e.set( a::ms, d::ms, gain, r::ms );
	
	e.keyOn();
	sus::ms => now;
	e.keyOff();
	r::ms => now;
}

// create our OSC receiver
OscRecv recv;
// use port 6449 (or whatever)
6449 => recv.port;
// start listening (launch thread)
recv.listen();

// create an address in the receiver, store in new variable
recv.event( "/sine, f f i i i i" ) @=> OscEvent @ oe;

// infinite event loop
while( true )
{
    // wait for event to arrive
    oe => now;
	
    // grab the next message from the queue. 
    while( oe.nextMsg() )
    {
		oe.getFloat() => float freq;
		oe.getFloat() => float gain;
		oe.getInt() => int a;
		oe.getInt() => int d;
		oe.getInt() => int s;
		oe.getInt() => int r;
		
		spork ~ sine(freq, gain, a, d, s, r);
    }
}
