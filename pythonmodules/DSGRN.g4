grammar D2;

/* options {
    language = Python2; 
} */


/* Lexer rules */

IDENT:
    ([a-zA-Z0-9_])+
    ;

WS: 
    [ \t\n\r] + -> skip 
    ;


/* Parser rules */

network:
    statement (('\n')+ statement)* ('\n')* EOF  /* EOF needed to parse everything */
    ;

statement:
    IDENT ':' expr (modifier)?
    ;

modifier:   /* using this for essential */
    ':' IDENT
    ;

term: 
    ('~')? IDENT
    ;

expr:
    term
    | '(' expr ')'
    | expr '+' expr
    | expr ('*')? expr
    ;


