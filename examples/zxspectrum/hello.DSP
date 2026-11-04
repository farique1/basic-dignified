## ZX Spectrum module v1.1.0: explicit LET and native numeric scalar names.
REM FIRST SPECTRUM MILESTONE
CLS
LET counter=1
{again}
PRINT "SPECTRUM ";counter
LET counter=counter+1
IF counter<=3 THEN GO TO {again}
PRINT "DONE"
STOP
