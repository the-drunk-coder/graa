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

SynthDef(\grain, {| bufnum, gain, start, length, rev, pan, cutoff, speed |
	var lim_cutoff = min(cutoff, 20000);
	var lim_gain = min(gain, 1.1);
	var cutenv = Env.new([0, lim_gain, lim_gain, 0], [0.004, length - 0.008, 0.004]);
	var sampl = LPF.ar(PlayBuf.ar(1, bufnum, speed, 1, startPos: BufDur.ir(bufnum) * 44100 * start), cutoff) * EnvGen.ar(cutenv, doneAction:2);
	Out.ar(0, Pan2.ar(sampl, pan));
	}
).store;

SynthDef(\grainrev, {| bufnum, gain, start, length, rev, pan, cutoff, speed |
	var lim_cutoff = min(cutoff,20000);
	var lim_gain = min(gain, 1.1);
	var cutenv = Env.new([0, lim_gain, lim_gain, 0], [0.004, length - 0.008, 0.004]);
	var sampl = LPF.ar(PlayBuf.ar(1, bufnum, speed, 1, startPos: BufDur.ir(bufnum) * 44100 * start), cutoff) * EnvGen.ar(cutenv);
	var revsampl = FreeVerb.ar(sampl, mix:rev, room:0.6);
	DetectSilence.ar(revsampl, doneAction:2);
	Out.ar(0, Pan2.ar(revsampl, pan));
	}
).store;