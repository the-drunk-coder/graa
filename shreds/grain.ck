SndBuf buf;
// one-shot sine spork
fun void grain(string samplepath, float start, int length, float gain, float rate, float rev)
{
	buf => ADSR e => JCRev reverb => dac;
		
	rev => reverb.mix;

	e.set( 10::ms, 0::ms, gain, 10::ms );
	0 => e.decayRate;
	
	if (gain > 1.0){
		1.0 => gain;
    }
	
	buf.samples() => int samples;
    (samples * start) $ int => int startpos;
	
	//<<< "sample: " + samplepath + " start: " + start + " length: " + length + " gain: " + gain + " rate: " + rate + " rev: " + rev + " startpos: " + startpos >>>;

	rate => buf.rate;
	gain => buf.gain;
	startpos => buf.pos;
	
	e.keyOn();
	(length - 20)::ms => now;
	e.keyOff();
	4::ms => now;
	
	if(rev > 0.0){
		1500::ms => now;
	}	
}

// create our OSC receiver
OscRecv recv;
// use port 6449 (or whatever)
6449 => recv.port;
// start listening (launch thread)
recv.listen();

// create an address in the receiver, store in new variable
recv.event( "/grain, s f i f f f" ) @=> OscEvent @ oe;

// infinite event loop
while( true )
{
    // wait for event to arrive
    oe => now;

    // grab the next message from the queue. 
    while( oe.nextMsg() )
    {
		oe.getString() => string samplepath;
		samplepath => buf.read;
		oe.getFloat() => float start;
		oe.getInt() => int length;
		oe.getFloat() => float gain;
		oe.getFloat() => float speed;
		oe.getFloat() => float rev;

		spork ~ grain(samplepath, start, length, gain, speed, rev);
    }
}
