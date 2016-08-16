grammar DSGRN;

/* options {
    language = Python2; 
} */


/* Lexer rules */

@lexer::members {
    boolean ignore=true;
}

/* White space is active for multiplication, otherwise ignored */
MULT_WS : [ \t] { ignore = false; } [\n\r] { ignore = true; } WS { ignore = true; };

NOT:
    '~'
    ;

IDENT:
    (CHAR)+
    ;

CHAR: 
    [a-zA-Z0-9_]
    ;

WS: 
    [ \t\n\r] + { if(ignore) skip(); } 
    ;



/* Parser rules */

network:
    statement (('\n')+ statement)* ('\n')* EOF  /* EOF needed to parse everything */
    ;

statement:
    IDENT ':' expr (essential)?
    ;

essential:
    ':' 'E'  /* parser rule instead of lexer rule so that white space is ignored and is node on parser tree */
    ;

expr:
    ( term | enclosed_term ) 
    | (sum | enclosed_sum)   
    | (mult | enclosed_mult)
    ;

term: 
    (NOT)? IDENT
    ;

enclosed_term: 
    '(' term ')'
    | '(' enclosed_term ')' 
    ;

sum:
    ( term | enclosed_term ) ('+' ( term | enclosed_term ))+    /* at least two terms */
    ;

enclosed_sum:
    '(' sum ')'
    | '(' enclosed_sum ')' 
    ;

mult:
    ( term | enclosed_term )
    | enclosed_sum
    | mult (MULT_WS)+ mult     /* active white space parsed first */
    | mult ('*')? mult         /* have to split ('*')? into 4 cases otherwise left recursion fails */
    | mult ('*')? enclosed_mult
    | enclosed_mult ('*')? mult 
    | enclosed_mult ('*')? enclosed_mult 
    ;

enclosed_mult:
    '(' mult ')'
    | '(' enclosed_mult ')'
    ;

