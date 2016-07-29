SynthDef.new(\buzz, { | freq, gain, a, d, s, r, cutoff, pan |
	var lim_cutoff = min(cutoff,15000);
	var lim_freq = min(freq, 15000);
	var lim_gain = min(gain, 1.1);
	var filterenv = Env.new([lim_freq, lim_cutoff, lim_cutoff * 0.5, lim_cutoff * 0.5, 0], [a, d, s, r]);
	var ampenv = Env.new([0, lim_gain, lim_gain*0.7, lim_gain*0.7, 0], [a, d, s, r]);
	var snd = BLowPass4.ar(LFSaw.ar(freq), EnvGen.ar(filterenv)) * EnvGen.ar(ampenv, doneAction: 2);
	Out.ar(0, Pan2.ar(snd, pan))
	}
).store;

SynthDef.new(\sqr, { | freq, gain, a, d, s, r, cutoff, pan |
	var lim_cutoff = min(cutoff,15000);
	var lim_freq = min(freq, 15000);
	var lim_gain = min(gain, 1.1);
	var filterenv = Env([freq, lim_cutoff, lim_cutoff * 0.5, lim_cutoff * 0.5, 0], [a, d, s, r]);
	var ampenv = Env([0, lim_gain, lim_gain*0.7, lim_gain*0.7, 0], [a, d, s, r]);
	var snd = BLowPass4.ar(LFPulse.ar(freq), EnvGen.ar(filterenv)) * EnvGen.ar(ampenv, doneAction: 2);
	Out.ar(0, Pan2.ar(snd, pan))
	}
).store;

SynthDef.new(\sine, { | freq, gain, a, d, s, r, pan |
	var lim_gain = min(gain, 1.1);
	var ampenv = Env([0, lim_gain, lim_gain*0.7, lim_gain*0.7, 0], [a, d, s, r]);
	var snd = SinOsc.ar(freq) * EnvGen.ar(ampenv, doneAction: 2);
	Out.ar(0, Pan2.ar(snd, pan))
	}
).store;

SynthDef.new(\noise, { | gain, a, d, s, r, pan |
	var lim_gain = min(gain, 1.1);
	var ampenv = Env([0, lim_gain, lim_gain*0.7, lim_gain*0.7, 0], [a, d, s, r]);
	var snd = WhiteNoise.ar() * EnvGen.ar(ampenv, doneAction: 2);
	Out.ar(0, Pan2.ar(snd, pan))
	}
).store;

SynthDef.new(\subt, { | freq, gain, a, d, s, r, pan |
	var lim_gain = min(gain, 1.1);
	var ampenv = Env([0, lim_gain, lim_gain*0.7, lim_gain*0.7, 0], [a, d, s, r]);
	var snd = Resonz.ar(Resonz.ar(BPF.ar(WhiteNoise.ar(), freq, 0.1, 3),freq, 0.1, 3), freq, 0.1, 3) * EnvGen.ar(ampenv, doneAction: 2);
	Out.ar(0, Pan2.ar(snd, pan))
	}
).store;

SynthDef.new(\subtrev, { | freq, gain, a, d, s, r, pan, rev |
	var lim_gain = min(gain, 1.1);
	var ampenv = Env([0, lim_gain, lim_gain*0.7, lim_gain*0.7, 0], [a, d, s, r]);
	var snd = Resonz.ar(Resonz.ar(BPF.ar(WhiteNoise.ar(), freq, 0.1, 3),freq, 0.1, 3), freq, 0.1, 3) * EnvGen.ar(ampenv);
	var revsnd = FreeVerb.ar(snd, mix:rev, room:0.6);
	DetectSilence.ar(revsnd, doneAction:2);
	Out.ar(0, Pan2.ar(revsnd, pan))
	}
).store;

SynthDef.new(\noiserev, { | gain, a, d, s, r, rev, pan |
	var lim_gain = min(gain, 1.1);
	var ampenv = Env([0, lim_gain, lim_gain*0.7, lim_gain*0.7, 0], [a, d, s, r]);
	var snd = WhiteNoise.ar() * EnvGen.ar(ampenv);
	var revsnd = FreeVerb.ar(snd, mix:rev, room:0.6);
	DetectSilence.ar(revsnd, doneAction:2);
	Out.ar(0, Pan2.ar(revsnd, pan))
	}
).store;

