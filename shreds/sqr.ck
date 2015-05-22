class MySqr{
	SqrOsc sqrosc => LPF lp => ADSR e => Dyno dyn => JCRev reverb => dac;
	ADSR filt => Gain fg => blackhole;
	10 => fg.gain;
	
	Step s;
	s => filt;
	1 => s.next;
	
	fun void sqr(float freq, float gain, int a, int d, int sus, int r, float rev, float cutoff) {	
	
		a + d + sus + r => int overall;
		freq => sqrosc.freq;

		e.set( a::ms, d::ms, gain, r::ms );
		filt.set( a::ms, (sus - r)::ms, gain, r::ms );

		dyn.limit;
		gain / 4 => dyn.thresh;
		
		if(d == 0) {
			0 => e.decayRate;
			0 => filt.decayRate;
		}

		rev => reverb.mix;
		
		now + overall::ms => time then;	
		spork ~ filteradsr(then, freq, cutoff);		
		e.keyOn();
		filt.keyOn();
		sus::ms => now;
		e.keyOff();
		filt.keyOff();	
		r::ms => now;

		if(rev > 0.0){
			2000::ms => now;
	    }
	}

	fun void filteradsr (time then, float freq, float cutoff) {
		while (now < then) {
			float currfilt;
			(filt.last() * 800 + 100) * cutoff => currfilt;
			currfilt => lp.freq;		
			1::ms => now;
		}
	}
}

// create our OSC receiver
OscRecv recv;
// use port 6449 (or whatever)
6449 => recv.port;
// start listening (launch thread)
recv.listen();

// create an address in the receiver, store in new variable
recv.event( "/sqr, f f i i i i f f" ) @=> OscEvent @ oe;

fun void sporkSqr(float freq, float gain, int a, int d, int sus, int r, float rev, float cutoff){
	MySqr mysqr;
	mysqr.sqr(freq, gain, a, d, sus, r, rev, cutoff);
}

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
		oe.getFloat() => float cutoff;
		
		spork ~ sporkSqr(freq, gain, a, d, s, r, rev, cutoff);
    }
}
