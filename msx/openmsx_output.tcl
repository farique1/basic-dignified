# OpenMSX Tcl script to send the MSX text responses to stderr

# The first two lines each enable output of a portion of the screen text
# They probably each monitor an output routine address hook through a break point
# And send the return result to the 'output' namespace and 'char' proc

# 'namespace' is a collection of commands and variables (like a class?)
# it creates and manipulates contexts for commands and variables
# 'eval' create a new namespace
# 'proc' creates a new procedure (like a method?)
# 'puts' write to a channel
# '-nonewline' suppresses automatic linefeed
# '%c' convert output to unicode
# 'stderr' is the output channel
# 'reg A' must be the internal openMSX output from the break points

debug set_bp 0x18 {[pc_in_slot 0 0]} {output::char}
debug set_bp 0xa2 {[pc_in_slot 0 0]} {output::char}

namespace eval output {
  proc char {} {
		puts -nonewline stderr [format %c [reg A]]
  }
}
