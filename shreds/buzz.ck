class MyBuzzer {
	SawOsc saw => LPF lp => ADSR e => Dyno dyn;
	ADSR filt => Gain fg => blackhole;
	10 => fg.gain;

	Step s;
	s => filt;
	1 => s.next;

	// one-shot sine spork
	fun void buzz(float freq, float gain, int a, int d, int sus, int r)
	{	
		a + d + sus + r => int overall;
		freq => saw.freq;

		e.set( a::ms, d::ms, gain, r::ms );
		filt.set( a::ms, (sus - r)::ms, gain, r::ms );

		dyn.limit;
		gain / 4 => dyn.thresh;
		
		if(d == 0){
			0 => e.decayRate;
			0 => filt.decayRate;
		}
		
		now + overall::ms => time then;	
		spork ~ filteradsr(then, freq);
		e.keyOn();
		filt.keyOn();
		sus::ms => now;
		e.keyOff();
		filt.keyOff();	
		r::ms => now;
		// disconnecting doesn't really help here ...
		dyn !=> dac;
		
	}

	fun void filteradsr (time then, float freq)
	{
		while (now < then)
		{
			float currfilt;
			filt.last() * 800 + 100 => currfilt;
			currfilt => lp.freq;		
			1::ms => now;
		}
	}

	fun void connect(UGen ugen){
		dyn => ugen;
    }
}

// create our OSC receiver
OscRecv recv;
// use port 6449 (or whatever)
6449 => recv.port;
// start listening (launch thread)
recv.listen();

// create an address in the receiver, store in new variable
recv.event( "/buzz, f f i i i i" ) @=> OscEvent @ oe;

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

		MyBuzzer buzzer;
		buzzer.connect(dac);
		spork ~ buzzer.buzz(freq, gain, a, d, s, r);
    }
}
