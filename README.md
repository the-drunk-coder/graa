# graa>
A music livecoding eDSL using Markov chains.

A short introduction (from a seminar presentation) can be found [here](http://www.parkellipsen.de/files/graa.pdf).

## Installation

### Requirements

Requirements to install graa>. To be honest, i've got no idea if it runs on any other system
than Linux at the moment.

First of all, you'll need Python3, on which graa> is based.

#### Required Python modules

* pyparsing
* pygame
* pythonosc
* infix
* music21
* graphviz
* pydot

#### Backends to create sound

Install the following backends as needed ...

(as of recently, i ditched the ChucK and dirt backends in favor of a unified backend based on SCSynth)

* SuperCollider 3
* MIDI Infrastructure

#### Frontends to interact with graa>

* Emacs

It's also possible to use graa> directly with the Python interpreter, but i wouldn't recommend it, as it
is very tedious.

### Installing graa>

* Check out this repository
* Set up emacs mode (see below)

#### Setting up emacs mode

Add the following lines to your .emacs, where graa-path points to the repository you just checked out.
Make sure to set the path, as it is required within graa-mode as well.

```lisp
(setq graa-path "/path/to/graa")
(add-to-list 'load-path graa-path)
(require 'graa-mode)
```

Now you should be ready to use graa> !

## Usage

First of all, start the backends, and, if needed, patch up MIDI.
Start scsynth (default port) and, if you haved done so, load the file 'graa_synth.scd' to get the synthdefs.

If you want to use Linuxsampler (i use it quite often for piano samples), make sure there are no port conflicts.

Then, start graa> itself.
* Load a graa> file with emacs (there are some in the examples folder you can check out)
* Use C-s to start graa>
* Use C-c to execute a single line
* Use C-a to execute multiple lines (esp. useful for the add() statements, as seen in the examples)
* Use C-x to expand a line to your current buffer (that is, the output is fed back as an add() statement ... useful for generators)
* Use C-q to quit graa>

So, that's the basic usage.

I've started writing a series of tutorial files (see tutorial folder) as of recently, but it isn't really complete yet.
Once you're through with the tutorial files, you might check the examples folder for some more input.

## Demonstrations

Demonstrations what you can do with graa> and a Disklavier:

* [Brownian Notes (2015)](https://vimeo.com/119627859)
* [On Stars and Planets (2015)](https://vimeo.com/119631281)


--

(c) 2015 by Niklas Reppel

Released under GPLv3 or later (for full license text see LICENSE.txt)