SynthDef.new(\sinerev, { | freq, gain, a, d, s, r, rev, pan |
	var lim_gain = min(gain, 1.1);
	var ampenv = Env([0, lim_gain, lim_gain*0.7, lim_gain*0.7, 0], [a, d, s, r]);
	var snd = SinOsc.ar(freq) * EnvGen.ar(ampenv);
	var revsnd = FreeVerb.ar(snd, mix:rev, room:0.6);
	DetectSilence.ar(revsnd, doneAction:2);
	Out.ar(0, Pan2.ar(revsnd, pan))
	}
).store;

SynthDef.new(\buzzrev, { | freq, gain, a, d, s, r, rev, cutoff, pan |
	var lim_cutoff = min(cutoff,15000);
	var lim_freq = min(freq, 15000);
	var lim_gain = min(gain, 1.1);
	var filterenv = Env([lim_freq, lim_cutoff, lim_cutoff * 0.8, lim_cutoff * 0.8, 0], [a, d, s, r]);
	var ampenv = Env([0, lim_gain, lim_gain*0.7, lim_gain*0.7, 0], [a, d, s, r]);
	var snd = BLowPass4.ar(LFSaw.ar(freq), EnvGen.ar(filterenv)) * EnvGen.ar(ampenv);
	var revsnd = FreeVerb.ar(snd, mix:rev, room:0.6);
	DetectSilence.ar(revsnd, doneAction:2);
	Out.ar(0, Pan2.ar(revsnd, pan))
	}
).store;

SynthDef.new(\sqrrev, { | freq, gain, a, d, s, r, rev, cutoff, pan |
	var lim_cutoff = min(cutoff,15000);
	var lim_freq = min(freq, 15000);
	var lim_gain = min(gain, 1.1);
	var filterenv = Env([lim_freq, lim_cutoff, lim_cutoff * 0.8, lim_cutoff * 0.8, 0], [a, d, s, r]);
	var ampenv = Env([0, lim_gain, lim_gain*0.7, lim_gain*0.7, 0], [a, d, s, r]);
	var snd = BLowPass4.ar(LFPulse.ar(freq), EnvGen.ar(filterenv)) * EnvGen.ar(ampenv);
	var revsnd = FreeVerb.ar(snd, mix:rev, room:0.6);
	DetectSilence.ar(revsnd, doneAction:2);
	Out.ar(0, Pan2.ar(revsnd, pan))
	}
).store;

SynthDef(\sampl, {| bufnum, gain, start, rev, pan, cutoff, speed |
	var lim_cutoff = min(cutoff, 20000);
	var lim_gain = min(gain, 1.1);
	var length = BufDur.ir(bufnum);
	var sampl = LPF.ar(PlayBuf.ar(1, bufnum, speed, 1, length * 44100 * start,  doneAction:2), cutoff) * gain;
	Out.ar(0, Pan2.ar(sampl, pan));
	}
).store;

SynthDef(\samplrev, {| bufnum, gain, start, rev, pan, cutoff, speed |
	var lim_cutoff = min(cutoff,20000);
	var lim_gain = min(gain, 1.1);
	var length =  BufDur.ir(bufnum);
	var cutenv = Env.new([0, lim_gain, lim_gain, 0], [0.004, length - 0.008, 0.004]);
	var sampl = LPF.ar(PlayBuf.ar(1, bufnum, speed), cutoff) * EnvGen.ar(cutenv);
	var revsampl = FreeVerb.ar(sampl, mix:rev, room:0.6);
	DetectSilence.ar(revsampl, doneAction:2);
	Out.ar(0, Pan2.ar(revsampl, pan));
	}
).store;

