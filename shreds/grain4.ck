SndBuf buf;
int samples;
string last_path;

// one-shot sine spork
fun void grain(string samplepath, float start, int length, float gain, float rate, float rev)
{
	buf => Envelope e => JCRev reverb => dac;
		
	rev => reverb.mix;
		
	if (gain > 1.0){
		1.0 => gain;
    }
	
	
    (samples * start) $ int => int startpos;
	
	//<<< "sample: " + samplepath + " start: " + start + " length: " + length + " gain: " + gain + " rate: " + rate + " rev: " + rev + " startpos: " + startpos >>>;
	
	rate => buf.rate;
	gain => buf.gain;
	startpos => buf.pos;

	15::ms => e.duration;
	e.target(gain);
	(length - 40)::ms => now;
	e.keyOff();
	15::ms => now;
	
	if(rev > 0.0){
		2500::ms => now;
	}	
}

// init OSC reciever
OscRecv recv;
6449 => recv.port;
recv.listen();
recv.event( "/graind, s f i f f f" ) @=> OscEvent @ oe;

// infinite event loop
while( true )
{
    // wait for event to arrive
    oe => now;

    // grab the next message from the queue. 
    while( oe.nextMsg() )
    {
		oe.getString() => string samplepath;
		if(samplepath != last_path){
			samplepath => buf.read;
			buf.samples() => samples;
			samplepath => last_path;
			//<<< "changed path" >>>;
		}
		oe.getFloat() => float start;
		oe.getInt() => int length;
		oe.getFloat() => float gain;
		oe.getFloat() => float speed;
		oe.getFloat() => float rev;

		spork ~ grain(samplepath, start, length, gain, speed, rev);
    }
}
