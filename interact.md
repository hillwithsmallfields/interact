Interact: a program for interacting with processes
==================================================

Interact is a data-driven alternative to the hard-coded "expect"-style
programming.  Instead of writing the expected received strings and
intended transmitted strings into your program, you set up a config
file (using, or perhaps misusing, YAML syntax) to control the
interactions.

The code is structured so that as well as running it as a program with
a config file, you can call it as a function with a dictionary as
input, where the dictionary is of the same form as is read from the
config files.

Since YAML uses the `#` character for comments, you can use shebang
syntax at the top of the config file (and set the executable
permission bit) to treat the interaction configuration as a program.

`interact` keeps a dictionary of variables which can be referred to in
response strings using Python's named `%`-substitution.o  Responses can
also set the values of variables.  This dictionary also binds the
string representation of integers to unused command-line arguments,
and string representations of integers with `\` prepended to the
capture groups for matched regular expressions.

Configuration sections
======================

`target`
========

This describes the process (or other entity) to interact with.

`target:run`
------------

A string used as a command line for starting the process.

`target:connect`
----------------

A socket or tty to connect to.

`responses`
-----------

This describes how to respond to things that the process sends.

It is a dictionary, with the keys being regular expressions to apply
to the received data, and the values being responses.

Each response may be a single string, or a list of strings which will
be executed in the order given.

Each response string has substitutions from the variables dictionary
made, and is then interpreted thus:

 - if it is of the form `a = expression`, the `expression` is evaluated
   and the result stored in the interaction variable `a`
 - if it starts with a `!`, the rest of the line is executed as a
   shell command
 - if it ends with `|`, the line is executed as a shell command and
   its output sent to the target
 - if it looks like a python function call, it is evaluated as such,
   with the functions `send` and `quit` being treated specially
 - anything else is sent as a literal string
 
`start`
-------
 
An action or list of actions, as for a response (above), to be
performed as soon as the target program (or socket connection) has
started.

`end`
-----
 
An action or list of actions, as for a response (above), to be
performed as when the target program (or socket connection) has
finished.

`settings`
==========

This gives the initial settings for variables which can be substituted
into responses.  Each value given in the YAML file is processed using
Python's `eval` function.