SynthDef(\grain, {| bufnum, gain, start, length, a, r, rev, pan, cutoff, speed |
	var lim_cutoff = min(cutoff, 20000);
	var lim_gain = min(gain, 1.1);
	var cutenv = Env.new([0, lim_gain, lim_gain, 0], [a, length, r]);
	var sampl = LPF.ar(PlayBuf.ar(1, bufnum, speed, 1, startPos: BufDur.ir(bufnum) * 44100 * start), cutoff) * EnvGen.ar(cutenv, doneAction:2);
	Out.ar(0, Pan2.ar(sampl, pan));
	}
).store;

SynthDef(\grainrev, {| bufnum, gain, start, length, a, r, rev, pan, cutoff, speed |
	var lim_cutoff = min(cutoff,20000);
	var lim_gain = min(gain, 1.1);
	var cutenv = Env.new([0, lim_gain, lim_gain, 0], [a, length, r]);
	var sampl = LPF.ar(PlayBuf.ar(1, bufnum, speed, 1, startPos: BufDur.ir(bufnum) * 44100 * start), cutoff) * EnvGen.ar(cutenv);
	var revsampl = FreeVerb.ar(sampl, mix:rev, room:0.6);
	DetectSilence.ar(revsampl, doneAction:2);
	Out.ar(0, Pan2.ar(revsampl, pan));
	}
).store;

// 8-Channel versions of sampl and grain ... channels ('pan' argument) reach from 0 to 7
SynthDef(\sampl8, {| bufnum, gain, start, rev, pan, cutoff, speed |
	var lim_cutoff = min(cutoff, 20000);
	var lim_gain = min(gain, 1.1);
	var length = BufDur.ir(bufnum);
	var sampl = LPF.ar(PlayBuf.ar(1, bufnum, speed, 1, length * 44100 * start,  doneAction:2), cutoff) * gain;
	Out.ar(0, PanAz.ar(8, sampl, pan * 0.25, orientation:0));
	}
).store;

SynthDef(\sampl8rev, {| bufnum, gain, start, rev, pan, cutoff, speed |
	var lim_cutoff = min(cutoff,20000);
	var lim_gain = min(gain, 1.1);
	var length =  BufDur.ir(bufnum);
	var cutenv = Env.new([0, lim_gain, lim_gain, 0], [0.004, length - 0.008, 0.004]);
	var sampl = LPF.ar(PlayBuf.ar(1, bufnum, speed), cutoff) * EnvGen.ar(cutenv);
	var revsampl = FreeVerb.ar(sampl, mix:rev, room:0.6);
	DetectSilence.ar(revsampl, doneAction:2);
	Out.ar(0, PanAz.ar(8, revsampl, pan * 0.25, orientation:0));
	}
).store;

SynthDef(\grain8, {| bufnum, gain, start, length, rev, pan, cutoff, speed |
	var lim_cutoff = min(cutoff, 20000);
	var lim_gain = min(gain, 1.1);
	var cutenv = Env.new([0, lim_gain, lim_gain, 0], [0.004, length - 0.008, 0.004]);
	var sampl = LPF.ar(PlayBuf.ar(1, bufnum, speed, 1, startPos: BufDur.ir(bufnum) * 44100 * start), cutoff) * EnvGen.ar(cutenv, doneAction:2);
	Out.ar(0, PanAz.ar(8, sampl, pan * 0.25, orientation:0));
	}
).store;

SynthDef(\grain8rev, {| bufnum, gain, start, length, rev, pan, cutoff, speed |
	var lim_cutoff = min(cutoff,20000);
	var lim_gain = min(gain, 1.1);
	var cutenv = Env.new([0, lim_gain, lim_gain, 0], [0.004, length - 0.008, 0.004]);
	var sampl = LPF.ar(PlayBuf.ar(1, bufnum, speed, 1, startPos: BufDur.ir(bufnum) * 44100 * start), cutoff) * EnvGen.ar(cutenv);
	var revsampl = FreeVerb.ar(sampl, mix:rev, room:0.6);
	DetectSilence.ar(revsampl, doneAction:2);
	Out.ar(0, PanAz.ar(8, revsampl, pan * 0.25, orientation:0));
	}
).store;

