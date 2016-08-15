grammar DSGRN;

/* options {
    language = Python2; 
} */

network:
    (statement)+ EOF
    ;

statement:
    ident ':' expr (essential)? ('\n')+
    ;

expr: 
    sum
    | mult_of_sums
    | term '*'? mult_of_sums
    ;

mult_of_sums:
    ('(' sum ')' ('*'? term|'*'? term '*'|'*')? )+
    ;

sum:
    (term|'(' term ')') ('+' (term|'(' term ')'))*
    ;

mult:
    term ((WSINLINE)+|'*'). term // white space is sometimes active
    | '(' term ')' '*'? term
    | term '*'? '(' term ')'
    | '(' term ')' '*'? '(' term ')'
    ;

term: 
    (NOT)? ident
    ;

ident:
    (CHAR)+
    ;

essential:
    ':' 'E'
    ;

NOT:
    '~'
    ;

CHAR: 
    [a-zA-Z0-9_]
    ;

WSINLINE:
    [ \t]
    ;

WS: 
    [ \t\n\r] + -> skip
    ;
