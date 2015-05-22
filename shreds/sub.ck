
// one-shot sine spork
fun void sub(float freq, float gain, int a, int d, int sus, int r, float rev)
{
	Noise n => BPF b => ResonZ res => ADSR e => Dyno dyn => JCRev reverb => dac;

	5 => b.gain;
	freq => b.freq;
	5 => res.gain;
	freq => res.freq;
	30 => b.Q;
	30 => res.Q;
	rev => reverb.mix;
	
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

	if(rev > 0.0){
		2000::ms => now;
	}
}

// create our OSC receiver
OscRecv recv;
// use port 6449 (or whatever)
6449 => recv.port;
// start listening (launch thread)
recv.listen();

// create an address in the receiver, store in new variable
recv.event( "/sub, f f i i i i f" ) @=> OscEvent @ oe;

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
		oe.getFloat() => float rev;
		
		spork ~ sub(freq, gain, a, d, s, r, rev);
    }
}
