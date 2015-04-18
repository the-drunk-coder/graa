
// one-shot sine spork
fun void noise(float gain, int a, int d, int sus, int r)
{
	Noise n => ADSR e => Dyno dyn => dac;

	e.set( a::ms, d::ms, gain, r::ms );

	if (gain > 1.0){
		1.0 => gain;
    }
	
	dyn.limit;
	gain / 4 => dyn.thresh;
	
	// ignore decay if zero
	if(d == 0){
		0 => e.decayRate;
    }
	
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
recv.event( "/nois, f i i i i" ) @=> OscEvent @ oe;

// infinite event loop
while( true )
{
    // wait for event to arrive
    oe => now;
	
    // grab the next message from the queue. 
    while( oe.nextMsg() )
    {		
		oe.getFloat() => float gain;
		oe.getInt() => int a;
		oe.getInt() => int d;
		oe.getInt() => int s;
		oe.getInt() => int r;
		
		spork ~ noise(gain, a, d, s, r);
    }
}