// Based on the risset port by Frederik Oloffson
SynthDef(\risset, {|pan, freq, gain, length, cutoff|
	var amps= #[1, 0.67, 1, 1.8, 2.67, 1.67, 1.46, 1.33, 1.33, 1, 1.33];
	var durs= #[1, 0.9, 0.65, 0.55, 0.325, 0.35, 0.25, 0.2, 0.15, 0.1, 0.075];
	var frqs= #[0.56, 0.56, 0.92, 0.92, 1.19, 1.7, 2, 2.74, 3, 3.76, 4.07];
	var dets= #[0, 1, 0, 1.7, 0, 0, 0, 0, 0, 0, 0];
	var src= LPF.ar(Mix.fill(11, {|i|
		var env= EnvGen.ar(Env.perc(0.015, length*durs[i], amps[i], -4.5), 1);
		SinOsc.ar(freq*frqs[i]+dets[i], 0, gain*env);
	}), cutoff);
	Out.ar(0, Pan2.ar(src, pan));
}).store;

// Based on the risset port by Frederik Oloffson
SynthDef(\rissetrev, {|pan, freq, gain, length, cutoff, rev|
	var amps= #[1, 0.67, 1, 1.8, 2.67, 1.67, 1.46, 1.33, 1.33, 1, 1.33];
	var durs= #[1, 0.9, 0.65, 0.55, 0.325, 0.35, 0.25, 0.2, 0.15, 0.1, 0.075];
	var frqs= #[0.56, 0.56, 0.92, 0.92, 1.19, 1.7, 2, 2.74, 3, 3.76, 4.07];
	var dets= #[0, 1, 0, 1.7, 0, 0, 0, 0, 0, 0, 0];
	var src= LPF.ar(Mix.fill(11, {|i|
		var env= EnvGen.ar(Env.perc(0.005, length*durs[i], amps[i], -4.5), 1);
		SinOsc.ar(freq*frqs[i]+dets[i], 0, gain*env);
	}), cutoff);
	var revsrc = FreeVerb.ar(src, mix:rev, room:0.6);
	DetectSilence.ar(revsrc, doneAction:2);
	Out.ar(0, Pan2.ar(revsrc, pan));
}).store;

SynthDef(\pluck, {|out=0, freq=440, pan=0, length=0.5, gain=0.3, cutoff=12000 |
	var pluck, period, string;
	pluck = PinkNoise.ar(Decay.kr(Impulse.kr(0.005), 0.05));
	period = freq.reciprocal;
	string = CombL.ar(pluck, period, period, length*6);
	string = LeakDC.ar(LPF.ar(Pan2.ar(string, pan), cutoff)) * gain;
	DetectSilence.ar(string, doneAction:2);
	Out.ar(2, string)
}).store;

SynthDef(\pluckrev, {|out=0, freq=440, pan=0, length=0.5, gain=0.3, cutoff=12000, rev=0.1|
	var pluck, period, string, revstring;
	pluck = PinkNoise.ar(Decay.kr(Impulse.kr(0.005), 0.05));
	period = freq.reciprocal;
	string = CombL.ar(pluck, period, period, length*6);
	string = LeakDC.ar(LPF.ar(Pan2.ar(string, pan), cutoff)) * gain;
	revstring = FreeVerb.ar(string, mix:rev, room:0.6);
	DetectSilence.ar(revstring, doneAction:2);
	Out.ar(2, revstring)
}).store;



/*
SynthDef(\pluck, {|pan, freq, gain, length, cutoff|
	var sig = Pluck.ar(WhiteNoise.ar(0.1), Impulse.kr(2), freq.reciprocal, freq.reciprocal, 10);
	Out.ar(0, Pan2.ar(sig, pan))
}).store;

SynthDef(\pluckrev, {|pan, freq, gain, length, cutoff, rev|
	var sig = Pluck.ar(WhiteNoise.ar(0.1), Impulse.kr(2), freq.reciprocal, freq.reciprocal, 10);
	var revsig = FreeVerb.ar(sig, mix:rev, room:0.6);
	DetectSilence.ar(revsig, doneAction:2);
	Out.ar(0, Pan2.ar(revsig, pan))
}).store;
*/